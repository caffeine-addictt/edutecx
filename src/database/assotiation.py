'''
Assosiation tables for many-to-many relaionships
'''

from src import db
from sqlalchemy import ForeignKey, Column, String, Float, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
  from .user import UserModel
  from .sale import SaleModel
  from .textbook import TextbookModel
  from .classroom import ClassroomModel




user_textbook_assotiation = db.Table(
  'user_textbook_assotiation',
  Column('user_id', String, ForeignKey('user_table.id')),
  Column('textbook_id', String, ForeignKey('textbook_table.id'))
)


ClassroomMemberRole = Literal['Owner', 'Educator', 'Student']
EnumClassroomMemberRole = Enum('Owner', 'Educator', 'Student')
class classroom_user_assotiation(db.Model):
  __tablename__ = 'classroom_user_assotiation'

  user_id = Column(String, ForeignKey('user_table.id'), nullable = False, primary_key = True)
  classroom_id = Column(String, ForeignKey('classroom_table.id'), nullable = False, primary_key = True)
  role: Mapped[ClassroomMemberRole] = mapped_column(EnumClassroomMemberRole, nullable = False, default = 'Student')

  def __init__(self, user: 'UserModel', classroom: 'ClassroomModel', role: ClassroomMemberRole) -> None:
    self.user_id = user.id
    self.classroom_id = classroom.id
    self.role = role
  
  def __repr__(self) -> str:
    return f'ClassroomMember({self.user_id}, {self.classroom_id}, {self.role})'
  
  def __hash__(self) -> int:
    return hash((self.user_id, self.classroom_id))
  
  def save(self) -> None:
    db.session.add(self)
    db.session.commit()
  
  def delete(self) -> None:
    db.session.delete(self)
    db.session.commit()


classroom_textbook_assotiation = db.Table(
  'classroom_textbook_assotiation',
  Column('classroom_id', String, ForeignKey('classroom_table.id')),
  Column('textbook_id', String, ForeignKey('textbook_table.id'))
)


assignment_textbook_assotiation = db.Table(
  'assignment_textbook_assotiation',
  Column('assignment_id', String, ForeignKey('assignment_table.id')),
  Column('textbook_id', String, ForeignKey('textbook_table.id'))
)



class sale_textbook_assotiation(db.Model):
  __tablename__ = 'sale_textbook_assotiation'

  sale_id = Column(String, ForeignKey('sale_table.id'), nullable = False, primary_key = True)
  textbook_id = Column(String, ForeignKey('textbook_table.id'), nullable = False, primary_key = True)

  sale: Mapped['SaleModel'] = relationship('SaleModel', back_populates = 'data')
  textbook: Mapped['TextbookModel'] = relationship('TextbookModel', back_populates = 'sales')
  cost: Mapped[float] = mapped_column(Float, nullable = False)

  def __init__(self, sale: 'SaleModel', textbook: 'TextbookModel', cost: int | float) -> None:
    self.cost = cost
    self.sale_id = sale.id
    self.textbook_id = textbook.id
  
  def __repr__(self) -> str:
    return f'SaleTextbook({self.sale_id}, {self.textbook_id})'
  
  def __hash__(self) -> int:
    return hash((self.sale_id, self.textbook_id))
  
  def save(self) -> None:
    db.session.add(self)
    db.session.commit()
  
  def delete(self) -> None:
    db.session.delete(self)
    db.session.commit()
