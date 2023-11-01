"""
Receipt model
"""

from src import db

import uuid
from datetime import datetime
from dataclasses import dataclass
from functools import cached_property
from typing import Optional, List, Dict, TYPE_CHECKING
from werkzeug.datastructures import FileStorage

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import (
  String,
  DateTime,
  ForeignKey
)


# Import at runtime to prevent circular imports
if TYPE_CHECKING:
  from .user import UserModel
  from .document import DocumentModel


@dataclass(init = True)
class ProductStatistics:
  quantity: int
  cost: float


class ReceiptModel(db.Model):
  """
  Receipt Model
  """

  __tablename__ = 'receipt_table'

  # Identifiers
  id: Mapped[str] = mapped_column(String, unique = True, primary_key = True, nullable = False, default = lambda: uuid.uuid4().hex)
  user_id: Mapped[str] = mapped_column(ForeignKey('user_table.id'), nullable = False)

  # Attributes
  user: Mapped['UserModel'] = relationship('UserModel', back_populates = 'orders')
  products_raw: Mapped[str] = mapped_column(String, nullable = False) # str(id:cost,id2:cost,...)

  # Logs
  created_at: Mapped[datetime] = mapped_column(DateTime, nullable = False, default = datetime.utcnow)

  def __init__(
    self,
    user: 'UserModel',
    products: List['DocumentModel']
  ) -> None:
    self.user_id = user.id
    self.products_raw = ','.join([
      f'{i.id}:{i.price:.2f}' for i in products
    ])

  def __repr__(self):
    """To be used with cache indexing"""
    return '%s(%s)' % (self.__class__.__name__, self.id)


  @cached_property
  def cleaned_products(self) -> Dict[str, ProductStatistics]:
    total: Dict[str, ProductStatistics] = {}
    for i in self.products_raw.split(','):
      productID, soldPrice = i.split(':')
      if total.get(productID):
        total[productID].quantity += 1
        total[productID].cost += float(soldPrice)
      else:
        total[productID] = ProductStatistics(1, float(soldPrice))

    return total
