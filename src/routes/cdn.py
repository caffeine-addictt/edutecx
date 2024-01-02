"""
Handles user uploaded content serving
"""

from src.database import UserModel

from flask import (
  Response,
  send_from_directory,
  current_app as app
)
from werkzeug.exceptions import Unauthorized

from src.service import auth_provider, cdn_provider
cdn_provider._dirCheck()




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
@app.route('/public/images/<path:filename>')
def uploaded_images(filename: str):
  return send_from_directory(
    cdn_provider.ImageLocation,
    filename
  )




# Editable Textbooks
@app.route('/public/editabletextbook/<path:filename>', methods = ['GET'])
@auth_provider.require_login
def editable_textbook_cdn(user: UserModel, filename: str):
  if user.privilege == 'Admin':
    return send_from_directory(
      cdn_provider.EditableTextbookLocation,
      filename
    )
  
  for book in user.owned_textbooks:
    if book.iuri.endswith(filename):
      return send_from_directory(
        cdn_provider.EditableTextbookLocation,
        filename
      )




# Textbooks
@app.route('/public/textbook/<path:filename>')
@auth_provider.require_login
def uploaded_textbooks(user: UserModel, filename: str):
  if user.privilege == 'Admin':
    return send_from_directory(
      cdn_provider.TextbookLocation,
      filename,
      as_attachment = True
    )
  
  for book in user.textbooks:
    if book.iuri.endswith(filename):
      return send_from_directory(
      cdn_provider.TextbookLocation,
      filename
    )
  
  else: raise Unauthorized()




# Admin graphs
@app.route('/public/graphs/<path:filename>')
@auth_provider.require_admin
def uploaded_graphs(user: UserModel, filename: str):
  return send_from_directory(
    cdn_provider.GraphFileLocation,
    filename
  )
