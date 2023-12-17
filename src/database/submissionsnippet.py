"""

"""

from src import db
from src.service.cdn_provider import deleteFile, clonePage

import uuid
from thread import Thread
from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import (
  String,
  DateTime,
  ForeignKey,
)


# Import UserModel at runtime to prevent circular imports
if TYPE_CHECKING:
  from .user import UserModel
  from .submission import SubmissionModel
  from .editabletextbook import EditableTextbookModel


class SubmissionSnippetModel(db.Model):
  """"""

  __tablename__ = 'submission_snippet_table'

  id: Mapped[str] = mapped_column(String, primary_key = True, unique = True, nullable = False, default = lambda: uuid.uuid4())
  student_id: Mapped[str] = mapped_column(ForeignKey('user_table.id'), nullable = False)
  submission_id: Mapped[str] = mapped_column(ForeignKey('submission_table.id'), nullable = False)

  uri      : Mapped[str] = mapped_column(String, nullable = True)
  iuri     : Mapped[str] = mapped_column(String, nullable = True)
  status   : Mapped[str] = mapped_column(String, nullable = False, default = 'Uploading')
  student   : Mapped['UserModel']          = relationship('UserModel', back_populates = 'submissions')
  submission: Mapped['SubmissionModel'] = relationship('SubmissionModel', back_populates = 'snippet')

  created_at: Mapped[datetime] = mapped_column(DateTime, nullable = False, default = datetime.utcnow)


  def __init__(
    self,
    student: 'UserModel',
    submission: 'SubmissionModel',
    editabletextbook: 'EditableTextbookModel',
    pages: int | tuple[int, int]
  ) -> None:
    self.student_id = student.id
    self.submission_id = submission.id
    self._handle_upload(editabletextbook, pages)

  def __repr__(self) -> str:
    """To be used with cache indexing"""
    return '%s(%s)' % (self.__class__.__name__, self.id)
  

  def _updateURI(self, filePath: str) -> None:
    self.iuri = filePath
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

