"""
Stores revoked tokens
"""

from src import db
from src.utils.ext import utc_time

from datetime import datetime, timedelta
from typing import Union
from flask import current_app as app

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import (
  String,
  DateTime,
)

class JWTBlocklistModel(db.Model):
  """
  Stores revoked tokens
  """

  __tablename__ = 'jwtblocklist_table'

  jti: Mapped[str] = mapped_column(String, primary_key = True, unique = True, nullable = False)
  created_at: Mapped[datetime] = mapped_column(DateTime, nullable = False, default = datetime.utcnow)

  def __init__(self, jti: str) -> None:
    self.jti = jti

  def save(self) -> None:
    """
    Commits self to the database\n
    Also invokes cleanup on expired tokens
    """
    self.__class__.clear_expired(
      app.config.get('JWT_ACCESS_TOKEN_EXPIRES', None),
      commit = False
    )
    db.session.add(self)
    db.session.commit()

  @classmethod
  def clear_expired(
    cls,
    live_time: Union[str, int, float] = '1week',
    commit: bool = True
  ) -> None:
    expiration_seconds = utc_time.convertToTime(live_time)
    lowest_limit = datetime.now() - timedelta(seconds = expiration_seconds)

    cls.query.filter(cls.created_at.timestamp() <= lowest_limit).delete()
    if commit: db.session.commit()

