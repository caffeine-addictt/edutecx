"""
Sale Endpoint
"""

from src import limiter
from flask_limiter import util
from src.utils.ext import utc_time
from src.utils.http import HTTPStatusCode
from src.database import SaleModel, UserModel
from src.service.auth_provider import require_login, require_admin
from src.utils.api import (
  SaleListRequest,
  SaleListReply,
  SaleGetRequest,
  SaleGetReply,
  _SaleGetData,
  GenericReply,
)

from datetime import datetime
from functools import lru_cache
from sqlalchemy import or_, and_
from flask import request, current_app as app


# Routes
basePath: str = '/api/v1/sale'
auth_limit = limiter.shared_limit(
  '100 per hour', scope=lambda _: request.host, key_func=util.get_remote_address
)

DateRange = tuple[datetime, datetime]


@app.route(f'{basePath}/list', methods=['GET'])
@auth_limit
@require_admin
def sale_list_api(user: UserModel):
  req = SaleListRequest(request)

  # Handle query
  req.createdLower = float(req.createdLower or 0)
  req.createdUpper = float(req.createdUpper or 0)
  req.priceLower = float(req.priceLower or 0)
  req.priceUpper = float(req.priceUpper or 0)

  dateRange: DateRange = (
    datetime.fromtimestamp(req.createdLower)
    if float('inf') != req.createdLower
    else utc_time.skip('1day'),
    datetime.fromtimestamp(req.createdUpper)
    if float('inf') != req.createdUpper
    else utc_time.skip('1day'),
  )
  priceRange = (req.priceLower, req.priceUpper)

  if dateRange[0] > dateRange[1]:
    return GenericReply(
      message='createdLower is larger than createdUpper',
      status=HTTPStatusCode.BAD_REQUEST,
    ).to_dict(), HTTPStatusCode.BAD_REQUEST

  if priceRange[0] > priceRange[1]:
    return GenericReply(
      message='priceLower is larger than priceUpper', status=HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST

  if not req.query or req.query == 'None':
    req.query = ''

  # Build query
  query = [
    and_(dateRange[0] <= SaleModel.created_at, SaleModel.created_at <= dateRange[1]),
    or_(
      SaleModel.id.contains(req.query),
      SaleModel.user_id.contains(req.query),
      SaleModel.discount_id.contains(req.query),
    ),
  ]

  filtered = SaleModel.query.filter(
    and_(*query) if req.criteria == 'and' else or_(*query)
  ).paginate(page=req.page, error_out=False)

  return SaleListReply(
    message='Successfully fetched sales',
    status=HTTPStatusCode.OK,
    data=[
      _SaleGetData(
        type=i.type,
        sale_id=i.id,
        user_id=i.user_id,
        discount_id=i.discount_id if i.discount_id else None,
        textbook_ids=[i.split(':')[0] for i in (i.textbook_ids).split(',')]
        if i.textbook_ids
        else [],
        paid=i.paid,
        paid_at=i.paid_at,
        total_cost=i.total_cost,
      )
      for i in filtered.items
    ],
  ).to_dict(), HTTPStatusCode.OK


@app.route(f'{basePath}/get', methods=['GET'])
@auth_limit
@require_login
def sale_get_api(user: UserModel):
  req = SaleGetRequest(request)

  sale = SaleModel.query.filter(SaleModel.id == req.sale_id).first()
  if not isinstance(sale, SaleModel):
    return GenericReply(
      message='Unable to locate sale', status=HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST

  if (user.privilege != 'Admin') or (sale.user_id != user.id):
    return GenericReply(
      message='Unauthorized', status=HTTPStatusCode.UNAUTHORIZED
    ).to_dict(), HTTPStatusCode.UNAUTHORIZED

  return SaleGetReply(
    message='Successfully fetched sale',
    status=HTTPStatusCode.OK,
    data=_SaleGetData(
      type=sale.type,
      sale_id=sale.id,
      user_id=user.id,
      discount_id=sale.discount_id if sale.discount_id else None,
      textbook_ids=list(sale.textbooks.keys()),
      paid=sale.paid,
      paid_at=sale.paid_at.timestamp() if sale.paid_at else None,
      total_cost=sale.total_cost,
    ),
  ).to_dict(), HTTPStatusCode.OK
