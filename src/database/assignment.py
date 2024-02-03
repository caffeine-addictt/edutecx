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
  from .submission import SubmissionModel
  from .association import assignment_textbook_association


class AssignmentModel(db.Model):
  """Assignment Model"""

  __tablename__ = 'assignment_table'

  # Identifiers
  id: Mapped[str] = mapped_column(
    String,
    unique=True,
    primary_key=True,
    nullable=False,
    default=lambda: uuid.uuid4().hex,
  )
  classroom_id: Mapped[str] = mapped_column(
    ForeignKey('classroom_table.id'), nullable=False
  )
  classroom: Mapped['ClassroomModel'] = relationship(
    'ClassroomModel', back_populates='assignments'
  )

  # Attributes
  title: Mapped[str] = mapped_column(String, nullable=False)
  description: Mapped[str] = mapped_column(String, nullable=False)
  due_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)
  requirement: Mapped[str] = mapped_column(String, nullable=True)
  textbooks: Mapped[List['TextbookModel']] = relationship(
    'TextbookModel',
    secondary='assignment_textbook_association',
    back_populates='assignments',
  )
  submissions: Mapped[List['SubmissionModel']] = relationship(
    'SubmissionModel', back_populates='assignment'
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
    classroom: 'ClassroomModel',
    title: str,
    description: str,
    due_date: Optional[datetime] = None,
    requirement: str = '',
    textbooks: List['TextbookModel'] = [],
  ) -> None:
    """
    Assignment model

    Parameters
    ----------
    `classroom: ClassroomModel`, required
      The class to allocate the assignment to

    `title: str`, required
      The title of the assignment

    `description: str`, required
      The description of the assignment

    `due_date: Optional[datetime]`, optional (defaults to None)
      The due date of the assignment

    `requirement: str`, optional (defaults to '')
      Format = str(docID:pageNum) | str(docID:pageNum:pageNum)

    `textbooks: TextbookModel[]`, optional (defaults to [])
      The textbooks to allocate to the assignment


    Returns
    -------
    `AssignmentModel`


    Raises
    ------
    `AssertionError`
      The format for requirement is invalid
    """
    assert re.match(r'^([a-za-Z0-9]{32}):\d+(:\d+)?$', requirement or ''), (
      'Invalid requirement format [%s]' % requirement
    )

    self.classroom_id = classroom.id
    self.title = title
    self.description = description
    self.requirement = requirement

    if due_date is not None:
      self.due_date = due_date

  def __repr__(self):
    """To be used with cache indexing"""
    return '%s(%s)' % (self.__class__.__name__, self.id)

  # DB
  def save(self) -> None:
    """Commits the model"""
    db.session.add(self)
    db.session.commit()

  def delete(self) -> None:
    """Deletes the model and its references"""
    for i in self.submissions:
      i.delete()

    db.session.delete(self)
    db.session.commit()
