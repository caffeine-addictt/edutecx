"""
Managing Admin-Only routes
"""

from src.utils.http import Parser
from src.utils.caching import customCache
from src.service.auth_provider import require_admin
from src.utils.ext import utc_time
from sqlalchemy import and_
from src.database import (
  UserModel,
  SaleModel,
  TextbookModel
)

from src.utils.http import HTTPStatusCode
from src.utils.api import (
  AdminGetRequest, AdminGetReply, _AdminGetData,
  GenericReply
)

import os
import re
import numpy
from datetime import datetime
import matplotlib.pyplot as plt
from thread import ParallelProcessing
from src.service.cdn_provider import _dirCheck, GraphFileLocation
from typing import Callable, Tuple, TypeVar, Any
from werkzeug.exceptions import InternalServerError
from flask import (
  abort,
  request,
  render_template,
  current_app as app
)


# Config
basePath: str = '/dashboard'

_TModel = TypeVar('_TModel', UserModel, SaleModel, TextbookModel)
_TYValue = TypeVar('_TYValue')
_YFunc = Callable[[_TModel], _TYValue]
LabelX = int
LabelY = int

DateRange = Tuple[datetime, datetime] | datetime | None




# Helper functions
def getDateRange(dateRange: DateRange = None) -> Tuple[datetime, datetime]:
  if isinstance(dateRange, datetime):
    return (
      dateRange,
      utc_time.skip('1y', dateRange)
    )

  if (not isinstance(dateRange, tuple)):
    return (utc_time.unskip('6months'), utc_time.skip('6months'))
  
  return dateRange


@customCache
def fetchAll(model: type[_TModel], dateRange: DateRange = None) -> list[_TModel]:
  range_ = getDateRange(dateRange)
  return model.query.filter(and_(
    (range_[0] <= model.created_at),
    (model.created_at <= range_[1])
  )).all()


def getURI(filename: str) -> str:
  if domain := app.config.get('DOMAIN'):
    return '/public/graphs/' + filename
  raise InternalServerError('Domain not configured')


@customCache
def drawGraph(
  model: type[_TModel],
  axisY: _YFunc[_TModel, _TYValue],
  title: str,
  nameExtra: str,
  labelCount: Tuple[LabelX, LabelY] = (6, 10),
  ylabel: str = 'Count',
  dateRange: DateRange = None
) -> str:
  """
  Draw the graph to an image

  Parameters
  ----------
  `model: Model`, required
    The model to draw a graph on
  
  `axisY: (model) -> Any`, required
    The function to calculate an individual Y-Axis plot point
  
  `nameExtra: str`, required
    Extra name to not collide with previous generations
  
  `labelCount: tuple[Xint, Yint]`, optional (defaults to tuple(6, 10))
    How many graph labels per axis
  
  `ylabel: str`, optional (defaults to 'Count')
    The Y-Axis title
  
  `dateRange: DateRange`, optional (defaults to None)
    The year to consider, else defaults to the past 12 months
  
  Returns
  -------
  uri: str
  """
  XValue = datetime

  fetched: list[_TModel] = fetchAll(model, dateRange)
  processed: list[Tuple[datetime, Any]] = []

  try:
    def _processor(m: _TModel) -> Tuple[XValue, _TYValue]:
      return (
        m.created_at,
        axisY(m)
      )
    process = ParallelProcessing(_processor, dataset = fetched, max_threads = 4, daemon = True)
    process.start()
    processed = process.get_return_values()
  
  except Exception:
    pass

  if len(processed) < 12:
    # Populate dummy data
    first = processed[0][0] if len(processed) >= 1 else None
    app.logger.error(processed)
    processed = [
      (utc_time.unskip(f'{i}months', first), 0)
      for i in range(13 - len(processed), 1, -1)
    ] + processed
    app.logger.error('hi')


  # Split format data
  hashMap = {}
  for x, y in processed:

    curr: _TYValue | None = hashMap.get(x)
    if isinstance(y, (int, float)):
      hashMap[f'{x.month}/{x.year}'] = (curr + y) if isinstance(curr, (int, float)) else y
  
  # Sort
  hashMap = dict(sorted(
    hashMap.items(),
    key = lambda a: int(''.join(a[0].split('/')[::-1]))
  ))
  
  # Plotting
  plt.figure(figsize = (16, 11))
  plt.plot(tuple(hashMap.keys()), tuple(hashMap.values()))

  # Curl X and Y points
  _width = len(hashMap)
  _height = max(hashMap.values())

  app.logger.debug(f'{_width, _height, _width // labelCount[0], _height // labelCount[1]}')
  plt.xticks(numpy.arange(0, _width + 1, max(1, round(_width / labelCount[0]))), minor = True)
  plt.yticks(numpy.arange(0, _height + 1, max(1, round(_height / labelCount[1]))), minor = True)

  # Label
  plt.title(title)
  plt.xlabel('Time')
  plt.ylabel(ylabel)
  plt.tick_params('both')
  plt.autoscale(True, 'both')


  # Upload
  _dirCheck()
  filename = str(model.id) + '_' + re.compile(r'[^a-zA-Z0-9-]').sub('', nameExtra) + '.svg'
  plt.savefig(os.path.join(GraphFileLocation, filename))
  plt.close()

  return getURI(filename)




# Routes
@app.route(basePath)
@require_admin
def dashboard(user: UserModel):
  
  return render_template('(admin)/index.html', data = Parser(
    user = user
  ))




# Graph generate endpoint
@app.route(f'{basePath}/graph', methods = ['POST'])
@require_admin
def dashboard_graph(user: UserModel):
  req = AdminGetRequest(request)

  match req.graphFor:
    case 'User':
      uri = drawGraph(
        UserModel,
        lambda _: 1,
        'Users Accounts Created Over a 12 Month Period',
        'created',
        ylabel = 'Accounts Created'
      )
    
    case 'Revenue':
      uri = drawGraph(
        SaleModel,
        lambda model: model.total_cost,
        'Revenue Over a 12 Month Period',
        'revenue',
        ylabel = 'Total Revenue ($)'
      )
    
    case 'Textbook':
      uri = drawGraph(
        TextbookModel,
        lambda _: 1,
        'Textbooks Created Over a 12 Month Period',
        'created',
        ylabel = 'Textbooks Created'
      )
    
    case _:
      return GenericReply(
        message = 'Invalid graphFor',
        status = HTTPStatusCode.BAD_REQUEST
      ).to_dict(), HTTPStatusCode.BAD_REQUEST
  
  return AdminGetReply(
    message = 'Successfully generated graph',
    status = HTTPStatusCode.OK,
    data = _AdminGetData(
      uri = uri
    )
  ).to_dict(), HTTPStatusCode.OK




# Users
@app.route(f'{basePath}/users', methods = ['GET'])
@require_admin
def dashboard_users(user: UserModel):
  return render_template('(admin)/user.html', data = Parser(
    users = fetchAll(UserModel)
  ))




# Revenue
@app.route(f'{basePath}/revenue', methods = ['GET'])
@require_admin
def dashboard_revenue(user: UserModel):
  return render_template('(admin)/sale.html', data = Parser(
    sales = fetchAll(SaleModel)
  ))




# Textbooks
@app.route(f'{basePath}/textbooks', methods = ['GET'])
def dashboard_textbooks():
  return render_template('(admin)/textbook.html', data = Parser(
    textbooks = fetchAll(TextbookModel)
  ))
