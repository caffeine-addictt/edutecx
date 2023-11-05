"""
HTTP Utils
"""

import re
from typing import Any, Union, TypedDict, Optional


class APIResponse(TypedDict):
  message: str
  status: int
  data: Optional[dict[str, Any] | Any]


class Parser:
  """
  Default Parser to client\n
  Allow Jinja to access values with "dot" syntax

  Examples
  --------
  ```python
  render_template('', data = Parser())
  render_template('', data = Parser( name = 'hi' ))
  ```
  """
  def __init__(self, **kwargs: Any) -> None:
    """
    Parameters
    ----------
    `**kwargs: Any`, optional (defaults to None)
    """
    for i, v in kwargs.items():
      object.__setattr__(self, i, v)


class StatusCodeNotFoundError(Exception):
  """
  HTTP Status Code Not Found Error

  Raised when a status code is not found
  """
  def __init__(self, message: Union[str, None] = None, *args, **kwargs) -> None:
    super().__init__(message, *args, **kwargs)


class HTTPStatusCode:
  """
  Contains HTTP status code mapped to its intended use-case

  `Immutable`\n
  `Uninstantiable`
  """

  # 2XX - recieved, understood and accepted
  OK = 200
  CREATED = 201
  ACCEPTED = 202
  NON_AUTHORITATIVE_INFORMATION = 203
  NO_CONTENT = 204
  RESET_CONTENT = 205
  PARTIAL_CONTENT = 206
  MULTI_STATUS = 207
  ALREADY_REPORTED = 208
  IM_USED = 226

  # 3XX - redirection, more actions needed
  MULTIPLE_CHOICE = 300
  MOVED_PERMANENTLY = 301
  FOUND = 302
  SEE_OTHER = 303
  NOT_MODIFIED = 304
  TEMPORARY_REDIRECT = 307
  PERMANENT_REDIRECT = 308

  # 4XX - client error, bad syntax or cannot be fufiled
  BAD_REQUEST = 400
  UNAUTHORIZED = 401
  PAYMENT_REQUIRED = 402 # Experimental
  FORBIDDEN = 403
  NOT_FOUND = 404
  METHOD_NOT_ALLOWED = 405
  NOT_ACCEPTABLE = 406
  PROXY_AUTHENTICATION_REQUIRED = 407
  REQUEST_TIMEOUT = 408
  CONFLICT = 409
  GONE = 410
  LENGTH_REQUIRED = 411
  PRECONDITION_FAILED = 412
  CONTENT_TOO_LARGE = 413
  URI_TOO_LONG = 414
  UNSUPPORTED_MEDIA_FORMAT = 415
  RANGE_NOT_SATISFIABLE = 416
  EXPECTATION_FAILED = 417
  MISDIRECTED_REQUEST = 421
  UNPROCESSABLE_ENTITY = 422
  LOCKED = 423
  FAILED_DEPENDENCY = 424
  TOO_EARLY = 425
  UPGRADE_REQUIRED = 426
  PRECONDITION_REQUIRED = 428
  TOO_MANY_REQUESTS = 429
  REQUEST_HEADER_TOO_LARGE = 431
  UNAVAILABLE_FOR_LEGAL_REASONS = 451

  # 5XX - server failed to fufil apparent valid request
  INTERNAL_SERVER_ERROR = 500
  NOT_IMPLEMENTED = 501
  BAD_GATEWAY = 502
  SERVICE_UNAVAILABLE = 503
  GATEWAY_TIMEOUT = 504
  HTTP_VERSION_NOT_SUPPORTED = 505
  VARIANT_ALSO_NEGOTIATES = 506
  INSUFFICIENT_STORAGE = 507
  LOOP_DETECTED = 508
  NOT_EXTENDED = 510
  NETWORK_AUTHENTICATION_REQUIRED = 511


  def __init__(self) -> None:
    raise NotImplementedError('This class is not instantiable')
  
  def __setattr__(self, __name: str, __value: Any) -> None:
    raise NotImplementedError('This class is immutable')
  
  @staticmethod
  def getNameFromCode(code: int) -> Union[str, None]:
    """
    Fetch the status name from its code

    
    Parameters
    ----------
    `code: int`, required
      The status code to fetch


    Returns
    -------
    `code: str`
      The name of the status code

    
    Raises
    ------
    `StatusCodeNotFoundError`
      When the code is invalid
    """
    for name, value in HTTPStatusCode.__dict__.items():
      if value == code:
        return name
      
    raise StatusCodeNotFoundError(f'{code} is not a valid status code!')
  

def escape_id(id: str) -> str:
  """
  Escapes a ID parameters generated from uuid4().hex

  Allowed characters are a-z and 0-9

  Parameters
  ----------
  `id: str`, required

  Returns
  `Escaped ID: str`
  """
  regex = re.compile(r'[a-z0-9]')
  return regex.sub('', id)