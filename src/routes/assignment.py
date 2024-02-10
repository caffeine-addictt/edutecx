"""
Handles assignment routes
"""

from src.database import UserModel, AssignmentModel
from src.service import auth_provider

from src.utils.http import escape_id
from flask import render_template, current_app as app


@app.route('/assignments')
@auth_provider.require_login
def assignments(user: UserModel):
  return render_template('(assignment)/assignment_list.html')


@app.route('/assignments/<string:id>')
@auth_provider.require_login
def assignment(user: UserModel, id: str):
  id = escape_id(id)
  assignment = AssignmentModel.query.filter_by(AssignmentModel.id == id).first()

  if not isinstance(assignment, AssignmentModel):
    return render_template(
      '(assignment)/assignment_error.html', message='Assignment does not exist'
    )

  if (user.privilege != 'Admin') or not assignment.classroom.is_member(user):
    return render_template(
      '(assignment)/assignment_error.html',
      message='You do not have access to this assignment',
    )

  return render_template('(assignment)/assignment.html', assignment=assignment)


@app.route('/assignments/new', methods=['GET'])
@auth_provider.require_educator(unauthorized_redirect='/pricing')
def assignment_new(user: UserModel):
  return render_template('(assignment)/assignment_new.html')
