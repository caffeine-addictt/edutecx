"""
User Model
"""

from src import db

import uuid
from datetime import datetime
from typing import Literal, Optional, TYPE_CHECKING

from custom_lib.flask_login import UserMixin
from sqlalchemy.orm import Mapped, mapped_column, relationship, Relationship
from sqlalchemy import (
  String,
  DateTime,
  ForeignKey,
)


# Import TokenModel at runtime to prevent circular imports
if TYPE_CHECKING:
  from .token import TokenModel
  from .classroom import ClassroomModel


class UserModel(db.Model, UserMixin):
  """
  User Model
  """

  __tablename__ = 'user_table'

  # Identifiers
  id        : Mapped[str]                  = mapped_column(String, primary_key = True, default = lambda: uuid.uuid4().hex)
  email     : Mapped[str]                  = mapped_column(String, unique = True, nullable = False)
  username  : Mapped[str]                  = mapped_column(String, unique = True, nullable = False)

  # Auth
  privilege : Mapped[str]                  = mapped_column(String, default = False)
  password  : Mapped[str]                  = mapped_column(String, nullable = False)

  # Token
  token     : Mapped[Optional['TokenModel']] = relationship(back_populates = 'user')

  # Class (Classroom feature)
  classroom : Mapped[Optional['ClassroomModel']] = relationship(back_populates = 'members')

  # Logs
  created_at: Mapped[datetime]             = mapped_column(DateTime, nullable = False, default = datetime.utcnow)
  updated_at: Mapped[datetime]             = mapped_column(DateTime, nullable = False, default = datetime.utcnow)

  def __init__(self,
    email: str,
    username: str,
    password: str,
    privilege: Literal['User', 'Admin']
  ) -> None:
    self.email     = email
    self.username  = username
    self.privilege = privilege
    self.password  = password
    