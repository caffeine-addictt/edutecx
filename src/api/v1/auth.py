"""
RESTful auth api for session persistence with jwt w/ rate limiting
"""

from src import db, limiter
from flask_limiter import util
from src.service import email_provider
from src.service import auth_provider
from src.utils.ext import utc_time

from src.utils.http import HTTPStatusCode
from src.utils.passwords import hash_password
from src.database import UserModel, TokenModel, JWTBlocklistModel
from sqlalchemy import or_

from src.utils.api import (
  TokenRefreshReply,
  _TokenRefreshData,
  LoginRequest,
  LoginReply,
  _LoginData,
  RegisterRequest,
  RegisterReply,
  VerifyEmailRequest,
  VerifyEmailReply,
  GenericReply,
)

import re
from typing import Optional
from flask import (
  request,
  current_app as app,
)
from flask_jwt_extended import (
  decode_token,
  jwt_required,
  get_current_user,
  create_access_token,
  create_refresh_token,
)

# Routes
basePath: str = '/api/v1'
auth_limit = limiter.shared_limit(
  '100 per hour', scope=lambda _: request.host, key_func=util.get_remote_address
)


@app.route(f'{basePath}/login', methods=['POST'])
@auth_limit
@auth_provider.anonymous_required(admin_override=False)
def apiv1_Login():
  req = LoginRequest(request)

  # Ensure email and password exist
  if (
    (not req.email)
    or (req.email == 'None')
    or (not req.password)
    or (req.password == 'None')
  ):
    return GenericReply(
      message='Missing email or password', status=HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST

  # Ensure user exists
  user: UserModel | None = UserModel.query.filter(UserModel.email == req.email).first()
  if not isinstance(user, UserModel) or not user.verify_password(req.password):
    return GenericReply(
      message='Invalid email or password', status=HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST

  # Check for locked account
  if user.status == 'Locked':
    return GenericReply(
      message='Your account has been locked, contact us at edutecx@ngjx.org for more information',
      status=HTTPStatusCode.FORBIDDEN,
    ).to_dict(), HTTPStatusCode.FORBIDDEN

  # Create tokens
  add_claims = {
    'aud': request.host,
    'remember_me': req.remember_me in ['y', True],
  }
  refresh_token = create_refresh_token(identity=user, additional_claims=add_claims)
  access_token = create_access_token(identity=user, fresh=True)

  return LoginReply(
    message='Login successful',
    status=HTTPStatusCode.OK,
    data=_LoginData(access_token=access_token, refresh_token=refresh_token),
  ).to_dict(), HTTPStatusCode.OK


@app.route(f'{basePath}/register', methods=['POST'])
@auth_limit
@auth_provider.anonymous_required
def apiV1Register():
  req = RegisterRequest(request)

  # Ensure email and password exist
  if (
    (not req.email)
    or (not req.username)
    or (not req.password)
    or (req.email == 'None')
    or (req.username == 'None')
    or (req.password == 'None')
  ):
    return GenericReply(
      message='Missing email, username or password', status=HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST

  # Validate Email
  if not email_provider.dns_check(req.email):
    return GenericReply(
      message='Email is invalid and/or cannot be reached',
      status=HTTPStatusCode.BAD_REQUEST,
    ).to_dict(), HTTPStatusCode.BAD_REQUEST

  # Validate Username
  if not re.fullmatch(r'^[a-zA-Z][a-zA-Z0-9_-]{4,20}$', req.username):
    return GenericReply(
      message='Username has to be between 5 to 20 charcters inclusive, start with a letter and only {_-} special characters are allowed',
      status=HTTPStatusCode.BAD_REQUEST,
    ).to_dict(), HTTPStatusCode.BAD_REQUEST

  # Validate password
  if not re.fullmatch(
    r'^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[?!@$%^#&*-]).{8,20}$', req.password
  ):
    return GenericReply(
      message='Password has to be between 8 to 20 characters inclusive, contain at least 1 upper and lower case letter, \
                contain at least 1 digit and contain at least 1 {!@$%^#&*-} special character',
      status=HTTPStatusCode.BAD_REQUEST,
    ).to_dict(), HTTPStatusCode.BAD_REQUEST

  # Check if user exists
  existing: Optional[UserModel] = UserModel.query.filter(
    or_(UserModel.email == req.email, UserModel.username == req.username)
  ).first()
  if existing:
    return GenericReply(
      message='Email or username already exists', status=HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST

  user = UserModel(
    email=req.email,
    username=req.username,
    password=hash_password(req.password).decode('utf-8'),
    privilege=req.privilege,
  )
  token = TokenModel(user=user, token_type='Verification')

  # Send verification code
  try:
    res = email_provider.send_email(
      req.email,
      emailType='Verification',
      data=email_provider.VerificationEmailData(
        username=req.username,
        cta_link='https://edutecx.ngjx.org/verify/' + str(token.token),
      ),
    )

    if res != True:
      raise Exception(res[1])

  except Exception as e:
    app.logger.error(f'Failed to send verification email: {e}')
    return GenericReply(
      message='Failed to send verification email',
      status=HTTPStatusCode.INTERNAL_SERVER_ERROR,
    ).to_dict(), HTTPStatusCode.INTERNAL_SERVER_ERROR

  user.save()
  token.save()

  return RegisterReply(
    message='Registered successfully', status=HTTPStatusCode.OK
  ).to_dict(), HTTPStatusCode.OK


@app.route(f'{basePath}/refresh', methods=['POST'])
@limiter.limit('10/hour', key_func=util.get_remote_address)
@jwt_required(refresh=True)
def apiV1Refresh():
  identity = get_current_user()
  access_token = create_access_token(identity=identity, fresh=False)

  return TokenRefreshReply(
    message='Refreshed access token',
    status=HTTPStatusCode.OK,
    data=_TokenRefreshData(access_token=access_token),
  ).to_dict(), HTTPStatusCode.OK


@app.route(f'{basePath}/send-verification-email', methods=['POST'])
@auth_limit
@auth_provider.require_login(ignore_verification=True)
def apiV1SendVerificationEmail(user: UserModel):
  if user.email_verified:
    return GenericReply(
      message='Email already verified', status=HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST

  # Check for locked account
  if user.status == 'Locked':
    return GenericReply(
      message='Your account has been locked, contact us at edutecx@ngjx.org for more information',
      status=HTTPStatusCode.FORBIDDEN,
    ).to_dict(), HTTPStatusCode.FORBIDDEN

  if user.token:
    if utc_time.skip('5minutes', user.token.created_at) >= utc_time.get():
      return GenericReply(
        message='Generating tokens too quickly', status=HTTPStatusCode.TOO_MANY_REQUESTS
      ).to_dict(), HTTPStatusCode.TOO_MANY_REQUESTS

    user.token.delete()

  newToken = TokenModel(user=user, token_type='Verification')

  try:
    res = email_provider.send_email(
      user.email,
      emailType='Verification',
      data=email_provider.VerificationEmailData(
        username=user.username,
        cta_link='https://edutecx.ngjx.org/verify/' + str(newToken.token),
      ),
    )

    if res != True:
      raise Exception(res[1])

    newToken.save()

  except Exception as e:
    app.logger.error(f'Failed to send verification email: {e}')
    return GenericReply(
      message='Failed to send verification email',
      status=HTTPStatusCode.INTERNAL_SERVER_ERROR,
    ).to_dict(), HTTPStatusCode.INTERNAL_SERVER_ERROR

  return GenericReply(
    message='Verification email sent', status=HTTPStatusCode.OK
  ).to_dict(), HTTPStatusCode.OK


@app.route(f'{basePath}/verify-email', methods=['POST'])
@auth_limit
@auth_provider.require_login(ignore_verification=True)
def apiV1VerifyEmail(user: UserModel):
  req = VerifyEmailRequest(request)

  # Check for locked account
  if user.status == 'Locked':
    return GenericReply(
      message='Your account has been locked, contact us at edutecx@ngjx.org for more information',
      status=HTTPStatusCode.FORBIDDEN,
    ).to_dict(), HTTPStatusCode.FORBIDDEN

  if user.email_verified:
    return GenericReply(
      message='Email already verified', status=HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST

  if (
    not user.token
    or (user.token.token_type != 'Verification')
    or (user.token.token != req.token)
  ):
    return GenericReply(
      message='Invalid token', status=HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST

  if user.token.expires_at < utc_time.get():
    return GenericReply(
      message='Token expired', status=HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST

  user.email_verified = True
  user.token.delete()
  user.save()

  return VerifyEmailReply(
    message='Email verified', status=HTTPStatusCode.OK
  ).to_dict(), HTTPStatusCode.OK
