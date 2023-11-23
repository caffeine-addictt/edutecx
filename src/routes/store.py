"""
Handles store routes
"""

from src.service import auth_provider
from src.database import UserModel, DocumentModel
from typing import List

import os
import stripe
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


# TODO: Add SQL sanitization and caching to all DB models
@app.route('/store')
def store():
  query = request.args.get('search', '')
  documents: List['DocumentModel'] = DocumentModel.query.all() # TODO: Filtering from query

  return render_template('(misc)/store.html')

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
