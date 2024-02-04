"""
Handles submission routes
"""

from src.database import UserModel, SubmissionModel
from src.service import auth_provider

from src.utils.http import escape_id
from flask import render_template, current_app as app


@app.route('/submissions')
@auth_provider.require_login
def submissions(_: UserModel):
  return render_template('(submission)/submission_list.html')


@app.route('/submissions/<string:id>')
@auth_provider.require_login
def submission(user: UserModel, id: str):
  id = escape_id(id)

  submission = SubmissionModel.query.filter(SubmissionModel.id == id).first()
  if not isinstance(submission, SubmissionModel):
    return render_template(
      '(submission)/submission_error.html', message='Unable to locate submission'
    )

  if (user.privilege != 'Admin') and (
    (submission.student_id != user.id)
    or (not submission.assignment.classroom.is_privileged(user))
  ):
    return render_template('(submission)/submission_error.html', message='Unauthorized')

  return render_template('(submission)/submission.html', submission=submission)
