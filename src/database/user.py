"""
User Model
"""

from src import db
from src.utils import passwords

import uuid
from functools import cache, cached_property
from datetime import datetime
from typing import Literal, List, Optional, TYPE_CHECKING

from custom_lib.flask_login import UserMixin
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import (
  String,
  DateTime
)


# Import TokenModel at runtime to prevent circular imports
if TYPE_CHECKING:
  from .token import TokenModel
  from .classroom import ClassroomModel
  from .submission import SubmissionModel
  from .comment import CommentModel
  from .document import DocumentModel
  from .receipt import ReceiptModel


PrivilegeTypes = Literal['User', 'Admin']
ClassroomMemberType = Literal['Student', 'Educator', 'Owner']

class ClassroomMember:
  """ClassroomMember"""
  def __init__(self, user: 'UserModel', classroom: 'ClassroomModel', role: ClassroomMemberType) -> None:
    self.classroom = classroom
    self.role = role
    self.user = user

  def __repr__(self):
    """To be used with cache indexing"""
    return '%s(%s-%s)' % (self.__class__.__name__, self.user.id, self.classroom.id)
  

# TODO: A way to persist document edits per user
# TODO: Store user sessions
# TODO: Add a help method for fetching uploaded and bought documents
class UserModel(db.Model, UserMixin):
  """
  User Model
  """

  __tablename__ = 'user_table'

  # Identifiers
  id      : Mapped[str] = mapped_column(String, unique = True, primary_key = True, nullable = False, default = lambda: uuid.uuid4().hex)
  email   : Mapped[str] = mapped_column(String, unique = True, nullable = False)
  username: Mapped[str] = mapped_column(String, unique = True, nullable = False)

  # Auth
  privilege     : Mapped[str] = mapped_column(String, default = False)
  password_hash : Mapped[str] = mapped_column(String, nullable = False)

  # Token
  token: Mapped[Optional['TokenModel']] = relationship('TokenModel', back_populates = 'user')

  # Class (Classroom feature)
  comments        : Mapped[List['CommentModel']]    = relationship('CommentModel', back_populates = 'author')
  submissions     : Mapped[List['SubmissionModel']] = relationship('SubmissionModel', back_populates = 'student')
  owned_classrooms: Mapped[List['ClassroomModel']]  = relationship('ClassroomModel', primaryjoin = 'UserModel.id == ClassroomModel.owner_id', back_populates = 'owner')

  # Documents
  documents      : Mapped[str]                   = mapped_column(String, nullable = True)
  owned_documents: Mapped[List['DocumentModel']] = relationship('DocumentModel', primaryjoin = 'UserModel.id == DocumentModel.author_id', back_populates = 'author')

  # Orders
  orders: Mapped[List['ReceiptModel']] = relationship('ReceiptModel', back_populates = 'user')

  # Logs
  created_at: Mapped[datetime] = mapped_column(DateTime, nullable = False, default = datetime.utcnow)
  last_login: Mapped[datetime] = mapped_column(DateTime, nullable = False, default = datetime.utcnow)

  def __init__(self,
    email: str,
    username: str,
    password: str,
    privilege: PrivilegeTypes
  ) -> None:
    self.email     = email
    self.username  = username
    self.privilege = privilege
    self.password_hash  = password

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
  def password(self) -> None:
    raise AttributeError('Password is not reaadable!')

  @cached_property
  def classrooms(self) -> list[ClassroomMember]:
    from .classroom import ClassroomModel as cm # Import in runtime to prevent circular imports

    asStudent: list['ClassroomModel'] = cm.query.filter(cm.student_ids.contains(self.id)).all()
    asEducator: list['ClassroomModel'] = cm.query.filter(cm.educator_ids.contains(self.id)).all()
    asOwner: list['ClassroomModel'] = self.owned_classrooms

    classes: list[ClassroomMember] = []
    for i in asStudent: classes.append(ClassroomMember(self, i, 'Student'))
    for i in asEducator: classes.append(ClassroomMember(self, i, 'Educator'))
    for i in asOwner: classes.append(ClassroomMember(self, i, 'Owner'))

    return classes
  

  # Editing
  def join_class(self, *classrooms: 'ClassroomModel') -> None:
    """
    Add user to the classroom\n
    `COMMITS`

    
    Parameters
    ----------
    `*classrooms: ClassroomModel`

    
    Returns
    -------
    `None`

    
    Examples
    --------
    ```py
      join_class(class1)
      join_class(class2, class3)
    ```
    """
    cleaned_classroms = set(classrooms)
    joined_classes = self.classrooms

    for class_ in cleaned_classroms:
      already_joined: bool = any([i.classroom.id == class_.id for i in joined_classes])
      if not already_joined:
        class_.add_students(self)

    db.session.commit()
    return None

  def exit_class(self, *classrooms: 'ClassroomModel') -> None:
    """
    Remove user from the classroom\n
    `COMMITS`

    
    Parameters
    ----------
    `*classrooms: ClassroomModel`

    
    Returns
    -------
    `None`

    
    Examples
    --------
    ```py
      exit_class(class1)
      exit_class(class2, class3)
    ```
    """
    cleanedClassroms = set(classrooms)
    joinedClasses = self.classrooms

    for class_ in joinedClasses:
      matched: bool = any([ i.id == class_.classroom.id for i in cleanedClassroms])
      match (matched and class_.role):
        case 'Student':
          class_.classroom.remove_students(self)
          break

        case 'Educator':
          class_.classroom.remove_educators(self)
          break

    db.session.commit()
    return None


  # Querying
  @staticmethod
  @cache
  def query_by(primary_key: Optional[str], **kwargs) -> List['UserModel']:
    """
    Query with caching

    Parameters
    ----------
    `primary_key: str`, optional (defaults to None)
    `**kwargs: dict[str, Any]`, optional (defaults to {})

    Returns
    -------
    `list['UserModel']`
    """
    if primary_key is not None:
      kwargs['id'] = primary_key

    return UserModel.query.filter_by(**kwargs).all()


  # Verification
  def verify_password(self, password: str) -> bool:
    try:
      is_equal = passwords.compare_password(password, self.password_hash.encode())
      return is_equal
    except Exception:
      return False
