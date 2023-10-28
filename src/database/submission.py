"""
Submission model
"""

from src import db

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import (
  String,
  DateTime,
  ForeignKey,
)


# Import UserModel at runtime to prevent circular imports
if TYPE_CHECKING:
  from .user import UserModel
  from .assignment import AssignmentModel
  from .comment import CommentModel


# TODO: Add the edited page of documentModel (after figuring out how to edit it :'>)
class SubmissionModel(db.Model):
  """
  Submission Model
  """

  __tablename__ = 'submission_table'

  # Identifiers
  id           : Mapped[str] = mapped_column(String, primary_key = True, unique = True, nullable = False, default = lambda: uuid.uuid4().hex)
  student_id   : Mapped[str] = mapped_column(ForeignKey('user_table.id'), nullable = False)
  assignment_id: Mapped[str] = mapped_column(ForeignKey('assignment_table.id'), nullable = False)

  # Attributes
  student   : Mapped['UserModel']       = relationship('UserModel', back_populates = 'submissions')
  assignment: Mapped['AssignmentModel'] = relationship('AssignmentModel', back_populates = 'submissions')
  comments  : Mapped['CommentModel']    = relationship('CommentModel', back_populates = 'submission')

  # Logs
  created_at: Mapped[datetime] = mapped_column(DateTime, nullable = False, default = datetime.utcnow)
  updated_at: Mapped[datetime] = mapped_column(DateTime, nullable = False, default = datetime.utcnow)

  
  def __init__(self, student: 'UserModel', assignment: 'AssignmentModel') -> None:
    self.student_id = student.id
    self.assignment_id = assignment.id
