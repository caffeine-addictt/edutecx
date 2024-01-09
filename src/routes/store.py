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
