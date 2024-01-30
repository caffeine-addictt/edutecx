"""
Submission Snippet Model
"""

from src import db
from src.service.cdn_provider import deleteFile, uploadSubmission

import uuid
from thread import Thread
from datetime import datetime
from typing import TYPE_CHECKING, Literal
from werkzeug.datastructures import FileStorage

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import (
  Enum,
  String,
  DateTime,
  ForeignKey,
)


# Import UserModel at runtime to prevent circular imports
if TYPE_CHECKING:
  from .user import UserModel
  from .submission import SubmissionModel


SnippetUploadStatus = Literal['Uploading', 'Uploaded']
EnumSnippetUploadStatus = Enum('Uploading', 'Uploaded', name = 'SnippetUploadStatus')


class SubmissionSnippetModel(db.Model):
  """Submission Snippet Model"""

  __tablename__ = 'submission_snippet_table'

  id           : Mapped[str] = mapped_column(String, primary_key = True, unique = True, nullable = False, default = lambda: uuid.uuid4())
  student_id   : Mapped[str] = mapped_column(ForeignKey('user_table.id'), nullable = False)
  submission_id: Mapped[str] = mapped_column(ForeignKey('submission_table.id'), nullable = False)

  uri       : Mapped[str]                 = mapped_column(String, nullable = True)
  iuri      : Mapped[str]                 = mapped_column(String, nullable = True)
  status    : Mapped[SnippetUploadStatus] = mapped_column(EnumSnippetUploadStatus, nullable = False, default = 'Uploading')
  student   : Mapped['UserModel']         = relationship('UserModel', back_populates = 'snippets')
  submission: Mapped['SubmissionModel']   = relationship('SubmissionModel', back_populates = 'snippet')

  created_at: Mapped[datetime] = mapped_column(DateTime, nullable = False, default = datetime.utcnow)


  def __init__(
    self,
    student: 'UserModel',
    submission: 'SubmissionModel',
    upload: FileStorage
  ) -> None:
    """
    Submission Snippet Model

    Parameters
    ----------
    `student: UserModel`, required

    `submission: SubmissionModel`, required

    `upload: FileStorage`, required
    """
    self.student_id = student.id
    self.submission_id = submission.id
    self._handle_upload(upload)

  def __repr__(self) -> str:
    """To be used with cache indexing"""
    return '%s(%s)' % (self.__class__.__name__, self.id)
  

  def _handle_upload(self, upload: FileStorage) -> None:
    filename = f'{self.id}-{self.student_id or ""}{self.submission_id}'
    filePath = uploadSubmission(upload, filename)

    self.iuri = filePath
    self.uri = f'/public/textbook/{filePath.split("/")[-1]}'
    self.status = 'Uploaded'
    self.save()

  
  def save(self) -> None:
    """Commits the model"""
    db.session.add(self)
    db.session.commit()

  def delete(self) -> None:
    """Deletes the model and its references"""
    Thread(target = deleteFile, args = [self.iuri]).start()
    
    db.session.delete(self)
    db.session.commit()

