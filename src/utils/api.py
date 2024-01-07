"""
API Parser
"""

from .forcetype import recursiveValidation
from typing import Any, Union, Literal, Optional, Mapping

from requests import Response as ReqResponse
from flask import Request, Response as FlaskResponse
from werkzeug.exceptions import BadRequest
from werkzeug.datastructures import FileStorage

from abc import abstractmethod
from dataclasses import dataclass




class _APIBase:
  """API Base Class"""

  @abstractmethod
  def __init__(self) -> None:
    ...

  def __str__(self) -> str:
    return str(self.__dict__)
        
  def to_dict(self) -> dict[str, Any]:
    return {
      i: (
        (isinstance(v, _APIBase) and v.to_dict())
        or (isinstance(v, (list, tuple)) and type(v)([ v2 if not isinstance(v2, _APIBase) else v2.to_dict() for v2 in v ]))
        or (isinstance(v, Mapping) and type(v)({ i2: v2 if not isinstance(v2, _APIBase) else v2.to_dict() for i2, v2 in v.items() }))
        or v
      )
      for i,v in self.__dict__.items()
    }
  
  def get(self, name: Any, default = None) -> Any | None:
    return self.__dict__.get(name, default)


class _APIParser(_APIBase):
  """
  API Parser

  Auto loads variables from json, dictionary or form
  """

  def __init__(self, req: Request | FlaskResponse | ReqResponse | dict[str, Any], isResponse: bool = False) -> None:
    """
    Loads values from response object

    Raises
    ------
    BadRequest: code 400
    """
    if isinstance(req, (Request, FlaskResponse, ReqResponse)):
      annotationMap = None
      try:
        annotationMap = { i:v for i,v in self.__dict__.items() if not i.startswith('__') }
        annotationMap.update(self.__annotations__.copy())
      except Exception: annotationMap = annotationMap or dict()
    else: annotationMap = req

    if isResponse:
      annotationMap['status'] = int
      annotationMap['message'] = str


    for variableName, variableType in annotationMap.items():
      
      variable = None
      if isinstance(req, Request):
        try: variable = req.json.get(variableName, None) if req.is_json and req.json else None
        except Exception: pass

        try: variable = variable if variable is not None else req.form.get(variableName, None)
        except Exception: pass

        try: variable = variable if variable is not None else req.args.get(variableName, None)
        except Exception: pass
        
      elif isinstance(req, FlaskResponse):
        try: variable = req.json.get(variableName, None) if req.json else None
        except Exception: pass

      elif isinstance(req, ReqResponse):
        try: variable = req.json().get(variableName, None) if req.json else None
        except Exception: pass

      else:
        try: variable = req.get(variableName, None)
        except Exception: pass

      
      if variableType == '':
        self.__dict__[variableName] = recursiveValidation(variable, str) or ''
        continue

      interpreted = recursiveValidation(variable, variableType)
      if (interpreted is not None) or self.get('ignore_none'):
        self.__dict__[variableName] = interpreted
      else:
        raise BadRequest('%s is not valid. Expected %s, Got %s' % (variableName, variableType, variable))




# Base classes
class _APIResponse(_APIParser):
  """
  API Response

  For interpreting api responses
  """

  message: str
  status: int

  def __init__(self, req: Request | FlaskResponse | ReqResponse | dict[str, Any]) -> None:
    """
    Loads values from response object

    Raises
    ------
    BadRequest: code 400
    """
    super().__init__(req, True)


class _APIRequest(_APIParser):
  """
  API Request
  
  For interpreting API requests
  """


@dataclass
class _APIReply(_APIBase):
  """
  API Reply

  For replying to API requests
  """

  message: str
  status: int

class _Files(dict[str, FileStorage]):
  def __init__(self, requestFiles: Mapping[str, FileStorage]):
    super().__init__(requestFiles)
  







# Generic
class GenericResponse(_APIResponse):
  """Generic Response"""

class GenericReply(_APIReply):
  """Generic Reply"""








# Register
class RegisterRequest(_APIRequest):
  """API Request for register"""
  email: str
  username: str
  password: str
  privilege: Literal['Student', 'Educator']

