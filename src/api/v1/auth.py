"""
RESTful auth api for session persistence with jwt
"""

from src import db, limiter
from src.utils.http import HTTPStatusCode
from src.utils.passwords import hash_password
from src.service import auth_provider
from src.database import UserModel
from sqlalchemy import or_

from typing import Optional
from flask import (
  request,
  current_app as app,
)
from flask_jwt_extended import (
  jwt_required,
  get_jwt_identity,
  create_access_token,
  create_refresh_token,
)

# Routes
basePath: str = '/api/v1'
auth_limit = limiter.shared_limit('100 per hour', scope = lambda _: request.host)


@app.route(f'{basePath}/login', methods = ['POST'])
@auth_limit
def apiv1_Login():
  if request.json:
    email = request.json.get('email', None)
    password = request.json.get('password', None)
  else:
    email = request.form.get('email', None)
    password = request.form.get('password', None)

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
  access_token = create_access_token(identity = user, fresh = True)
  refresh_token = create_refresh_token(identity = user)

  return {
    'message': 'Login successful',
    'data': {
      'access_token': access_token,
      'refresh_token': refresh_token
    },
    'status': 200
  }, 200


@app.route(f'{basePath}/refresh', methods = ['POST'])
@auth_limit
@jwt_required(refresh = True)
def apiV1Refresh():
  identity = get_jwt_identity()
  access_token = create_access_token(identity = identity, fresh = False)
  return {
    'message': 'Refreshed access token',
    'status': HTTPStatusCode.OK,
    'data': {
      'access_token': access_token
    }
  }


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
  