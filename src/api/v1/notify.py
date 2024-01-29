"""
Notification Endpoint
"""

from markupsafe import escape
from src.database import UserModel
from src.utils.http import HTTPStatusCode
from src.service.auth_provider import optional_login
from src.utils.api import (
  NotifyMakeRequest, NotifyReply,
  NotifyGetReply,
  GenericReply
)

from flask import (
  flash,
  request,
  get_flashed_messages,
  current_app as app
)


basePath: str = '/api/v1/notify'




@app.route(f'{basePath}/make', methods = ['POST'])
@optional_login
def notify_new(user: UserModel | None):
  req = NotifyMakeRequest(request)
  req.category = req.category or 'info'

  req.message = str(escape(req.message))
  if (not req.message) or (req.message == 'None'):
    return GenericReply(
      message = 'Message cannot be empty',
      status = HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST

  flash(req.message, req.category)
  return NotifyReply(
    message = 'Successfully created new notification',
    status = HTTPStatusCode.OK
  ).to_dict(), HTTPStatusCode.OK




@app.route(f'{basePath}/get', methods = ['GET'])
@optional_login
def notify_get(user: UserModel | None):
  return NotifyGetReply(
    message = 'Successfully fetched notifications',
    status = HTTPStatusCode.OK,
    data = get_flashed_messages(with_categories = True)
  ).to_dict(), HTTPStatusCode.OK