RegisterReply = GenericReply
RegisterResponse = GenericResponse










# Token
@dataclass
class _TokenRefreshData(_APIBase):
  access_token: str

@dataclass
class TokenRefreshReply(_APIReply):
  """API Reply for refreshing JWT access token"""
  data: _TokenRefreshData

class TokenRefreshResponse(_APIResponse):
  """API Response for refreshing JWT access token"""
  data: _TokenRefreshData








# Verify Email
class VerifyEmailRequest(_APIRequest):
  """API Request for verifying email"""
  token: str

VerifyEmailReply = GenericReply
VerifyEmailResponse = GenericResponse








# Notify MAKE
class NotifyMakeRequest(_APIRequest):
  """API Request for making a notification"""
  message: str
  category: Optional[Literal['info', 'success', 'danger']]

NotifyReply = GenericReply
NotifyResponse = GenericResponse








# Notify GET
@dataclass
class NotifyGetReply(_APIReply):
  """API Reply for getting notifications"""
  data: list[tuple[str, str]] | list[str]








# Login
@dataclass
class _LoginData(_APIBase):
  access_token: str
  refresh_token: str

class LoginRequest(_APIRequest):
  """API Request for login"""
  email: str
  password: str
  remember_me: bool

class LoginResponse(_APIResponse):
  """API Response for login"""
  data: _LoginData

@dataclass
class LoginReply(_APIReply):
  """API Reply for login"""
  data: _LoginData








# Stripe Subscription MAKE
@dataclass
class _StripeSubscriptionData(_APIBase):
  session_id: str
  public_key: str

class StripeSubscriptionRequest(_APIRequest):
  """API Request for making a stripe session"""
  tier: Literal['Unlimited']
  discount = ''

@dataclass
class StripeSubscriptionReply(_APIReply):
  """API Reply for making a stripe session"""
  data: _StripeSubscriptionData








# Stripe Checkout MAKE
@dataclass
class _StripeCheckoutData(_APIBase):
  session_id: str
  public_key: str

class StripeCheckoutRequest(_APIRequest):
  """API Request for making a stripe session"""
  cart: list[str]
  discount = ''

@dataclass
class StripeCheckoutReply(_APIReply):
  """API Reply for making a stripe session"""
  data: _StripeCheckoutData








# Stripe Subscription CANCEL
class StripeSubscriptionCancelRequest(_APIRequest):
  """API Request for canceling a stripe session"""
  subscription_id: str

StripeSubscriptionCancelReply = GenericReply








# Stripe EXPIRE
class StripeExpireRequest(_APIRequest):
  """API Request for expiring a stripe session"""
  session_id: str

StripeExpireReply = GenericReply








# Stripe Status
@dataclass
class _StripeStatusData(_APIBase):
  paid          : bool
  total_cost    : float
  user_id       : str
  transaction_id: str
  used_discount : Optional[str]
  paid_at       : float
  created_at    : float

class StripeStatusRequest(_APIRequest):
  """API Request for getting stripe status"""
  session_id: str

@dataclass
class StripeStatusReply(_APIReply):
  """API Reply for getting stripe status"""
  data: _StripeStatusData








# Store GET
class StoreGetRequest(_APIRequest):
  """
  API Request for store
  
  categories to be separated by ','
  """
  criteria: Literal['and', 'or']
  query = ''
  page = 1
  categories: str
  priceLower = 0.0
  priceUpper = float('inf')
  createdLower = 0.0
  createdUpper = float('inf')

@dataclass
class StoreGetReply(_APIReply):
  """API Reply for store"""
  data: list['_TextbookGetData']








# Assignment GET
@dataclass
class _AssignmentGetData(_APIBase):
  id          : str
  classroom_id: str
  title       : str
  description : str
  due_date    : Union[float, str]
  textbooks   : str
  requirement : str
  submissions : list[str]
  created_at  : float
  updated_at  : float

class AssignmentGetRequest(_APIRequest):
  """API Request for assignment fetching"""
  assignment_id: str

