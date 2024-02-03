"""
Submission Snippet Endpoint
"""

from src import limiter
from src.database import SubmissionSnippetModel, UserModel
from src.service.auth_provider import require_login
from src.utils.http import HTTPStatusCode
from src.utils.api import (
  SubmissionSnippetGetReply,
  SubmissionSnippetGetRequest,
  _SubmissionSnippetGetData,
  GenericReply,
)

from flask_limiter import util
from flask import request, current_app as app


# Routes
basePath: str = '/api/v1/submissionsnippet'
auth_limit = limiter.shared_limit(
  '100 per hour', scope=lambda _: request.host, key_func=util.get_remote_address
)


@app.route(f'{basePath}/get', methods=['GET'])
@auth_limit
@require_login
def submissionsnippet_get_api(user: UserModel):
  req = SubmissionSnippetGetRequest(request)

  submissionSnippet = SubmissionSnippetModel.query.filter(
    SubmissionSnippetModel.id == req.submissionSnippet_id
  ).first()
  if not isinstance(submissionSnippet, SubmissionSnippetModel):
    return GenericReply(
      message='Unable to locate submission snippet', status=HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST

  if (user.privilege != 'Admin') and (
    not submissionSnippet.submission.assignment.classroom.is_member(user)
  ):
    return GenericReply(
      message='Unauthorized', status=HTTPStatusCode.UNAUTHORIZED
    ).to_dict(), HTTPStatusCode.UNAUTHORIZED

  return SubmissionSnippetGetReply(
    message='Successfully fetched submission snippet information',
    status=HTTPStatusCode.OK,
    data=_SubmissionSnippetGetData(
      id=submissionSnippet.id,
      student_id=submissionSnippet.student_id,
      submission_id=submissionSnippet.submission_id,
      uri=submissionSnippet.uri,
      status=submissionSnippet.status,
      created_at=submissionSnippet.created_at.timestamp(),
    ),
  ).to_dict(), HTTPStatusCode.OK
