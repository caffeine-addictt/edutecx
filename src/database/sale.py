"""
Sale model
"""

from src import db

import uuid
from datetime import datetime
from dataclasses import dataclass
from functools import cached_property
from typing import List, Dict, TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import (
  String,
  DateTime,
  ForeignKey
)


# Import at runtime to prevent circular imports
if TYPE_CHECKING:
  from .user import UserModel
  from .textbook import TextbookModel


@dataclass(init = True)
class SaleInfo:
  cost: float
  textbook: 'TextbookModel'


class SaleModel(db.Model):
  """
  Sale Model
  """

  __tablename__ = 'sale_table'

  # Identifiers
  id: Mapped[str] = mapped_column(String, unique = True, primary_key = True, nullable = False, default = lambda: uuid.uuid4().hex)
  user_id: Mapped[str] = mapped_column(ForeignKey('user_table.id'), nullable = False)

  # Attributes
  user: Mapped['UserModel'] = relationship('UserModel', back_populates = 'transactions')
  textbook_ids: Mapped[str] = mapped_column(String, nullable = False) # str(id:cost,id2:cost,...)

  # Logs
  created_at: Mapped[datetime] = mapped_column(DateTime, nullable = False, default = datetime.utcnow)


  def __init__(
    self,
    user: 'UserModel',
    textbooks: List['TextbookModel']
  ) -> None:
    self.user_id = user.id
    self.textbook_ids = ','.join([
      f'{i.id}:{i.price}' for i in textbooks
    ])

  def __repr__(self):
    """To be used with cache indexing"""
    return '%s(%s)' % (self.__class__.__name__, self.id)


  @cached_property
  def total_cost(self) -> float:
    return sum([ v.cost for _, v in self.textbooks.items() ])

  @cached_property
  def textbooks(self) -> Dict[str, SaleInfo]:
    data = {}
    for v in self.textbook_ids.split(','): uid, cost = v.split(':'); data[uid] = cost

    from .textbook import TextbookModel as tm
    queried: List['TextbookModel'] = tm.query.filter(TextbookModel.id.in_(list(data.keys()))).all()

    return {
      txtbook.id: SaleInfo(data[txtbook.id], txtbook)
      for txtbook in queried
    }
  

  # DB
  def save(self) -> None:
    """Commits the model"""
    db.session.add(self)
    db.session.commit()

  def delete(self, commit: bool = True) -> None:
    """Deletes the model and its references"""
    db.session.delete(self)
    if commit: db.session.commit()