@dataclass
class AssignmentGetReply(_APIReply):
  """API Reply for fetching assignment"""
  data: _AssignmentGetData

class AssignmentGetResponse(_APIResponse):
  """API Response for fetching assignment"""
  data: _AssignmentGetData








# Assignment CREATE
@dataclass
class _AssignmentCreateData(_APIBase):
  assignment_id: str

class AssignmentCreateRequest(_APIRequest):
  """
  API Request for assignment creation
  
  due_date: int (UNIX Millies) | str ('infinity')
  """
  classroom_id: str
  title: str
  description: str
  due_date: Union[float, str]
  requirement: str

@dataclass
class AssignmentCreateReply(_APIReply):
  """API Reply for creating a new assignment"""
  data: _AssignmentCreateData

class AssignmentCreateResponse(_APIResponse):
  """API Response for creating a new assignment"""
  data: _AssignmentCreateData








# Assignment EDIT
class AssignmentEditRequest(_APIRequest):
  """API Request for assignment editing"""
  assignment_id: str
  ignore_none = True
  title: Union[str, None]
  description: Union[str, None]
  due_date: Union[float, str, None]
  requirement: Union[str, None]

AssignmentEditReply = GenericReply
AssignmentEditResponse = GenericResponse








# Assignment DELETE
class AssignmentDeleteRequest(_APIRequest):
  """API Request for assignment deletion"""
  assignment_id: str

AssignmentDeleteReply = GenericReply
AssignmentDeleteResponse = GenericResponse








# Classroom LIST
@dataclass
class _ClassroomListData(_APIBase):
  id         : str
  title      : str
  description: str
  cover_image: Union[str, None]
  created_at : float

@dataclass
class ClassroomListReply(_APIReply):
  """API Reply for listing classrooms"""
  data: list[_ClassroomListData]








# Classroom GET
@dataclass
class _ClassroomGetData(_APIBase):
  id            : str
  owner_id      : str
  educator_ids  : list[str]
  student_ids   : list[str]
  textbook_ids  : list[str]
  title         : str
  description   : str
  assignments   : list[str]
  cover_image   : Union[str, None]
  invite_id     : str
  invite_enabled: bool
  created_at    : float
  updated_at    : float

class ClassroomGetRequest(_APIRequest):
  """API Request for classroom fetching"""
  classroom_id: str

@dataclass
class ClassroomGetReply(_APIReply):
  """API Reply for fetching classroom"""
  data: _ClassroomGetData

class ClassroomGetResponse(_APIResponse):
  """API Response for fetching classroom"""
  data: _ClassroomGetData








# Classroom CREATE
@dataclass
class _ClassroomCreateData(_APIBase):
  classroom_id: str

class ClassroomCreateRequest(_APIRequest):
  """API Request for classroom creation"""
  owner_id: str
  title: str
  description: str

@dataclass
class ClassroomCreateReply(_APIReply):
  """API Reply for creating a new classroom"""
  data: _ClassroomCreateData

class ClassroomCreateResponse(_APIResponse):
  """API Response for creating a classroom"""
  data: _ClassroomCreateData








# Classroom EDIT
class ClassroomEditRequest(_APIRequest):
  """API Request for classroom editing"""
  ignore_none   = True
  classroom_id  : Optional[str]
  title         : Optional[str]
  description   : Optional[str]
  cover_image   : Optional[str]
  invite_enabled: Optional[bool]

ClassroomEditReply = GenericReply
ClassroomEditResponse = GenericResponse








# Classroom DELETE
class ClassroomDeleteRequest(_APIRequest):
  """API Request for classroom deletion"""
  classroom_id: str

ClassroomDeleteReply = GenericReply
ClassroomDeleteResponse = GenericResponse








# Classroom JOIN
class ClassroomJoinRequest(_APIRequest):
  """API Request for classroom joining"""
  classroom_id: str

ClassroomJoinReply = GenericReply
ClassroomJoinResponse = GenericResponse








# Classroom LEAVE
class ClassroomLeaveRequest(_APIRequest):
  """API Request for classroom leaving"""
  classroom_id: str

