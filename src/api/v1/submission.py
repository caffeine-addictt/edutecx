"""
Submission Endpoint
"""

from src import limiter
from src.database import (
  SubmissionModel,
  UserModel,
  AssignmentModel,
  SubmissionSnippetModel,
  TextbookModel,
)
from src.service.auth_provider import require_login
from src.service.cdn_provider import BadFileEXT
from src.utils.http import HTTPStatusCode
from src.utils.ext import utc_time
from src.utils.api import (
  SubmissionListRequest,
  SubmissionListReply,
  SubmissionGetRequest,
  SubmissionGetReply,
  _SubmissionGetData,
  SubmissionCreateRequest,
  SubmissionCreateReply,
  _SubmissionCreateData,
  SubmissionDeleteRequest,
  SubmissionDeleteReply,
  GenericReply,
)

from typing import Optional
from datetime import datetime
from flask_limiter import util
from sqlalchemy import and_, or_
from flask import request, current_app as app


# Routes
basePath: str = '/api/v1/submission'
auth_limit = limiter.shared_limit(
  '100 per hour', scope=lambda _: request.host, key_func=util.get_remote_address
)

DateRange = tuple[datetime, datetime] | datetime | None


@app.route(f'{basePath}/list', methods=['GET'])
@auth_limit
@require_login
def submission_list_api(user: UserModel):
  req = SubmissionListRequest(request)

  # Handle query
  req.createdLower = float(req.createdLower or 0)
  req.createdUpper = float(req.createdUpper or 0)

  dateRange: DateRange = (
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

  if not req.query or req.query == 'None':
    req.query = ''

  return SubmissionListReply(
    message='Successfully fetched submissions',
    status=HTTPStatusCode.OK,
    data=[
      _SubmissionGetData(
        submission_id=submission.id,
        student_id=submission.student_id,
        assignment_id=submission.assignment_id,
        comments=[i.id for i in submission.comments],
        snippet=submission.snippet.uri,
        created_at=submission.created_at.timestamp(),
        updated_at=submission.updated_at.timestamp(),
      )
      for submission in user.submissions
      if (
        (
          (req.criteria == 'and') and (
            (dateRange[0] <= submission.created_at)
            and (submission.created_at <= dateRange[1])
            and (req.query in submission.assignment.classroom.title)
          )
        )
        or (
          (req.criteria == 'or') and (
            (dateRange[0] <= submission.created_at and submission.created_at <= dateRange[1])
            or (req.query in submission.assignment.classroom.title)
          )
        )
      )
    ],
  ).to_dict()


@app.route(f'{basePath}/get', methods=['GET'])
@auth_limit
@require_login
def submission_get_api(user: UserModel):
  req = SubmissionGetRequest(request)

  submission = SubmissionModel.query.filter(
    SubmissionModel.id == req.submission_id
  ).first()
  if not isinstance(submission, SubmissionModel):
    return GenericReply(
      message='Could not locate submission', status=HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST

  if (
    (user.privilege != 'Admin')
    and (user.id != submission.student_id)
    and (not submission.assignment.classroom.is_privileged(user))
  ):
    return GenericReply(
      message='Unauthorized', status=HTTPStatusCode.UNAUTHORIZED
    ).to_dict(), HTTPStatusCode.UNAUTHORIZED

  return SubmissionGetReply(
    message='Successfully fetched submission',
    status=HTTPStatusCode.OK,
    data=_SubmissionGetData(
      submission_id=submission.id,
      student_id=submission.student_id,
      assignment_id=submission.assignment_id,
      comments=[i.id for i in submission.comments],
      snippet=submission.snippet.uri,
      created_at=submission.created_at.timestamp(),
      updated_at=submission.updated_at.timestamp(),
    ),
  ).to_dict(), HTTPStatusCode.OK


@app.route(f'{basePath}/create', methods=['POST'])
@auth_limit
@require_login
def submission_create_api(user: UserModel):
  req = SubmissionCreateRequest(request)

  upload = request.files.get('upload')
  if not upload:
    return GenericReply(
      message='Missing upload', status=HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST

  assignment = AssignmentModel.query.filter(
    AssignmentModel.id == req.assignment_id
  ).first()
  if not isinstance(assignment, AssignmentModel):
    return GenericReply(
      message='Could not locate assignment', status=HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST

  if assignment.classroom.is_member(user):
    return GenericReply(
      message='Unauthorized', status=HTTPStatusCode.UNAUTHORIZED
    ).to_dict(), HTTPStatusCode.UNAUTHORIZED

  submission: Optional[SubmissionModel] = None
  snippet: Optional[SubmissionSnippetModel] = None
  try:
    submission = SubmissionModel(student=user, assignment=assignment)
    submission.save()

    snippet = SubmissionSnippetModel(student=user, submission=submission, upload=upload)
    snippet.save()

  except Exception as e:
    if isinstance(submission, SubmissionModel):
      submission.delete()

    if isinstance(snippet, SubmissionSnippetModel):
      snippet.delete()

    if isinstance(e, BadFileEXT):
      return GenericReply(
        message=str(e), status=HTTPStatusCode.BAD_REQUEST
      ).to_dict(), HTTPStatusCode.BAD_REQUEST

    app.logger.error(f'Failed to create submission: {e}')
    return GenericReply(
      message='Something went wrong!', status=HTTPStatusCode.INTERNAL_SERVER_ERROR
    ).to_dict(), HTTPStatusCode.INTERNAL_SERVER_ERROR

  return SubmissionCreateReply(
    message='Successfully created submission',
    status=HTTPStatusCode.OK,
    data=_SubmissionCreateData(submission_id=submission.id, snippet_id=snippet.id),
  ).to_dict(), HTTPStatusCode.OK


@app.route(f'{basePath}/delete', methods=['POST'])
@auth_limit
@require_login
def submission_delete_api(user: UserModel):
  req = SubmissionDeleteRequest(request)

  submission = SubmissionModel.query.filter(
    SubmissionModel.id == req.submission_id
  ).first()
  if not isinstance(submission, SubmissionModel):
    return GenericReply(
      message='Unable to locate submission', status=HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST

  if (user.privilege != 'Admin') and (
    not submission.assignment.classroom.is_privileged(user)
  ):
    return GenericReply(
      message='Unauthorized', status=HTTPStatusCode.UNAUTHORIZED
    ).to_dict(), HTTPStatusCode.UNAUTHORIZED

  submission.delete()
  return SubmissionDeleteReply(
    message='Submission deleted successfully', status=HTTPStatusCode.OK
  ).to_dict(), HTTPStatusCode.OK
