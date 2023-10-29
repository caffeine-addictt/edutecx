"""
HTTP Utils
"""

from typing import Any, Union

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