"""
Stripe Endpoint'
"""

from src.database import UserModel, TextbookModel, SaleModel
from src.service.auth_provider import require_login
from src.utils.http import HTTPStatusCode
from src.utils.api import (
  StripeMakeRequest, StripeMakeReply, _StripeMakeData,
  GenericReply
)

import json
import stripe
from flask import (
  request,
  url_for,
  current_app as app
)


basePath: str = '/api/v1/stripe'



@app.route(f'{basePath}/create-session', methods = ['POST'])
@require_login
def create_stripe_session_api(user: UserModel):
  req = StripeMakeRequest(request)
  
  if not req.cart:
    return GenericReply(
      message = 'Cart cannot be empty',
      status = HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST
  

  # Validate items exist
  found: list[TextbookModel] = TextbookModel.query.filter(TextbookModel.id.in_(req.cart)).all()
  if len(found) != len(req.cart):
    return GenericReply(
      message = 'Invalid items in cart',
      status = HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST
  

  # Generate SaleModel
  sale = SaleModel(user, found)

  
  # Create Item
  items: list[str] = []
  for txtbook in found:
    items.append(stripe.Price.create(
      currency = 'sgd',
      unit_amount = int(txtbook.price * 100),
      metadata = {'order_id': sale.id}
    )['id'])

  session = stripe.checkout.Session(
    line_items = [ {'price': i, 'quantity': 1} for i in items ],
    mode = 'payment',
    success_url = url_for('checkout/success', _external = True) + '?session_id={CHECKOUT_SESSION_ID}',
    cancel_url = url_for('checkout/cancel', _external = True)
  )

  return StripeMakeReply(
    message = 'Checkout session created',
    status = HTTPStatusCode.OK,
    data = _StripeMakeData(
      session_id = session['id'],
      public_key = app.config.get('STRIPE_PUBLIC_KEY', '')
    )
  ).to_dict(), HTTPStatusCode.OK




@app.route('/webhook', methods = ['POST'])
@require_login
def stripe_webhook_api(user: UserModel):
  payload = request.get_data()

  try:
    event = stripe.Event.construct_from(
      json.loads(payload),
      stripe.api_key
    )
  except ValueError:
    return GenericReply(
      message = 'Invalid payload',
      status = HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST


  # Handle the checkout.session.completed event
  match event.type:
    case 'payment_intent.succeeded':
      # Payment succeeded
      data = event.data.object
      print(data)
      ...

  return GenericReply(
    message = 'Webhook received',
    status = HTTPStatusCode.OK
  ).to_dict(), HTTPStatusCode.OK
