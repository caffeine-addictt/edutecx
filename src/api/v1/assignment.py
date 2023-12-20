"""
Assignment Endpoint
"""

from src import db, limiter
from src.database import AssignmentModel, ClassroomModel, UserModel
from src.service.auth_provider import require_login
from src.utils.http import HTTPStatusCode
from src.utils.ext import utc_time
from src.utils.api import (
  AssignmentCreateRequest, AssignmentCreateReply, _AssignmentCreateData,
  AssignmentEditRequest,
  AssignmentDeleteRequest,
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
  req = AssignmentCreateRequest(request)


  # Validate requirement
  if (not re.match(r'^(\d+(:\d+)?)$', req.requirement)) or (
    (i := req.requirement.split(':')) and (
      (len(i) > 2)
      or
      ((len(i) == 2) and (i[1] < i[0]))
    )
  ):
    return GenericReply(
      message = 'Invalid requirement',
      status = HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST
  

  # Validate due_date
  if (req.due_date != 'infinity' and not isinstance(req.due_date, int)) or (utc_time.get().timestamp() >= int(req.due_date)):
    return GenericReply(
      message = 'Invalid due date',
      status = HTTPStatusCode.BAD_REQUEST
    ), HTTPStatusCode.BAD_REQUEST
  
  due_date = datetime.fromtimestamp(req.due_date) if isinstance(req.due_date, int) else None


  # Validate classroom
  classroom = ClassroomModel.query.filter(and_(
    ClassroomModel.id == req.classroom_id,
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
    title = req.title,
    description = req.description,
    due_date = due_date,
    requirement = req.requirement
  )
  newAssignment.save()

  return AssignmentCreateReply(
    message = 'Assignment created successfully',
    status = HTTPStatusCode.OK,
    data = _AssignmentCreateData(
      assignment_id = newAssignment.id
    )
  ).to_dict(), HTTPStatusCode.OK




@app.route(f'{basePath}/edit', method = ['POST'])
@auth_limit
@require_login
def assignment_edit_api(user: UserModel):
  req = AssignmentEditRequest(request)

  assignment = AssignmentModel.query.filter(AssignmentModel.id == req.assignment_id).first()
  if not assignment or not isinstance(assignment, AssignmentModel):
    return GenericReply(
      message = 'Unable to locate assignment',
      status = HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST
  
  if (user.privilege != 'Admin') and (user.id not in [assignment.classroom.owner_id, *assignment.classroom.educator_ids]):
    return GenericReply(
      message = 'Unauthorized',
      status = HTTPStatusCode.UNAUTHORIZED
    ).to_dict(), HTTPStatusCode.UNAUTHORIZED
  
  # Manually state allow list
  for key in [
    'title',
    'description',
    'due_date',
    'requirement'
  ]:
    value = req.get(key, None)

    if (value is not None) or (not req.ignore_none):
      assignment.__setattr__(key, value)
  
  return GenericReply(
    message = 'Successfully edited assignment',
    status = HTTPStatusCode.OK
  ).to_dict(), HTTPStatusCode.OK





@app.route(f'{basePath}/delete', methods = ['POST'])
@auth_limit
@require_login
def assignment_delete_api(user: UserModel):
  req = AssignmentDeleteRequest(request)

  # Validate
  assignment = AssignmentModel.query.filter(AssignmentModel.id == req.assignment_id).first()
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


  return GenericReply(
    message = 'Assignment deleted successfully',
    status = HTTPStatusCode.OK
  ).to_dict(), HTTPStatusCode.OK