ClassroomLeaveReply = GenericReply
ClassroomLeaveResponse = GenericResponse








# Textbook LIST
class TextbookListRequest(_APIRequest):
  """API Request for textbook listing"""
  criteria: Literal['and', 'or']
  query = ''
  page = 1
  priceLower = 0.0
  priceUpper = float('inf')
  createdLower = 0.0
  createdUpper = float('inf')

@dataclass
class TextbookListReply(_APIReply):
  """API Reply for listing textbooks"""
  data: list['_TextbookGetData']








# Textbook GET
@dataclass
class _TextbookGetData(_APIBase):
  id         : str
  author_id  : str
  title      : str
  description: str
  categories : list[str]
  price      : float
  discount   : float
  uri        : str
  status     : str
  cover_image: Optional[str]
  created_at : float
  updated_at : float

class TextbookGetRequest(_APIRequest):
  """API Request for textbook fetching"""
  textbook_id: str

@dataclass
class TextbookGetReply(_APIReply):
  """API Reply for fetching textbook"""
  data: _TextbookGetData

class TextbookGetResponse(_APIResponse):
  """API Response for fetching textbook"""
  data: _TextbookGetData








# Textbook CREATE
@dataclass
class _TextbookCreateData(_APIBase):
  textbook_id: str

class TextbookCreateRequest(_APIRequest):
  """API Request for textbook creation"""
  author_id  : str
  title      : str
  description: str
  price      : float
  discount   : float

@dataclass
class TextbookCreateReply(_APIReply):
  """API Reply for creating a new textbook"""
  data: _TextbookCreateData

class TextbookCreateResponse(_APIResponse):
  """API Response for creating a new textbook"""
  data: _TextbookCreateData








# Textbook EDIT
class TextbookEditRequest(_APIRequest):
  """API Request for textbook editing"""
  ignore_none = True
  textbook_id: str
  title      : Optional[str]
  description: Optional[str]
  categories : Optional[list[str]]
  price      : Optional[float]
  discount   : Optional[float]

TextbookEditReply = GenericReply
TextbookEditResponse = GenericResponse








# Textbook DELETE
class TextbookDeleteRequest(_APIRequest):
  """API Request for textbook deletion"""
  textbook_id: str

TextbookDeleteReply = GenericReply
TextbookDeleteResponse = GenericResponse








# Comment GET
@dataclass
class _CommentGetData(_APIBase):
  author_id: str
  submission_id: str
  assignment_id: str
  classroom_id: str
  text: str
  created_at: float
  updated_at: float

class CommentGetRequest(_APIRequest):
  """API Request for comment fetching"""
  comment_id: str

@dataclass
class CommentGetReply(_APIReply):
  """API Reply for getting comments"""
  data: _CommentGetData

class CommentGetResponse(_APIResponse):
  """API Response for getting comments"""
  data: _CommentGetData








# Comment CREATE
@dataclass
class _CommentCreateData(_APIBase):
  comment_id: str

class CommentCreateRequest(_APIRequest):
  """API Request for comment creation"""
  submission_id: str
  text: str

@dataclass
class CommentCreateReply(_APIReply):
  """API Reply for creating a comment"""
  data: _CommentCreateData

class CommentCreateResponse(_APIResponse):
  """API Response for creating a comment"""
  data: _CommentCreateData








# EditableTextbook GET
@dataclass
class _EditableTextbookGetData(_APIBase):
  editabletextbook_id: str
  user_id            : str
  textbook_id        : str
  uri                : str
  status             : str
  created_at         : float
  updated_at         : float

class EditableTextbookGetRequest(_APIRequest):
  """API Request for fetching editable textbook"""
  editabletextbook_id: str

@dataclass
class EditableTextbookGetReply(_APIReply):
  """API Reply for fetching editable textbook"""
  data: _EditableTextbookGetData

class EditableTextbookGetResponse(_APIResponse):
  """API Response for fetching editable textbook"""
  data: _EditableTextbookGetData








# EditableTextbook LIST
class EditableTextbookListRequest(_APIRequest):
  """API Request for textbook listing"""
  user_id: str
  page = 1

