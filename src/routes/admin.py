"""
Managing Admin-Only routes
"""

from functools import lru_cache
from src.service.auth_provider import require_admin
from src.utils.ext import utc_time
from sqlalchemy import and_, or_
from flask_sqlalchemy.query import Query
from src.database import (
  UserModel,
  SaleModel,
  TextbookModel
)

from src.utils.http import HTTPStatusCode
from src.utils.api import (
  AdminGraphGetRequest,
  AdminGetRequest, AdminGetReply,
  _UserGetData, _SaleGetData, _TextbookGetData,
  GenericReply
)

import numpy
from io import StringIO
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from thread import ParallelProcessing
from typing import Callable, Tuple, TypeVar, Any
from werkzeug.exceptions import BadRequest
from flask import (
  request,
  Response,
  render_template,
  current_app as app,
  stream_template_string
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


@lru_cache
def fetchAll(model: type[_TModel], dateRange: DateRange = None) -> Query:
  range_ = getDateRange(dateRange)
  return model.query.filter(and_(
    (range_[0] <= model.created_at),
    (model.created_at <= range_[1])
  ))


# @lru_cache
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
    processed = [
      (utc_time.unskip(f'{i}months', first), 0)
      for i in range(13 - len(processed), 1, -1)
    ] + processed


  # Split format data
  hashMap = {}
  for x, y in processed:
    curr: _TYValue | None = hashMap.get(x)
    if isinstance(y, (int, float)):
      # f'{x.month}/{x.year}'
      hashMap[x] = (curr + y) if isinstance(curr, (int, float)) else y
  
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

  # Write to stream
  f = StringIO()
  plt.savefig(f, format = 'svg')
  plt.close()

  return f




# Routes
@app.route(basePath)
@require_admin
def dashboard(user: UserModel):
  return render_template('(admin)/index.html')




# Graph generate endpoint
@app.route(f'{basePath}/graph', methods = ['POST'])
@require_admin
@lru_cache
def dashboard_graph(user: UserModel):
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




# Paginated endpoint
@app.route(f'{basePath}/get', methods = ['GET'])
@require_admin
def dashboard_get(user: UserModel):
  req = AdminGetRequest(request)
  model = (req.requestFor == 'User' and UserModel) \
          or (req.requestFor == 'Sale' and SaleModel) \
          or (req.requestFor == 'Textbook' and TextbookModel)

  if not model:
    raise BadRequest('Invalid requestFor')
  
  # Handle query
  dateRange: DateRange = (
    datetime.fromtimestamp(req.createdLower) if float('inf') != req.createdLower else utc_time.skip('1day'),
    datetime.fromtimestamp(req.createdUpper) if float('inf') != req.createdUpper else utc_time.skip('1day')
  )
  priceRange = (req.priceLower, req.priceUpper)

  if dateRange[0] > dateRange[1]:
    raise BadRequest('createdLower is larger than createdUpper')
  
  if priceRange[0] > priceRange[1]:
    raise BadRequest('priceLower is larger than priceUpper')


  # Build query
  queryPayload = []
  query: Query

  match req.requestFor:
    case 'User':
      queryPayload.append(or_(
        UserModel.id.contains(req.query),
        UserModel.username.contains(req.query)
      ))
      query = fetchAll(UserModel, dateRange)
    
    case 'Sale':
      query = fetchAll(SaleModel, dateRange)

    case 'Textbook':
      queryPayload.append(and_(
        priceRange[0] <= TextbookModel.price,
        TextbookModel.price <= priceRange[1]
      ))
      queryPayload.append(or_(
        TextbookModel.id.contains(req.query),
        TextbookModel.author_id.contains(req.query)
      ))
      query = fetchAll(TextbookModel, dateRange)
  
  if query and queryPayload:
    query = query.filter(or_(*queryPayload) if req.criteria == 'or' else and_(*queryPayload))

  
  # JSONify
  payload = []
  for entry in query.paginate(error_out = False):
    match req.requestFor:
      case 'User':
        payload.append(_UserGetData(
          entry.id,
          username = entry.username,
          privilege = entry.privilege,
          profile_image = entry.profile_image,
          created_at = entry.created_at.timestamp(),
          last_login = entry.last_login.timestamp()
        ))
        continue

      case 'Sale':
        payload.append(_SaleGetData(
          sale_id = entry.id,
          user_id = entry.user_id,
          textbook_ids = entry.textbook_ids.split(',')
        ))
        continue

      case 'Textbook':
        payload.append(_TextbookGetData(
          id = entry.id,
          author_id = entry.author_id,
          title = entry.title,
          description = entry.description,
          categories = entry.categories.split('|'),
          price = entry.price,
          discount = entry.discount,
          uri = entry.uri,
          status = entry.status,
          cover_image = entry.cover_image.uri if entry.cover_image else None,
          created_at = entry.created_at.timestamp(),
          updated_at = entry.updated_at.timestamp(),
        ))
        continue


  return AdminGetReply(
    message = f'Successfully fetched {req.requestFor}',
    status = HTTPStatusCode.OK,
    data = payload
  ).to_dict(), HTTPStatusCode.OK




# Users
@app.route(f'{basePath}/users', methods = ['GET'])
@require_admin
def dashboard_users(user: UserModel):
  return render_template('(admin)/user.html')




# Revenue
@app.route(f'{basePath}/revenue', methods = ['GET'])
@require_admin
def dashboard_revenue(user: UserModel):
  return render_template('(admin)/revenue.html')




# Textbooks
@app.route(f'{basePath}/textbooks', methods = ['GET'])
def dashboard_textbooks():
  return render_template('(admin)/textbook.html')
