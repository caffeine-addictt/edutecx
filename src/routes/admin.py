"""
Managing Admin-Only routes
"""

from src.utils.caching import customCache
from src.utils.http import Parser, escape_id
from src.service.auth_provider import require_admin
from src.utils.http import HTTPStatusCode
from src.database import (
  UserModel,
  SaleModel,
  TextbookModel
)

import os
import re
import numpy
import matplotlib.pyplot as plt
from thread import ParallelProcessing
from src.service.cdn_provider import _dirCheck, GraphFileLocation
from typing import Callable, Tuple, TypeVar, Literal
from flask import (
  abort,
  request,
  render_template,
  current_app as app
)


# Config
basePath: str = '/dashboard'

_Model = Literal['UserModel', 'SaleModel', 'TextbookModel']
_TModel = TypeVar('_TModel', UserModel, SaleModel, TextbookModel)
_TYValue = TypeVar('_TYValue')
_YFunc = Callable[[_TModel], _TYValue]
LabelX = int
LabelY = int




# Helper functions
@customCache
def fetchAll(model: _Model) -> list[_TModel]:
  match model:
    case 'UserModel':
      return UserModel.query.all()
    case 'SaleModel':
      return SaleModel.query.all()
    case 'TextbookModel':
      return TextbookModel.query.all()


def getURI(filename: str) -> str:
  if domain := os.getenv('DOMAIN'):
    return domain + '/public/graphs/' + filename
  abort(HTTPStatusCode.INTERNAL_SERVER_ERROR)


@customCache
def drawGraph(
  model: _Model,
  axisY: _YFunc[_TModel, _TYValue],
  nameExtra: str,
  labelCount: Tuple[LabelX, LabelY] = (5, 10),
  ylabel: str = 'Count'
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
  
  `labelCount: tuple[Xint, Yint]`, optional (defaults to tuple(5, 10))
    How many graph labels per axis
  
  `ylabel: str`, required
    The Y-Axis title
  
  Returns
  -------
  uri: str
  """
  XValue = str

  fetched = fetchAll(model)

  def _processor(m: _TModel) -> Tuple[XValue, _TYValue]:
    return (
      m.created_at.strftime('%m'),
      axisY(m)
    )
  process = ParallelProcessing(_processor, dataset = fetched, max_threads = 4, daemon = True)
  process.start()
  processed: list[Tuple[XValue, _TYValue]] = process.get_return_values()


  # Split format data
  hashMap = {}
  for x, y in processed:

    curr: _TYValue | None = hashMap.get(x)
    if isinstance(y, (int, float)):
      hashMap[x] = (curr + y) if isinstance(curr, (int, float)) else y
  
  # Sort
  hashMap = dict(sorted(hashMap.items()))
  
  # Plotting
  plt.plot(tuple(hashMap.keys()), tuple(hashMap.values()))

  # Curl X and Y points
  _width = len(hashMap)
  _height = max(hashMap.values())
  plt.xticks(numpy.arange(0, _width + 1, _width // labelCount[0]))
  plt.yticks(numpy.arange(0, _height + 1, _height // labelCount[1]))

  # Label
  plt.xlabel('Date')
  plt.ylabel(ylabel)


  # Upload
  _dirCheck()
  filename = model + '_' + re.compile(r'[^a-zA-Z0-9-]').sub('', nameExtra) + '.png'
  plt.savefig(os.path.join(GraphFileLocation, filename))
  plt.close()

  return getURI(filename)




# Routes
@app.route(basePath)
@require_admin
def dashboard(user: UserModel):
  
  return render_template('(admin)/index.html', data = Parser(
    
  ))




# Users
@app.route(f'{basePath}/users')
def dashboard_users():
  # graph = drawGraph(UserModel)

  return render_template('(admin)/user_list.html', data = Parser(

  ))

@app.route(f'{basePath}/users/<string:id>')
def dashboard_user(id: str):
  id = escape_id(id)

  return render_template('(admin)/user.html', data = Parser(
    id = id, typeof = type(id)
  ))




# Revenue
@app.route(f'{basePath}/sales')
def dashboard_sales():
  # graph = drawGraph(SaleModel)

  return render_template('(admin)/sale_list.html', data = Parser(

  ))

@app.route(f'{basePath}/sales/<string:id>')
def dashboard_sale(id: str):
  id = escape_id(id)

  return render_template('(auth)/sale.html', data = Parser(

  ))




# Textbooks
@app.route(f'{basePath}/textbooks', methods = ['GET'])
def dashboard_textbooks():
  graphFilename = drawGraph(
    'TextbookModel',
    lambda _: 1,
    'created',
    ylabel = 'Created'
  )

  return render_template('(admin)/textbook_list.html', graphURI = graphFilename)
