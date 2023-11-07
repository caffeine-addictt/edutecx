"""
Stores revoked tokens
"""

from src import db
from src.utils.ext import utc_time

from datetime import datetime, timedelta
from typing import Union, Literal
from flask import current_app as app

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import (
  or_,
  String,
  DateTime,
)

class JWTBlocklistModel(db.Model):
  """
  Stores revoked tokens
  """

  __tablename__ = 'jwtblocklist_table'

  jti: Mapped[str] = mapped_column(String, primary_key = True, unique = True, nullable = False)
  token_type: Mapped[str] = mapped_column(String, nullable = False)
  created_at: Mapped[datetime] = mapped_column(DateTime, nullable = False, default = datetime.utcnow)

  def __init__(self, jti: str, token_type: Literal['access', 'refresh']) -> None:
    self.jti = jti
    self.token_type = token_type

  def save(self) -> None:
    """
    Commits self to the database
    """
    db.session.add(self)
    db.session.commit()

  def save_with_cleanup(self) -> None:
    """
    Commits self to the database\n
    Also invokes cleanup on expired tokens
    """
    self.__class__.clear_expired(commit = False)
    db.session.add(self)
    db.session.commit()

  @classmethod
  def clear_expired(
    cls,
    access_live_time: Union[str, int, float] = '1week',
    refresh_live_time: Union[str, int, float] = '1week1',
    commit: bool = True
  ) -> None:
    now = utc_time.get()
    access_lowest_limit = now - timedelta(seconds = utc_time.convertToTime(access_live_time))
    refresh_lowest_limit = now - timedelta(seconds = utc_time.convertToTime(refresh_live_time))

    cls.query.filter(or_(
      (cls.token_type.like('access') and cls.created_at.timestamp() <= access_lowest_limit.timestamp()),
      (cls.token_type.like('refresh') and cls.created_at.timestamp() <= refresh_lowest_limit.timestamp())
    )).delete()
    if commit: db.session.commit()

