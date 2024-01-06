"""
Comment model
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
  from .submission import SubmissionModel


class CommentModel(db.Model):
  """Comment Model"""

  __tablename__ = 'comment_table'

  # Identifiers
  id           : Mapped[str] = mapped_column(String, primary_key = True, unique = True, nullable = False, default = lambda: uuid.uuid4().hex)
  submission_id: Mapped[str] = mapped_column(ForeignKey('submission_table.id'), nullable = False)
  author_id    : Mapped[str] = mapped_column(ForeignKey('user_table.id'), nullable = False)

  # Attributes
  text      : Mapped[str]               = mapped_column(String, nullable = False)
  author    : Mapped['UserModel']       = relationship('UserModel', back_populates = 'comments')
  submission: Mapped['SubmissionModel'] = relationship('SubmissionModel', back_populates = 'comments')

  # Logs
  created_at: Mapped[datetime] = mapped_column(DateTime, nullable = False, default = datetime.utcnow)
  updated_at: Mapped[datetime] = mapped_column(DateTime, nullable = False, default = datetime.utcnow)

  def __init__(self, author: 'UserModel', submission: 'SubmissionModel', text: str) -> None:
    """
    Comment Model

    Parameters
    ----------
    `author: UserModel`, required
    
    `submission: SubmissionModel`, required

    `text: String`, required
    """
    self.author_id = author.id
    self.submission_id = submission.id
    self.text = text

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
    db.session.delete(self)
    db.session.commit()