@dataclass
class EditableTextbookListReply(_APIReply):
  """API Reply for listing textbooks"""
  data: list[_EditableTextbookGetData]

class EditableTextbookListResponse(_APIResponse):
  """API Response for listing textbooks"""
  data: list[_EditableTextbookGetData]








# EditableTextbook ALL
class EditableTextbookAllRequest(_APIRequest):
  """API Request for textbook listing"""
  user_id: str

@dataclass
class EditableTextbookAllReply(_APIReply):
  """API Reply for listing textbooks"""
  data: list[_EditableTextbookGetData]

class EditableTextbookAllResponse(_APIResponse):
  """API Response for listing textbooks"""
  data: list[_EditableTextbookGetData]








# EditableTextbook CREATE
@dataclass
class _EditableTextbookCreateData(_APIBase):
  editabletextbook_id: str

class EditableTextbookCreateRequest(_APIRequest):
  """API Request for creating a new editable textbook"""
  textbook_id: str

@dataclass
class EditableTextbookCreateReply(_APIReply):
  """API Reply for creating a new editable textbook"""
  data: _EditableTextbookCreateData

class EditableTextbookCreateResponse(_APIResponse):
  """API Response for creating a new editable textbook"""
  data: _EditableTextbookCreateData








# EditableTextbook EDIT
class EditableTextbookEditRequest(_APIRequest):
  """API Request for editing editable textbook"""
  editabletextbook_id: str
  files: _Files

EditableTextbookEditReply = GenericReply
EditableTextbookEditResponse = GenericResponse








# EditableTextbook DELETE
class EditableTextbookDeleteRequest(_APIRequest):
  """API Request for deleting editable textbook"""
  editabletextbook_id: str

EditableTextbookDeleteReply = GenericReply
EditableTextbookDeleteResponse = GenericResponse








# Image GET
@dataclass
class _ImageGetData(_APIBase):
  uri: str
  image_id: str

class ImageGetRequest(_APIRequest):
  """API Request for image fetching"""
  files: _Files
  image_id: str

@dataclass
class ImageGetReply(_APIReply):
  """API Reply for fetching image"""
  data: _ImageGetData

class ImageGetResponse(_APIResponse):
  """API Response for fetching image"""
  data: _ImageGetData








# Image CREATE
@dataclass
class _ImageCreateData(_APIBase):
  image_id: str
  uri: str

class ImageCreateRequest(_APIRequest):
  """API Request for image creation"""
  files       : _Files
  user_id     : Optional[str]
  textbook_id : Optional[str]
  classroom_id: Optional[str]

@dataclass
class ImageCreateReply(_APIReply):
  """API Reply for creating a new image"""
  data: _ImageCreateData

class ImageCreateResponse(_APIResponse):
  """API Response for creating a new image"""
  data: _ImageCreateData








# Image DELETE
class ImageDeleteRequest(_APIRequest):
  """API Request for image deletion"""
  image_id: str

ImageDeleteReply = GenericReply
ImageDeleteResponse = GenericResponse








# Sale LIST
class SaleListRequest(_APIRequest):
  """API Request for sale listing"""
  criteria: Literal['and', 'or']
  query = ''
  page = 1
  priceLower = 0.0
  priceUpper = float('inf')
  createdLower = 0.0
  createdUpper = float('inf')

@dataclass
class SaleListReply(_APIReply):
  """API Reply for listing sales"""
  data: list['_SaleGetData']








# Sale GET
@dataclass
class _SaleGetData(_APIBase):
  type        : Literal['OneTime', 'Subscription']
  sale_id     : str
  user_id     : str
  discount_id : Optional[str]
  textbook_ids: list[str]
  paid        : bool
  paid_at     : Optional[float]
  total_cost  : float

class SaleGetRequest(_APIRequest):
  """API Request for sale fetching"""
  sale_id: str

@dataclass
class SaleGetReply(_APIReply):
  """API Reply for sale fetching image"""
  data: _SaleGetData

class SaleaGetResponse(_APIResponse):
  """API Response for sale fetching image"""
  data: _SaleGetData








