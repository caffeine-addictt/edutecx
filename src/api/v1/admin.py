"""
Admin-Only Endpoints
"""

import numpy
import logging
from io import StringIO
from sqlalchemy import and_
from datetime import datetime
import matplotlib.pyplot as plt
from functools import cache
import matplotlib.dates as mdates
from thread import ParallelProcessing
from flask_sqlalchemy.query import Query
from typing import Callable, Tuple, TypeVar, Any
from flask import (
  request,
  Response,
  current_app as app,
  stream_template_string
)

from src.database import UserModel, SaleModel, TextbookModel
from src.utils.http import HTTPStatusCode
from src.service import auth_provider
from src.utils.ext import utc_time
from src.utils.api import (
  AdminGraphGetRequest,
  AdminGetRequest, AdminGetReply,
  _UserGetData, _SaleGetData, _TextbookGetData,
  GenericReply
)


# Mute matplotlib INFO stdout
logging.getLogger('matplotlib').setLevel(logging.WARNING)

# Config
basePath: str = '/api/v1/admin'

_TModel = TypeVar('_TModel', UserModel, SaleModel, TextbookModel)
_TYValue = TypeVar('_TYValue')
_YFunc = Callable[[_TModel], _TYValue]
LabelX = int
LabelY = int

DateRange = Tuple[datetime, datetime] | datetime | None


# Helper Functions
def getDateRange(dateRange: DateRange = None) -> Tuple[datetime, datetime]:
  if isinstance(dateRange, datetime):
    return (
      dateRange,
      utc_time.skip('1y', dateRange)
    )

  if (not isinstance(dateRange, tuple)):
    return (utc_time.unskip('6months'), utc_time.skip('6months'))
  
  return dateRange

@cache
def fetchAll(model: type[_TModel], dateRange: DateRange = None) -> Query:
  range_ = getDateRange(dateRange)
  return model.query.filter(and_(
    (range_[0] <= model.created_at),
    (model.created_at <= range_[1])
  ))


# Drawing
def drawGraph(
  model: type[_TModel],
  axisY: _YFunc[_TModel, _TYValue],
  title: str,
  labelCount: Tuple[LabelX, LabelY] = (6, 10),
  ylabel: str = 'Count',
  dateRange: DateRange = None
) -> StringIO:
  """
  Draw the graph to an image

  Parameters
  ----------
  `model: Model`, required
    The model to draw a graph on
  
  `axisY: (model) -> Any`, required
    The function to calculate an individual Y-Axis plot point
  
  `title: str`, required
  
  `labelCount: tuple[Xint, Yint]`, optional (defaults to tuple(6, 10))
    How many graph labels per axis
  
  `ylabel: str`, optional (defaults to 'Count')
    The Y-Axis title
  
  `dateRange: DateRange`, optional (defaults to None)
    The year to consider, else defaults to the past 12 months
  
  Returns
  -------
  svg: StringIO
  """
  XValue = datetime

  fetched: list[_TModel] = fetchAll(model, dateRange).all()
  processed: list[Tuple[XValue, _TYValue | int]] = []

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
    processed = [
      (utc_time.unskip(f'{i}months', first), 0)
      for i in range(13 - len(processed), 1, -1)
    ] + processed


  # Split format data
  hashMap = {}
  for x, y in processed:
    curr: _TYValue | None = hashMap.get(x)
    if isinstance(y, (int, float)):
      hashMap[f'{x.month}/{x.year}'] = (curr + y) if isinstance(curr, (int, float)) else y
  
  # Plotting
  plt.figure(figsize = (16, 11))
  plt.plot(tuple(hashMap.keys()), tuple(hashMap.values()))

  # Curl X and Y points
  _width = len(hashMap)
  _height = max(hashMap.values())

  plt.xticks(numpy.arange(0, _width + 1, max(1, round(_width / labelCount[0]))), minor = True)
  plt.yticks(numpy.arange(0, _height + 1, max(1, round(_height / labelCount[1]))), minor = True)

  # Format X-Axis dates
  plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%Y'))

  # Label
  plt.title(title)
  plt.xlabel('Time')
  plt.ylabel(ylabel)
  plt.tick_params('both')
  plt.autoscale(True, 'both')

  # Set Y-Axis Limit
  plt.ylim([0, _height + 1])

  # Write to stream
  f = StringIO()
  plt.savefig(f, format = 'svg')
  plt.close()

  return f


@app.route(f'{basePath}/draw', methods = ['POST'])
@auth_provider.require_admin
def admin_draw_api(_: UserModel):
  req = AdminGraphGetRequest(request)

  match req.graphFor:
    case 'User':
      svg = drawGraph(
        UserModel,
        lambda _: 1,
        'Users Accounts Created Over a 12 Month Period',
        ylabel = 'Accounts Created'
      )
    
    case 'Revenue':
      svg = drawGraph(
        SaleModel,
        lambda model: model.total_cost,
        'Revenue Over a 12 Month Period',
        ylabel = 'Total Revenue ($)'
      )
    
    case 'Textbook':
      svg = drawGraph(
        TextbookModel,
        lambda _: 1,
        'Textbooks Created Over a 12 Month Period',
        ylabel = 'Textbooks Created'
      )
    
    case _:
      return GenericReply(
        message = 'Invalid graphFor',
        status = HTTPStatusCode.BAD_REQUEST
      ).to_dict(), HTTPStatusCode.BAD_REQUEST

  return Response(
    stream_template_string(svg.getvalue()),
    status = HTTPStatusCode.OK,
    mimetype = 'image/svg+xml'
  )
