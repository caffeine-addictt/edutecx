'''
Assosiation tables for many-to-many relaionships
'''

from src import db
from sqlalchemy import ForeignKey, Column, String, Enum
from sqlalchemy.orm import Mapped, mapped_column

from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
  from .user import UserModel
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
