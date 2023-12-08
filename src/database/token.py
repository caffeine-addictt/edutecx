"""
Token Model

Managing verification password reset tokens
"""

from src import db
from src.utils.ext import utc_time

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Literal, Optional

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import (
  String,
  DateTime,
  ForeignKey
)

# Import at runtime to prevent circular imports
if TYPE_CHECKING:
  from .user import UserModel

TokenType = Literal['Verification', 'PasswordReset']


class TokenModel(db.Model):
  """
  Token Model
  Verification and Password Reset
  """
  __tablename__ = 'token_table'

  id  : Mapped[str]         = mapped_column(ForeignKey('user_table.id'), primary_key = True, nullable = False)
  user: Mapped['UserModel'] = relationship('UserModel', back_populates = 'token')

  token     : Mapped[str] = mapped_column(String, nullable = False, unique = True, default = lambda: uuid.uuid4().hex)
  token_type: Mapped[str] = mapped_column(String, nullable = False)

  expires_at: Mapped[datetime] = mapped_column(DateTime, nullable = False, default = lambda: utc_time.skip('1day'))
  created_at: Mapped[datetime] = mapped_column(DateTime, nullable = False, default = lambda: utc_time.get())

  def __init__(self, user: 'UserModel', token_type: TokenType, token: Optional[str] = None) -> None:
    """
    Parameters
    ----------
    `user: UserModel`, required
      The UserModel to assign the token to

    `token_type: TokenTypes[str]`, required
      The token type

    `token: str`, optional (defaults to None)
      The token hex string, if None, the token will be generated

    Returns
    -------
    `None`
    """
    self.id = user.id
    self.user = user
    self.token_type = token_type
    
    if isinstance(token, str):
      self.token = token

  def __repr__(self):
    """To be used with cache indexing"""
    return '%s(%s)' % (self.__class__.__name__, self.id)

  def save(self) -> None:
    """Commits the model"""
    db.session.add(self)
    db.session.commit()

  def delete(self, commit: bool = True) -> None:
    """Deletes the model and its references"""
    db.session.delete(self)
    if commit: db.session.commit()
