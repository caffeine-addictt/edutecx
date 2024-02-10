"""
Assignment Endpoint
"""

from src import limiter
from src.database import AssignmentModel, ClassroomModel, UserModel
from src.service.auth_provider import require_login
from src.utils.http import HTTPStatusCode
from src.utils.ext import utc_time
from src.utils.api import (
  AssignmentListRequest,
  AssignmentListReply,
  AssignmentGetRequest,
  AssignmentGetReply,
  _AssignmentGetData,
  AssignmentCreateRequest,
  AssignmentCreateReply,
  _AssignmentCreateData,
  AssignmentEditRequest,
  AssignmentEditReply,
  AssignmentDeleteRequest,
  AssignmentDeleteReply,
  GenericReply,
)

from datetime import datetime
from flask_limiter import util
from flask import request, current_app as app

from sqlalchemy import and_, or_


# Routes
basePath: str = '/api/v1/assignment'
auth_limit = limiter.shared_limit(
  '100 per hour', scope=lambda _: request.host, key_func=util.get_remote_address
)


@app.route(f'{basePath}/list', methods=['GET'])
@auth_limit
@require_login
def assignment_list_api(user: UserModel):
  req = AssignmentListRequest(request)

  dateRange: tuple[datetime, datetime] = (
    datetime.fromtimestamp(req.createdLower)
    if float('inf') != req.createdLower
    else utc_time.skip('1day'),
    datetime.fromtimestamp(req.createdUpper)
    if float('inf') != req.createdUpper
    else utc_time.skip('1day'),
  )

  if dateRange[0] > dateRange[1]:
    return GenericReply(
      message='createdLower is larger than createdUpper',
      status=HTTPStatusCode.BAD_REQUEST,
    ).to_dict(), HTTPStatusCode.BAD_REQUEST

  if req.query == 'None':
    req.query = ''

  # Build query
  query = [
    and_(
      dateRange[0] <= AssignmentModel.created_at,
      AssignmentModel.created_at <= dateRange[1],
    ),
    or_(
      AssignmentModel.id.contains(req.query),
      AssignmentModel.title.contains(req.query),
      AssignmentModel.requirement.contains(req.query),
    ),
  ]

  filtered = AssignmentModel.query.filter(
    and_(
      (AssignmentModel.classroom.members.contains(user)),
      and_(*query) if req.criteria == 'and' else or_(*query),
    )
  ).paginate(page=req.page, error_out=False)

  return AssignmentListReply(
    message='Successfully fetched assignment list',
    status=HTTPStatusCode.OK,
    data=[
      _AssignmentGetData(
        id=assignment.id,
        classroom_id=assignment.classroom.id,
        title=assignment.title,
        description=assignment.description,
        due_date=assignment.due_date.timestamp(),
        textbooks=[i.id for i in assignment.textbooks],
        requirement=assignment.requirement,
        submissions=[i.id for i in assignment.submissions],
        created_at=assignment.created_at.timestamp(),
        updated_at=assignment.updated_at.timestamp(),
      )
      for assignment in filtered
    ],
  ).to_dict(), HTTPStatusCode.OK


