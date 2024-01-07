"""
Comment Endpoint
"""

from src import limiter
from src.database import CommentModel, UserModel, SubmissionModel
from src.service.auth_provider import require_login
from src.utils.http import HTTPStatusCode
from src.utils.api import (
  CommentGetRequest, CommentGetReply, _CommentGetData,
  CommentCreateRequest, CommentCreateReply, _CommentCreateData,
  GenericReply
)

from flask_limiter import util
from flask import (
  request,
  current_app as app
)


# Routes
basePath: str = '/api/v1/comment'
auth_limit = limiter.shared_limit('100 per hour', scope = lambda _: request.host, key_func = util.get_remote_address)




@app.route(f'{basePath}/get', methods = ['GET'])
@auth_limit
@require_login
def comment_get_api(user: UserModel):
  req = CommentGetRequest(request)

  comment = CommentModel.query.filter(CommentModel.id == req.comment_id).first()
  if not isinstance(comment, CommentModel):
    return GenericReply(
      message = 'Could not locate comment',
      status = HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST
  

  if (user.privilege != 'Admin') and \
      (user.id != comment.author_id) and \
      (not comment.submission.assignment.classroom.is_privileged(user)):
    return GenericReply(
      message = 'Unauthorized',
      status = HTTPStatusCode.UNAUTHORIZED
    ).to_dict(), HTTPStatusCode.UNAUTHORIZED
  
  
  return CommentGetReply(
    message = 'Successfully fetched comment',
    status = HTTPStatusCode.OK,
    data = _CommentGetData(
      author_id = comment.author_id,
      submission_id = comment.submission_id,
      assignment_id = comment.submission.assignment_id,
      classroom_id = comment.submission.assignment.classroom_id,
      text = comment.text,
      created_at = comment.created_at.timestamp(),
      updated_at = comment.updated_at.timestamp()
    )
  ).to_dict(), HTTPStatusCode.OK




@app.route(f'{basePath}/create', methods = ['POST'])
@auth_limit
@require_login
def comment_create_api(user: UserModel):
  req = CommentCreateRequest(request)

  submission = SubmissionModel.query.filter(SubmissionModel.id == req.submission_id).first()
  if not isinstance(submission, SubmissionModel):
    return GenericReply(
      message = 'Could not locate submission',
      status = HTTPStatusCode.BAD_REQUEST
    ).to_dict(), HTTPStatusCode.BAD_REQUEST
  
  if (user.privilege != 'Admin') and \
      (user.id != submission.student_id) and \
      (not submission.assignment.classroom.is_privileged(user)):
    return GenericReply(
      message = 'Unauthorized',
      status = HTTPStatusCode.UNAUTHORIZED
    ).to_dict(), HTTPStatusCode.UNAUTHORIZED
  

  newComment = CommentModel(
    author = user,
    submission = submission,
    text = req.text
  )
  newComment.save()


  return CommentCreateReply(
    message = 'Successfully created comment',
    status = HTTPStatusCode.OK,
    data = _CommentCreateData(
      comment_id = newComment.id
    )
  ).to_dict(), HTTPStatusCode.OK
