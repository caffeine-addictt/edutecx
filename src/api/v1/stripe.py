"""
Stripe Endpoint'
"""

from src.database import UserModel, TextbookModel, SaleModel, SaleInfo, DiscountModel
from src.service.auth_provider import require_login
from src.utils.http import HTTPStatusCode
from src.utils.api import (
  StripeMakeRequest, StripeMakeReply, _StripeMakeData,
  StripeCancelRequest, StripeCancelReply,
  StripeStatusRequest, StripeStatusReply, _StripeStatusData,
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
  

  # Validate discount
  discount = req.discount and DiscountModel.query.filter(DiscountModel.code == req.discount).first()
  if req.discount and not isinstance(discount, DiscountModel):
    return GenericReply(
      message = 'Invalid discount code',
      status = HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST
  

  # Validate items exist
  found: list[TextbookModel] = TextbookModel.query.filter(TextbookModel.id.in_(req.cart)).all()
  if len(found) != len(req.cart):
    return GenericReply(
      message = 'Invalid items in cart',
      status = HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST
  

  # Ensure discount is valid
  if discount:
    if discount.textbook and (not discount.textbook.id in found):
      return GenericReply(
        message = 'Invalid discount code',
        status = HTTPStatusCode.BAD_REQUEST
      ).to_dict(), HTTPStatusCode.BAD_REQUEST

    if discount.expires_at and (discount.expires_at < datetime.utcnow()):
      return GenericReply(
        message = 'Discount expired',
        status = HTTPStatusCode.BAD_REQUEST
      ).to_dict(), HTTPStatusCode.BAD_REQUEST
    
    if discount.limit and (discount.limit <= discount.used):
      return GenericReply(
        message = 'Discount limit reached',
        status = HTTPStatusCode.BAD_REQUEST
      ).to_dict(), HTTPStatusCode.BAD_REQUEST
  

  # Expire existing sessions
  for pending in user.pending_transactions:
    try:
      stripe.checkout.Session.expire(pending.session_id)
    except Exception as e:
      app.logger.error(f'Failed to expire session {pending.session_id}: {e}')
    pending.delete()

  
  # Create Item
  items: list[str] = []
  saleinfo: list[SaleInfo] = []
  for txtbook in found:
    if discount and discount.textbook and discount.textbook.id == txtbook.id:
      cost = round(txtbook.price * discount.multiplier * 100, 2)
    else:
      cost = round(txtbook.price * (discount.multiplier if discount else 1) * 100, 2)

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
    cancel_url = url_for('checkout_cancel', _external = True) + '?session_id={CHECKOUT_SESSION_ID}',
  )


  # Generate SaleModel
  SaleModel(
    user = user,
    saleinfo = saleinfo,
    session_id = session['id'],
    discount = discount or None
  ).save()

  return StripeMakeReply(
    message = 'Checkout session created',
    status = HTTPStatusCode.OK,
    data = _StripeMakeData(
      session_id = session['id'],
      public_key = app.config.get('STRIPE_PUBLIC_KEY', '')
    )
  ).to_dict(), HTTPStatusCode.OK




@app.route(f'{basePath}/cancel', methods = ['POST'])
@require_login
def stripe_cancel_api(user: UserModel):
  req = StripeCancelRequest(request)

  pending = [ i for i in user.pending_transactions if i.session_id == req.session_id ]
  if len(pending) == 0:
    return GenericReply(
      message = 'Pending transaction not found',
      status = HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST
  
  pending = pending[0]

  try:
    stripe.checkout.Session.expire(pending.session_id)

  except Exception as e:
    app.logger.error(f'Failed to expire session {pending.session_id}: {e}')
    return GenericReply(
      message = 'Failed to expire session',
      status = HTTPStatusCode.INTERNAL_SERVER_ERROR
    ).to_dict(), HTTPStatusCode.INTERNAL_SERVER_ERROR

  pending.delete()

  return StripeCancelReply(
    message = 'Checkout cancelled',
    status = HTTPStatusCode.OK
  ).to_dict(), HTTPStatusCode.OK




@app.route(f'{basePath}/status', methods = ['POST'])
@require_login
def stripe_status_api(user: UserModel):
  req = StripeStatusRequest(request)

  transactions = set([ *user.pending_transactions, *user.transactions ])
  for transaction in transactions:
    if transaction.session_id == req.session_id:
      return StripeStatusReply(
        message = 'Fetched checkout status',
        status = HTTPStatusCode.OK,
        data = _StripeStatusData(
          paid = transaction.paid,
          total_cost = transaction.total_cost,
          user_id = user.id,
          paid_at = transaction.paid_at.timestamp(),
          created_at = transaction.created_at.timestamp()
        )
      ).to_dict(), HTTPStatusCode.OK


  return GenericReply(
    message = 'Transaction not found',
    status = HTTPStatusCode.BAD_REQUEST
  ).to_dict(), HTTPStatusCode.BAD_REQUEST




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
