"""
Handles assignment routes
"""

from src.database import UserModel, AssignmentModel
from src.service import auth_provider

from src.utils.http import escape_id
from flask import (
  render_template,
  current_app as app
)



@app.route('/assignments')
@auth_provider.require_login
def assignments(user: UserModel):
  return render_template('(assignment)/assignment_list.html')


@app.route('/assignments/<string:id>')
@auth_provider.require_login
def assignment(user: UserModel, id: str):
  id = escape_id(id)
  return render_template('(assignment)/assignment.html')


@app.route('/assignment/new', methods = ['GET'])
@auth_provider.require_educator(unauthorized_redirect = '/pricing')
def assignment_new(user: UserModel):
  return render_template('(assignment)/assignment_new.html')
