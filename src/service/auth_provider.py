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

def generateURI(defaultURI: str, usePathCallback: bool) -> str:
  """
  Handles logic for interpreting callbackURI

  Parameters
  ----------
  `defaultURI: str`, required
    The default uri

  `usePathCallback: bool`, required
    Whether or not to use path callback
  """
  if usePathCallback:
    redirect_to = request.args.get('callbackURI', defaultURI)
  else:
    redirect_to = defaultURI

  if (defaultURI == redirect_to) and ('%s' in redirect_to):
    redirect_to = redirect_to % parse.quote_plus(request.path)
  else:
    redirect_to = parse.unquote_plus(redirect_to)
    if (a := redirect_to.split('?')) and (len(a) > 1) and ('callbackURI=%s' not in a[1]):
      redirect_to = a[0] + '?' + '&'.join([
        i for i in (a[1].split('&') + [ f'callbackURI={parse.quote_plus(request.path)}' ])
      ])
  
  return redirect_to

def handleLockedRedirect() -> 'RouteResponse':
  if request.path.startswith('/api') or request.method == 'POST':
    return {
      'message': 'Your account has been locked, contact us at edutecx@ngjx.org for more information',
      'status': HTTPStatusCode.UNAUTHORIZED
    }, HTTPStatusCode.UNAUTHORIZED
  
  return redirect(
    f'/logout?callbackURI={parse.quote_plus(request.path)}',
    code = HTTPStatusCode.SEE_OTHER
  ), HTTPStatusCode.SEE_OTHER




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
        verification_redirect = verification_redirect,
        fresh_access_token = fresh_access_token,
        refresh_token_only = refresh_token_only
      )
    return early
  
  @wraps(__function)
  def wrapper(*args: P.args, **kwargs: P.kwargs) -> RouteResponse:
    verify_jwt_in_request(fresh = fresh_access_token, refresh = refresh_token_only)
    user: UserModel = get_current_user()

    # Check for locked account
    if user.status == 'Locked':
      return redirect(
        '/logout?callbackURI=%s' % parse.quote_plus(request.path),
        code = HTTPStatusCode.SEE_OTHER
      ), HTTPStatusCode.SEE_OTHER

    if not user.email_verified:
      return redirect(
        verification_redirect % parse.quote_plus(request.path),
        code = HTTPStatusCode.SEE_OTHER
      ), HTTPStatusCode.SEE_OTHER

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
  ignore_verification: bool = False,
  fresh_access_token: bool = False,
  refresh_token_only: bool = False,
  ignore_locked: bool = False
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
  
  `ignore_locked: bool`, optional (defaults to False)
    Whether to ignore locked accounts, redirects to login which will force logout by default

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
  refresh_token_only: bool = False,
  ignore_locked: bool = False
) -> FullParamReturn[P]: ...

def require_login(
  __function: UserRouteEndpoint[P] | None = None,
  *,
  verification_redirect: str = '/verify?callbackURI=%s',
  ignore_verification: bool = False,
  fresh_access_token: bool = False,
  refresh_token_only: bool = False,
  ignore_locked: bool = False
) -> UserWrappedReturn[P]:
  if not callable(__function):
    def early(__function: UserRouteEndpoint[P]) -> FullParamReturn[P]:
      return require_login(
        __function,
        verification_redirect = verification_redirect,
        ignore_verification = ignore_verification,
        fresh_access_token = fresh_access_token,
        refresh_token_only = refresh_token_only,
        ignore_locked = ignore_locked
      )
    return early
  
  @wraps(__function)
  def wrapper(*args: P.args, **kwargs: P.kwargs) -> RouteResponse:
    verify_jwt_in_request(fresh = fresh_access_token, refresh = refresh_token_only)
    user: UserModel = get_current_user()

    # Check for locked account
    if user.status == 'Locked' and not ignore_locked:
      return handleLockedRedirect()

    if not user.email_verified and not ignore_verification:
      return redirect(
        verification_redirect % parse.quote_plus(request.path),
        code = HTTPStatusCode.SEE_OTHER
      ), HTTPStatusCode.SEE_OTHER

    return __function(user, *args, **kwargs)
  return wrapper








@overload
def require_educator(__function: UserRouteEndpoint[P]) -> NoParamReturn[P]:
  """
  Decorator for enforcing educator-only routes

  Returns
  -------
  `decorator: (...) -> ...`

  Use Case
  --------
  >>> @app.route('/')
  >>> @require_educator
  >>> def myRoute(user: UserModel): ...
  """

