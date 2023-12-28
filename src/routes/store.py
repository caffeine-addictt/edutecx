"""
Handles store routes
"""

from src.service import auth_provider
from src.database import UserModel, TextbookModel
from src.utils.http import HTTPStatusCode
from werkzeug.exceptions import BadRequest
from src.utils.api import (
  StoreGetRequest, StoreGetReply, _TextbookGetData
)

import re
import stripe
from datetime import datetime
from src.utils.ext import utc_time
from src.utils.caching import customCache

from sqlalchemy import and_, or_
from flask_sqlalchemy.pagination import Pagination
from flask import (
  flash,
  request,
  render_template,
  current_app as app
)

stripe.api_key = app.config.get('STRIPE_API_KEY')




# Store
@app.route('/store')
def store():
  return render_template('(misc)/store.html')


# Store Get
@app.route('/store/get', methods = ['GET'])
def store_get():
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
  discountRange = (req.discountLower, req.discountUpper)

  if dateRange[0] > dateRange[1]:
    raise BadRequest('createdLower is larger than createdUpper')
  
  if priceRange[0] > priceRange[1]:
    raise BadRequest('priceLower is larger than priceUpper')
  
  if discountRange[0] > discountRange[1]:
    raise BadRequest('discountLower is larger than discountUpper')
  

  # Build query
  filterResult = filterTextbooks(
    criteria = req.criteria,
    filterPayload = [
      and_(
        dateRange[0] <= TextbookModel.created_at,
        TextbookModel.created_at <= dateRange[1]
      ),
      and_(
        priceRange[0] <= TextbookModel.price,
        TextbookModel.price <= priceRange[1]
      ),
      and_(
        discountRange[0] <= TextbookModel.discount,
        TextbookModel.discount <= discountRange[1]
      ),
      or_(*[
        TextbookModel.categories.contains(category)
        for category in categories
      ]),
      TextbookModel.title.contains(req.query)
    ],
    page = req.page
  )

  # Compile data
  compiled: list[_TextbookGetData] = [
    _TextbookGetData(
      id = textbook.id,
      uri = textbook.uri,
      status = textbook.status,
      author_id = textbook.author_id,
      title = textbook.title,
      description = textbook.description,
      categories = textbook.categories,
      price = textbook.price,
      discount = textbook.discount,
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








@app.route('/cart')
@auth_provider.require_login
def cart(user: UserModel):
  return render_template('(misc)/cart.html')


@app.route('/checkout', methods = ['GET', 'POST'])
@auth_provider.require_login
def checkout(user: UserModel):
  form = None

  if request.method == 'POST' and form:
    # TODO: STRIPE https://stripe.com/docs/checkout/quickstart?lang=python
    try:
      checkout_session = stripe.checkout.Session.create(
        line_items = [{

        }],
        mode = 'payment',
        success_url = '',
        cancel_url = ''
      )

      # return redirect() # TODO: Redirect to stripe
    except Exception as e:
      flash(str(e))

  return render_template('(misc)/checkout.html')




# Functions
@customCache
def filterTextbooks(
  criteria: str,
  filterPayload: list,
  page: int
) -> Pagination:
  return TextbookModel.query.filter(
    and_(*filterPayload) if criteria == 'and' else or_(*filterPayload)
  ).paginate(page = page, error_out = False)
