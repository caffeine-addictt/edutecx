"""
Editable Textbook Endpoint
"""

from src import limiter
from src.database import EditableTextbookModel, UserModel, TextbookModel
from src.service.auth_provider import require_login
from src.utils.http import HTTPStatusCode
from src.utils.api import (
  EditableTextbookGetRequest, EditableTextbookGetReply, _EditableTextbookGetData,
  EditableTextbookCreateRequest, EditableTextbookCreateReply, _EditableTextbookCreateData,
  EditableTextbookEditRequest, EditableTextbookEditReply,
  EditableTextbookDeleteRequest, EditableTextbookDeleteReply,
  GenericReply
)

from flask_limiter import util
from flask import (
  request,
  current_app as app
)


# Routes
basePath: str = '/api/v1/editabletextbook'
auth_limit = limiter.shared_limit('100 per hour', scope = lambda _: request.host, key_func = util.get_remote_address)




@app.route(f'{basePath}/get', methods = ['GET'])
@auth_limit
@require_login
def editabletextbook_get_api(user: UserModel):
  req = EditableTextbookGetRequest(request)


  etextbook = EditableTextbookModel.query.filter(EditableTextbookModel.id == req.editabletextbook_id).first()
  if (not etextbook) and (not isinstance(etextbook, EditableTextbookModel)):
    return GenericReply(
      message = 'Unable to locate editable textbook',
      status = HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST

  if (user.privilege != 'Admin') and (user.id != etextbook.user_id):
    return GenericReply(
      message = 'Unauthorized',
      status = HTTPStatusCode.UNAUTHORIZED
    ).to_dict(), HTTPStatusCode.UNAUTHORIZED


  return EditableTextbookGetReply(
    message = 'Successfully fetched editable textbook',
    status = HTTPStatusCode.OK,
    data = _EditableTextbookGetData(
      editabletextbook_id = etextbook.id,
      user_id = etextbook.user_id,
      textbook_id = etextbook.textbook_id,
      uri = etextbook.uri,
      status = etextbook.status,
      created_at = etextbook.created_at.timestamp()
    )
  ).to_dict(), HTTPStatusCode.OK




@app.route(f'{basePath}/create', methods = ['POST'])
@auth_limit
@require_login
def editabletextbook_create_api(user: UserModel):
  req = EditableTextbookCreateRequest(request)

  if (user.privilege != 'Admin') and (req.textbook_id not in ''.join(i.textbook_ids for i in user.transactions)):
    return GenericReply(
      message = 'Unauthorized',
      status = HTTPStatusCode.UNAUTHORIZED
    ).to_dict(), HTTPStatusCode.UNAUTHORIZED
  
  textbook = TextbookModel.query.filter(TextbookModel.id == req.textbook_id).first()
  if not isinstance(textbook, TextbookModel):
    return GenericReply(
      message = 'Unable to locate textbook',
      status = HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST
  
  
  newETextbook = EditableTextbookModel(user, textbook)
  newETextbook.save()

  return EditableTextbookCreateReply(
    message = 'Successfully created editable textbook',
    status = HTTPStatusCode.OK,
    data = _EditableTextbookCreateData(
      editabletextbook_id = newETextbook.id
    )
  ).to_dict(), HTTPStatusCode.OK




@app.route(f'{basePath}/edit', methods = ['POST'])
@auth_limit
@require_login
def editabletextbook_edit_api(user: UserModel):
  req = EditableTextbookEditRequest(request)
  upload = req.files.get('upload')

  if not upload:
    return GenericReply(
      message = 'No change supplied',
      status = HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST
  
  
  etextbook = EditableTextbookModel.query.filter(EditableTextbookModel.id == req.editabletextbook_id).first()
  if (not etextbook) and (not isinstance(etextbook, EditableTextbookModel)):
    return GenericReply(
      message = 'Unable to locate editable textbook',
      status = HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST

  if (user.privilege != 'Admin') and (user.id != etextbook.user_id):
    return GenericReply(
      message = 'Unauthorized',
      status = HTTPStatusCode.UNAUTHORIZED
    ).to_dict(), HTTPStatusCode.UNAUTHORIZED
  

  etextbook.update(upload)
  return EditableTextbookEditReply(
    message = 'Successfully edited editable textbook',
    status = HTTPStatusCode.OK
  ).to_dict(), HTTPStatusCode.OK




@app.route(f'{basePath}/delete', methods = ['POST'])
@auth_limit
@require_login
def editabletextbook_delete_api(user: UserModel):
  req = EditableTextbookDeleteRequest(request)

  etextbook = EditableTextbookModel.query.filter(EditableTextbookModel.id == req.editabletextbook_id).first()
  if (not etextbook) and (not isinstance(etextbook, EditableTextbookModel)):
    return GenericReply(
      message = 'Unable to locate editable textbook',
      status = HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST

  if (user.privilege != 'Admin') and (user.id != etextbook.user_id):
    return GenericReply(
      message = 'Unauthorized',
      status = HTTPStatusCode.UNAUTHORIZED
    ).to_dict(), HTTPStatusCode.UNAUTHORIZED
  
  etextbook.delete()
  return EditableTextbookDeleteReply(
    message = 'Successfully deleted editable textbook',
    status = HTTPStatusCode.OK
  ).to_dict(), HTTPStatusCode.OK
