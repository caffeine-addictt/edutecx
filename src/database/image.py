"""
Image Model
"""

from src import db
from src.service.cdn_provider import uploadImage, deleteFile

import uuid
from thread import Thread
from datetime import datetime
from typing import TYPE_CHECKING, Optional
from werkzeug.datastructures import FileStorage

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import (
  String,
  DateTime,
  ForeignKey
)


# Import at runtime to prevent circular imports
if TYPE_CHECKING:
  from .user import UserModel
  from .textbook import TextbookModel
  from .classroom import ClassroomModel

# TODO: Filepath (iURI) -> URI
class ImageModel(db.Model):
  """Image Model"""

  __tablename__ = 'image_table'

  id          : Mapped[str] = mapped_column(String, unique = True, primary_key = True, nullable = False, default = lambda: uuid.uuid4().hex)
  user_id     : Mapped[Optional[str]] = mapped_column(ForeignKey('user_table.id'), nullable = True)
  textbook_id : Mapped[Optional[str]] = mapped_column(ForeignKey('textbook_table.id'), nullable = True)
  classroom_id: Mapped[Optional[str]] = mapped_column(ForeignKey('classroom_table.id'), nullable = True)

  uri      : Mapped[str] = mapped_column(String, nullable = True)
  iuri     : Mapped[str] = mapped_column(String, nullable = True)
  status   : Mapped[str] = mapped_column(String, nullable = False, default = 'Uploading')
  user     : Mapped[Optional['UserModel']]      = relationship('UserModel', back_populates = 'profile_image')
  textbook : Mapped[Optional['TextbookModel']]  = relationship('TextbookModel', back_populates = 'cover_image')
  classroom: Mapped[Optional['ClassroomModel']] = relationship('ClassroomModel', back_populates = 'cover_image')

  created_at: Mapped[datetime] = mapped_column(DateTime, nullable = False, default = datetime.utcnow)


  def __init__(
    self,
    file: FileStorage,
    user: Optional['UserModel'] = None,
    textbook: Optional['TextbookModel'] = None,
    classroom: Optional['ClassroomModel'] = None
  ) -> None:
    """
    Image Model

    Parameters
    ----------
    `file: FileStorage`, required

    `user: UserModel`, optional

    `textbook: TextbookModel`, optional

    `classroom: ClassroomModel`, optional
    """
    # Make use of the fact that Boolean is a subclass of INT
    if (bool(user) + bool(textbook)+ bool(classroom)) != 1:
      raise Exception('Only 1 parent reference is allowed')

    self.user_id = user and user.id
    self.textbook_id = textbook and textbook.id
    self.classroom_id = classroom and classroom.id
    self._upload_handler(file)

  def __repr__(self):
    """To be used with cache indexing"""
    return '%s(%s)' % (self.__class__.__name__, self.id)
  

  def _upload_handler(self, file: FileStorage) -> None:
    """Threaded background upload process"""
    def updateURI(filePath: str):
      self.iuri = filePath
      self.uri = f'/public/image/{filePath.split("/")[-1]}'
      self.status = 'Uploaded'
      self.save()

    filename = f'{self.id}-{self.user_id or ""}{self.textbook_id or ""}{self.classroom_id or ""}'

    uploadJob = Thread(uploadImage, kwargs = {
      'file': file,
      'filename': filename
    })
    uploadJob.add_hook(updateURI)
    uploadJob.start()


  # DB
  def save(self) -> None:
    """Commits model"""
    db.session.add(self)
    db.session.commit()

  def delete(self, commit: bool = True) -> None:
    """Deletes model and its references"""
    deleteJob = Thread(target = deleteFile, args = [self.iuri])
    deleteJob.start()

    db.session.delete(self)
    if commit: db.session.commit()
