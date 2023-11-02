"""
Handles misc routing
"""

from src.database import DocumentModel
from src.utils.http import escape_id
from src.utils.ext.login import loggedin_required

from typing import List
from flask import (
  g,
  abort,
  flash,
  request,
  render_template,
  current_app as app
)


# General routes
@app.route('/')
@loggedin_required()
def index():
  return render_template('(misc)/root.html')

# TODO: Get stored user session
@app.route('/cart')
@loggedin_required()
def cart():
  return render_template('(misc)/cart.html')

# TODO: Add SQL sanitization and caching to all DB models
@app.route('/store')
@loggedin_required()
def store():
  query = request.args.get('search', '')
  documents: List['DocumentModel'] = DocumentModel.query.all()

  return render_template('(misc)/store.html')


# Textbooks
@app.route('/textbooks')
@loggedin_required()
def textbooks():
  user = g.current_user
  documents = None # TODO: UserModel helper method
  return render_template('(misc)/textbook_list.html', documents = documents)

@app.route('/textbooks/<string:id>')
@loggedin_required()
def textbooks_id(id: str):
  id = escape_id(id)
  document = None # TODO: UserModel helper method
  return render_template('(misc)/textbook.html', document = document)


# Classrooms
@app.route('/classrooms')
@loggedin_required()
def classrooms():
  user = g.current_user

  # Check if user is in a classroom
  isInClassroom = False
  if not isInClassroom:
    abort(404)

  classes = None

  return render_template('(misc)/classroom_list.html', classes = classes)

@app.route('/classrooms/<string:id>')
@loggedin_required()
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
@loggedin_required()
def assignments():
  # Get assignments
  return render_template('(misc)/assignment_list.html')

@app.route('/assignments/<string:id>')
@loggedin_required()
def assignment(id: str):
  id = escape_id(id)

  return render_template('(misc)/assignment.html')


# Submissions
@app.route('/submissions')
@loggedin_required()
def submissions():
  return render_template('(misc)/submission_list.html')

@app.route('/submissions/<string:id>')
@loggedin_required()
def submission():
  return render_template('(misc)/submission.html')
