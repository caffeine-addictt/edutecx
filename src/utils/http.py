"""
HTTP Utils
"""

import re
from typing import Any, Union

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

  OK = 200
  CREATED = 201

  PERMANENT_REDIRECT = 307
  TEMPORARY_REDIRECT = 308

  BAD_REQUEST = 400
  UNAUTHORIZED = 401
  FORBIDDEN = 403
  ERROR_NOT_FOUND = 404
  METHOD_NOT_ALLOWED = 405
  UNSUPPORTED_MEDIA_FORMAT = 415
  TOO_MANY_REQUESTS = 429

  INTERNAL_SERVER_ERROR = 500


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