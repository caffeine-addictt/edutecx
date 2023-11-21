"""
Auth Provider
"""

from functools import wraps
from typing import Optional, Callable, Any, Literal, Concatenate

from src.database.user import PrivilegeTypes, UserModel
from src.utils.http import HTTPStatusCode
from werkzeug.exceptions import HTTPException, Unauthorized

from urllib.parse import quote
from flask import redirect, request
from flask_jwt_extended import (
  get_current_user,
  verify_jwt_in_request
)


def optional_jwt() -> bool:
  try:
    if verify_jwt_in_request():
      return True
    return False
  except Exception:
    return False


def require_admin(func: Callable[Concatenate[UserModel, ...], Any]) -> Callable[..., Any]:
  """
  Enforces Admin-Only JWT authentication for routes

  Returns
  -------
  `decorator: (...) -> ...`
  """
  @wraps(func)
  def wrapper(*args: Any, **kwargs: Any) -> Any:
    verify_jwt_in_request()
    user: UserModel = get_current_user()

    match (user.privilege != 'Admin') and request.method:
      case 'POST':
        return {
          'message': 'Unauthorized',
          'status': HTTPStatusCode.UNAUTHORIZED
        }, HTTPStatusCode.UNAUTHORIZED
      
      case 'GET':
        raise Unauthorized()
      
      case _:
        return func(user, *args, **kwargs)
  return wrapper




def require_login(func: Callable[Concatenate[UserModel, ...], Any]) -> Callable[..., Any]:
  """
  Decorator for enforcing loggedin only routes

  Returns
  -------
  `decorator: (...) -> ...`
  """
  @wraps(func)
  def wrapper(*args, **kwargs):
    verify_jwt_in_request()
    return func(get_current_user(), *args, **kwargs)
  return wrapper
