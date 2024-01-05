"""
Submission Snippet Model
"""

from src import db
from src.service.cdn_provider import deleteFile, clonePage

import uuid
from thread import Thread
from datetime import datetime
from typing import TYPE_CHECKING, Literal

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
  from .editabletextbook import EditableTextbookModel


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
    editabletextbook: 'EditableTextbookModel',
    pages: int | tuple[int, int]
  ) -> None:
    """
    Submission Snippet Model

    Parameters
    ----------
    `student: UserModel`, required

    `submission: SubmissionModel`, required

    `editabletextbook: EditableTextbookModel`, required
      The pages to clone from

    `pages: int | tuple[int, int]`, required
      The page indexes (Page 1 => index 0)
      Tuple is the same as pageList[index1 : index2]
    """
    self.student_id = student.id
    self.submission_id = submission.id
    self._handle_upload(editabletextbook, pages)

  def __repr__(self) -> str:
    """To be used with cache indexing"""
    return '%s(%s)' % (self.__class__.__name__, self.id)
  

  def _updateURI(self, filePath: str) -> None:
    self.iuri = filePath
    self.uri = f'/public/textbook/{filePath.split("/")[-1]}'
    self.status = 'Uploaded'
    self.save()

  def _handle_upload(self, editabletextbook: 'EditableTextbookModel', pages: int | tuple[int, int]) -> None:
    filename = f'{self.id}-{self.student_id or ""}{self.submission_id}'

    uploadJob = Thread(clonePage, kwargs = {
      'fileLocation': editabletextbook.iuri,
      'newfilename': filename,
      'pages': pages
    })
    uploadJob.add_hook(self._updateURI)
    uploadJob.start()

  
  def save(self) -> None:
    """Commits the model"""
    db.session.add(self)
    db.session.commit()

  def delete(self, commit: bool = True) -> None:
    """Deletes the model and its references"""
    Thread(target = deleteFile, args = [self.iuri]).start()
    
    db.session.delete(self)
    if commit: db.session.commit()

