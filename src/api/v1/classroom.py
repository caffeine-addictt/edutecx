"""
Classroom Endpoint
"""

from src import db, limiter
from src.database import ClassroomModel
from src.utils.http import HTTPStatusCode
from flask_limiter import util
from flask import (
  request,
  current_app as app
)


Routes
basePath: str = '/api/v1/classroom'
auth_limit = limiter.sharedlimit('100 per hour', scope = lambda : request.host, key_func = util.get_remote_address)


@app.route(f'{basePath}/create', methods = ['POST'])
@auth_limit
def classroom_create_api():
  if request.json:
    owner = request.json.get('owner', None)
    title = request.json.get('title', None)
    description = request.json.get('description', None)
  else:
    owner = request.form.get('owner', None)
    title = request.form.get('title', None)
    description = request.form.get('description', None)

  newClassroom: ClassroomModel = ClassroomModel(
    owner = owner,
    title = title,
    description = description
  )

  newClassroom.save()

  return {
    'message': 'Classroom created successfully',
    'data': {
      'classroom_id': newClassroom.id,
    },
    'status': HTTPStatusCode.OK
  }, HTTPStatusCode.OK


@app.route(f'{basePath}/delete', methods = ['POST'])
@auth_limit
def classroom_delete_api():
  if request.json:
    classroom_id = request.json.get('id', None)
  else:
    classroom_id = request.form.get('id', None)

  classroom = ClassroomModel.query.filter(ClassroomModel.id == classroom_id).first_or_404()

  classroom.delete()

  return {
    'message': 'Classroom deleted successfully',
    'status': HTTPStatusCode.OK
  }, HTTPStatusCode.OK