@overload
def require_educator(
  *,
  verification_redirect: str = '/verify?callbackURI=%s',
  unauthorized_redirect: str | None = None,
  ignore_verification: bool = False,
  fresh_access_token: bool = False,
  refresh_token_only: bool = False
) -> UserWithParamReturn[P]:
  """
  Decorator for enforcing educator-only routes

  Parameters
  ----------
  `verification_redirect: str`, optional (defaults to '/verify?callbackURI=%s')
    Email verification endpoint
  
  `unauthorized_redirect: str`, optional (defaults to None)
    Endpoint to redirect to if user is not educator, raises 401 UNAUTHORIZED by default
  
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
  >>> @require_educator()
  >>> def myRoute(user: UserModel): ...
  OR
  >>> @app.route('/')
  >>> @require_educator(verification_redirect = '/custom-endpoint')
  >>> def myRoute(user: UserModel): ...
  """

@overload
def require_educator(
  __function: UserRouteEndpoint[P],
  *,
  verification_redirect: str = '/verify?callbackURI=%s',
  unauthorized_redirect: str | None = None,
  ignore_verification: bool = False,
  fresh_access_token: bool = False,
  refresh_token_only: bool = False
) -> FullParamReturn[P]: ...

def require_educator(
  __function: UserRouteEndpoint[P] | None = None,
  *,
  verification_redirect: str = '/verify?callbackURI=%s',
  unauthorized_redirect: str | None = None,
  ignore_verification: bool = False,
  fresh_access_token: bool = False,
  refresh_token_only: bool = False
) -> UserWrappedReturn[P]:
  if not callable(__function):
    def early(__function: UserRouteEndpoint[P]) -> FullParamReturn[P]:
      return require_educator(
        __function,
        verification_redirect = verification_redirect,
        unauthorized_redirect = unauthorized_redirect,
        ignore_verification = ignore_verification,
        fresh_access_token = fresh_access_token,
        refresh_token_only = refresh_token_only
      )
    return early
  
  @wraps(__function)
  def wrapper(*args: P.args, **kwargs: P.kwargs) -> RouteResponse:
    verify_jwt_in_request(fresh = fresh_access_token, refresh = refresh_token_only)
    user: UserModel = get_current_user()

    # Check for locked account
    if user.status == 'Locked' and not ignore_locked:
      return handleLockedRedirect()

    if not user.email_verified and not ignore_verification:
      return redirect(
        verification_redirect % parse.quote_plus(request.path),
        code = HTTPStatusCode.SEE_OTHER
      ), HTTPStatusCode.SEE_OTHER

    return __function(user, *args, **kwargs)
  return wrapper








@overload
def require_educator(__function: UserRouteEndpoint[P]) -> NoParamReturn[P]:
  """
  Decorator for enforcing educator-only routes

  Returns
  -------
  `decorator: (...) -> ...`

  Use Case
  --------
  >>> @app.route('/')
  >>> @require_educator
  >>> def myRoute(user: UserModel): ...
  """

@overload
def require_educator(
  *,
  verification_redirect: str = '/verify?callbackURI=%s',
  unauthorized_redirect: str | None = None,
  ignore_verification: bool = False,
  fresh_access_token: bool = False,
  refresh_token_only: bool = False
) -> UserWithParamReturn[P]:
  """
  Decorator for enforcing educator-only routes

  Parameters
  ----------
  `verification_redirect: str`, optional (defaults to '/verify?callbackURI=%s')
    Email verification endpoint
  
  `unauthorized_redirect: str`, optional (defaults to None)
    Endpoint to redirect to if user is not educator, raises 401 UNAUTHORIZED by default
  
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
  >>> @require_educator()
  >>> def myRoute(user: UserModel): ...
  OR
  >>> @app.route('/')
  >>> @require_educator(verification_redirect = '/custom-endpoint')
  >>> def myRoute(user: UserModel): ...
  """

@overload
def require_educator(
  __function: UserRouteEndpoint[P],
  *,
  verification_redirect: str = '/verify?callbackURI=%s',
  unauthorized_redirect: str | None = None,
  ignore_verification: bool = False,
  fresh_access_token: bool = False,
  refresh_token_only: bool = False
) -> FullParamReturn[P]: ...

