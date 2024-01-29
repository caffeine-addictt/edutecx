'''
Assosiation tables for many-to-many relaionships
'''

from src import db
from sqlalchemy import ForeignKey, Column, String


user_textbook_assotiation = db.Table(
  'user_textbook_assotiation',
  Column('user_id', String, ForeignKey('user_table.id')),
  Column('textbook_id', String, ForeignKey('textbook_table.id'))
)


