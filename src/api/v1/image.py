"""
Image Endpoint
"""

from src import limiter
from src.utils.http import HTTPStatusCode
from src.database import ImageModel, UserModel, ClassroomModel, TextbookModel
from src.service.auth_provider import require_login
from src.utils.api import (
  ImageGetRequest, ImageGetReply, _ImageGetData,
  ImageCreateRequest, ImageCreateReply, _ImageCreateData,
  ImageDeleteRequest, ImageDeleteReply,
  GenericReply
)

from typing import Mapping, Literal, Union
from flask_limiter import util
from flask import (
  request,
  current_app as app
)



# Routes
basePath: str = '/api/v1/image'
auth_limit = limiter.shared_limit('100 per hour', scope = lambda _: request.host, key_func = util.get_remote_address)




@app.route(f'{basePath}/get', methods = ['GET'])
@auth_limit
@require_login
def image_get_api(user: UserModel):
  req = ImageGetRequest(request)

  image = ImageModel.query.filter(ImageModel.id == req.image_id).first()
  if (not image) or (not isinstance(image, ImageModel)):
    return GenericReply(
      message = 'Unable to locate image',
      status = HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST
  

  # Validate
  if (
    image.classroom and (user.privilege != 'Admin') and (user.id not in [
      image.classroom.owner_id,
      *image.classroom.student_ids,
      *image.classroom.educator_ids
    ])
  ):
    return GenericReply(
      message = 'Unauthorized',
      status = HTTPStatusCode.UNAUTHORIZED
    ).to_dict(), HTTPStatusCode.UNAUTHORIZED

  
  return ImageGetReply(
    message = 'Successfully fetched textbook',
    status = HTTPStatusCode.OK,
    data = _ImageGetData(
      uri = image.uri,
      image_id = image.id
    )
  ).to_dict(), HTTPStatusCode.OK




@app.route(f'{basePath}/create', methods = ['POST'])
@auth_limit
@require_login
def image_create_api(user: UserModel):
  req = ImageCreateRequest(request)

  # Validate
  if len(list(filter(None, [req.classroom_id, req.textbook_id, req.user_id]))) != 1:
    return GenericReply(
      message = 'Invalid identifier',
      status = HTTPStatusCode.BAD_REQUEST
    ).to_dict(),  HTTPStatusCode.BAD_REQUEST
  
  upload = req.files.get('upload')
  if not upload:
    return GenericReply(
      message = 'No file supplied',
      status = HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST
  

  if req.user_id:
    author = user if user.id == req.user_id else UserModel.query.filter(UserModel.id == req.user_id).first()
    if not author or not isinstance(author, UserModel):
      return GenericReply(
        message = 'Invalid user',
        status = HTTPStatusCode.BAD_REQUEST
      ).to_dict(), HTTPStatusCode.BAD_REQUEST
    
    newImage = ImageModel(upload, user = user)
  
  elif req.classroom_id:
    classroom = ClassroomModel.query.filter(ClassroomModel.id == req.classroom_id).first()
    if not isinstance(classroom, ClassroomModel):
      return GenericReply(
        message = 'Invalid classroom',
        status = HTTPStatusCode.BAD_REQUEST
      ).to_dict(), HTTPStatusCode.BAD_REQUEST
    
    newImage = ImageModel(upload, classroom = classroom)
  
  elif req.textbook_id:
    textbook = TextbookModel.query.filter(TextbookModel.id == req.textbook_id).first()
    if not isinstance(textbook, TextbookModel):
      return GenericReply(
        message = 'Invalid textbook',
        status = HTTPStatusCode.BAD_REQUEST
      ).to_dict(), HTTPStatusCode.BAD_REQUEST
    
    newImage = ImageModel(upload, textbook = textbook)
  
  else:
    return GenericReply(
      message = 'No parent supplied',
      status = HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST
  

  newImage.save()
  return ImageCreateReply(
    message = 'Image created successfully',
    status = HTTPStatusCode.OK,
    data = _ImageCreateData(
      image_id = newImage.id,
      uri = newImage.uri
    )
  ).to_dict(), HTTPStatusCode.OK




@app.route(f'{basePath}/edit', methods = ['POST'])
@auth_limit
@require_login
def image_edit_api(user: UserModel):
  ...
  





@app.route(f'{basePath}/delete', methods = ['POST'])
@auth_limit
@require_login
def image_delete_api(user: UserModel):
  req = ImageDeleteRequest(request)

  image = ImageModel.query.filter(ImageModel.id == req.image_id).first()
  if (not image) or (not isinstance(image, ImageModel)):
    return GenericReply(
      message = 'Unable to locate image',
      status = HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST
  

  if (
    (image.user and (user.privilege != 'Admin') and (user.id != image.user.id))
    or
    (image.classroom and (user.privilege != 'Admin') and (user.id != image.classroom.owner_id))
    or
    (image.textbook and (user.privilege != 'Admin') and (user.id != image.textbook.author_id))
  ):
    return GenericReply(
      message = 'Unauthorized',
      status = HTTPStatusCode.UNAUTHORIZED
    ).to_dict(), HTTPStatusCode.UNAUTHORIZED
  
  
  image.delete()
  return ImageDeleteReply(
    message = 'Image deleted successfully',
    status = HTTPStatusCode.OK
  ).to_dict(), HTTPStatusCode.OK
