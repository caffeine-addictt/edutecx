"""
Textbook Model
"""

from src import db
from src.service.cdn_provider import uploadTextbook, deleteFile

import uuid
from thread import Thread
from datetime import datetime
from typing import Optional, TYPE_CHECKING, List, Literal
from werkzeug.datastructures import FileStorage

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Enum, Float, String, DateTime, ForeignKey

# Import at runtime to prevent circular imports
if TYPE_CHECKING:
  from .user import UserModel
  from .sale import SaleModel
  from .image import ImageModel
  from .discount import DiscountModel
  from .classroom import ClassroomModel
  from .assignment import AssignmentModel
  from .association import (
    user_textbook_association,
    classroom_textbook_association,
    assignment_textbook_association,
    sale_textbook_association,
  )


TextbookStatus = Literal['Available', 'Unavailable', 'DMCA']
EnumTextbookStatus = Enum('Available', 'Unavailable', 'DMCA', name='TextbookStatus')

TextbookUploadStatus = Literal['Uploading', 'Uploaded']
EnumTextbookUploadStatus = Enum('Uploading', 'Uploaded', name='TextbookUploadStatus')


class TextbookModel(db.Model):
  """Textbook Model"""

  __tablename__ = 'textbook_table'

  # Identifier
  id: Mapped[str] = mapped_column(
    String,
    unique=True,
    primary_key=True,
    nullable=False,
    default=lambda: uuid.uuid4().hex,
  )
  author_id: Mapped[str] = mapped_column(ForeignKey('user_table.id'), nullable=False)

  # Attributes
  title: Mapped[str] = mapped_column(String, nullable=False)
  description: Mapped[str] = mapped_column(String, nullable=True, default='')
  categories: Mapped[str] = mapped_column(
    String, nullable=False, default=''
  )  # 'category1|category2...'
  price: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

  author: Mapped['UserModel'] = relationship(
    'UserModel', back_populates='owned_textbooks'
  )
  discounts: Mapped[List['DiscountModel']] = relationship(
    'DiscountModel', back_populates='textbook'
  )
  bought_by: Mapped[List['UserModel']] = relationship(
    'UserModel', secondary='user_textbook_association', back_populates='textbooks'
  )
  classrooms: Mapped[List['ClassroomModel']] = relationship(
    'ClassroomModel',
    secondary='classroom_textbook_association',
    back_populates='textbooks',
  )
  assignments: Mapped[List['AssignmentModel']] = relationship(
    'AssignmentModel',
    secondary='assignment_textbook_association',
    back_populates='textbooks',
  )
  sales: Mapped[List['sale_textbook_association']] = relationship(
    'sale_textbook_association', back_populates='textbook'
  )

  uri: Mapped[str] = mapped_column(String, nullable=True)
  iuri: Mapped[str] = mapped_column(String, nullable=True)
  status: Mapped[TextbookStatus] = mapped_column(
    EnumTextbookStatus, nullable=False, default='Available'
  )
  upload_status: Mapped[TextbookUploadStatus] = mapped_column(
    EnumTextbookUploadStatus, nullable=False, default='Uploading'
  )
  cover_image: Mapped[Optional['ImageModel']] = relationship(
    'ImageModel', back_populates='textbook'
  )

  # Logs
  created_at: Mapped[datetime] = mapped_column(
    DateTime, nullable=False, default=datetime.utcnow
  )
  updated_at: Mapped[datetime] = mapped_column(
    DateTime, nullable=False, default=datetime.utcnow
  )

  def __init__(
    self,
    author: 'UserModel',
    file: FileStorage,
    title: str,
    description: str = '',
    categories: List[str] = [],
    price: float = 0.0,
    discount: float = 0.0,
  ) -> None:
    """
    Textbook Model

    Parameters
    ----------
    `author: UserModel`, required

    `file: FileStorage`, required
      From request.form.files[0]

    `title: str`, required

    `description: str, optional

    `categories: str[]`, optional

    `price: float`, optional

    `discount: float`, optional
      The discount amount between 0 and 1 inclusive.
      CurrentPrice = Price * (1 - `discount`)
    """
    assert isinstance(price, float)
    assert isinstance(discount, float) and (0 <= discount <= 1)

    self.id = uuid.uuid4().hex
    self.author_id = author.id
    self.title = title
    self.description = description
    self.categories = '|'.join(categories)

    self.price = price
    self.discount = discount
    self._upload_handler(file)

  def __repr__(self) -> str:
    """To be used with cache indexing"""
    return '%s(%s)' % (self.__class__.__name__, self.id)

  def _upload_handler(self, file: FileStorage) -> None:
    """Threaded background upload process"""
    self.upload_status = 'Uploading'
    filename = f'{self.id}-{self.author_id or ""}'

    filePath = uploadTextbook(file, filename)
    self.iuri = filePath
    self.uri = f'/public/textbook/{filePath.split("/")[-1]}'
    self.upload_status = 'Uploaded'
    self.save()

  # DB
  def save(self) -> None:
    """Commits the model"""
    db.session.add(self)
    db.session.commit()

  def delete(self) -> None:
    """Deletes the model and its references"""
    Thread(deleteFile, args=[self.iuri]).start()

    if self.cover_image:
      self.cover_image.delete()
    for i in self.discounts:
      i.delete()

    db.session.delete(self)
    db.session.commit()
