"""
Notification Endpoint
"""

from markupsafe import escape
from src.utils.http import HTTPStatusCode
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
def notify_new():
  req = NotifyMakeRequest(request)
  req.category = req.category or 'info'

  req.message = str(escape(req.message))
  if not req.message:
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
def notify_get():
  return NotifyGetReply(
    message = 'Successfully fetched notifications',
    status = HTTPStatusCode.OK,
    data = get_flashed_messages(with_categories = True)
  ).to_dict(), HTTPStatusCode.OK
