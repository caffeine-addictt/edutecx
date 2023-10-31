"""
Extensions for flask_login
"""

from urllib import parse
from functools import wraps
from src.utils.http import HTTPStatusCode

from typing import Callable, Any
from flask import (
  g,
  abort,
  request,
  redirect,
  Response
)


def admin_required(login_uri: str = '/login') -> Callable[..., Callable[..., Any]]:
  """
  Decorator for enforcing admin-only routes

    
  Parameters
  ----------
  `login_uri : str`, optional (default is '/')
    The URI to redirect to when the user is not logged in

    
  Returns
  -------
  `function: (...) -> Any`
    Returns the decorator


  Raises
  ------
  `401 UNAUTHORIZED Error`


  Examples
  --------
  ```py
    @app.route('/my-route')
    @admin_required(login_uri = '/login')
    def my_route():
      return render_template(...)
  ```
  """
  def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:

      # Not logged in, redirect to login_uri with callbackURI
      if not g.user.is_authenticated:
        current_path = parse.quote(request.path)
        return redirect(f'{login_uri}?callbackURI={current_path}', code = HTTPStatusCode.TEMPORARY_REDIRECT)
      
      if g.user.privilege != 'Admin':
        return abort(HTTPStatusCode.UNAUTHORIZED)
      
      return func(*args, **kwargs)

    return wrapper
  return decorator


def loggedin_required(login_uri: str = '/login') -> Callable[..., Callable[..., Any]]:
  """
  Decorator for enforcing logged in -only routes

    
  Parameters
  ----------
  `login_uri : str`, optional (default is '/')
    The URI to redirect to when the user is not logged in

    
  Returns
  -------
  `function: (...) -> Any`
    Returns the decorator


  Examples
  --------
  ```py
    @app.route('/my-route')
    @loggedin_required(login_uri = '/login')
    def my_route():
      return render_template(...)
  ```
  """
  def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:

      # Not logged in, redirect to login_uri with callbackURI
      if not g.user.is_authenticated:
        current_path = parse.quote(request.path)
        return redirect(f'{login_uri}?callbackURI={current_path}', code = HTTPStatusCode.TEMPORARY_REDIRECT)
      
      return func(*args, **kwargs)

    return wrapper
  return decorator


def not_loggedin_required(logout_uri: str = '/logout') -> Callable[..., Callable[..., Any]]:
  """
  Decorator for enforcing not logged in routes

    
  Parameters
  ----------
  `logout_uri : str`, optional (default is '/')
    The URI to redirect to when the user is already logged in

    
  Returns
  -------
  `function: (...) -> Any`
    Returns the decorator


  Examples
  --------
  ```py
    @app.route('/my-route')
    @not_loggedin_required(logout_uri = '/logout')
    def my_route():
      return render_template(...)
  ```
  """
  def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
      if g.user.is_authenticated:
        return redirect(logout_uri, code = HTTPStatusCode.PERMANENT_REDIRECT)
      
      return func(*args, **kwargs)

    return wrapper
  return decorator
