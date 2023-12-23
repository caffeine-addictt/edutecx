"""
Submission Endpoint
"""

from src import limiter
from src.database import SubmissionModel, UserModel, AssignmentModel, SubmissionSnippetModel, EditableTextbookModel
from src.service.auth_provider import require_login
from src.utils.http import HTTPStatusCode
from src.utils.api import (
  SubmissionGetRequest, SubmissionGetReply, _SubmissionGetData,
  SubmissionCreateRequest, SubmissionCreateReply, _SubmissionCreateData,
  GenericReply
)

from typing import Optional
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
  req = SubmissionCreateRequest(request)

  upload = req.files.get('upload')
  if not upload:
    return GenericReply(
      message = 'No upload supplied',
      status = HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST
  

  editabletextbook = EditableTextbookModel.query.filter(EditableTextbookModel.id == req.editabletextbook_id).first()
  if not isinstance(editabletextbook, EditableTextbookModel):
    return GenericReply(
      message = 'Could not locate editable textbook',
      status = HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST
  

  assignment = AssignmentModel.query.filter(AssignmentModel.id == req.assignment_id).first()
  if not isinstance(assignment, AssignmentModel):
    return GenericReply(
      message = 'Could not locate assignment',
      status = HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST
  
  if user.id not in [
    assignment.classroom.owner_id,
    *assignment.classroom.student_ids.split('|'),
    *assignment.classroom.educator_ids.split('|')
  ]:
    return GenericReply(
      message = 'Unauthorized',
      status = HTTPStatusCode.UNAUTHORIZED
    ).to_dict(), HTTPStatusCode.UNAUTHORIZED
  

  assignmentReq = tuple( int(i) for i in assignment.requirement.split(':')[1:] )
  if len(assignmentReq) == 1: assignmentReq = assignmentReq[0]
  elif len(assignmentReq) != 2:
    return GenericReply(
      message = 'Something went wrong!',
      status = HTTPStatusCode.INTERNAL_SERVER_ERROR
    ).to_dict(), HTTPStatusCode.INTERNAL_SERVER_ERROR
  

  submission: Optional[SubmissionModel] = None
  snippet: Optional[SubmissionSnippetModel] = None
  try:
    submission = SubmissionModel(
      student = user,
      assignment = assignment
    )
    submission.save()

    snippet = SubmissionSnippetModel(
      student = user,
      submission = submission,
      editabletextbook = editabletextbook,
      pages = assignmentReq
    )
    snippet.save()
  
  except Exception:
    if isinstance(submission, SubmissionModel):
      submission.delete()
    
    if isinstance(snippet, SubmissionSnippetModel):
      snippet.delete()

    return GenericReply(
      message = 'Something went wrong!',
      status = HTTPStatusCode.INTERNAL_SERVER_ERROR
    ).to_dict(), HTTPStatusCode.INTERNAL_SERVER_ERROR
  

  return SubmissionCreateReply(
    message = 'Successfully created submission',
    status = HTTPStatusCode.OK,
    data = _SubmissionCreateData(
      submission_id = submission.id,
      snippet_id = snippet.id
    )
  ).to_dict(), HTTPStatusCode.OK




@app.route(f'{basePath}/delete', methods = ['POST'])
@auth_limit
@require_login
def submission_delete_api(user: UserModel):
  ...
