"""
RESTful auth api for session persistence with jwt w/ rate limiting
"""

from src import db, limiter
from flask_limiter import util
from src.utils.http import HTTPStatusCode
from src.utils.passwords import hash_password
from src.database import UserModel
from sqlalchemy import or_

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
  if request.json:
    email = request.json.get('email', None)
    password = request.json.get('password', None)
    remember_me = request.json.get('remember_me', None)
  else:
    email = request.form.get('email', None)
    password = request.form.get('password', None)
    remember_me = request.form.get('remember_me', None)

  # Ensure email and password exist
  if not email or not password:
    return {
      'message': 'Missing email or password',
      'status': HTTPStatusCode.BAD_REQUEST
    }, HTTPStatusCode.BAD_REQUEST
  
  # Ensure user exists
  user: Optional[UserModel] = UserModel.query.filter(UserModel.email == email).first()
  if not user or not user.verify_password(password):
    return {
      'message': 'Invalid email or password',
      'status': HTTPStatusCode.BAD_REQUEST
    }, HTTPStatusCode.BAD_REQUEST

  # Create tokens
  add_claims = {
    'aud': request.host,
    'remember_me': bool(remember_me),
  }
  refresh_token = create_refresh_token(identity = user, additional_claims = add_claims)
  access_token = create_access_token(identity = user, fresh = True)

  return {
    'message': 'Login successful',
    'data': {
      'access_token': access_token,
      'refresh_token': refresh_token
    },
    'status': HTTPStatusCode.OK
  }, HTTPStatusCode.OK




@app.route(f'{basePath}/register', methods = ['POST'])
@auth_limit
def apiV1Register():
  if request.json:
    email = request.json.get('email', None)
    username = request.json.get('username', None)
    password = request.json.get('password', None)
  else:
    email = request.form.get('email', None)
    username = request.form.get('username', None)
    password = request.form.get('password', None)

  # Ensure email and password exist
  if not email or not username or not password:
    return {
      'message': 'Missing email or username',
      'status': HTTPStatusCode.BAD_REQUEST
    }, HTTPStatusCode.BAD_REQUEST
  
  # Check if user exists
  existing: Optional[UserModel] = UserModel.query.filter(or_(
    UserModel.email == email,
    UserModel.username == username
  )).first()
  if existing:
    return {
      'message': 'Email or username already exists',
      'status': HTTPStatusCode.BAD_REQUEST
    }, HTTPStatusCode.BAD_REQUEST
  
  user: UserModel = UserModel(
    email = email,
    username = username,
    password = hash_password(password).decode('utf-8'),
    privilege = 'User'
  )

  db.session.add(user)
  db.session.commit()

  return {
    'message': 'Registered successfully',
    'status': HTTPStatusCode.OK
  }, HTTPStatusCode.OK




@app.route(f'{basePath}/refresh', methods = ['POST'])
@limiter.limit('10/hour', key_func = util.get_remote_address)
@jwt_required(refresh = True)
def apiV1Refresh():
  identity = get_current_user()
  access_token = create_access_token(identity = identity, fresh = False)
  return {
    'message': 'Refreshed access token',
    'status': HTTPStatusCode.OK,
    'data': {
      'access_token': access_token
    }
  }, HTTPStatusCode.OK
