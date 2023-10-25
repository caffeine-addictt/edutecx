"""
Token Model

managing verification token and  password reset token
"""

from src import db
from src.utils.ext import utc_time
from . import UserModel

import uuid
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, Relationship, backref
from sqlalchemy import (
  String,
  Boolean,
  DateTime,
  ForeignKey,
  literal
)


# TODO: Add ForeignKey reference to UserModel.token
class TokenModel(db.Model):
  """
  Token Model
  Verification and Password Reset
  """
  __tablename__ = 'tokens'

  user_id        : Mapped[str]      = mapped_column(String, ForeignKey('users.id'), primary_key = True, nullable = False)
  user: Mapped[UserModel] = Relationship('UserModel', backref = backref('tokens', uselist = False))

  token: Mapped[str] = mapped_column(String, nullable = False, unique = True, default = lambda: uuid.uuid4().hex)
  token_type: Mapped[str] = mapped_column(String, nullable = False)

  expires_at: Mapped[datetime] = mapped_column(DateTime, nullable = False, default = lambda: utc_time.skip('1day'))
  created_at: Mapped[datetime] = mapped_column(DateTime, nullable = False, default = lambda: utc_time.get())

  def __init__(self, user_id: str, token_type: str, token: str | None = None) -> None:
    """
    Parameters
    ----------
    `user_id: str`, required
      The UserID of the UserModel to assign the token to

    `token_type: str`, required
      The token type

    `token: str`, optional (defaults to None)
      The token hex string, if None, the token will be generated

    Returns
    -------
    `None`
    """
    self.user_id = user_id
    self.token_type = token_type
    
    if isinstance(token, str):
      self.token = token
