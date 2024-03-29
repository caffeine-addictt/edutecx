"""
Handles textbook routes
"""

from src.database import UserModel, TextbookModel
from src.service import auth_provider
from src.utils.http import escape_id
from flask import render_template, current_app as app


@app.route('/textbooks')
@auth_provider.require_login
def textbooks(user: UserModel):
  return render_template('(textbook)/textbook_list.html')


@app.route('/textbooks/<string:id>')
@auth_provider.require_login
def textbooks_focused(user: UserModel, id: str):
  id = escape_id(id)
  textbook = TextbookModel.query.filter(TextbookModel.id == id).first()
  if not isinstance(textbook, TextbookModel):
    return render_template(
      '(textbook)/textbook_error.html', message='Unable to locate textbook'
    )

  if (user.privilege != 'Admin') and textbook not in (
    user.textbooks + user.owned_textbooks
  ):
    return render_template(
      '(textbook)/textbook_error.html',
      message='You are not authorized to access this textbook',
    )

  return render_template('(textbook)/textbook.html', textbook=textbook)


@app.route('/textbooks/new', methods=['GET'])
@auth_provider.require_educator(unauthorized_redirect='/pricing')
def textbook_new(user: UserModel):
  return render_template('(textbook)/textbook_new.html', user=user)
