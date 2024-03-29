"""
Submission model
"""

from src import db

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List

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
  from .submissionsnippet import SubmissionSnippetModel


class SubmissionModel(db.Model):
  """Submission Model"""

  __tablename__ = 'submission_table'

  # Identifiers
  id: Mapped[str] = mapped_column(
    String,
    primary_key=True,
    unique=True,
    nullable=False,
    default=lambda: uuid.uuid4().hex,
  )
  student_id: Mapped[str] = mapped_column(ForeignKey('user_table.id'), nullable=False)
  assignment_id: Mapped[str] = mapped_column(
    ForeignKey('assignment_table.id'), nullable=False
  )

  # Attributes
  student: Mapped['UserModel'] = relationship('UserModel', back_populates='submissions')
  comments: Mapped[List['CommentModel']] = relationship(
    'CommentModel', back_populates='submission'
  )
  assignment: Mapped['AssignmentModel'] = relationship(
    'AssignmentModel', back_populates='submissions'
  )
  snippet: Mapped['SubmissionSnippetModel'] = relationship(
    'SubmissionSnippetModel', back_populates='submission'
  )

  # Logs
  created_at: Mapped[datetime] = mapped_column(
    DateTime, nullable=False, default=datetime.utcnow
  )
  updated_at: Mapped[datetime] = mapped_column(
    DateTime, nullable=False, default=datetime.utcnow
  )

  def __init__(self, student: 'UserModel', assignment: 'AssignmentModel') -> None:
    """
    Submission Model

    Parameters
    ----------
    `student: UserModel`, required

    `assignment: AssignmentModel`, required
    """
    self.student_id = student.id
    self.assignment_id = assignment.id

  def __repr__(self) -> str:
    """To be used with cache indexing"""
    return '%s(%s)' % (self.__class__.__name__, self.id)

  def save(self) -> None:
    """Commits the model"""
    db.session.add(self)
    db.session.commit()

  def delete(self) -> None:
    """Deletes the model and its references"""
    for i in self.comments:
      i.delete()
    self.snippet.delete()

    db.session.delete(self)
    db.session.commit()
