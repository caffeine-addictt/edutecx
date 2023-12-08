"""
Classroom Endpoint
"""

from src import db, limiter
from src.database import ClassroomModel
from flask_limiter import util
from flask import (
  request,
  current_app as app
)


# Routes
basePath: str = '/api/v1/classroom'
auth_limit = limiter.shared_limit('100 per hour', scope = lambda _: request.host, key_func = util.get_remote_address)


# @app.route(f'{basePath}/create', methods = ['POST'])
# @auth_limit
# def classroom_create_api():

#   user: ClassroomModel = ClassroomModel(
#     email = email,
#     username = username,
#     password = hash_password(password).decode('utf-8'),
#     privilege = 'User'
#   )

#   db.session.add(user)
#   db.session.commit()

#   return {

#   }