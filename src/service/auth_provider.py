"""
Auth Provider
"""

from functools import wraps
from typing import Callable, Any, Concatenate, ParamSpec, TypeVar

from src.database.user import UserModel
from src.utils.http import HTTPStatusCode
from werkzeug.exceptions import Unauthorized

from flask import request
from flask_jwt_extended import (
  get_current_user,
  verify_jwt_in_request
)




P = ParamSpec('P')
T = TypeVar('T')

def optional_jwt() -> bool:
  """
  Checks for and verifies JWT in cookies/header
  """
  try:
    if verify_jwt_in_request():
      return True
    return False
  except Exception:
    return False


def require_admin(func: Callable[Concatenate[UserModel, P], T]) -> Callable[P, T | tuple[dict[str, Any], int]]:
  """
  Enforces Admin-Only JWT authentication for routes

  Returns
  -------
  `decorator: (...) -> ...`

  Use Case
  --------
  >>> @app.route('/')
  >>> @require_admin
  >>> def myRoute(user: UserModel): ...
  """
  @wraps(func)
  def wrapper(*args: P.args, **kwargs: P.kwargs) -> T | tuple[dict[str, Any], int]:
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




def require_login(func: Callable[Concatenate[UserModel, P], T]) -> Callable[P, T | tuple[dict[str, Any], int]]:
  """
  Decorator for enforcing login-only routes

  Returns
  -------
  `decorator: (...) -> ...`

  Use Case
  --------
  >>> @app.route('/')
  >>> @require_login
  >>> def myRoute(user: UserModel): ...
  """
  @wraps(func)
  def wrapper(*args: P.args, **kwargs: P.kwargs) -> T | tuple[dict[str, Any], int]:
    verify_jwt_in_request()
    return func(get_current_user(), *args, **kwargs)
  return wrapper




def optional_login(func: Callable[Concatenate[UserModel | None, P], T]) -> Callable[P, T | tuple[dict[str, Any], int]]:
  """
  Decorator for enforcing login-optional routes

  Returns
  -------
  `decorator: (...) -> ...`

  Use Case
  --------
  >>> @app.route('/')
  >>> @optional_login
  >>> def myRoute(user: UserModel | None): ...
  """
  @wraps(func)
  def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
    return func(
      optional_jwt() and get_current_user() or None,
      *args,
      **kwargs
    )
  return wrapper
