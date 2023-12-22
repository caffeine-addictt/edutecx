"""
Submission Endpoint
"""

from src import limiter
from src.database import SubmissionModel, UserModel
from src.service.auth_provider import require_login
from src.utils.http import HTTPStatusCode
from src.utils.api import (
  SubmissionGetRequest, SubmissionGetReply, _SubmissionGetData,
  GenericReply
)

from flask_limiter import util
from flask import (
  request,
  current_app as app
)


# Routes
basePath: str = '/api/v1/submission'
auth_limit = limiter.shared_limit('100 per hour', scope = lambda _: request.host, key_func = util.get_remote_address)




@app.route(f'{basePath}/get', methods = ['GET'])
@auth_limit
@require_login
def submission_get_api(user: UserModel):
  req = SubmissionGetRequest(request)

  submission = SubmissionModel.query.filter(SubmissionModel.id == req.submission_id).first()
  if not isinstance(submission, SubmissionModel):
    return GenericReply(
      message = 'Could not locate submission',
      status = HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST
  
  if (user.privilege != 'Admin') and (user.id not in [
    submission.student_id,
    submission.assignment.classroom.owner_id,
    *submission.assignment.classroom.educator_ids.split('|')
  ]):
    return GenericReply(
      message = 'Unauthorized',
      status = HTTPStatusCode.UNAUTHORIZED
    ).to_dict(), HTTPStatusCode.UNAUTHORIZED
  

  return SubmissionGetReply(
    message = 'Successfully fetched submission',
    status = HTTPStatusCode.OK,
    data = _SubmissionGetData(
      submission_id = submission.id,
      student_id = submission.student_id,
      assignment_id = submission.assignment_id,
      comments = [ i.id for i in submission.comments ],
      snippet = submission.snippet.uri,
      created_at = submission.created_at.timestamp(),
      updated_at = submission.updated_at.timestamp()
    )
  )




@app.route(f'{basePath}/create', methods = ['POST'])
@auth_limit
@require_login
def submission_create_api(user: UserModel):
  ...




@app.route(f'{basePath}/delete', methods = ['POST'])
@auth_limit
@require_login
def submission_delete_api(user: UserModel):
  ...
