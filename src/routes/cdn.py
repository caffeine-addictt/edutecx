"""
Handles user uploaded content serving
"""

from src.database import UserModel
from src.service import auth_provider, cdn_provider
cdn_provider._dirCheck()

from werkzeug.exceptions import Unauthorized, NotFound
from flask import (
  request,
  Response,
  send_from_directory,
  current_app as app
)




# Helper Function
def serve(location: str, filename: str) -> Response:
  """
  Handles downloading or serving
  """
  return send_from_directory(
    location,
    filename,
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
@app.route('/public/image/<path:filename>', methods = ['GET'])
def uploaded_images(filename: str):
  return serve(
    cdn_provider.ImageLocation,
    filename
  )




# Editable Textbooks
@app.route('/public/editabletextbook/<path:filename>', methods = ['GET'])
@auth_provider.require_login
def editable_textbook_cdn(user: UserModel, filename: str):
  if user.privilege == 'Admin':
    return serve(
      cdn_provider.EditableTextbookLocation,
      filename
    )
  
  for book in user.owned_textbooks:
    if book.iuri.endswith(filename):
      return serve(
        cdn_provider.EditableTextbookLocation,
        filename
      )
  
  raise NotFound()




# Textbooks
@app.route('/public/textbook/<path:filename>', methods = ['GET'])
@auth_provider.require_login
def uploaded_textbooks(user: UserModel, filename: str):
  if user.privilege == 'Admin':
    return serve(
      cdn_provider.TextbookLocation,
      filename
    )
  
  for book in user.textbooks:
    if book.iuri.endswith(filename):
      return serve(
      cdn_provider.TextbookLocation,
      filename
    )
  
  else: raise Unauthorized()




# Admin graphs
@app.route('/public/graph/<path:filename>', methods = ['GET'])
@auth_provider.require_admin
def uploaded_graphs(user: UserModel, filename: str):
  return serve(
    cdn_provider.GraphFileLocation,
    filename
  )