# Submission GET
@dataclass
class _SubmissionGetData(_APIBase):
  submission_id: str
  student_id   : str
  assignment_id: str
  comments     : list[str]
  snippet      : str
  created_at   : float
  updated_at   : float

class SubmissionGetRequest(_APIRequest):
  """API Request for fetching submissions"""
  submission_id: str

@dataclass
class SubmissionGetReply(_APIReply):
  """API Reply for fetching submissions"""
  data: _SubmissionGetData

class SubmissionGetResponse(_APIResponse):
  """API Response for fetching submissions"""
  data: _SubmissionGetData








# Submission CREATE
@dataclass
class _SubmissionCreateData(_APIBase):
  submission_id: str
  snippet_id: str

class SubmissionCreateRequest(_APIRequest):
  """API Request for creating submission"""
  files              : _Files
  student_id         : str
  assignment_id      : str
  editabletextbook_id: str

@dataclass
class SubmissionCreateReply(_APIReply):
  """API Reply for creating submission"""
  data: _SubmissionCreateData

class SubmissionCreateResponse(_APIResponse):
  """API Response for creating submission"""
  data: _SubmissionCreateData
  
  
  
  
  
  
  
  
# Submission DELETE
class SubmissionDeleteRequest(_APIRequest):
  """API Request for deleting submission"""
  submission_id: str

SubmissionDeleteReply = GenericReply
SubmissionDeleteResponse = GenericResponse








# SubmissionSnipet GET
@dataclass
class _SubmissionSnippetGetData(_APIBase):
  id           : str
  student_id   : str
  submission_id: str
  uri          : str
  status       : str
  created_at   : float

class SubmissionSnippetGetRequest(_APIRequest):
  """API Request for submission snippet fetching"""
  submissionSnippet_id: str

@dataclass
class SubmissionSnippetGetReply(_APIReply):
  """API Reply for fetching submission snippet"""
  data: _SubmissionSnippetGetData

class SubmissionSnippetGetResponse(_APIResponse):
  """API Response for fetching submission snippet"""
  data: _SubmissionSnippetGetData








# User LIST
class UserListRequest(_APIRequest):
  """API Request for fetching user list"""
  criteria: Literal['and', 'or']
  query = ''
  page = 1
  createdLower = 0.0
  createdUpper = float('inf')

@dataclass
class UserListReply(_APIReply):
  """API Reply for fetching user list"""
  data: list['_UserGetData']









# User GET
@dataclass
class _UserGetData(_APIBase):
  user_id      : str
  email        : str
  status       : str
  username     : str
  privilege    : str
  profile_image: Optional[str]
  created_at   : float
  last_login   : float

class UserGetRequest(_APIRequest):
  """API Request for fetching user"""
  user_id: str

@dataclass
class UserGetReply(_APIReply):
  """API Reply for fetching user"""
  data: _UserGetData

class UserGetResponse(_APIResponse):
  """API Response for fetching user"""
  data: _UserGetData








# User Edit
class UserEditRequest(_APIRequest):
  """API Request for editing user"""
  user_id  : str = ''
  email    : str = ''
  status   : str = ''
  username : str = ''
  password : str = ''
  privilege: str = ''

UserEditReply = GenericReply
UserEditResponse = GenericResponse








# User DELETE
class UserDeleteRequest(_APIRequest):
  """API Request for deleting user"""
  user_id: str

UserDeleteReply = GenericReply
UserDeleteResponse = GenericResponse








# Admin Graph GET
class AdminGraphGetRequest(_APIRequest):
  graphFor: Literal['User', 'Textbook', 'Revenue']








# Admin GET
class AdminGetRequest(_APIRequest):
  requestFor: Literal['User', 'Textbook', 'Sale']
  criteria: Literal['and', 'or']
  query = ''
  page = 1
  priceLower = 0.0
  priceUpper = float('inf')
  createdLower = 0.0
  createdUpper = float('inf')

@dataclass
class AdminGetReply(_APIReply):
  data: list[_UserGetData | _SaleGetData | _TextbookGetData]
