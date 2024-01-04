"""
Auth Provider
"""

from urllib import parse
from functools import wraps
from typing import Callable, Any, Concatenate, ParamSpec, TypeVar, overload

from src.database.user import UserModel
from src.utils.http import HTTPStatusCode
from werkzeug.exceptions import Unauthorized

from werkzeug.wrappers import Response as _WResponse
from flask import request, redirect, Response as _FResponse
from flask_jwt_extended import (
  get_current_user,
  verify_jwt_in_request
)




P = ParamSpec('P')
T = TypeVar('T')

def verify_jwt(
  optional: bool = False,
  fresh: bool = False,
  refresh: bool = False,
  locations: Any = None,
  verify_type: bool = True,
  skip_revocation_check: bool = False
) -> bool:
  """
  Checks for and verifies JWT in cookies/header
  """
  try:
    if verify_jwt_in_request(
      optional = optional,
      fresh = fresh,
      refresh = refresh,
      locations = locations,
      verify_type = verify_type,
      skip_revocation_check = skip_revocation_check
    ):
      return True
    return False
  except Exception:
    return False




RouteResponse = _FResponse | _WResponse | tuple[dict[str, Any], int] | dict[str, Any] | str | tuple[str, int] | tuple[_FResponse, int] | tuple[_WResponse, int]
NoParamReturn = Callable[P, RouteResponse]
FullParamReturn = Callable[P, RouteResponse]


# For User-required annotation
UserRouteEndpoint = Callable[Concatenate[UserModel, P], RouteResponse]
UserWithParamReturn = Callable[[UserRouteEndpoint[P]], NoParamReturn[P]]
UserWrappedReturn = NoParamReturn[P] | UserWithParamReturn[P] | FullParamReturn[P]

# For user-optional annotation
OptionalRouteEndpoint = Callable[Concatenate[UserModel | None, P], RouteResponse]
OptionalWithParamReturn = Callable[[OptionalRouteEndpoint[P]], NoParamReturn[P]]
OptionalWrappedReturn = NoParamReturn[P] | OptionalWithParamReturn[P] | FullParamReturn[P]

# For user-anonymous annotation
AnonRouteEndpoint = Callable[P, RouteResponse]
AnonWithParamReturn = Callable[[AnonRouteEndpoint[P]], NoParamReturn[P]]
AnonWrappedReturn = NoParamReturn[P] | AnonWithParamReturn[P] | FullParamReturn[P]








@overload
def require_admin(__function: UserRouteEndpoint[P]) -> NoParamReturn[P]:
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

@overload
def require_admin(
  *,
  verification_redirect: str = '/verify?callbackURI=%s',
  fresh_access_token: bool = False,
  refresh_token_only: bool = False
) -> UserWithParamReturn[P]:
  """
  Enforces Admin-Only JWT authentication for routes

  Parameters
  ----------
  `verification_redirect: str`, optional (defaults to '/verify?callbackURI=%s')
    Email verification endpoint
  
  `fresh_access_token: bool`, optional (defaults to False)
    Require access token to be new, else redirects to login
  
  `refresh_token_only: bool`, optional (defaults to False)
    Only allow refresh tokens to access routes, else redirects to unauthorized

  Returns
  -------
  `decorator wrapper: (...) -> ( (...) -> ... )`

  Use Case
  --------
  >>> @app.route('/')
  >>> @require_admin()
  >>> def myRoute(user: UserModel): ...
  OR
  >>> @app.route('/')
  >>> @require_admin(verification_redirect = '/custom-endpoint')
  >>> def myRoute(user: UserModel): ...
  """

@overload
def require_admin(
  __function: UserRouteEndpoint[P],
  *,
  verification_redirect: str = '/verify?callbackURI=%s',
  fresh_access_token: bool = False,
  refresh_token_only: bool = False
) -> FullParamReturn[P]: ...

