"""
Classroom model
"""

from src import db

import uuid
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import (
  String,
  Boolean,
  DateTime,
  ForeignKey,
)


# Import UserModel at runtime to prevent circular imports
if TYPE_CHECKING:
  from .user import UserModel
  from .textbook import TextbookModel
  from .assignment import AssignmentModel
  from .image import ImageModel


class ClassroomModel(db.Model):
  """Classroom model"""
  
  __tablename__ = 'classroom_table'

  # Identifiers
  id: Mapped[str] = mapped_column(String, primary_key = True, unique = True, nullable = False, default = lambda: uuid.uuid4().hex)

  # Stored as str(user1.id|user2.id|...)
  owner_id    : Mapped[str] = mapped_column(String, ForeignKey('user_table.id'), nullable = False)
  educator_ids: Mapped[str] = mapped_column(String, nullable = False, default = '')
  student_ids : Mapped[str] = mapped_column(String, nullable = False, default = '')
  textbook_ids: Mapped[str] = mapped_column(String, nullable = False, default = '')

  # Attributes
  owner      : Mapped['UserModel']             = relationship('UserModel', back_populates = 'owned_classrooms')
  title      : Mapped[str]                     = mapped_column(String, nullable = False, default = 'My Classroom')
  description: Mapped[str]                     = mapped_column(String, nullable = True, default = None)
  assignments: Mapped[List['AssignmentModel']] = relationship('AssignmentModel', back_populates = 'classroom')
  cover_image: Mapped[Optional['ImageModel']]  = relationship('ImageModel', back_populates = 'classroom')

  # Invite
  invite_id     : Mapped[str]  = mapped_column(String, unique = True, nullable = False, default = lambda: uuid.uuid4().hex)
  invite_enabled: Mapped[bool] = mapped_column(Boolean, default = False)

  # Logs
  created_at: Mapped[datetime] = mapped_column(DateTime, nullable = False, default = datetime.utcnow)
  updated_at: Mapped[datetime] = mapped_column(DateTime, nullable = False, default = datetime.utcnow)


  def __init__(
    self,
    owner: 'UserModel',
    title: str,
    description: str,
    invite_enabled: bool = True
  ) -> None:
    """
    Classroom Model

    Parameters
    ----------
    `owner: UserModel`, required
      The owner model
    
    `title: str`, required
      The title of the classroom

    `description: str`, required
      The description of the classroom

    `invite_enabled: bool`, optional (Default to True)
      Enable invite
    """
    self.id = uuid.uuid4().hex
    self.invite_id = uuid.uuid4().hex
    
    self.owner_id = owner.id
    self.title = title
    self.description = description
    self.invite_enabled = invite_enabled

  def __repr__(self):
    """To be used with cache indexing"""
    return '%s(%s)' % (self.__class__.__name__, self.id)

  
  # Private
  @staticmethod
  def _clean_id_str(data: Optional[str] = '', separator: str = '|') -> list[str]:
    """
    Turns DB model saved data str('id1|id2|id3|...) to list[str, ...]

    
    Parameters
    ----------
    `data: str`, required
    `separator: str`, optional (defaults to '|')


    Returns
    -------
    `data: list[str]`
    """
    return [i for i in (data or '').split(separator) if i]

  
  # Properties
  @property
  def students(self) -> list['UserModel'] | None:
    from .user import UserModel as usr
    return usr.query.filter(ClassroomModel.student_ids.contains(usr.id)).all()
  
  @property
  def educators(self) -> list['UserModel'] | None:
    from .user import UserModel as usr
    return usr.query.filter(ClassroomModel.educator_ids.contains(usr.id)).all()
    
  @property
  def textbooks(self) -> list['TextbookModel'] | None:
    from .user import UserModel as usr
    from .textbook import TextbookModel as tm
    return usr.query.filter(ClassroomModel.textbook_ids.contains(tm.id)).all()
  

  def is_student(self, user: 'UserModel') -> bool:
    """
    Checks if the user is a student in the classroom

    Parameters
    ----------
    `user: UserModel`, required
    """
    return user.id in self._clean_id_str(self.student_ids)
  
  def is_educator(self, user: 'UserModel') -> bool:
    """
    Checks if the user is an educator in the classroom

    Parameters
    ----------
    `user: UserModel`, required
    """
    return user.id in self._clean_id_str(self.educator_ids)
  
  def is_owner(self, user: 'UserModel') -> bool:
    """
    Checks if the user is the classroom owner

    Parameters
    ----------
    `user: UserModel`, required
    """
    return user.id == self.owner_id
  
  def is_member(self, user: 'UserModel') -> bool:
    """
    Checks if the user is a member of the classroom

    Parameters
    ----------
    `user: UserModel`, required
    """
    return self.is_student(user) or self.is_educator(user) or self.is_owner(user)
  
  def is_privileged(self, user: 'UserModel') -> bool:
    """
    Checks if the user is privileged in the classroom

    Parameters
    ----------
    `user: UserModel`, required
    """
    return self.is_owner(user) or self.is_educator(user)
  

  # Editing
  def add_students(self, *students: 'UserModel') -> None:
    """
    Add students to the classroom\n
    `DOES NOT COMMIT`\n
    `SKIPS IF OWNER`

    
    Parameters
    ----------
    `*students: UserModel`

    
    Returns
    -------
    `None`

    
    Examples
    --------
    ```py
      add_students(user1)
      add_students(user2, user3)
    ```
    """
    current_data = self._clean_id_str(self.student_ids)
    appended_data = set(current_data + [i.id for i in students if i.id != self.owner_id]) # Casted to set to prevent duplicates
    self.student_ids = '|'.join(appended_data)
    return None

  def remove_students(self, *students: 'UserModel') -> None:
    """
    Remove students from the classroom\n
    `DOES NOT COMMIT`

    
    Parameters
    ----------
    `*students: UserModel`

    
    Returns
    -------
    `None`

    
    Examples
    --------
    ```py
      remove_students(user1)
      remove_students(user2, user3)
    ```
    """
    to_exclude = set([str(i.id) for i in students]) # Casted to set to prevent duplicates
    current_data = self._clean_id_str(self.student_ids)
    filtered_data = set([i for i in current_data if i not in to_exclude]) # Casted to set to prevent duplicates
    self.student_ids = '|'.join(filtered_data)
    return None


  def add_educators(self, *educators: 'UserModel') -> None:
    """
    Add educators to the classroom\n
    `DOES NOT COMMIT`\n
    `SKIPS IF OWNER`

    
    Parameters
    ----------
    `*educators: UserModel`

    
    Returns
    -------
    `None`

    
    Examples
    --------
    ```py
      add_educators(user1)
      add_educators(user2, user3)
    ```
    """
    current_data = self._clean_id_str(self.educator_ids)
    appended_data = set(current_data + [i.id for i in educators if i.id != self.owner_id]) # Casted to set to prevent duplicates
    self.educator_ids = '|'.join(appended_data)
    return None

  def remove_educators(self, *educators: 'UserModel') -> None:
    """
    Remove educators from the classroom\n
    `DOES NOT COMMIT`

    
    Parameters
    ----------
    `*educators: UserModel`

    
    Returns
    -------
    `None`

    
    Examples
    --------
    ```py
      remove_educators(user1)
      remove_educators(user2, user3)
    ```
    """
    to_exclude = set([str(i.id) for i in educators]) # Casted to set to prevent duplicates
    current_data = self._clean_id_str(self.educator_ids)
    filtered_data = set([i for i in current_data if i not in to_exclude]) # Casted to set to prevent duplicates
    self.educator_ids = '|'.join(filtered_data)
    return None


  def add_textbooks(self, *textbooks: 'TextbookModel') -> None:
    """
    Add textbooks to the classroom\n
    `DOES NOT ENFORCE OWNED CLAUSE`\n
    `DOES NOT COMMIT`

    
    Parameters
    ----------
    `*textbooks: TextbookModel`

    
    Returns
    -------
    `None`

    
    Examples
    --------
    ```py
      add_textbooks(doc1)
      add_textbooks(doc2, doc3)
    ```
    """
    current_data = self._clean_id_str(self.textbook_ids)
    appended_data = set(current_data + [i.id for i in textbooks]) # Casted to set to prevent duplicates
    self.textbook_ids = '|'.join(appended_data)
    return None

  def remove_textbooks(self, *textbooks: 'TextbookModel') -> None:
    """
    Remove textbooks from the classroom\n
    `DOES NOT COMMIT`

    
    Parameters
    ----------
    `*textbooks: TextbookModel`

    
    Returns
    -------
    `None`

    
    Examples
    --------
    ```py
      remove_textbooks(doc1)
      remove_textbooks(doc2, doc3)
    ```
    """
    to_exclude = set([str(i.id) for i in textbooks]) # Casted to set to prevent duplicates
    current_data = self._clean_id_str(self.textbook_ids)
    filtered_data = set([i for i in current_data if i not in to_exclude]) # Casted to set to prevent duplicates
    self.textbook_ids = '|'.join(filtered_data)
    return None


  # DB
  def save(self) -> None:
    """Commits the model"""
    db.session.add(self)
    db.session.commit()

  def delete(self) -> None:
    """Deletes the model and cleans up references"""
    if self.cover_image: self.cover_image.delete()
    for i in self.assignments: i.delete()

    db.session.delete(self)
    db.session.commit()
