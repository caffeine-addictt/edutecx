"""
Document Model
"""

from src import db

import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from werkzeug.datastructures import FileStorage

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import (
  Float,
  String,
  DateTime,
  ForeignKey,
  LargeBinary
)

# Import TokenModel at runtime to prevent circular imports
if TYPE_CHECKING:
  from .user import UserModel


class DocumentModel(db.Model):
  """
  Document Model
  """

  __tablename__ = 'document_table'

  # Identifier
  id       : Mapped[str] = mapped_column(String, unique = True, primary_key = True, nullable = False, default = lambda: uuid.uuid4().hex)
  author_id: Mapped[str] = mapped_column(ForeignKey('user_table.id'), nullable = False)

  # Attributes
  price   : Mapped[float] = mapped_column(Float, nullable = False, default = 0.0)
  author  : Mapped['UserModel'] = relationship('UserModel', back_populates = 'owned_documents')
  filename: Mapped[str] = mapped_column(String, nullable = False, unique = True)
  data    : Mapped[LargeBinary] = mapped_column(LargeBinary, nullable = False)

  # Logs
  created_at: Mapped[datetime] = mapped_column(DateTime, nullable = False, default = datetime.utcnow)
  updated_at: Mapped[datetime] = mapped_column(DateTime, nullable = False, default = datetime.utcnow)

  def __init__(self, author: 'UserModel', file: FileStorage, price: Optional[float]) -> None:
    self.author_id = author.id

    # ? Or might it be better to save file to local $path and save the abs path to it?
    self.filename = self.id + (file.filename or '.pdf')[-4:]
    self.data = file.read()

    if price is not None:
      self.price = price