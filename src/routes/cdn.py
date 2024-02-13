"""
Handles user uploaded content serving
"""

import requests
import cloudinary.api
from flask import current_app as app
from flask import Response, request, send_file, send_from_directory


from typing import Literal, Union, overload
from werkzeug.exceptions import BadRequest, NotFound, Unauthorized


from src.database import SubmissionSnippetModel, UserModel
from src.service import auth_provider, cdn_provider

cdn_provider._dirCheck()


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


def serve(
  location: Union[CloudinaryFolder, str], identifier: str
  ) -> auth_provider.RouteResponse:
  if not identifier:
    raise BadRequest('Invalid identifier')

  if (ENV == 'production') and (
    location in ['image-uploads', 'textbook-uploads', 'submission-uploads']
  ):
    uploadData = cloudinary.api.resource(f'{location}/{identifier}')

    if not uploadData:
      raise NotFound()

    return send_file(
      requests.get(uploadData['secure_url'], stream=True).raw,
      mimetype=f'{uploadData["resource_type"] if location != "textbook-uploads" else "application"}/{uploadData["format"]}',
      as_attachment=bool(request.args.get('download', None)),
    )

  elif ENV == 'production':
    raise BadRequest('Invalid location')
  return send_from_directory(
    location,
    identifier,
    as_attachment=bool(request.args.get('download', None)),
  )


# Misc
@app.route('/robots.txt')
def noindex():
  response = Response(
    response='User-agent: *\nDisallow: /\n', status=200, mimetype='text/plain'
  )
  response.headers['Content-Type'] = 'text/plain; charset=utf-8'
  return response


# Images
@app.route('/public/image/<path:ident>', methods=['GET'])
@auth_provider.optional_login
def uploaded_images(_: UserModel | None, ident: str):
  return serve(
    'image-uploads' if ENV == 'production' else cdn_provider.ImageLocation, ident
  )


# Textbooks
@app.route('/public/textbook/<path:ident>', methods=['GET'])
@auth_provider.require_login
def uploaded_textbooks(user: UserModel, ident: str):
  if user.privilege == 'Admin':
    return serve(
      'textbook-uploads' if ENV == 'production' else cdn_provider.TextbookLocation,
      ident,
    )

  for book in user.textbooks + user.owned_textbooks:
    if book.iuri.endswith(ident):
      return serve(
        'textbook-uploads' if ENV == 'production' else cdn_provider.TextbookLocation,
        ident,
      )

    else:
      raise Unauthorized()
  raise NotFound()


# Submissions
@app.route('/public/submission/<path:ident>', methods=['GET'])
@auth_provider.require_login
def uploaded_submissions(user: UserModel, ident: str):
  if user.privilege == 'Admin':
    return serve(
      'submission-uploads' if ENV == 'production' else cdn_provider.SubmissionUpload,
      ident,
    )

  snippet = SubmissionSnippetModel.query.filter(
    SubmissionSnippetModel.iuri.contains(ident)
  ).first()
  if not isinstance(snippet, SubmissionSnippetModel):
    raise NotFound()

  if (snippet.student == user) or snippet.submission.assignment.classroom.is_privileged(
    user
  ):
    return serve(
      'submission-uploads' if ENV == 'production' else cdn_provider.SubmissionUpload,
      ident,
    )

  raise Unauthorized()
