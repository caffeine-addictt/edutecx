"""
Assignment Endpoint
"""

from src import db, limiter
from src.database import AssignmentModel, ClassroomModel, UserModel
from src.service.auth_provider import require_login
from src.utils.http import HTTPStatusCode
from src.utils.ext import utc_time
from src.utils.api import (
  GenericReply
)

import re
from datetime import datetime
from flask_limiter import util
from flask import (
  request,
  current_app as app
)

from sqlalchemy import and_, or_


# Routes
basePath: str = '/api/v1/assignment'
auth_limit = limiter.shared_limit('100 per hour', scope = lambda _: request.host, key_func = util.get_remote_address)




@app.route(f'{basePath}/create', methods = ['POST'])
@auth_limit
@require_login
def assignment_create_api(user: UserModel):
  if request.json:
    classroom_id = request.json.get('classroom_id', None)
    title = request.json.get('title', None)
    description = request.json.get('description', None)
    due_date = request.json.get('due_date', None)
    requirement = request.json.get('requirement', None)
  else:
    classroom_id = request.form.get('classroom_id', None)
    title = request.form.get('title', None)
    description = request.form.get('description', None)
    due_date = request.form.get('due_date', None) # UNIX Millies / infinity
    requirement = request.form.get('requirement', None)


  # Validate
  title = str(title)
  description = str(description)
  requirement = str(requirement)


  # Validate requirement
  if not re.match(r'^[\d|(\d:\d)]$', requirement):
    return GenericReply(
      message = 'Invalid requirement',
      status = HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST
  

  # Validate due_date
  if (due_date != 'infinity' and not isinstance(due_date, int)) or (utc_time.get().timestamp() >= int(due_date)):
    return GenericReply(
      message = 'Invalid due date',
      status = HTTPStatusCode.BAD_REQUEST
    ), HTTPStatusCode.BAD_REQUEST
  
  else:
    due_date = datetime.fromtimestamp(int(due_date))



  # Validate classroom
  classroom = ClassroomModel.query.filter(and_(
    ClassroomModel.id == classroom_id,
    or_(
      ClassroomModel.owner_id == user.id,
      ClassroomModel.educator_ids.contains(user.id)
    )
  )).first()

  if not classroom or not isinstance(classroom, ClassroomModel):
    return GenericReply(
      message = 'Invalid classroom',
      status = HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST



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
@require_login
def assignment_delete_api(user: UserModel):
  if request.json:
    assignment_id = request.json.get('id', None)
  else:
    assignment_id = request.form.get('id', None)


  # Validate
  assignment = AssignmentModel.query.filter(AssignmentModel.id == assignment_id).first()
  if not assignment or not isinstance(assignment, AssignmentModel):
    return GenericReply(
      message = 'Could not located assignment',
      status = HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST
  
  if user.id not in set(assignment.classroom.owner_id, *assignment.classroom.educator_ids):
    return GenericReply(
      message = 'Unauthorized',
      status = HTTPStatusCode.UNAUTHORIZED
    ).to_dict(), HTTPStatusCode.UNAUTHORIZED

  assignment.delete()


  return {
    'message': 'Classroom deleted successfully',
    'status': HTTPStatusCode.OK
  }, HTTPStatusCode.OK
