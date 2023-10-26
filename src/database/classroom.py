"""
Classroom model
"""

from src import db

import uuid
from datetime import datetime
from typing import List, Literal, Optional, TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship, Relationship
from sqlalchemy import (
  String,
  DateTime,
  ForeignKey,
)


# Import UserModel at runtime to prevent circular imports
if TYPE_CHECKING:
  from .user import UserModel


class ClassroomModel(db.Model):
  """
  Classroom model
  """
  
  __tablename__ = 'classroom_table'

  # Identifiers
  id: Mapped[str] = mapped_column(String, primary_key = True, default = lambda: uuid.uuid4().hex)

  # People
  educators: Mapped[List['UserModel']] = relationship()