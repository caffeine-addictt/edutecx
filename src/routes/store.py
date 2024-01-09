"""
Handles store routes
"""

from src.utils.http import escape_id
from src.service import auth_provider
from src.utils.http import HTTPStatusCode
from werkzeug.exceptions import BadRequest
from src.database import UserModel, TextbookModel
from src.utils.api import (
  StoreGetRequest, StoreGetReply, _TextbookGetData
)

import re
from datetime import datetime
from functools import lru_cache
from src.utils.ext import utc_time
from src.utils.http import HashableDict

from sqlalchemy import and_, or_
from flask_sqlalchemy.pagination import Pagination
from flask import (
  flash,
  request,
  render_template,
  current_app as app
)








# Store
@app.route('/store')
@auth_provider.optional_login
def store(user: UserModel | None):
  return render_template('(store)/store.html')




# Store focus view
@app.route('/store/<id:string>')
@auth_provider.optional_login
def store_focused(user: UserModel | None, textbook_id: str):
  textbook_id = escape_id(textbook_id)
  textbook = TextbookModel.query.filter(TextbookModel.id == textbook_id).first_or_404()
  return render_template('(store)/store_focused.html', textbook = textbook, user = user)


# Store Get
@app.route('/store/get', methods = ['GET'])
@auth_provider.optional_login
def store_get(user: UserModel | None):
  req = StoreGetRequest(request)

  # Handle query
  # regex to parse only proper categories
  categories = re.match(re.compile(r'^[a-zA-Z-_,]$'), req.categories)
  if (not categories) or (categories != req.categories):
    raise BadRequest('Invalid characters in category filter')
  categories = str(categories).split(',')

  dateRange: tuple[datetime, datetime] = (
    datetime.fromtimestamp(req.createdLower) if float('inf') != req.createdLower else utc_time.skip('1day'),
    datetime.fromtimestamp(req.createdUpper) if float('inf') != req.createdUpper else utc_time.skip('1day')
  )
  priceRange = (req.priceLower, req.priceUpper)

  if dateRange[0] > dateRange[1]:
    raise BadRequest('createdLower is larger than createdUpper')
  
  if priceRange[0] > priceRange[1]:
    raise BadRequest('priceLower is larger than priceUpper')
  

  # Build query
  filterResult = filterTextbooks(
    criteria = req.criteria,
    filterPayload = HashableDict(
      one = and_(
        dateRange[0] <= TextbookModel.created_at,
        TextbookModel.created_at <= dateRange[1]
      ),
      two = and_(
        priceRange[0] <= TextbookModel.price,
        TextbookModel.price <= priceRange[1]
      ),
      three = or_(*[
        TextbookModel.categories.contains(category)
        for category in categories
      ]),
      four = TextbookModel.title.contains(req.query)
    ),
    page = req.page
  )

  # Compile data
  compiled: list[_TextbookGetData] = [
    _TextbookGetData(
      id = textbook.id,
      uri = textbook.uri,
      status = textbook.upload_status,
      author_id = textbook.author_id,
      title = textbook.title,
      description = textbook.description,
      categories = textbook.categories,
      price = textbook.price,
      cover_image = textbook.cover_image,
      created_at = textbook.created_at.timestamp(),
      updated_at = textbook.updated_at.timestamp()
    )
    for textbook in filterResult
  ]

  return StoreGetReply(
    message = 'Successfully fetched textbooks',
    status = HTTPStatusCode.OK,
    data = compiled
  ).to_dict(), HTTPStatusCode.OK




# Cart GET
@app.route('/cart', methods = ['GET'])
@auth_provider.require_login
def cart(user: UserModel):
  return render_template('(store)/cart.html')




@app.route('/checkout-success', methods = ['GET'])
@auth_provider.require_login
def checkout_success(user: UserModel):
  return render_template('(store)/checkout_success.html')




@app.route('/checkout-cancel', methods = ['GET'])
@auth_provider.require_login
def checkout_cancel(user: UserModel):
  return render_template('(store)/checkout_cancel.html')




@app.route('/pricing', methods = ['GET'])
@auth_provider.optional_login
def pricing_page(user: UserModel | None):
  return render_template('(store)/pricing.html')




# Functions
@lru_cache
def filterTextbooks(
  criteria: str,
  filterPayload: HashableDict,
  page: int
) -> Pagination:
  return TextbookModel.query.filter(
    and_(*filterPayload) if criteria == 'and' else or_(*filterPayload)
  ).paginate(page = page, error_out = False)
