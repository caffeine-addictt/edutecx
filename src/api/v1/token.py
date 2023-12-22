"""
Token Endpoint
"""

from src import limiter
from src.utils.http import HTTPStatusCode
from src.database import TokenModel, UserModel
from src.service.auth_provider import optional_login
from src.utils.api import (
  TokenGetRequest, TokenGetReply, _TokenGetData,
  TokenCreateRequest, TokenCreateReply, _TokenCreateData,
  TokenDeleteRequest, TokenDeleteReply,
  GenericReply
)

from sqlalchemy import or_
from flask_limiter import util
from flask import (
  request,
  current_app as app
)


# Routes
basePath: str = '/api/v1/token'
auth_limit = limiter.shared_limit('100 per hour', scope = lambda _: request.host, key_func = util.get_remote_address)




@app.route(f'{basePath}/get', methods = ['GET'])
@auth_limit
def token_get_api():
  req = TokenGetRequest(request)

  token = TokenModel.query.filter(TokenModel.token == req.token).first()
  if not isinstance(token, TokenModel):
    return GenericReply(
      message = 'Failed to locate token',
      status = HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST
  
  return TokenGetReply(
    message = 'Successfully fetched token',
    status = HTTPStatusCode.OK,
    data = _TokenGetData(
      token = token.token,
      token_type = token.token_type,
      expires_at = token.expires_at.timestamp(),
      created_at = token.created_at.timestamp()
    )
  ).to_dict(), HTTPStatusCode.OK




@app.route(f'{basePath}/create', methods = ['POST'])
@auth_limit
@optional_login
def token_create_api(user: UserModel | None):
  req = TokenCreateRequest(request)

  if (req.token_type == 'Verification'):
    if not user:
      return GenericReply(
        message = 'Unauthorized',
        status = HTTPStatusCode.UNAUTHORIZED
      ).to_dict(), HTTPStatusCode.UNAUTHORIZED
    
    elif user.email_verified:
      return GenericReply(
        message = 'Already verified',
        status = HTTPStatusCode.BAD_REQUEST
      ).to_dict(), HTTPStatusCode.BAD_REQUEST
  

  if (req.token_type != 'Verification') or (req.token_type != 'PasswordReset'):
    return GenericReply(
      message = 'Invalid token type',
      status = HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST
  
  
  user = user if user and (user.id == req.user_id) else UserModel.query.filter(UserModel.id == req.user_id).first()
  if not isinstance(user, UserModel):
    return GenericReply(
      message = 'Unable to locate user',
      status = HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST
  

  newToken = TokenModel(
    user = user,
    token_type = req.token_type
  )
  newToken.save()

  return TokenCreateReply(
    message = 'Successfully created token',
    status = HTTPStatusCode.OK,
    data = _TokenCreateData(
      token = newToken.token,
      token_id = newToken.id
    )
  ).to_dict(), HTTPStatusCode.OK




@app.route(f'{basePath}/delete', methods = ['POST'])
@auth_limit
def token_delete_api():
  req = TokenDeleteRequest(request)

  if len(list(filter(None, [req.token, req.token_id]))) != 1:
    return GenericReply(
      message = 'Invalid identifiers',
      status = HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST
  
  token = TokenModel.query.filter(or_(
    TokenModel.id == req.token_id,
    TokenModel.token == req.token
  )).first()
  
  if not isinstance(token, TokenModel):
    return GenericReply(
      message = 'Could not locate token',
      status = HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST
  

  token.delete()
  return TokenDeleteReply(
    message = 'Successfully deleted token',
    status = HTTPStatusCode.OK
  ).to_dict(), HTTPStatusCode.OK
