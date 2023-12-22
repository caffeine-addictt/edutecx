"""
Image Endpoint
"""

from src import db, limiter
from src.utils.http import HTTPStatusCode
from src.database import ImageModel, UserModel
from src.service.auth_provider import require_login
from src.utils.api import (
  ImageGetRequest, ImageGetReply, _ImageGetData,
  ImageCreateRequest, ImageCreateReply, _ImageCreateData,
  # TextbookEditRequest, TextbookEditReply,
  ImageDeleteRequest, ImageDeleteReply,
  GenericReply
)

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

  # TODO: Make sure at least one id is not none 

  author = user if user.id == req.author_id else UserModel.query.filter(UserModel.id == req.author_id).first()
  if not author or not isinstance(author, UserModel):
    return GenericReply(
      message = 'Invalid user',
      status = HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST


  newImage = ImageModel(
    file = req.files.get('upload')
    user = user
    textbook = textbook
    classroom = classroom
  )
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

# TODO Authorisation to delete image
  
  image.delete()
  return ImageDeleteReply(
    message = 'Image deleted successfully',
    status = HTTPStatusCode.OK
  ).to_dict(), HTTPStatusCode.OK
