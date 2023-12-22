"""
Submission Endpoint
"""

from src import limiter
from src.database import SubmissionModel, UserModel
from src.service.auth_provider import require_login

from flask_limiter import util
from flask import (
  request,
  current_app as app
)


# Routes
basePath: str = '/api/v1/submission'
auth_limit = limiter.shared_limit('100 per hour', scope = lambda _: request.host, key_func = util.get_remote_address)




@app.route(f'{basePath}/get', methods = ['GET'])
@auth_limit
@require_login
def submission_get_api(user: UserModel):
  ...




@app.route(f'{basePath}/create', methods = ['POST'])
@auth_limit
@require_login
def submission_create_api(user: UserModel):
  ...




@app.route(f'{basePath}/edit', methods = ['POST'])
@auth_limit
@require_login
def submission_edit_api(user: UserModel):
  ...





@app.route(f'{basePath}/delete', methods = ['POST'])
@auth_limit
@require_login
def submission_delete_api(user: UserModel):
  ...
