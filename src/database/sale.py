"""
Sale model
"""

from src import db

import uuid
from datetime import datetime
from dataclasses import dataclass
from functools import cached_property
from typing import Optional, Literal, List, Dict, TYPE_CHECKING, overload

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import (
  Enum,
  Float,
  String,
  Boolean,
  DateTime,
  ForeignKey
)


# Import at runtime to prevent circular imports
if TYPE_CHECKING:
  from .user import UserModel
  from .textbook import TextbookModel
  from .discount import DiscountModel
  from .assotiation import sale_textbook_assotiation


SaleType = Literal['OneTime', 'Subscription']
EnumSaleType = Enum('OneTime', 'Subscription', name = 'SaleType')

@dataclass
class SaleInfo:
  cost: float
  textbook: 'TextbookModel'


class SaleModel(db.Model):
  """Sale Model"""

  __tablename__ = 'sale_table'

  # Identifiers
  id          : Mapped[str]           = mapped_column(String, unique = True, primary_key = True, nullable = False, default = lambda: uuid.uuid4().hex)
  user_id     : Mapped[str]           = mapped_column(ForeignKey('user_table.id'), nullable = False)
  discount_id : Mapped[Optional[str]] = mapped_column(ForeignKey('discount_table.id'), nullable = True)

  # Stripe IDs
  session_id     : Mapped[Optional[str]] = mapped_column(String, nullable = True)
  subscription_id: Mapped[Optional[str]] = mapped_column(String, nullable = True)

  # Attributes
  type         : Mapped[SaleType]                  = mapped_column(EnumSaleType, nullable = False)
  paid         : Mapped[bool]                      = mapped_column(Boolean, nullable = False, default = False)
  total_cost   : Mapped[float]                     = mapped_column(Float, nullable = False)

  user         : Mapped['UserModel']                       = relationship('UserModel')
  used_discount: Mapped[Optional['DiscountModel']]         = relationship('DiscountModel', back_populates = 'used_by')
  data         : Mapped[List['sale_textbook_assotiation']] = relationship('sale_textbook_assotiation', back_populates = 'sale')

  # Logs
  paid_at   : Mapped[datetime] = mapped_column(DateTime, nullable = True)
  created_at: Mapped[datetime] = mapped_column(DateTime, nullable = False, default = datetime.utcnow)


  @overload
  def __init__(
    self,
    user: 'UserModel',
    saleType: Literal['OneTime'],
    *,
    saleinfo: List[SaleInfo],
    session_id: Optional[str] = None,
    discount: Optional['DiscountModel'] = None
  ) -> None:
    """
    Sale Model

    Parameters
    ----------
    `user: UserModel`, required

    `saleType: Literal['OneTime']`, required

    `saleinfo: List[SaleInfo]`, required

    `session_id: str`, optional (defaults to None)

    `discount: DiscountModel`, optional (defaults to None)
    """

  @overload
  def __init__(
    self,
    user: 'UserModel',
    saleType: Literal['Subscription'],
    *,
    total_cost: float,
    session_id: Optional[str] = None,
    discount: Optional['DiscountModel'] = None
  ) -> None:
    """
    Sale Model

    Parameters
    ----------
    `user: UserModel`, required

    `saleType: Literal['Subscription']`, required

    `total_cost: float`, required

    `session_id: str`, optional (defaults to None)

    `discount: DiscountModel`, optional (defaults to None)
    """

  def __init__(
    self,
    user: 'UserModel',
    saleType: SaleType,
    saleinfo: Optional[List[SaleInfo]] = None,
    total_cost: Optional[float] = None,
    *,
    session_id: Optional[str] = None,
    discount: Optional['DiscountModel'] = None
  ) -> None:
    self.user_id = user.id
    self.session_id = session_id
    self.type = saleType
    self.discount_id = discount and discount.id

    self.total_cost = total_cost or 0

    if saleType == 'OneTime':
      from .assotiation import sale_textbook_assotiation as sta
      self.data = []
      for info in (saleinfo or []):
        self.total_cost += info.cost

        newSta = sta(self, info.textbook, info.textbook.price)
        newSta.save()
        self.data.append(newSta)
    
    if discount:
      discount.used += 1
      discount.save()


  def __repr__(self):
    """To be used with cache indexing"""
    return '%s(%s)' % (self.__class__.__name__, self.id)


  @cached_property
  def textbooks(self) -> Dict[str, SaleInfo]:
    if self.type != 'OneTime':
      raise ValueError('Is not a one-time sale')

    return {
      assotiation.textbook.id: SaleInfo(assotiation.cost, assotiation.textbook)
      for assotiation in self.data
    }

  

  # DB
  def save(self) -> None:
    """Commits the model"""
    db.session.add(self)
    db.session.commit()

  def delete(self) -> None:
    """Deletes the model and its references"""
    db.session.delete(self)
    db.session.commit()
