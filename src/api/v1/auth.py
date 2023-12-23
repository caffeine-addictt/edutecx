"""
RESTful auth api for session persistence with jwt w/ rate limiting
"""

from src import limiter
from flask_limiter import util
from src.utils.http import HTTPStatusCode
from src.utils.passwords import hash_password
from src.database import UserModel
from sqlalchemy import or_

from src.utils.api import (
  TokenRefreshReply, _TokenRefreshData,
  LoginRequest, LoginReply, _LoginData,
  RegisterRequest, RegisterReply,
  GenericReply
)

from typing import Optional
from flask import (
  request,
  current_app as app,
)
from flask_jwt_extended import (
  jwt_required,
  get_current_user,
  create_access_token,
  create_refresh_token,
)

# Routes
basePath: str = '/api/v1'
auth_limit = limiter.shared_limit('100 per hour', scope = lambda _: request.host, key_func = util.get_remote_address)




@app.route(f'{basePath}/login', methods = ['POST'])
@auth_limit
def apiv1_Login():
  req = LoginRequest(request)

  # Ensure email and password exist
  if not req.email or not req.password:
    return GenericReply(
      message = 'Missing email or password',
      status = HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST
  
  # Ensure user exists
  user: UserModel | None = UserModel.query.filter(UserModel.email == req.email).first()
  if not isinstance(user, UserModel) or not user.verify_password(req.password):
    return GenericReply(
      message = 'Invalid email or password',
      status = HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST

  # Create tokens
  add_claims = {
    'aud': request.host,
    'remember_me': bool(req.remember_me),
  }
  refresh_token = create_refresh_token(identity = user, additional_claims = add_claims)
  access_token = create_access_token(identity = user, fresh = True)

  return LoginReply(
    message = 'Login successful',
    status = HTTPStatusCode.OK,
    data = _LoginData(
      access_token = access_token,
      refresh_token = refresh_token
    )
  ).to_dict(), HTTPStatusCode.OK




@app.route(f'{basePath}/register', methods = ['POST'])
@auth_limit
def apiV1Register():
  req = RegisterRequest(request)

  # Ensure email and password exist
  if not req.email or not req.username or not req.password:
    return GenericReply(
      message = 'Missing email or username',
      status = HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST
  
  # Check if user exists
  existing: Optional[UserModel] = UserModel.query.filter(or_(
    UserModel.email == req.email,
    UserModel.username == req.username
  )).first()
  if existing:
    return GenericReply(
      message = 'Email or username already exists',
      status = HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST
  
  UserModel(
    email = req.email,
    username = req.username,
    password = hash_password(req.password).decode('utf-8'),
    privilege = 'User'
  ).save()

  return RegisterReply(
    message = 'Registered successfully',
    status = HTTPStatusCode.OK
  ).to_dict(), HTTPStatusCode.OK




@app.route(f'{basePath}/refresh', methods = ['POST'])
@limiter.limit('10/hour', key_func = util.get_remote_address)
@jwt_required(refresh = True)
def apiV1Refresh():
  identity = get_current_user()
  access_token = create_access_token(identity = identity, fresh = False)

  return TokenRefreshReply(
    message = 'Refreshed access token',
    status = HTTPStatusCode.OK,
    data = _TokenRefreshData(
      access_token = access_token
    )
  ).to_dict(), HTTPStatusCode.OK
