"""
Stripe Endpoint'
"""

from src.database import UserModel, TextbookModel, SaleModel, SaleInfo
from src.service.auth_provider import require_login
from src.utils.http import HTTPStatusCode
from src.utils.api import (
  StripeMakeRequest, StripeMakeReply, _StripeMakeData,
  GenericReply
)

import json
import stripe
from datetime import datetime
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

  
  # Create Item
  items: list[str] = []
  saleinfo: list[SaleInfo] = []
  for txtbook in found:
    cost = round(txtbook.price, 2) # TODO: Discount logic

    saleinfo.append(SaleInfo(cost, txtbook))
    items.append(stripe.Price.create(
      currency = 'sgd',
      unit_amount = int(cost * 100),
      product_data = {'name': f'{txtbook.title}'}
    )['id'])


  session = stripe.checkout.Session.create(
    line_items = [ {'price': i, 'quantity': 1} for i in items ],
    mode = 'payment',
    payment_method_types = ['card'],
    success_url = url_for('checkout_success', _external = True) + '?session_id={CHECKOUT_SESSION_ID}',
    cancel_url = url_for('checkout_cancel', _external = True)
  )


  # Generate SaleModel
  sale = SaleModel(user, saleinfo)
  sale.session_id = session['id']
  sale.save()

  return StripeMakeReply(
    message = 'Checkout session created',
    status = HTTPStatusCode.OK,
    data = _StripeMakeData(
      session_id = session['id'],
      public_key = app.config.get('STRIPE_PUBLIC_KEY', '')
    )
  ).to_dict(), HTTPStatusCode.OK




@app.route(f'{basePath}/webhook', methods = ['POST'])
def stripe_webhook_api():
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
    case 'checkout.session.completed':
      session = stripe.checkout.Session.retrieve(
        event.data.object['id'],
        expand = ['line_items']
      )
      
      # Query sale model
      sale = SaleModel.query.filter(SaleModel.session_id == session['id']).first()
      if not isinstance(sale, SaleModel):
        return GenericReply(
          message = 'Failed to locate sale',
          status = HTTPStatusCode.BAD_REQUEST
        ).to_dict(), HTTPStatusCode.BAD_REQUEST
      
      sale.session_id = None
      sale.paid = True
      sale.paid_at = datetime.utcnow()
      sale.save()
    
    case 'checkout.session.expired':
      session = stripe.checkout.Session.retrieve(
        event.data.object['id']
      )

      # Query sale model
      sale = SaleModel.query.filter(SaleModel.session_id == session['id']).first()
      if isinstance(sale, SaleModel):
        sale.delete()
      

  return GenericReply(
    message = 'Webhook received',
    status = HTTPStatusCode.OK
  ).to_dict(), HTTPStatusCode.OK
