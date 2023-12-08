"""
Handles store routes
"""

from src.service import auth_provider
from src.database import UserModel, TextbookModel
from src.utils.http import HashableDict
from typing import List, Optional

import os
import stripe
from functools import cache

from sqlalchemy import and_, or_
from flask_sqlalchemy.pagination import Pagination
from flask import (
  g,
  abort,
  flash,
  session,
  request,
  render_template,
  current_app as app
)

stripe.api_key = app.config.get('STRIPE_API_KEY') # TODO: Add to config.py and .env


@app.route('/store')
@auth_provider.optional_login
def store(user: Optional[UserModel]):
  # Get the search params
  page = request.args.get('page', 1, type = int)
  criteria = request.args.get('criteria', 'or', type = lambda x: (x.lower() == 'and' and 'and') or 'or') # 'and' or 'or'
  queryString = request.args.get('query', '', type = str)
  priceLimit = request.args.get('price_limit', float('inf'), type = float)
  categoryFilter = request.args.get('category', [], type = lambda x: x.lower().split(','))

  # Filter
  textbooks: Pagination = filterTextbooks(
    criteria = criteria,
    filterExpression = HashableDict(
      queryString = TextbookModel.title.like(f'%{queryString}%'),
      priceLimit = (TextbookModel.price < priceLimit),
      *{i: TextbookModel.categories.like(f'%{category}%') for i, category in enumerate(categoryFilter)}
    ),
    page = page
  )

  return render_template('(misc)/store.html', textbooks = textbooks)

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
@cache
def filterTextbooks(
  criteria: str,
  filterExpression: HashableDict,
  page: int
) -> Pagination:
  return TextbookModel.query.filter(
    and_(*filterExpression.values()) if criteria == 'and' else or_(*filterExpression.values())
  ).paginate(page = page, error_out = False)
  