def require_admin(
  __function: UserRouteEndpoint[P] | None = None,
  *,
  verification_redirect: str = '/verify?callbackURI=%s',
  fresh_access_token: bool = False,
  refresh_token_only: bool = False
) -> UserWrappedReturn[P]:
  if not callable(__function):
    def early(__function: UserRouteEndpoint[P]) -> FullParamReturn[P]:
      return require_admin(
        __function,
        verification_redirect = verification_redirect
      )
    return early
  
  @wraps(__function)
  def wrapper(*args: P.args, **kwargs: P.kwargs) -> RouteResponse:
    verify_jwt_in_request(fresh = fresh_access_token, refresh = refresh_token_only)
    user: UserModel = get_current_user()

    if not user.email_verified:
      return redirect(
        verification_redirect % parse.quote_plus(request.path),
        code = HTTPStatusCode.SEE_OTHER
      )

    if user.privilege != 'Admin':
      raise Unauthorized()

    return __function(user, *args, **kwargs)
  return wrapper








@overload
def require_login(__function: UserRouteEndpoint[P]) -> NoParamReturn[P]:
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

@overload
def require_login(
  *,
  verification_redirect: str = '/verify?callbackURI=%s',
  ignore_verification: bool = True,
  fresh_access_token: bool = False,
  refresh_token_only: bool = False
) -> UserWithParamReturn[P]:
  """
  Decorator for enforcing login-only routes

  Parameters
  ----------
  `verification_redirect: str`, optional (defaults to '/verify?callbackURI=%s')
    Email verification endpoint
  
  `ignore_verification: bool`, optional (defaults to False)
    Whether to ignore unverified emails and allow access
  
  `fresh_access_token: bool`, optional (defaults to False)
    Require access token to be new, else redirects to login
  
  `refresh_token_only: bool`, optional (defaults to False)
    Only allow refresh tokens to access routes, else redirects to unauthorized

  Returns
  -------
  `decorator wrapper: (...) -> ( (...) -> ... )`

  Use Case
  --------
  >>> @app.route('/')
  >>> @require_login()
  >>> def myRoute(user: UserModel): ...
  OR
  >>> @app.route('/')
  >>> @require_login(verification_redirect = '/custom-endpoint')
  >>> def myRoute(user: UserModel): ...
  """

@overload
def require_login(
  __function: UserRouteEndpoint[P],
  *,
  verification_redirect: str = '/verify?callbackURI=%s',
  ignore_verification: bool = False,
  fresh_access_token: bool = False,
  refresh_token_only: bool = False
) -> FullParamReturn[P]: ...

def require_login(
  __function: UserRouteEndpoint[P] | None = None,
  *,
  verification_redirect: str = '/verify?callbackURI=%s',
  ignore_verification: bool = False,
  fresh_access_token: bool = False,
  refresh_token_only: bool = False
) -> UserWrappedReturn[P]:
  if not callable(__function):
    def early(__function: UserRouteEndpoint[P]) -> FullParamReturn[P]:
      return require_login(
        __function,
        verification_redirect = verification_redirect,
        ignore_verification = ignore_verification
      )
    return early
  
  @wraps(__function)
  def wrapper(*args: P.args, **kwargs: P.kwargs) -> RouteResponse:
    verify_jwt_in_request(fresh = fresh_access_token, refresh = refresh_token_only)
    user: UserModel = get_current_user()

    if not user.email_verified:
      return redirect(
        verification_redirect % parse.quote_plus(request.path),
        code = HTTPStatusCode.SEE_OTHER
      )

    return __function(get_current_user(), *args, **kwargs)
  return wrapper








@overload
def optional_login(__function: OptionalRouteEndpoint[P]) -> NoParamReturn[P]:
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