@app.route(f'{basePath}/get', methods=['GET'])
@auth_limit
@require_login
def assignment_get_api(user: UserModel):
  req = AssignmentGetRequest(request)

  assignment = AssignmentModel.query.filter(
    AssignmentModel.id == req.assignment_id
  ).first()
  if not isinstance(assignment, AssignmentModel):
    return GenericReply(
      message='Unable to locate assignment', status=HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST

  if (user.privilege != 'Admin') and (not assignment.classroom.is_member(user)):
    return GenericReply(
      message='Unauthorized', status=HTTPStatusCode.UNAUTHORIZED
    ).to_dict(), HTTPStatusCode.UNAUTHORIZED

  return AssignmentGetReply(
    message='Successfully fetched assignment information',
    status=HTTPStatusCode.OK,
    data=_AssignmentGetData(
      id=assignment.id,
      classroom_id=assignment.classroom.id,
      title=assignment.title,
      description=assignment.description,
      due_date=assignment.due_date.timestamp(),
      textbooks=[i.id for i in assignment.textbooks],
      requirement=assignment.requirement,
      submissions=[i.id for i in assignment.submissions],
      created_at=assignment.created_at.timestamp(),
      updated_at=assignment.updated_at.timestamp(),
    ),
  ).to_dict(), HTTPStatusCode.OK


@app.route(f'{basePath}/create', methods=['POST'])
@auth_limit
@require_login
def assignment_create_api(user: UserModel):
  req = AssignmentCreateRequest(request)

  # Validate due_date
  if (req.due_date != 'infinity' and not isinstance(req.due_date, (int, float))) or (
    utc_time.get().timestamp() >= int(req.due_date)
  ):
    return GenericReply(
      message='Invalid due date', status=HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST

  due_date = (
    datetime.fromtimestamp(req.due_date)
    if isinstance(req.due_date, (int, float))
    else None
  )

  # Validate classroom
  classroom = ClassroomModel.query.filter(
    and_(
      ClassroomModel.id == req.classroom_id,
      or_(ClassroomModel.owner_id == user.id, ClassroomModel.educators.contains(user)),
    )
  ).first()

  if not classroom or not isinstance(classroom, ClassroomModel):
    return GenericReply(
      message='Invalid classroom', status=HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST

  if not req.title or (req.title == 'None'):
    return GenericReply(
      message='Invalid title', status=HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST

  if not req.description or (req.description == 'None'):
    return GenericReply(
      message='Invalid description', status=HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST

  if not req.requirement or (req.requirement == 'None'):
    return GenericReply(
      message='Invalid requirement', status=HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST

  if due_date and due_date < utc_time.get():
    return GenericReply(
      message='Due date is in the past', status=HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST

  newAssignment = AssignmentModel(
    classroom=classroom,
    title=req.title,
    description=req.description,
    due_date=due_date,
    requirement=req.requirement,
  )
  newAssignment.save()

  return AssignmentCreateReply(
    message='Assignment created successfully',
    status=HTTPStatusCode.OK,
    data=_AssignmentCreateData(assignment_id=newAssignment.id),
  ).to_dict(), HTTPStatusCode.OK


@app.route(f'{basePath}/edit', methods=['POST'])
@auth_limit
@require_login
def assignment_edit_api(user: UserModel):
  req = AssignmentEditRequest(request)
  toChange = {
    key: '' if not i or i == 'None' else i
    for key in ['title', 'description', 'due_date', 'requirement']
    if (
      (i := req.get(key, None)) and (i not in [None, 'None']) or (not req.ignore_none)
    )
  }

  if not any(toChange.values()):
    return GenericReply(
      message='No change supplied', status=HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST

  assignment = AssignmentModel.query.filter(
    AssignmentModel.id == req.assignment_id
  ).first()
  if not isinstance(assignment, AssignmentModel):
    return GenericReply(
      message='Unable to locate assignment', status=HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST

  if (user.privilege != 'Admin') and not assignment.classroom.is_privileged(user):
    return GenericReply(
      message='Unauthorized', status=HTTPStatusCode.UNAUTHORIZED
    ).to_dict(), HTTPStatusCode.UNAUTHORIZED

  for key, value in toChange.items():
    assignment.__setattr__(key, value)

  assignment.updated_at = utc_time.get()
  assignment.save()

  return AssignmentEditReply(
    message='Successfully edited assignment', status=HTTPStatusCode.OK
  ).to_dict(), HTTPStatusCode.OK


@app.route(f'{basePath}/delete', methods=['POST'])
@auth_limit
@require_login
def assignment_delete_api(user: UserModel):
  req = AssignmentDeleteRequest(request)

  # Validate
  assignment = AssignmentModel.query.filter(
    AssignmentModel.id == req.assignment_id
  ).first()
  if not isinstance(assignment, AssignmentModel):
    return GenericReply(
      message='Could not located assignment', status=HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST

  if not assignment.classroom.is_privileged(user):
    return GenericReply(
      message='Unauthorized', status=HTTPStatusCode.UNAUTHORIZED
    ).to_dict(), HTTPStatusCode.UNAUTHORIZED

  assignment.delete()

  return AssignmentDeleteReply(
    message='Assignment deleted successfully', status=HTTPStatusCode.OK
  ).to_dict(), HTTPStatusCode.OK
