"""
Textbook Endpoint
"""

from src import limiter
from src.utils.http import HTTPStatusCode
from src.database import TextbookModel, UserModel, ImageModel
from src.service.auth_provider import require_login
from src.utils.ext import utc_time
from src.utils.api import (
  TextbookGetRequest, TextbookGetReply, _TextbookGetData,
  TextbookCreateRequest, TextbookCreateReply, _TextbookCreateData,
  TextbookEditRequest, TextbookEditReply,
  TextbookDeleteRequest, TextbookDeleteReply,
  GenericReply
)

from werkzeug.datastructures import FileStorage
from flask_limiter import util
from flask import (
  request,
  current_app as app
)


# Routes
basePath: str = '/api/v1/textbook'
auth_limit = limiter.shared_limit('100 per hour', scope = lambda _: request.host, key_func = util.get_remote_address)




@app.route(f'{basePath}/get', methods = ['GET'])
@auth_limit
@require_login
def textbooks_get_api(user: UserModel):
  req = TextbookGetRequest(request)

  textbook = TextbookModel.query.filter(TextbookModel.id == req.textbook_id).first()
  if not isinstance(textbook, TextbookModel):
    return GenericReply(
      message = 'Unable to locate textbook',
      status = HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST
  

  return TextbookGetReply(
    message = 'Successfully fetched textbook',
    status = HTTPStatusCode.OK,
    data = _TextbookGetData(
      id = textbook.id,
      author_id = textbook.author_id,
      title = textbook.title,
      description = textbook.description,
      categories = textbook.categories.split('|'),
      price = textbook.price,
      discount = textbook.discount,
      uri = textbook.uri,
      status = textbook.status,
      cover_image = textbook.cover_image.uri if textbook.cover_image else None,
      created_at = textbook.created_at.timestamp(),
      updated_at = textbook.updated_at.timestamp(),
    )
  ).to_dict(), HTTPStatusCode.OK




@app.route(f'{basePath}/create', methods = ['POST'])
@auth_limit
@require_login
def textbook_create_api(user: UserModel):
  req = TextbookCreateRequest(request)

  author = user if user.id == req.author_id else UserModel.query.filter(UserModel.id == req.author_id).first()
  if not isinstance(author, UserModel):
    return GenericReply(
      message = 'Invalid user',
      status = HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST
  

  newTextbook = TextbookModel(
    author = author,
    file = req.files['upload'],
    title = req.title,
    description = req.description,
    price = req.price,
    discount = req.discount
  )
  newTextbook.save()

  if cover_img := req.files.get('cover_img'):
    ImageModel(
      file = cover_img,
      textbook = newTextbook
    ).save()


  return TextbookCreateReply(
    message = 'Textbook created successfully',
    status = HTTPStatusCode.OK,
    data = _TextbookCreateData(
      textbook_id = newTextbook.id
    )
  ).to_dict(), HTTPStatusCode.OK




@app.route(f'{basePath}/edit', methods = ['POST'])
@auth_limit
@require_login
def textbooks_edit_api(user: UserModel):
  req = TextbookEditRequest(request)

  toChange = {key: req.get(key, None) for key in [
    'title',
    'description',
    'categories',
    'price',
    'discount'
  ] if ((req.get(key, None) is not None) or (not req.ignore_none))}

  if (i := req.files.get('cover_img')) or (not req.ignore_none):
    toChange['cover_img'] = i

  if not any(toChange.values()):
    return GenericReply(
      message = 'No change supplied',
      status = HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST
  

  textbook = TextbookModel.query.filter(TextbookModel.id == req.textbook_id).first()
  if not isinstance(textbook, TextbookModel):
    return GenericReply(
      message = 'Unable to locate textbook',
      status = HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST
  
  if (user.privilege != 'Admin') and (user.id != textbook.author_id):
    return GenericReply(
      message = 'Unauthorized',
      status = HTTPStatusCode.UNAUTHORIZED
    ).to_dict(), HTTPStatusCode.UNAUTHORIZED
  
  
  for key, value in toChange.items():
    if isinstance(value, FileStorage):
      curr: ImageModel | None = textbook.__getattribute__(key)
      if curr: curr.delete()

      ImageModel(
        file = value,
        textbook = textbook
      ).save()
    
    else:
      textbook.__setattr__(key, value)
    
  textbook.updated_at = utc_time.get()
  textbook.save()

  return TextbookEditReply(
    message = 'Successfully edited textbook',
    status = HTTPStatusCode.OK
  ).to_dict(), HTTPStatusCode.OK




@app.route(f'{basePath}/delete', methods = ['POST'])
@auth_limit
@require_login
def textbook_delete_api(user: UserModel):
  req = TextbookDeleteRequest(request)

  textbook = TextbookModel.query.filter(TextbookModel.id == req.textbook_id).first()
  if not isinstance(textbook, TextbookModel):
    return GenericReply(
      message = 'Unable to locate textbook',
      status = HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST

  if (user.privilege != 'Admin') and (user.id != textbook.author_id):
    return GenericReply(
      message = 'Unauthorized',
      status = HTTPStatusCode.UNAUTHORIZED
    ).to_dict(), HTTPStatusCode.UNAUTHORIZED


  textbook.delete()
  return TextbookDeleteReply(
    message = 'Textbook deleted successfully',
    status = HTTPStatusCode.OK
  ).to_dict(), HTTPStatusCode.OK
