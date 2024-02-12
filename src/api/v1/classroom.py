"""
Classroom Endpoint
"""

from src import limiter
from src.database import ClassroomModel, UserModel, TextbookModel
from src.utils.http import HTTPStatusCode, escape_id
from src.service.auth_provider import require_login
from src.utils.ext import utc_time
from src.utils.api import (
  ClassroomListReply,
  _ClassroomListData,
  ClassroomGetRequest,
  ClassroomGetReply,
  _ClassroomGetData,
  ClassroomCreateRequest,
  ClassroomCreateReply,
  _ClassroomCreateData,
  ClassroomEditRequest,
  ClassroomEditReply,
  ClassroomDeleteRequest,
  ClassroomDeleteReply,
  ClassroomJoinRequest,
  ClassroomJoinReply,
  ClassroomLeaveRequest,
  ClassroomLeaveReply,
  GenericReply,
)

from flask_limiter import util
from flask import request, current_app as app


# Routes
basePath: str = '/api/v1/classroom'
auth_limit = limiter.shared_limit(
  '100 per hour', scope=lambda _: request.host, key_func=util.get_remote_address
)


@app.route(f'{basePath}/list', methods=['GET'])
@auth_limit
@require_login
def classroom_list_api(user: UserModel):
  return ClassroomListReply(
    message='Successfully fetched classrooms',
    status=HTTPStatusCode.OK,
    data=[
      _ClassroomListData(
        id=classroom.id,
        owner_id=classroom.owner_id,
        owner_username=classroom.owner.username,
        title=classroom.title,
        description=classroom.description,
        cover_image=classroom.cover_image.id if classroom.cover_image else None,
        created_at=classroom.created_at.timestamp(),
      )
      for classroom in (user.classrooms + user.owned_classrooms)
    ],
  ).to_dict(), HTTPStatusCode.OK


