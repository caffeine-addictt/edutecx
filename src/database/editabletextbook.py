"""
EditableTextbook Model
"""

from src import db
from src.service.cdn_provider import cloneTextbook, updateEditableTextbook, deleteFile

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
  ForeignKey
)

if TYPE_CHECKING:
  from .user import UserModel
  from .textbook import TextbookModel


EditableTextbookUploadStatus = Literal['Uploading', 'Uploaded']
EnumEditableTextbookUploadStatus = Enum('Uploading', 'Uploaded', name = 'EditableTextbookUploadStatus')


class EditableTextbookModel(db.Model):
  """Editable Textbook Model"""

  __tablename__ = 'editable_textbook_table'

  id         : Mapped[str] = mapped_column(String, primary_key = True, unique = True, default = lambda: uuid.uuid4().hex)
  user_id    : Mapped[str] = mapped_column(ForeignKey('user_table.id'))
  textbook_id: Mapped[str] = mapped_column(ForeignKey('textbook_table.id'))

  uri      : Mapped[str]                          = mapped_column(String, nullable = True)
  iuri     : Mapped[str]                          = mapped_column(String, nullable = True)
  status   : Mapped[EditableTextbookUploadStatus] = mapped_column(EnumEditableTextbookUploadStatus, nullable = False, default = 'Uploading')
  user     : Mapped['UserModel']                  = relationship('UserModel', back_populates = 'textbooks')
  origin   : Mapped['TextbookModel']              = relationship('TextbookModel', back_populates = 'derrived')

  updated_at: Mapped[datetime] = mapped_column(DateTime, nullable = False, default = datetime.utcnow)
  created_at: Mapped[datetime] = mapped_column(DateTime, nullable = False, default = datetime.utcnow)


  def __init__(self, user: 'UserModel', textbook: 'TextbookModel'):
    """
    Editable Textbook Model

    Parameters
    ----------
    `user: UserModel`, required

    `textbook: TextbookModel`, required
    """
    self.user_id = user.id
    self.textbook_id = textbook.id

    self._handle_upload(textbook)


  def _handle_upload(self, textbook: 'TextbookModel') -> None:
    filename = f'{self.id}-{self.user_id or ""}{self.textbook_id}'
    filePath = cloneTextbook(textbook.iuri, filename)

    self.iuri = filePath
    self.uri = f'/public/editabletextbook/{filePath.split("/")[-1]}'
    self.status = 'Uploaded'
    self.updated_at = datetime.utcnow()
    self.save()


  def update(self, file: FileStorage) -> None:
    """Update the file content"""
    self.status = 'Uploading'
    updateEditableTextbook(self.iuri, file)

    self.status = 'Uploaded'
    self.updated_at = datetime.utcnow()
    self.save()

  
  def save(self) -> None:
    """Commits the model"""
    db.session.add(self)
    db.session.commit()

  def delete(self) -> None:
    """Deletes the model and its references"""
    Thread(deleteFile, args = [self.iuri]).start()
    
    db.session.delete(self)
    db.session.commit()
