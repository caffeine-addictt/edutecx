"""
Handles submission routes
"""

from src.database import UserModel, SubmissionModel
from src.service import auth_provider

from src.utils.http import escape_id
from flask import (
  render_template,
  current_app as app
)




@app.route('/submissions')
@auth_provider.require_login
def submissions(user: UserModel):
  # Get submissions
  return render_template('(submission)/submission_list.html')


@app.route('/submissions/<string:id>')
@auth_provider.require_login
def submission(user: UserModel, id: str):
  id = escape_id(id)
  return render_template('(submission)/submission.html')
