"""
Classroom Endpoint
"""

from src import db, limiter
from src.database import ClassroomModel, UserModel
from src.utils.http import HTTPStatusCode
from src.service.auth_provider import require_login
from src.utils.api import (
  ClassroomCreateRequest, ClassroomCreateReply, _ClassroomCreateData,
  ClassroomDeleteRequest,
  GenericReply
)

from sqlalchemy import and_, or_
from flask_limiter import util
from flask import (
  request,
  current_app as app
)


#Routes
basePath: str = '/api/v1/classroom'
auth_limit = limiter.shared_limit('100 per hour', scope = lambda _: request.host, key_func = util.get_remote_address)




@app.route(f'{basePath}/create', methods = ['POST'])
@auth_limit
@require_login
def classroom_create_api(user: UserModel):
  req = ClassroomCreateRequest(request)

  # Validate
  if (user.id != req.owner_id) and (user.privilege != 'Admin'):
    return GenericReply(
      message = 'Unauthorized',
      status = HTTPStatusCode.UNAUTHORIZED,
    ).to_dict(), HTTPStatusCode.UNAUTHORIZED

  owner = user if user.id == req.owner_id else UserModel.query.filter(UserModel.id == req.owner_id).first()
  if not owner or not isinstance(owner, UserModel):
    return GenericReply(
      message = 'Invalid user',
      status = HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST

  newClassroom: ClassroomModel = ClassroomModel(
    owner = owner,
    title = req.title,
    description = req.description
  )
  newClassroom.save()

  return ClassroomCreateReply(
    message = 'Classroom created successfully',
    status = HTTPStatusCode.OK,
    data = _ClassroomCreateData(
      classroom_id = newClassroom.id
    )
  ).to_dict(), HTTPStatusCode.OK




@app.route(f'{basePath}/delete', methods = ['POST'])
@auth_limit
@require_login
def classroom_delete_api(user: UserModel):
  req = ClassroomDeleteRequest(request)

  classroom = ClassroomModel.query.filter(ClassroomModel.id == req.classroom_id).first()

  if not classroom or not isinstance(classroom, ClassroomModel):
    return GenericReply(
      message = 'Invalid classroom',
      status = HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST
  
  if (user.privilege != 'Admin') and (classroom.owner_id != user.id):
    return GenericReply(
      message = 'Unauthorized',
      status = HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST

  classroom.delete()
  return GenericReply(
    message = 'Classroom deleted successfully',
    status = HTTPStatusCode.OK
  ).to_dict(), HTTPStatusCode.OK