@overload
def optional_login(
  *,
  verification_redirect: str = '/verify?callbackURI=%s',
  ignore_verification: bool = True
) -> OptionalWithParamReturn[P]:
  """
  Decorator for enforcing login-only routes

  Parameters
  ----------
  `verification_redirect: str`, optional (defaults to '/verify?callbackURI=%s')
    Email verification endpoint
  
  `ignore_verification: bool`, optional (defaults to True)
    Whether to ignore unverified emails and allow access

  Returns
  -------
  `decorator wrapper: (...) -> ( (...) -> ... )`

  Use Case
  --------
  >>> @app.route('/')
  >>> @require_login()
  >>> def myRoute(user: UserModel): ...
  OR
  >>> @app.route('/')
  >>> @require_login(verification_redirect = '/custom-endpoint')
  >>> def myRoute(user: UserModel | None): ...
  """

@overload
def optional_login(
  __function: OptionalRouteEndpoint[P],
  *,
  verification_redirect: str = '/verify?callbackURI=%s',
  ignore_verification: bool = True
) -> FullParamReturn[P]: ...

def optional_login(
  __function: OptionalRouteEndpoint[P] | None = None,
  *,
  verification_redirect: str = '/verify?callbackURI=%s',
  ignore_verification: bool = True
) -> OptionalWrappedReturn[P]:
  if not callable(__function):
    def early(__function: OptionalRouteEndpoint[P]) -> FullParamReturn[P]:
      return optional_login(
        __function,
        verification_redirect = verification_redirect,
        ignore_verification = ignore_verification
      )
    return early
  
  @wraps(__function)
  def wrapper(*args: P.args, **kwargs: P.kwargs) -> RouteResponse:
    user: UserModel | None = get_current_user() if verify_jwt() else None

    if user and not ignore_verification and not user.email_verified:
      return redirect(
        verification_redirect % parse.quote_plus(request.path),
        code = HTTPStatusCode.SEE_OTHER
      )

    return __function(
      user,
      *args,
      **kwargs
    )
  return wrapper








@overload
def anonymous_required(__function: AnonRouteEndpoint[P]) -> NoParamReturn[P]:
  """
  Decorator for enforcing anonymous-optional routes

  Returns
  -------
  `decorator: (...) -> ...`

  Use Case
  --------
  >>> @app.route('/')
  >>> @anonymous_required
  >>> def myRoute(): ...
  """

@overload
def anonymous_required(
  *,
  admin_override: bool = True,
  loggedin_redirect: str = '/'
) -> AnonWithParamReturn[P]:
  """
  Decorator for enforcing anonymous-only routes

  Parameters
  ----------
  `admin_override: bool`, optional (defaults to True)
    Whether to allow admins to access the route

  `loggedin_redirect: str`, optional (defaults to '/')
    Redirect endpoint if logged in

  Returns
  -------
  `decorator wrapper: (...) -> ( (...) -> ... )`

  Use Case
  --------
  >>> @app.route('/')
  >>> @anonymous_required()
  >>> def myRoute(): ...
  OR
  >>> @app.route('/')
  >>> @require_login(verification_redirect = '/custom-endpoint')
  >>> def myRoute(user: UserModel | None): ...
  """

@overload
def anonymous_required(
  __function: AnonRouteEndpoint[P],
  *,
  admin_override: bool = True,
  loggedin_redirect: str = '/'
) -> FullParamReturn[P]: ...

def anonymous_required(
  __function: AnonRouteEndpoint[P] | None = None,
  *,
  admin_override: bool = True,
  loggedin_redirect: str = '/'
) -> AnonWrappedReturn[P]:
  if not callable(__function):
    def early(__function: AnonRouteEndpoint[P]) -> FullParamReturn[P]:
      return anonymous_required(
        __function,
        admin_override = admin_override,
        loggedin_redirect = loggedin_redirect
      )
    return early
  
  @wraps(__function)
  def wrapper(*args: P.args, **kwargs: P.kwargs) -> RouteResponse:
    user: UserModel | None = get_current_user() if verify_jwt() else None
    if (user and not admin_override) or (user and admin_override and (user.privilege != 'Admin')):
      return redirect(
        loggedin_redirect % parse.quote_plus(request.path),
        code = HTTPStatusCode.SEE_OTHER
      )

    return __function(*args, **kwargs)
  return wrapper
