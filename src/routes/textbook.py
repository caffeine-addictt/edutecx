"""
Handles textbook routes
"""

from src.database import UserModel, EditableTextbookModel
from src.service import auth_provider

from werkzeug.exceptions import Unauthorized
from src.utils.http import escape_id
from flask import (
  render_template,
  current_app as app
)




@app.route('/textbooks')
@auth_provider.require_login
def textbooks(user: UserModel):
  return render_template('(textbook)/textbook_list.html')


@app.route('/textbooks/<string:id>')
@auth_provider.require_login
def textbooks_focused(user: UserModel, id: str):
  id = escape_id(id)
  textbook = EditableTextbookModel.query.filter(EditableTextbookModel.id == id).first()
  return render_template('(textbook)/textbook.html', textbook = textbook)


@app.route('/textbooks/new', methods = ['GET'])
@auth_provider.require_educator(unauthorized_redirect = '/pricing')
def textbook_new(user: UserModel):
  return render_template('(textbook)/textbook_new.html', user = user)
