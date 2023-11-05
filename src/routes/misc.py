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

# TODO: Get stored user session
@app.route('/cart')
def cart():
  return render_template('(misc)/cart.html')

# TODO: Add SQL sanitization and caching to all DB models
@app.route('/store')
def store():
  query = request.args.get('search', '')
  documents: List['DocumentModel'] = DocumentModel.query.all()

  return render_template('(misc)/store.html')

@app.route('/profile')
def profile():
  return render_template('(misc)/profile.html')


# Textbooks
@app.route('/textbooks')
def textbooks():
  user = g.current_user
  documents = None # TODO: UserModel helper method
  return render_template('(misc)/textbook_list.html', documents = documents)

@app.route('/textbooks/<string:id>')
def textbooks_id(id: str):
  id = escape_id(id)
  document = None # TODO: UserModel helper method
  return render_template('(misc)/textbook.html', document = document)


# Classrooms
@app.route('/classrooms')
def classrooms():
  user = g.current_user

  # Check if user is in a classroom
  isInClassroom = False
  if not isInClassroom:
    abort(404)

  classes = None

  return render_template('(misc)/classroom_list.html', classes = classes)

@app.route('/classrooms/<string:id>')
def classroom():
  user = g.current_user

  # Check if user is in a classroom
  isInClassroom = False
  if not isInClassroom:
    abort(404)

  classes = None

  return render_template('(misc)/classroom_list.html', classes = classes)


# Assignments
@app.route('/assignments')
def assignments():
  # Get assignments
  return render_template('(misc)/assignment_list.html')

@app.route('/assignments/<string:id>')
def assignment(id: str):
  id = escape_id(id)

  return render_template('(misc)/assignment.html')


# Submissions
@app.route('/submissions')
def submissions():
  # Get submissions
  return render_template('(misc)/submission_list.html')

@app.route('/submissions/<string:id>')
def submission():
  return render_template('(misc)/submission.html')
