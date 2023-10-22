"""
User Model
"""

from . import db

import uuid
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import (
  UUID,
  String,
  Boolean,
  DateTime
)



class UserModel(db.Model):
  """
  User Model
  """

  __tablename__ = 'users'

  # Identifiers
  id        : Mapped[str]      = mapped_column(String, primary_key = True, default = lambda: uuid.uuid4().hex)
  email     : Mapped[str]      = mapped_column(String, unique = True, nullable = False)
  username  : Mapped[str]      = mapped_column(String, unique = True, nullable = False)

  # Auth
  admin     : Mapped[bool]     = mapped_column(Boolean, default = False)
  password  : Mapped[str]      = mapped_column(String, nullable = False)
  token     : Mapped[str]      = mapped_column(String, nullable = True)

  # Logs
  created_at: Mapped[datetime] = mapped_column(DateTime, nullable = False, default = datetime.utcnow)
  updated_at: Mapped[datetime] = mapped_column(DateTime, nullable = False, default = datetime.utcnow)
