"""
Handles user uploaded content serving
"""

from src.database import UserModel
from src.service import auth_provider, cdn_provider
cdn_provider._dirCheck()

import requests
import cloudinary.api
from werkzeug.exceptions import Unauthorized, BadRequest, NotFound
from typing import Union, Literal, overload
from flask import (
  request,
  Response,
  send_file,
  send_from_directory,
  current_app as app
)


ENV = app.config.get('ENV')
CloudinaryFolder = Literal['image-uploads', 'textbook-uploads', 'submission-uploads']


# Helper Function
@overload
def serve(location: CloudinaryFolder, identifier: str) -> auth_provider.RouteResponse:
  """Handles downloading or serving for production"""
  ...

@overload
def serve(location: str, identifier: str) -> auth_provider.RouteResponse:
  """Handles downloading or serving for development"""
  ...

def serve(location: Union[CloudinaryFolder, str], identifier: str) -> auth_provider.RouteResponse:
  if not identifier:
    raise BadRequest('Invalid identifier')

  if (ENV == 'production') and (location in ['image-uploads', 'textbook-uploads', 'submission-uploads']):
    uploadData = cloudinary.api.resource(f'{location}/{identifier}')

    if not uploadData:
      raise NotFound()

    return send_file(
      requests.get(uploadData['secure_url'], stream = True).raw,
      mimetype = f'{uploadData["resource_type"]}/{uploadData["format"]}',
      as_attachment = bool(request.args.get('download', None))
    )
  
  elif ENV == 'production':
    raise BadRequest('Invalid location')

  return send_from_directory(
    location,
    identifier,
    as_attachment = bool(request.args.get('download', None)),
  )



# Misc
@app.route('/robots.txt')
def noindex():
  response = Response(
    response = 'User-agent: *\nDisallow: /\n',
    status = 200,
    mimetype = 'text/plain'
  )
  response.headers['Content-Type'] = 'text/plain; charset=utf-8'
  return response




# Images
@app.route('/public/image/<path:ident>', methods = ['GET'])
@auth_provider.optional_login
def uploaded_images(user: UserModel | None, ident: str):
  return serve(
    'image-uploads' if ENV == 'production' else cdn_provider.ImageLocation,
    ident
  )




# Textbooks
@app.route('/public/textbook/<path:ident>', methods = ['GET'])
@auth_provider.require_login
def uploaded_textbooks(user: UserModel, ident: str):
  if user.privilege == 'Admin':
    return serve(
      'textbook-uploads' if ENV == 'production' else cdn_provider.TextbookLocation,
      ident
    )
  
  for book in user.textbooks:
    if book.iuri.endswith(ident):
      return serve(
      'textbook-uploads' if ENV == 'production' else cdn_provider.TextbookLocation,
      ident
    )
  
    else: raise Unauthorized()
  raise NotFound()
