"""
Classroom Endpoint
"""

from src import limiter
from src.database import ClassroomModel, UserModel
from src.utils.http import HTTPStatusCode
from src.service.auth_provider import require_login
from src.utils.ext import utc_time
from src.utils.api import (
  ClassroomGetRequest, ClassroomGetReply, _ClassroomGetData,
  ClassroomCreateRequest, ClassroomCreateReply, _ClassroomCreateData,
  ClassroomEditRequest, ClassroomEditReply,
  ClassroomDeleteRequest, ClassroomDeleteReply,
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




@app.route(f'{basePath}/get', methods = ['GET'])
@auth_limit
@require_login
def classroom_get_api(user: UserModel):
  req = ClassroomGetRequest(request)

  classroom = ClassroomModel.query.filter(ClassroomModel.id == req.classroom_id).first()
  if not isinstance(classroom, ClassroomModel):
    return GenericReply(
      message = 'Classroom could not be located',
      status = HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST
  

  if (user.privilege != 'Admin') and (user.id not in [
    classroom.owner_id,
    *classroom.educator_ids.split('|'),
    *classroom.student_ids.split('|')
  ]):
    return GenericReply(
      message = 'Unauthorized',
      status = HTTPStatusCode.UNAUTHORIZED
    ).to_dict(), HTTPStatusCode.UNAUTHORIZED
  

  return ClassroomGetReply(
    message = 'Successfully fetched classroom information',
    status = HTTPStatusCode.OK,
    data = _ClassroomGetData(
      id = classroom.id,
      owner_id = classroom.owner_id,
      educator_ids = classroom.educator_ids.split('|'),
      student_ids = classroom.student_ids.split('|'),
      textbook_ids = classroom.textbook_ids.split('|'),
      title = classroom.title,
      description = classroom.description,
      assignments = [ i.id for i in classroom.assignments ],
      cover_image = classroom.cover_image.uri if classroom.cover_image else None,
      invite_id = classroom.invite_id,
      invite_enabled = classroom.invite_enabled,
      created_at = classroom.created_at.timestamp(),
      updated_at = classroom.updated_at.timestamp(),
    )
  ).to_dict(), HTTPStatusCode.OK




@app.route(f'{basePath}/create', methods = ['POST'])
@auth_limit
@require_login
def classroom_create_api(user: UserModel):
  req = ClassroomCreateRequest(request)


  if (user.id != req.owner_id) and (user.privilege != 'Admin'):
    return GenericReply(
      message = 'Unauthorized',
      status = HTTPStatusCode.UNAUTHORIZED,
    ).to_dict(), HTTPStatusCode.UNAUTHORIZED


  owner = user if user.id == req.owner_id else UserModel.query.filter(UserModel.id == req.owner_id).first()
  if not isinstance(owner, UserModel):
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




@app.route(f'{basePath}/edit', methods = ['POST'])
@auth_limit
@require_login
def classroom_edit_api(user: UserModel):
  req = ClassroomEditRequest(request)
  toChange = {key: req.get(key) for key in [
    'classroom_id',
    'title',
    'description',
    'cover_image',
    'invite_enabled'
  ] if ((req.get(key, None) is not None) or (not req.ignore_none))}

  if not any(toChange.values()):
    return GenericReply(
      message = 'No change supplied',
      status = HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST


  classroom = ClassroomModel.query.filter(ClassroomModel.id == req.classroom_id).first()
  if not isinstance(classroom, ClassroomModel):
    return GenericReply(
      message = 'Classroom could not be located',
      status = HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST
  
  if (user.privilege != 'Admin') and (classroom.owner_id != user.id):
    return GenericReply(
      message = 'Unauthorized',
      status = HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST
  

  for key, value in toChange.items():
    classroom.__setattr__(key, value)
    
  classroom.updated_at = utc_time.get()
  classroom.save()
  
  return ClassroomEditReply(
    message = 'Successfully edited classroom',
    status = HTTPStatusCode.OK
  ).to_dict(), HTTPStatusCode.OK




@app.route(f'{basePath}/delete', methods = ['POST'])
@auth_limit
@require_login
def classroom_delete_api(user: UserModel):
  req = ClassroomDeleteRequest(request)


  classroom = ClassroomModel.query.filter(ClassroomModel.id == req.classroom_id).first()
  if not isinstance(classroom, ClassroomModel):
    return GenericReply(
      message = 'Classroom could not be located',
      status = HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST
  
  if (user.privilege != 'Admin') and (classroom.owner_id != user.id):
    return GenericReply(
      message = 'Unauthorized',
      status = HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST


  classroom.delete()
  return ClassroomDeleteReply(
    message = 'Classroom deleted successfully',
    status = HTTPStatusCode.OK
  ).to_dict(), HTTPStatusCode.OK
