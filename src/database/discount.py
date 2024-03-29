"""
Discount Model
"""

from src import db

import uuid
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import (
  Float,
  String,
  Integer,
  DateTime,
  ForeignKey,
)


# Import TokenModel at runtime to prevent circular imports
if TYPE_CHECKING:
  from .sale import SaleModel
  from .textbook import TextbookModel


class DiscountModel(db.Model):
  """
  Discount Model
  """

  __tablename__ = 'discount_table'

  id: Mapped[str] = mapped_column(
    String,
    primary_key=True,
    unique=True,
    nullable=False,
    default=lambda: uuid.uuid4().hex,
  )
  textbook_id: Mapped[Optional[str]] = mapped_column(
    ForeignKey('textbook_table.id'), nullable=False
  )

  code: Mapped[str] = mapped_column(String, nullable=False)
  used: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
  used_by: Mapped[List['SaleModel']] = relationship(
    'SaleModel', back_populates='used_discount'
  )
  limit: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
  multiplier: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
  textbook: Mapped[Optional['TextbookModel']] = relationship(
    'TextbookModel', back_populates='discounts'
  )

  expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
  created_at: Mapped[datetime] = mapped_column(
    DateTime, nullable=False, default=datetime.utcnow
  )

  def __init__(
    self,
    code: str,
    multiplier: float,
    textbook: Optional['TextbookModel'] = None,
    *,
    expires_at: Optional[datetime] = None,
    limit: Optional[int] = None,
  ) -> None:
    """
    Discount Model

    Parameters
    ----------
    `code: str`, required

    `multiplier: float`, required
      The discount multiplier from x0 to x3

    `textbook: TextbookModel`, optional (defaults to None)

    `expires_at: datetime`, optional (defaults to None)

    `limit: int`, optional (defaults to None)

    Raises
    ------
    AssertionError : If `multiplier` is not between 0 and 3
    """
    assert 0 <= multiplier <= 3, 'Multiplier must be between 0 and 3'

    self.code = code
    self.multiplier = multiplier
    self.textbook = textbook
    self.expires_at = expires_at
    self.limit = limit

  def __repr__(self) -> str:
    return f'{self.__class__.__name__}(code={self.code})'

  def save(self) -> None:
    """Commits the model"""
    db.session.add(self)
    db.session.commit()

  def delete(self) -> None:
    """Deletes the model and its references"""
    db.session.delete(self)
    db.session.commit()
