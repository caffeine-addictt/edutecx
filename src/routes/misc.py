"""
Handles misc routing
"""

from src.database import DocumentModel, UserModel
from src.utils.http import escape_id

from typing import List
from flask import (
  g,
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
  flash(message = user.username, category = 'danger')
  return render_template('(misc)/home.html')

@app.route('/profile')
@auth_provider.require_login
def profile(user: UserModel):
  return render_template('(misc)/profile.html')


# Textbooks
@app.route('/textbooks')
@auth_provider.require_login
def textbooks(user: UserModel):
  user = g.current_user
  documents = None # TODO: UserModel helper method
  return render_template('(misc)/textbook_list.html', documents = documents)

@app.route('/textbooks/<string:id>')
@auth_provider.require_login
def textbooks_id(user: UserModel, id: str):
  id = escape_id(id)
  document = None # TODO: UserModel helper method
  return render_template('(misc)/textbook.html', document = document)


# Classrooms
@app.route('/classrooms')
@auth_provider.require_login
def classrooms(user: UserModel):
  # Check if user is in a classroom
  isInClassroom = False
  if not isInClassroom:
    abort(404)

  classes = None

  return render_template('(misc)/classroom_list.html', classes = classes)

@app.route('/classrooms/<string:id>')
@auth_provider.require_login
def classroom(user: UserModel):
  # Check if user is in a classroom
  isInClassroom = False
  if not isInClassroom:
    abort(404)

  classes = None

  return render_template('(misc)/classroom_list.html', classes = classes)


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
