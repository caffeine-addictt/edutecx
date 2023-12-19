"""
Assignment Endpoint
"""

from src import db, limiter
from src.database import AssignmentModel
from src.utils.http import HTTPStatusCode
from flask_limiter import util
from flask import (
  request,
  current_app as app
)


Routes
basePath: str = '/api/v1/assignment'
auth_limit = limiter.sharedlimit('100 per hour', scope = lambda : request.host, key_func = util.get_remote_address)


@app.route(f'{basePath}/create', methods = ['POST'])
@auth_limit
def assignment_create_api():
  if request.json:
    classroom = request.json.get('classroom', None)
    title = request.json.get('title', None)
    description = request.json.get('description', None)
    due_date = request.json.get('due_date', None)
    requirement = request.json.get('requirement', None)
  else:
    classroom = request.form.get('classroom', None)
    title = request.form.get('title', None)
    description = request.form.get('description', None)
    due_date = request.form.get('due_date', None)
    requirement = request.form.get('requirement', None)

  newAssignment: AssignmentModel = AssignmentModel(
    classroom = classroom,
    title = title,
    description = description,
    due_date = due_date,
    requirement = requirement


  )

  newAssignment.save()

  return {
    'message': 'Assignment created successfully',
    'data': {
      'assignment_id': newAssignment.id,
    },
    'status': HTTPStatusCode.OK
  }, HTTPStatusCode.OK


@app.route(f'{basePath}/delete', methods = ['POST'])
@auth_limit
def assignment_delete_api():
  if request.json:
    assignment_id = request.json.get('id', None)
  else:
    assignment_id = request.form.get('id', None)

  assignment = AssignmentModel.query.filter(AssignmentModel.id == assignment_id).first_or_404()

  assignment.delete()

  return {
    'message': 'Classroom deleted successfully',
    'status': HTTPStatusCode.OK
  }, HTTPStatusCode.OK