"""
User Endpoint
"""

from src import limiter
from flask_limiter import util
from src.utils.http import HTTPStatusCode
from src.database import UserModel

from src.service.auth_provider import require_login
from src.utils.api import (
  UserGetRequest, UserGetReply, _UserGetData,
  UserDeleteRequest, UserDeleteReply,
  GenericReply
)

from flask import (
  request,
  current_app as app,
)

# Routes
basePath: str = '/api/v1/user'
auth_limit = limiter.shared_limit('100 per hour', scope = lambda _: request.host, key_func = util.get_remote_address)




@app.route(f'{basePath}/get', methods = ['GET'])
@auth_limit
@require_login
def user_get_api(user: UserModel):
  req = UserGetRequest(request)

  if (user.privilege != 'Admin') or (user.id != req.user_id):
    return GenericReply(
      message = 'Unauthorized',
      status = HTTPStatusCode.UNAUTHORIZED
    ).to_dict(), HTTPStatusCode.UNAUTHORIZED
  
  foundUser = user if user.id == req.user_id else UserModel.query.filter(UserModel.id == req.user_id).first()
  if not isinstance(foundUser, UserModel):
    return GenericReply(
      message = 'Unable to lcoate user',
      status = HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST
  
  
  return UserGetReply(
    message = 'Successfully fetched user',
    status = HTTPStatusCode.OK,
    data = _UserGetData(
      user_id = foundUser.id,
      username = foundUser.username,
      privilege = foundUser.privilege,
      profile_image = user.profile_image.uri if user.profile_image else None,
      created_at = foundUser.created_at.timestamp(),
      last_login = foundUser.last_login.timestamp()
    )
  ).to_dict(), HTTPStatusCode.OK




@app.route(f'{basePath}/delete', methods = ['POST'])
@auth_limit
@require_login
def user_delete_api(user: UserModel):
  req = UserDeleteRequest(request)

  if (user.privilege != 'Admin') and (user.id !=  req.user_id):
    return GenericReply(
      message = 'Unauthorized',
      status = HTTPStatusCode.UNAUTHORIZED
    ).to_dict(), HTTPStatusCode.UNAUTHORIZED
  
  foundUser = user if user.id == req.user_id else UserModel.query.filter(UserModel.id == req.user_id).first()
  if not isinstance(foundUser, UserModel):
    return GenericReply(
      message = 'Unable to locate user',
      status = HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST
  
  foundUser.delete()
  return UserDeleteReply(
    message = 'Successfully deleted user',
    status = HTTPStatusCode.OK
  ).to_dict(), HTTPStatusCode.OK