def require_educator(
  __function: UserRouteEndpoint[P] | None = None,
  *,
  verification_redirect: str = '/verify?callbackURI=%s',
  unauthorized_redirect: str | None = None,
  ignore_verification: bool = False,
  fresh_access_token: bool = False,
  refresh_token_only: bool = False
) -> UserWrappedReturn[P]:
  if not callable(__function):
    def early(__function: UserRouteEndpoint[P]) -> FullParamReturn[P]:
      return require_educator(
        __function,
        verification_redirect = verification_redirect,
        unauthorized_redirect = unauthorized_redirect,
        ignore_verification = ignore_verification,
        fresh_access_token = fresh_access_token,
        refresh_token_only = refresh_token_only
      )
    return early
  
  @wraps(__function)
  def wrapper(*args: P.args, **kwargs: P.kwargs) -> RouteResponse:
    verify_jwt_in_request(fresh = fresh_access_token, refresh = refresh_token_only)
    user: UserModel = get_current_user()

    if not user.email_verified and not ignore_verification:
      return redirect(
        verification_redirect % parse.quote_plus(request.path),
        code = HTTPStatusCode.SEE_OTHER
      )
    
    if user.privilege not in ['Educator', 'Admin']:
      if unauthorized_redirect:
        return redirect(
          unauthorized_redirect,
          code = HTTPStatusCode.SEE_OTHER
        )
      raise Unauthorized()

    return __function(user, *args, **kwargs)
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
  ignore_verification: bool = True,
  ignore_locked: bool = False
) -> OptionalWithParamReturn[P]:
  """
  Decorator for enforcing login-only routes

  Parameters
  ----------
  `verification_redirect: str`, optional (defaults to '/verify?callbackURI=%s')
    Email verification endpoint
  
  `ignore_verification: bool`, optional (defaults to True)
    Whether to ignore unverified emails and allow access
  
  `ignore_locked: bool`, optional (defaults to False)
    Whether to ignore locked accounts, redirects to login which will force logout by default

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
  ignore_verification: bool = True,
  ignore_locked: bool = False
) -> FullParamReturn[P]: ...

def optional_login(
  __function: OptionalRouteEndpoint[P] | None = None,
  *,
  verification_redirect: str = '/verify?callbackURI=%s',
  ignore_verification: bool = True,
  ignore_locked: bool = False
) -> OptionalWrappedReturn[P]:
  if not callable(__function):
    def early(__function: OptionalRouteEndpoint[P]) -> FullParamReturn[P]:
      return optional_login(
        __function,
        verification_redirect = verification_redirect,
        ignore_verification = ignore_verification,
        ignore_locked = ignore_locked
      )
    return early
  
  @wraps(__function)
  def wrapper(*args: P.args, **kwargs: P.kwargs) -> RouteResponse:
    user: UserModel | None = get_current_user() if verify_jwt() else None

    # Check for locked account
    if user and not ignore_locked and user.status == 'Locked':
      return handleLockedRedirect()

    if user and not ignore_verification and not user.email_verified:
      return redirect(
        verification_redirect % parse.quote_plus(request.path),
        code = HTTPStatusCode.SEE_OTHER
      ), HTTPStatusCode.SEE_OTHER

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
  loggedin_redirect: str = '/',
  use_path_callback: bool = True
) -> AnonWithParamReturn[P]:
  """
  Decorator for enforcing anonymous-only routes

  Parameters
  ----------
  `admin_override: bool`, optional (defaults to True)
    Whether to allow admins to access the route

  `loggedin_redirect: str`, optional (defaults to '/')
    Redirect endpoint if logged in
  
  `use_path_callback: bool`, optional (defaults to True)
    Whether to use the current path callbackURI as a default

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
  loggedin_redirect: str = '/',
  use_path_callback: bool = True
) -> FullParamReturn[P]: ...

def anonymous_required(
  __function: AnonRouteEndpoint[P] | None = None,
  *,
  admin_override: bool = True,
  loggedin_redirect: str = '/',
  use_path_callback: bool = True
) -> AnonWrappedReturn[P]:
  if not callable(__function):
    def early(__function: AnonRouteEndpoint[P]) -> FullParamReturn[P]:
      return anonymous_required(
        __function,
        admin_override = admin_override,
        loggedin_redirect = loggedin_redirect,
        use_path_callback = use_path_callback
      )
    return early
  
  @wraps(__function)
  def wrapper(*args: P.args, **kwargs: P.kwargs) -> RouteResponse:
    user: UserModel | None = get_current_user() if verify_jwt() else None

    # Check for locked account
    if user and user.status == 'Locked':
      return handleLockedRedirect()

    if (user and not admin_override) or (user and admin_override and (user.privilege != 'Admin')):
      return redirect(
        generateURI(loggedin_redirect, use_path_callback),
        code = HTTPStatusCode.SEE_OTHER
      ), HTTPStatusCode.SEE_OTHER

    return __function(*args, **kwargs)
  return wrapper
