"""
User Endpoint
"""

from src import limiter
from flask_limiter import util
from src.utils.http import HTTPStatusCode
from src.database import UserModel, ImageModel

from src.utils.ext import utc_time
from src.utils.passwords import hash_password
from src.service.email_provider import dns_check
from src.service.auth_provider import require_login, require_admin
from src.utils.api import (
  UserListRequest, UserListReply,
  UserGetRequest, UserGetReply, _UserGetData,
  UserEditRequest, UserEditReply,
  UserDeleteRequest, UserDeleteReply,
  GenericReply
)

import re
from datetime import datetime
from functools import lru_cache
from sqlalchemy import or_, and_
from flask import (
  request,
  current_app as app,
)

# Routes
basePath: str = '/api/v1/user'
auth_limit = limiter.shared_limit('100 per hour', scope = lambda _: request.host, key_func = util.get_remote_address)

DateRange = tuple[datetime, datetime] | datetime | None




@app.route(f'{basePath}/list', methods = ['GET'])
@auth_limit
@require_admin
@lru_cache
def user_list_api(user: UserModel):
  req = UserListRequest(request)

  # Handle query
  dateRange: DateRange = (
    datetime.fromtimestamp(req.createdLower) if float('inf') != req.createdLower else utc_time.skip('1day'),
    datetime.fromtimestamp(req.createdUpper) if float('inf') != req.createdUpper else utc_time.skip('1day')
  )

  if dateRange[0] > dateRange[1]:
    return GenericReply(
      message = 'createdLower is larger than createdUpper',
      status = HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST
  
  if req.query == 'None':
    req.query = ''
  

  # Build query
  query = [
    and_(
      dateRange[0] <= UserModel.created_at,
      UserModel.created_at <= dateRange[1],
    ),
    or_(
      UserModel.id.contains(req.query),
      UserModel.username.contains(req.query),
    )
  ]
  
  filtered = UserModel.query.filter(
    and_(*query) if req.criteria == 'and' else or_(*query)
  ).paginate(page = req.page, error_out = False)

  return UserListReply(
    message = 'Successfully fetched users',
    status = HTTPStatusCode.OK,
    data = [
      _UserGetData(
        user_id = i.id,
        email = i.email,
        status = i.status,
        username = user.username,
        privilege = i.privilege,
        profile_image = i.profile_image.uri if i.profile_image else None,
        created_at = i.created_at.timestamp(),
        last_login = i.last_login.timestamp()
      )
      for i in filtered
    ]
  ).to_dict(), HTTPStatusCode.OK




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
      email = foundUser.email,
      status = foundUser.status,
      username = foundUser.username,
      privilege = foundUser.privilege,
      profile_image = user.profile_image.uri if user.profile_image else None,
      created_at = foundUser.created_at.timestamp(),
      last_login = foundUser.last_login.timestamp()
    )
  ).to_dict(), HTTPStatusCode.OK




@app.route(f'{basePath}/edit', methods = ['POST'])
@auth_limit
@require_login
def user_edit_api(user: UserModel):
  req = UserEditRequest(request)

  if req.user_id and (req.user_id != 'None') and (user.privilege != 'Admin') and (user.id != req.user_id):
    return GenericReply(
      message = 'Unauthorized',
      status = HTTPStatusCode.UNAUTHORIZED
    ).to_dict(), HTTPStatusCode.UNAUTHORIZED
  
  foundUser = user if req.user_id and (req.user_id != 'None') and user.id == req.user_id else UserModel.query.filter(UserModel.id == req.user_id).first()
  if not isinstance(foundUser, UserModel):
    return GenericReply(
      message = 'Unable to locate user',
      status = HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST
  
  if req.privilege and (req.privilege != 'None') and (user.privilege != 'Admin'):
    return GenericReply(
      message = 'Only admins can edit privileges',
      status = HTTPStatusCode.UNAUTHORIZED
    ).to_dict(), HTTPStatusCode.UNAUTHORIZED
  
  if req.status and (req.status != 'None') and (user.privilege != 'Admin'):
    return GenericReply(
      message = 'Only admins can edit status',
      status = HTTPStatusCode.UNAUTHORIZED
    ).to_dict(), HTTPStatusCode.UNAUTHORIZED
  
  if req.password and (req.password != 'None') and not re.fullmatch(r'^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[?!@$%^#&*-]).{8,20}$', req.password):
    return GenericReply(
      message = 'Password has to be between 8 to 20 characters inclusive, contain at least 1 upper and lower case letter, \
                contain at least 1 digit and contain at least 1 {!@$%^#&*-} special character',
      status = HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST
  
  if req.username and (req.username != 'None') and not re.fullmatch(r'^[a-zA-Z][a-zA-Z0-9_-]{4,20}$', req.username):
    return GenericReply(
      message = 'Username has to be between 5 to 20 charcters inclusive, start with a letter and only {_-} special characters are allowed',
      status = HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST
  
  if req.email and (req.email != 'None') and not dns_check(req.email):
    return GenericReply(
      message = 'Email is invalid and/or cannot be reached',
      status = HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST
  
  
  # Edit User
  changed = False
  profileImg = request.files.get('upload', None)

  if profileImg:
    if foundUser.profile_image:
      foundUser.profile_image.delete()
    ImageModel(profileImg, user = user).save()
    changed = True
  
  if req.password and (req.password != 'None'):
    foundUser.password_hash = hash_password(req.password).decode('utf-8')
    changed = True
  
  if (req.privilege == 'Student') or (req.privilege == 'Educator'):
    foundUser.privilege = req.privilege
    changed = True
  
  if (req.status == 'Active') or (req.status == 'Locked'):
    foundUser.status = req.status
    changed = True
  
  if req.username and (req.username != 'None') and (req.username != foundUser.username):
    foundUser.username = req.username
    changed = True
  
  if req.email and (req.email != 'None') and (req.email != foundUser.email):
    foundUser.email = req.email
    foundUser.email_verified = False
    changed = True
  
  # Handle no changes
  if not changed:
    return GenericReply(
      message = 'No change supplied',
      status = HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST

  foundUser.save()
  return UserEditReply(
    message = 'Successfully edited user',
    status = HTTPStatusCode.OK
  ).to_dict(), HTTPStatusCode.OK




@app.route(f'{basePath}/delete', methods = ['POST'])
@auth_limit
@require_login
def user_delete_api(user: UserModel):
  req = UserDeleteRequest(request)

  if (user.privilege != 'Admin') and (user.id != req.user_id):
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
