"""
Textbook Model
"""

from src import db
from src.utils.ext.threading import Thread
from src.service.cdn_provider import uploadTextbook

import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING, List
from werkzeug.datastructures import FileStorage

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import (
  Float,
  String,
  DateTime,
  ForeignKey
)

# Import TokenModel at runtime to prevent circular imports
if TYPE_CHECKING:
  from .user import UserModel
  from .image import ImageModel
  from .editabletextbook import EditableTextbookModel


# TODO: Textbook PDF upload
class TextbookModel(db.Model):
  """
  Textbook Model
  """

  __tablename__ = 'textbook_table'

  # Identifier
  id       : Mapped[str] = mapped_column(String, unique = True, primary_key = True, nullable = False, default = lambda: uuid.uuid4().hex)
  author_id: Mapped[str] = mapped_column(ForeignKey('user_table.id'), nullable = False)

  # Attributes
  price      : Mapped[float] = mapped_column(Float, nullable = False, default = 0.0)
  discount   : Mapped[float] = mapped_column(Float, nullable = False, default = 0.0)
  author     : Mapped['UserModel'] = relationship('UserModel', back_populates = 'owned_textbooks')

  uri        : Mapped[str]                    = mapped_column(String, nullable = True)
  iuri       : Mapped[str]                    = mapped_column(String, nullable = True)
  status     : Mapped[str]                    = mapped_column(String, nullable = False, default = 'Uploading')
  cover_image: Mapped[Optional['ImageModel']] = relationship('ImageModel', back_populates = 'textbook')
  derrived   : Mapped[List['EditableTextbookModel']] = relationship('EditableTextbookModel', back_populates = 'origin')

  # Logs
  created_at: Mapped[datetime] = mapped_column(DateTime, nullable = False, default = datetime.utcnow)
  updated_at: Mapped[datetime] = mapped_column(DateTime, nullable = False, default = datetime.utcnow)

  def __init__(
    self,
    author: 'UserModel',
    file: FileStorage,
    price: float = 0.0,
    discount: float = 0.0,
  ) -> None:
    assert isinstance(price, float)
    assert isinstance(discount, float) and (0 <= discount <= 1)

    self.author_id = author.id
    self.price = price
    self.discount = discount
    self._upload_handler(file)
      
  def __repr__(self) -> str:
    """To be used with cache indexing"""
    return '%s(%s)' % (self.__class__.__name__, self.id)
  

  def _upload_handler(self, file: FileStorage) -> None:
    """Threaded background upload process"""
    def updateURI(filePath: str):
      self.iuri = filePath
      self.status = 'Uploaded'
      self.save()

    filename = f'{self.id}-{self.author_id or ""}'

    uploadJob = Thread(uploadTextbook)
    uploadJob.add_hook(updateURI)
    uploadJob.start(file = file, filename = filename)
  
  
  # DB
  def save(self) -> None:
    """Commits the model"""
    db.session.add(self)
    db.session.commit()

  def delete(self, commit: bool = True) -> None:
    # """Deletes the model and its references"""
    # if self.cover_image: self.cover_image.delete(commit = False)

    # db.session.delete(self)
    # if commit: db.session.commit()
    
    # Deleting textbooks are not allowed
    pass