@app.route(f'{basePath}/get', methods=['GET'])
@auth_limit
@require_login
def classroom_get_api(user: UserModel):
  req = ClassroomGetRequest(request)

  classroom = ClassroomModel.query.filter(ClassroomModel.id == req.classroom_id).first()
  if not isinstance(classroom, ClassroomModel):
    return GenericReply(
      message='Classroom could not be located', status=HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST

  if (user.privilege != 'Admin') and classroom.is_member(user):
    return GenericReply(
      message='Unauthorized', status=HTTPStatusCode.UNAUTHORIZED
    ).to_dict(), HTTPStatusCode.UNAUTHORIZED

  return ClassroomGetReply(
    message='Successfully fetched classroom information',
    status=HTTPStatusCode.OK,
    data=_ClassroomGetData(
      id=classroom.id,
      owner_id=classroom.owner_id,
      educator_ids=[i.id for i in classroom.educators],
      student_ids=[i.id for i in classroom.students],
      textbook_ids=[i.id for i in classroom.textbooks],
      title=classroom.title,
      description=classroom.description,
      assignments=[i.id for i in classroom.assignments],
      cover_image=classroom.cover_image.uri if classroom.cover_image else None,
      invite_id=classroom.invite_id,
      invite_enabled=classroom.invite_enabled,
      created_at=classroom.created_at.timestamp(),
      updated_at=classroom.updated_at.timestamp(),
    ),
  ).to_dict(), HTTPStatusCode.OK


@app.route(f'{basePath}/create', methods=['POST'])
@auth_limit
@require_login
def classroom_create_api(user: UserModel):
  req = ClassroomCreateRequest(request)

  if (
      (not req.title)
      or (req.title == 'None')
      or (not req.description)
      or (req.description == 'None')
      ):
    return GenericReply(
      message='Invalid title or description', status=HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST

  if req.owner_id and (user.id != req.owner_id) and (user.privilege != 'Admin'):
    return GenericReply(
      message='Unauthorized',
      status=HTTPStatusCode.UNAUTHORIZED,
    ).to_dict(), HTTPStatusCode.UNAUTHORIZED

  owner = (
    user
    if (not req.owner_id) or (user.id == req.owner_id)
    else UserModel.query.filter(UserModel.id == req.owner_id).first()
  )
  if not isinstance(owner, UserModel):
    return GenericReply(
      message='Invalid user', status=HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST

  # Enforce limitations
  if owner.privilege not in ['Admin', 'Educator']:
    return GenericReply(
      message='Unauthorized', status=HTTPStatusCode.UNAUTHORIZED
    ).to_dict(), HTTPStatusCode.UNAUTHORIZED

  if (owner.membership == 'Free') and (len(owner.owned_classrooms) >= 3):
    return GenericReply(
      message='You have reached your classroom limit', status=HTTPStatusCode.FORBIDDEN
    ).to_dict(), HTTPStatusCode.FORBIDDEN

  newClassroom: ClassroomModel = ClassroomModel(
    owner=owner,
    title=req.title,
    description=req.description,
    invite_enabled=req.invite_enabled in ['y', True],
  )
  newClassroom.save()

  return ClassroomCreateReply(
    message='Classroom created successfully',
    status=HTTPStatusCode.OK,
    data=_ClassroomCreateData(classroom_id=newClassroom.id),
  ).to_dict(), HTTPStatusCode.OK


@app.route(f'{basePath}/edit', methods=['POST'])
@auth_limit
@require_login
def classroom_edit_api(user: UserModel):
  req = ClassroomEditRequest(request)
  toChange = {
    key: '' if not i or i == 'None' else i
    for key in [
      'classroom_id',
      'title',
      'description',
      'textbook_ids',
      'cover_image',
      'invite_enabled',
    ]
    if (
      (i := req.get(key, None)) and (i not in [None, 'None']) or (not req.ignore_none)
    )
  }

  if not any(toChange.values()):
    return GenericReply(
      message='No change supplied', status=HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST

  classroom = ClassroomModel.query.filter(ClassroomModel.id == req.classroom_id).first()
  if not isinstance(classroom, ClassroomModel):
    return GenericReply(
      message='Classroom could not be located', status=HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST

  if (user.privilege != 'Admin') and not classroom.is_owner(user):
    return GenericReply(
      message='Unauthorized', status=HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST

  for key, value in toChange.items():
    if key == 'textbook_ids':
      newTextbooks: list[TextbookModel] = []
      for newID in value:
        txtbook = TextbookModel.query.filter(
          TextbookModel.id == escape_id(newID)
        ).first()
        if not isinstance(txtbook, TextbookModel):
          return GenericReply(
            message=f'Invalid textbook id: {newID}', status=HTTPStatusCode.BAD_REQUEST
          ).to_dict(), HTTPStatusCode.BAD_REQUEST
        newTextbooks.append(txtbook)

      classroom.textbooks = newTextbooks

    elif key == 'invite_enabled':
      classroom.invite_enabled = value in [True, 'y']

    else:
      classroom.__setattr__(key, value)

  classroom.updated_at = utc_time.get()
  classroom.save()

  return ClassroomEditReply(
    message='Successfully edited classroom', status=HTTPStatusCode.OK
  ).to_dict(), HTTPStatusCode.OK


@app.route(f'{basePath}/delete', methods=['POST'])
@auth_limit
@require_login
def classroom_delete_api(user: UserModel):
  req = ClassroomDeleteRequest(request)

  classroom = ClassroomModel.query.filter(ClassroomModel.id == req.classroom_id).first()
  if not isinstance(classroom, ClassroomModel):
    return GenericReply(
      message='Classroom could not be located', status=HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST

  if (user.privilege != 'Admin') and not classroom.is_owner(user):
    return GenericReply(
      message='Unauthorized', status=HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST

  classroom.delete()
  return ClassroomDeleteReply(
    message='Classroom deleted successfully', status=HTTPStatusCode.OK
  ).to_dict(), HTTPStatusCode.OK


@app.route(f'{basePath}/join', methods=['POST'])
@auth_limit
@require_login
def classroom_join_api(user: UserModel):
  req = ClassroomJoinRequest(request)

  classroom = ClassroomModel.query.filter(
    ClassroomModel.invite_id == req.invite_id
  ).first()
  if not isinstance(classroom, ClassroomModel):
    return GenericReply(
      message='Classroom could not be located', status=HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST

  if not classroom.invite_enabled:
    return GenericReply(
      message='Classroom invite is disabled', status=HTTPStatusCode.FORBIDDEN
    ).to_dict(), HTTPStatusCode.FORBIDDEN

  # Impose limitations
  if classroom.is_member(user):
    return GenericReply(
      message='You are already a member of this classroom',
      status=HTTPStatusCode.FORBIDDEN
    ).to_dict(), HTTPStatusCode.FORBIDDEN

  elif (classroom.owner.membership == 'Free') and (len(classroom.members) > 5):
    return GenericReply(
      message='The classroom owner has reached the classroom limit',
      status=HTTPStatusCode.FORBIDDEN,
    ).to_dict(), HTTPStatusCode.FORBIDDEN

  else:
    classroom.add_students(user)
    classroom.save()

  return ClassroomJoinReply(
    message='Successfully joined classroom',
    status=HTTPStatusCode.OK,
    data=_ClassroomCreateData(classroom_id=classroom.id),
  ).to_dict(), HTTPStatusCode.OK


@app.route(f'{basePath}/leave', methods=['POST'])
@auth_limit
@require_login
def classroom_leave_api(user: UserModel):
  req = ClassroomLeaveRequest(request)

  classroom = ClassroomModel.query.filter(ClassroomModel.id == req.classroom_id).first()
  if not isinstance(classroom, ClassroomModel):
    return GenericReply(
      message='Classroom could not be located', status=HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST

  if classroom.is_student(user):
    classroom.remove_students(user)
    classroom.save()

  elif classroom.is_educator(user):
    classroom.remove_educators(user)
    classroom.save()

  elif classroom.is_owner(user):
    return GenericReply(
      message='The classroom owner cannot leave', status=HTTPStatusCode.FORBIDDEN
    ).to_dict(), HTTPStatusCode.FORBIDDEN

  else:
    return GenericReply(
      message='You are not a member of this classroom', status=HTTPStatusCode.FORBIDDEN
    ).to_dict(), HTTPStatusCode.FORBIDDEN

  return ClassroomLeaveReply(
    message='Successfully left classroom', status=HTTPStatusCode.OK
  ).to_dict(), HTTPStatusCode.OK
