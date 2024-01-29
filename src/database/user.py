"""
User Model
"""

from src import db
from src.utils import passwords

import uuid
from functools import cache, cached_property
from datetime import datetime
from typing import Literal, List, Optional, TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import (
  Enum,
  String,
  Boolean,
  DateTime
)


# Import TokenModel at runtime to prevent circular imports
if TYPE_CHECKING:
  from .token import TokenModel
  from .classroom import ClassroomModel
  from .submission import SubmissionModel
  from .comment import CommentModel
  from .textbook import TextbookModel
  from .sale import SaleModel
  from .image import ImageModel
  from .submissionsnippet import SubmissionSnippetModel
  from .assotiation import user_textbook_assotiation


UserStatus = Literal['Active', 'Locked']
EnumUserStatus = Enum('Active', 'Locked', name = 'UserStatus')

PrivilegeType = Literal['Student', 'Educator', 'Admin']
EnumPrivilegeType = Enum('Student', 'Educator', 'Admin', name = 'PrivilegeType')

SubscriptionStatus = Literal['Active', 'Inactive', 'Cancelled']
EnumSubscriptionStatus = Enum('Active', 'Inactive', 'Cancelled', name = 'SubscriptionStatus')

MembershipType = Literal['Free', 'Unlimited']
EnumMembershipType = Enum('Free', 'Unlimited', name = 'MembershipType')


ClassroomMemberType = Literal['Student', 'Educator', 'Owner']
class ClassroomMember:
  """ClassroomMember"""
  def __init__(self, user: 'UserModel', classroom: 'ClassroomModel', role: ClassroomMemberType) -> None:
    self.classroom = classroom
    self.role = role
    self.user = user

  def __repr__(self) -> str:
    """To be used with cache indexing"""
    return '%s(%s-%s)' % (self.__class__.__name__, self.user.id, self.classroom.id)
  

class UserModel(db.Model):
  """User Model"""

  __tablename__ = 'user_table'

  # Identifiers
  id      : Mapped[str] = mapped_column(String, unique = True, primary_key = True, nullable = False, default = lambda: uuid.uuid4().hex)
  email   : Mapped[str] = mapped_column(String, unique = True, nullable = False)
  username: Mapped[str] = mapped_column(String, unique = True, nullable = False)

  # Auth
  status        : Mapped[UserStatus]     = mapped_column(EnumUserStatus, nullable = False, default = 'Active')
  privilege     : Mapped[PrivilegeType]  = mapped_column(EnumPrivilegeType, nullable = False)
  membership    : Mapped[MembershipType] = mapped_column(EnumMembershipType, nullable = False, default = 'Free')
  password_hash : Mapped[str]            = mapped_column(String, nullable = False)
  email_verified: Mapped[bool]           = mapped_column(Boolean, nullable = False, default = False)

  # Misc
  token        : Mapped[Optional['TokenModel']] = relationship('TokenModel', back_populates = 'user')
  profile_image: Mapped[Optional['ImageModel']] = relationship('ImageModel', back_populates = 'user')

  # Class (Classroom feature)
  comments        : Mapped[List['CommentModel']]           = relationship('CommentModel', back_populates = 'author')
  submissions     : Mapped[List['SubmissionModel']]        = relationship('SubmissionModel', back_populates = 'student')
  snippets        : Mapped[List['SubmissionSnippetModel']] = relationship('SubmissionSnippetModel', back_populates = 'student')
  classrooms      : Mapped[List['ClassroomModel']]         = relationship('ClassroomModel', secondary = 'classroom_user_assotiation', back_populates = 'members')
  owned_classrooms: Mapped[List['ClassroomModel']]         = relationship('ClassroomModel', primaryjoin = 'UserModel.id == ClassroomModel.owner_id', back_populates = 'owner', overlaps = 'classrooms', viewonly = True)

  # Textbooks
  textbooks      : Mapped[List['TextbookModel']] = relationship('TextbookModel', secondary = 'user_textbook_assotiation', back_populates = 'bought_by')
  owned_textbooks: Mapped[List['TextbookModel']] = relationship('TextbookModel', primaryjoin = 'UserModel.id == TextbookModel.author_id', back_populates = 'author', overlaps = 'textbooks')

  # Transactions
  subscription_id     : Mapped[Optional[str]]      = mapped_column(String, nullable = True)
  subscription_status : Mapped[SubscriptionStatus] = mapped_column(EnumSubscriptionStatus, nullable = False, default = 'Inactive')            
  transactions        : Mapped[List['SaleModel']]  = relationship('SaleModel', primaryjoin = 'and_(SaleModel.user_id == UserModel.id, SaleModel.paid == True)', back_populates = 'user')
  pending_transactions: Mapped[List['SaleModel']]  = relationship('SaleModel', primaryjoin = 'and_(SaleModel.user_id == UserModel.id, SaleModel.paid != True)', overlaps = 'transactions', back_populates = 'user')

  # Logs
  created_at: Mapped[datetime] = mapped_column(DateTime, nullable = False, default = datetime.utcnow)
  last_login: Mapped[datetime] = mapped_column(DateTime, nullable = False, default = datetime.utcnow)


  def __init__(self,
    email: str,
    username: str,
    password: str,
    privilege: PrivilegeType,
    *,
    membership: MembershipType = 'Free'
  ) -> None:
    """
    User Model

    Parameters
    ----------
    `email: str`, required

    `username: str`, required

    `password: str`, required
      The hashed password

    `privilege: PrivilegeTypes`
      Look at src.database.PrivilegeTypes
    """
    self.id = uuid.uuid4().hex
    self.email     = email
    self.username  = username
    self.privilege = privilege
    self.password_hash  = password
    self.membership = membership

  def __repr__(self) -> str:
    """To be used with cache indexing"""
    return '%s(%s)' % (self.__class__.__name__, self.id)

    
  # Properties
  @property
  def password(self) -> None:
    raise AttributeError('Password is not reaadable!')

  # Editing
  def join_class(self, *classrooms: 'ClassroomModel', commits: bool = True) -> None:
    """
    Add user to the classroom\n
    `COMMITS`

    
    Parameters
    ----------
    `*classrooms: ClassroomModel`

    `commits: bool`

    
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
    cleaned_classrooms = set(classrooms)

    for class_ in cleaned_classrooms:
      if class_ in self.classrooms:
        class_.add_students(self)
        

    if commits: db.session.commit()
    return None

  def exit_class(self, *classrooms: 'ClassroomModel', commits: bool = True) -> None:
    """
    Remove user from the classroom\n
    `COMMITS`

    
    Parameters
    ----------
    `*classrooms: ClassroomModel`

    `commits: bool`

    
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
    cleaned_classrooms = set(classrooms)

    for class_ in self.classrooms:
      if class_ not in cleaned_classrooms:
        continue

      if self in class_.students:
        class_.remove_students(self)
      
      if self in class_.educators:
        class_.remove_educators(self)

    if commits: db.session.commit()
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

  # DB
  def save(self) -> None:
    """Commit the model"""
    db.session.add(self)
    db.session.commit()

  def delete(self) -> None:
    """Deletes the model and its references"""
    if self.token: self.token.delete()
    if self.profile_image: self.profile_image.delete()

    for i in self.comments: i.delete()
    for i in self.submissions: i.delete()

    for i in self.transactions: i.delete()
    for i in self.owned_textbooks: i.delete()
    for i in self.owned_classrooms: i.delete()
    self.exit_class(*self.classrooms)

    db.session.delete(self)
    db.session.commit()
