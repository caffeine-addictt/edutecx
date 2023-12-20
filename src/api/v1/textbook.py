"""
Textbook Endpoint
"""

from src import db, limiter
from src.database import TextbookModel
from src.utils.http import HTTPStatusCode
from flask_limiter import util
from flask import (
  request,
  current_app as app
)


# Routes
basePath: str = '/api/v1/textbook'
auth_limit = limiter.shared_limit('100 per hour', scope = lambda _: request.host, key_func = util.get_remote_address)

@app.route(f'{basePath}/create', methods = ['POST'])
@auth_limit
def textbook_create_api():
  if request.json:
    author = request.json.get('author', None)
    file = request.json.get('file', None)
    title = request.json.get('title', None)
    description = request.json.get('description', None)
    price = request.json.get('price', None)
    discount = request.json.get('discount', None)

  else:
    author = request.form.get('author', None)
    file = request.form.get('file', None)
    title = request.form.get('title', None)
    description = request.form.get('description', None)
    price = request.form.get('price', None)
    discount = request.form.get('discount', None)

  newTextbook: TextbookModel = TextbookModel(
    author = author,
    file = file,
    title = title,
    description = description,
    price = price,
    discount = discount
  )

  newTextbook.save()
  
  return {
    'message': 'Textbook created successfully',
    'data': {
      'textbook_id': newTextbook.id,
    },
    'status': HTTPStatusCode.OK
  }, HTTPStatusCode.OK
  
@app.route(f'{basePath}/delete', methods = ['POST'])
@auth_limit
def textbook_delete_api():
  if request.json:
    textbook_id = request.json.get('id', None)
  else:
    textbook_id = request.form.get('id', None)

  textbook = TextbookModel.query.filter(TextbookModel.id == textbook_id).first_or_404()

  textbook.delete()

  return {
    'message': 'Textbook deleted successfully',
    'status': HTTPStatusCode.OK
  }, HTTPStatusCode.OK
  
