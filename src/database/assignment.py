"""
Assignment model
"""

from src import db

import re
import uuid
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import (
  String,
  DateTime,
  ForeignKey,
)


# Import UserModel at runtime to prevent circular imports
if TYPE_CHECKING:
  from .classroom import ClassroomModel
  from.submission import SubmissionModel


# TODO: Add required pages to be submitted
class AssignmentModel(db.Model):
  """
  Assignment Model
  """

  __tablename__ = 'assignment_table'

  # Identifiers
  id          : Mapped[str]              = mapped_column(String, unique = True, primary_key = True, nullable = False, default = lambda: uuid.uuid4().hex)
  classroom_id: Mapped[str]              = mapped_column(ForeignKey('classroom_table.id'), nullable = False)
  classroom   : Mapped['ClassroomModel'] = relationship('ClassroomModel', back_populates = 'assignments')

  # Attributes
  title      : Mapped[str]                     = mapped_column(String, nullable = False)
  description: Mapped[str]                     = mapped_column(String, nullable = False)
  due_date   : Mapped[datetime]                = mapped_column(DateTime, nullable = True)
  documents  : Mapped[str]                     = mapped_column(String, nullable = True)
  requirement: Mapped[str]                     = mapped_column(String, nullable = True)
  submissions: Mapped[List['SubmissionModel']] = relationship('SubmissionModel', back_populates = 'assignment')

  # Logs
  created_at: Mapped[datetime] = mapped_column(DateTime, nullable = False, default = datetime.utcnow)
  updated_at: Mapped[datetime] = mapped_column(DateTime, nullable = False, default = datetime.utcnow)


  def __init__(
    self,
    classroom: 'ClassroomModel',
    title: str,
    description: str,
    due_date: Optional[datetime] = None
  ) -> None:
    self.classroom_id = classroom.id
    self.title = title
    self.description = description

    if due_date is not None:
      self.due_date = due_date

  def __repr__(self):
    """To be used with cache indexing"""
    return '%s(%s)' % (self.__class__.__name__, self.id)

  
  def set_requirement(self, requirement: Optional[str] = '') -> None:
    """
    Set the assignment requirement


    Parameters
    ----------
    `requirement: str`, optional
      Format = str(docID:pageNum) | str(docID:pageNum:pageNum) | str(docID:pageNum:pageNum,...)
    """
    assert re.match(r'^([a-zA-Z0-9]+:\d+(:[\d*+])?(,)?)*$', requirement or ''), 'Invalid requirement format [%s]' % requirement


