"""
Handles misc routing
"""

from src.database import TextbookModel, UserModel
from src.utils.http import escape_id

from typing import List
from flask import (
  abort,
  flash,
  request,
  render_template,
  current_app as app
)

from src.service import auth_provider


# General routes
@app.route('/')
def index():
  return render_template('(misc)/root.html')


@app.route('/home')
@auth_provider.require_login
def home(user: UserModel):
  return render_template('(misc)/home.html', user = user)


@app.route('/profile')
@auth_provider.require_login
def profile(user: UserModel):
  return render_template('(misc)/profile.html', user = user)




# Textbooks
@app.route('/textbooks')
@auth_provider.require_login
def textbooks(user: UserModel):
  return render_template('(misc)/textbook_list.html')


@app.route('/textbooks/<string:id>')
@auth_provider.require_login
def textbooks_id(user: UserModel, id: str):
  return render_template('(misc)/textbook.html')




# Classrooms
@app.route('/classrooms', methods = ['GET'])
@auth_provider.require_login
def classrooms(user: UserModel):
  return render_template('(misc)/classroom_list.html', user = user)


@app.route('/classrooms/<string:id>')
@auth_provider.require_login
def classroom(user: UserModel):
  return render_template('(misc)/classroom.html')




# Assignments
@app.route('/assignments')
@auth_provider.require_login
def assignments(user: UserModel):
  # Get assignments
  return render_template('(misc)/assignment_list.html')


@app.route('/assignments/<string:id>')
@auth_provider.require_login
def assignment(user: UserModel, id: str):
  id = escape_id(id)

  return render_template('(misc)/assignment.html')




# Submissions
@app.route('/submissions')
@auth_provider.require_login
def submissions(user: UserModel):
  # Get submissions
  return render_template('(misc)/submission_list.html')


@app.route('/submissions/<string:id>')
@auth_provider.require_login
def submission(user: UserModel):
  return render_template('(misc)/submission.html')
