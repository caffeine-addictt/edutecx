"""
Stripe Endpoint'
"""

from src import limiter
from flask_limiter import util

from sqlalchemy import and_
from src.database import UserModel, TextbookModel, SaleModel, SaleInfo, DiscountModel
from src.service.auth_provider import require_login
from src.utils.http import HTTPStatusCode
from src.utils.api import (
  StripeSubscriptionRequest, StripeSubscriptionReply, _StripeSubscriptionData,
  StripeCheckoutRequest, StripeCheckoutReply, _StripeCheckoutData,
  StripeSubscriptionCancelRequest, StripeSubscriptionCancelReply,
  StripeExpireRequest, StripeExpireReply,
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




@app.route(f'{basePath}/create-subscription-session', methods = ['POST'])
@require_login
def create_stripe_subscription_session_api(user: UserModel):
  req = StripeSubscriptionRequest(request)

  if user.membership != 'Free':
    return GenericReply(
      message = 'Already subscribed',
      status = HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST
  
  # Validate discount
  discount = (req.discount != 'None') and DiscountModel.query.filter(DiscountModel.code == req.discount).first()
  if (req.discount != 'None') and not isinstance(discount, DiscountModel):
    return GenericReply(
      message = 'Invalid discount code',
      status = HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST
  
  if discount:
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
  
  
  # Create Price
  total_cost: float = round(app.config.get('UNLIMITED_TIER_PRICE', 0), 2)
  price = stripe.Price.create(
    currency = 'sgd',
    recurring = {
      'interval': 'month',
      'interval_count': 1
    },
    unit_amount = int(total_cost * 100),
    product_data = {'name': 'EduTecX Unlimited Tier'}
  )
  
  # Create Session
  session = stripe.checkout.Session.create(
    line_items = [{
      'price': price['id'],
      'quantity': 1
    }],
    mode = 'subscription',
    success_url = url_for('checkout_success', _external = True) + '?session_id={CHECKOUT_SESSION_ID}',
    cancel_url = url_for('checkout_cancel', _external = True) + '?session_id={CHECKOUT_SESSION_ID}'
  )

  SaleModel(
    user = user,
    saleType = 'Subscription',
    total_cost = total_cost,
    session_id = session['id'],
    discount = discount or None
  ).save()

  return StripeSubscriptionReply(
    message = 'Successfully created subscription',
    status = HTTPStatusCode.OK,
    data = _StripeSubscriptionData(
      session_id = session['id'],
      public_key = app.config.get('STRIPE_PUBLIC_KEY', '')
    )
  ).to_dict(), HTTPStatusCode.OK




@app.route(f'{basePath}/create-checkout-session', methods = ['POST'])
@require_login
def create_stripe_checkout_session_api(user: UserModel):
  req = StripeCheckoutRequest(request)
  
  if not req.cart:
    return GenericReply(
      message = 'Cart cannot be empty',
      status = HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST
  

  # Validate discount
  discount = (req.discount != 'None') and DiscountModel.query.filter(DiscountModel.code == req.discount).first()
  if (req.discount != 'None') and not isinstance(discount, DiscountModel):
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
  

  # Ensure textbook is not already owned
  if any((user in i.bought_by) for i in found):
    return GenericReply(
      message = 'One or more textbook(s) already owned',
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
      if pending.session_id:
        stripe.checkout.Session.expire(pending.session_id)
        pending.delete()

    except Exception as e:
      app.logger.error(f'Failed to expire session {pending.session_id}: {e}')

  
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
      product_data = {
        'name': f'{txtbook.title} by {txtbook.author.username}',
        'metadata': { 'id': txtbook.id }
      }
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
    saleType = 'OneTime',
    session_id = session['id'],
    discount = discount or None
  ).save()

  return StripeCheckoutReply(
    message = 'Checkout session created',
    status = HTTPStatusCode.OK,
    data = _StripeCheckoutData(
      session_id = session['id'],
      public_key = app.config.get('STRIPE_PUBLIC_KEY', '')
    )
  ).to_dict(), HTTPStatusCode.OK




@app.route(f'{basePath}/cancel-subscription', methods = ['POST'])
@require_login
def cancel_stripe_subscription_api(user: UserModel):
  req = StripeSubscriptionCancelRequest(request)

  if req.subscription_id == 'None':
    return GenericReply(
      message = 'Invalid subscription id',
      status = HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST

  # Validate Request
  if (user.privilege != 'Admin') and (user.subscription_id != req.subscription_id):
    return GenericReply(
      message = 'Unauthorized',
      status = HTTPStatusCode.UNAUTHORIZED
    ).to_dict(), HTTPStatusCode.UNAUTHORIZED


  # Locate Sale
  sale = SaleModel.query.filter(SaleModel.subscription_id == req.subscription_id).first()
  if not isinstance(sale, SaleModel):
    return GenericReply(
      message = 'Subscription not found',
      status = HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST


  # Cancel the subscription
  try:
    stripe.Subscription.modify(req.subscription_id, cancel_at_period_end = True)
  except Exception as e:
    app.logger.error(f'Failed to cancel subscription: {e}')
    return GenericReply(
      message = 'Failed to cancel subscription',
      status = HTTPStatusCode.INTERNAL_SERVER_ERROR
    ).to_dict(), HTTPStatusCode.INTERNAL_SERVER_ERROR


  # Update the user membership type
  user.subscription_status = 'Cancelled'
  user.save()


  return StripeSubscriptionCancelReply(
    message = 'Subscription will cancel at the end of period',
    status = HTTPStatusCode.OK
  ).to_dict(), HTTPStatusCode.OK




@app.route(f'{basePath}/expire-session', methods = ['POST'])
@require_login
def stripe_expiresession_api(user: UserModel):
  req = StripeExpireRequest(request)

  if req.session_id == 'None':
    return GenericReply(
      message = 'Invalid session id',
      status = HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST

  pending = [ i for i in user.pending_transactions if i.session_id == req.session_id ]
  if len(pending) == 0:
    return GenericReply(
      message = 'Pending transaction not found',
      status = HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST
  
  pending = pending[0]

  try:
    if pending.session_id:
      stripe.checkout.Session.expire(pending.session_id)

  except Exception as e:
    app.logger.error(f'Failed to expire session {pending.session_id}: {e}')
    return GenericReply(
      message = 'Failed to expire session',
      status = HTTPStatusCode.INTERNAL_SERVER_ERROR
    ).to_dict(), HTTPStatusCode.INTERNAL_SERVER_ERROR

  pending.delete()

  return StripeExpireReply(
    message = 'Checkout cancelled',
    status = HTTPStatusCode.OK
  ).to_dict(), HTTPStatusCode.OK




@app.route(f'{basePath}/status', methods = ['POST'])
@require_login
def stripe_status_api(user: UserModel):
  req = StripeStatusRequest(request)

  if req.session_id == 'None':
    return GenericReply(
      message = 'Invalid session id',
      status = HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST

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
          transaction_id = transaction.id,
          used_discount = transaction.used_discount.code if transaction.used_discount else None,
          paid_at = transaction.paid_at.timestamp(),
          created_at = transaction.created_at.timestamp()
        )
      ).to_dict(), HTTPStatusCode.OK


  return GenericReply(
    message = 'Transaction not found',
    status = HTTPStatusCode.BAD_REQUEST
  ).to_dict(), HTTPStatusCode.BAD_REQUEST




@app.route(f'{basePath}/webhook', methods = ['POST'])
@limiter.limit('10/second', scope = lambda _: request.host, key_func = util.get_remote_address)
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


  # Handle events
  match event.type:
    case 'checkout.session.completed': # Triggered when checkout succeeds
      session = stripe.checkout.Session.retrieve(event.data.object['id'])

      # Query sale model
      sale = SaleModel.query.filter(SaleModel.session_id == session['id']).first()
      if not isinstance(sale, SaleModel):
        return GenericReply(
          message = 'Failed to locate sale',
          status = HTTPStatusCode.BAD_REQUEST
        ).to_dict(), HTTPStatusCode.BAD_REQUEST
      

      sale.paid = True
      sale.session_id = None
      sale.paid_at = datetime.utcnow()

      if sale.type == 'Subscription':
        sale.user.membership = 'Unlimited'
        sale.user.subscription_status = 'Active'
        sale.user.subscription_id = event.data.object['subscription']
        sale.subscription_id = event.data.object['subscription']
        sale.user.save()

      sale.save()

      # Handle making textbooks availble to user
      if sale.type == 'OneTime':
        for info in sale.textbooks.values():
          info.textbook.bought_by.append(sale.user)
          info.textbook.save()



    case 'invoice.paid': # Handle recurring charge
      # Query most recent sale model
      sale = SaleModel.query.filter(
        SaleModel.subscription_id == event.data.object['subscription']
      ).order_by(SaleModel.created_at.desc()).first()

      if isinstance(sale, SaleModel) and sale.paid:
        # Handle recurring payment
        SaleModel(
          user = sale.user,
          saleType = 'Subscription',
          total_cost = sale.total_cost
        ).save()



    case 'checkout.session.expired':
      session = stripe.checkout.Session.retrieve(event.data.object['id'])

      # Query sale model
      sale = SaleModel.query.filter(SaleModel.session_id == session['id']).first()
      if isinstance(sale, SaleModel):
        sale.delete()
    


    case 'customer.subscription.deleted':
      user = UserModel.query.filter(UserModel.subscription_id == event.data.object['subscription']).first()
      if not isinstance(user, UserModel):
        return GenericReply(
          message = 'Unable to locate customer',
          status = HTTPStatusCode.BAD_REQUEST
        ).to_dict(), HTTPStatusCode.BAD_REQUEST
      
      user.membership = 'Free'
      user.subscription_status = 'Cancelled'
      user.save()
      

  return GenericReply(
    message = 'Webhook received',
    status = HTTPStatusCode.OK
  ).to_dict(), HTTPStatusCode.OK
