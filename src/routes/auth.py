"""
Managing user login/logout

! Note to self: redirects from POST -> GET needs code 302/303 to change request body as 307/308 preserves the original body
"""

from src import db, jwt
from src.database import UserModel, JWTBlocklistModel

from src.utils.ext import utc_time
from src.utils.http import HTTPStatusCode
from src.utils.api import TokenRefreshResponse, LoginResponse
from src.utils.forms import LoginForm, LogoutForm, RegisterForm
from src.service.auth_provider import optional_jwt
from src.utils.api import (
  GenericResponse
)

import requests
from urllib import parse
from flask import (
  flash,
  request,
  redirect,
  make_response,
  render_template,
  current_app as app,
)
from flask_jwt_extended import (
  decode_token,
  jwt_required,
  get_jwt_identity,

  unset_jwt_cookies,
  unset_access_cookies,
  unset_refresh_cookies,

  set_access_cookies,
  set_refresh_cookies,
)


# Config
@jwt.user_identity_loader
def user_identity_loader(user: 'UserModel'):
  return user.id

@jwt.user_lookup_loader
def user_lookup_loader(jwtHeader, jwtPayload):
  identity = jwtPayload["sub"]
  return UserModel.query.filter(UserModel.id == identity).first()

@jwt.user_lookup_error_loader
def user_lookup_error_loader(jwtHeader, jwtPayload):
  reloginResponse = make_response(redirect(
    request.path,
    HTTPStatusCode.SEE_OTHER
  ))

  unset_access_cookies(reloginResponse)
  unset_refresh_cookies(reloginResponse)
  unset_jwt_cookies(reloginResponse)
  return reloginResponse, HTTPStatusCode.SEE_OTHER

@app.after_request
def refresh_token(response):
  if request.method != 'GET' or request.path.startswith('/api/') or request.path.startswith('/static'):
    return response
  
  try:
    access_token = request.cookies.get('access_token_cookie')
    refresh_token = request.cookies.get('refresh_token_cookie')

    if not access_token or not refresh_token:
      raise Exception('Not logged in')
    
    access_decoded = decode_token(access_token, allow_expired = True)
    refresh_decoded = decode_token(refresh_token)

    if refresh_decoded['exp'] <= utc_time.get().timestamp():
      raise Exception('Refresh token expired')
    
    if utc_time.skip('1h').timestamp() < access_decoded['exp']:
      raise Exception('Access token not close to being expired')
    
    # Try to refresh access token
    refresh_response = requests.post(
      f'{request.url_root}api/v1/refresh',
      headers = {'Authorization': f'Bearer {refresh_token}'}
    )
    data = TokenRefreshResponse(refresh_response)

    if data.status != HTTPStatusCode.OK:
      raise Exception(f'{data.message}')
    
    set_access_cookies(response, str(data.data.get('access_token')))
    app.logger.info('Successfully Auto-Refreshed expiring access token')

    return response
  except Exception as e:
    app.logger.info(f'Failed to auto-refresh expiring access token: {e}')
    return response


# Error handling
@jwt.unauthorized_loader
def unauthorized_loader(msg: str):
  if request.path.startswith('/api/'):
    return {
      'message': msg,
      'status': HTTPStatusCode.UNAUTHORIZED
    }, HTTPStatusCode.UNAUTHORIZED
  else:
    return redirect(
      f'/login?callbackURI={parse.quote(request.path)}',
      code = HTTPStatusCode.SEE_OTHER
    ), HTTPStatusCode.SEE_OTHER

@jwt.invalid_token_loader
def invalid_token_loader(msg: str):
  if request.path.startswith('/api/'):
    return {
      'message': msg,
      'status': HTTPStatusCode.UNPROCESSABLE_ENTITY
    }, HTTPStatusCode.UNPROCESSABLE_ENTITY
  else:
    response = make_response(redirect(
      f'/login?callbackURI={parse.quote(request.path)}',
      code = HTTPStatusCode.SEE_OTHER
    ))
    return response, HTTPStatusCode.SEE_OTHER

@jwt.expired_token_loader
def expired_token_loader(jwtHeader, jwtPayload):
  if request.path.startswith('/api/'):
    return {
      'message': 'Token has expired',
      'status': HTTPStatusCode.UNAUTHORIZED
    }, HTTPStatusCode.UNAUTHORIZED
  else:
    try:
      # Refresh the token if refresh token is valid and they previously logged in with "remember me" checked

      accesss_token = request.cookies.get('access_token_cookie')
      refresh_token = request.cookies.get('refresh_token_cookie')

      if not accesss_token or not refresh_token:
        raise Exception('No cookies')
      
      decoded_refresh = decode_token(refresh_token)
      if not decoded_refresh.get('remember_me'):
        raise Exception('Did not log in with remember me checked!')
      
      response = requests.post(
        f'{request.root_url}api/v1/refresh',
        headers = {'Authorization': f'Bearer {refresh_token}'}
      )
      data = TokenRefreshResponse(response)

      if (data.status == HTTPStatusCode.OK) and not data.data.get('access_token'):
        raise Exception('Unable to refresh')
      
      successfulRefresh = make_response(
        redirect(request.path, code = HTTPStatusCode.FOUND),
        HTTPStatusCode.FOUND
      )

      app.logger.error('Auto-Refreshed expired access token with refresh token')
      set_access_cookies(successfulRefresh, str(data.data.get('access_token')))
      return successfulRefresh, HTTPStatusCode.FOUND

    except Exception as e:
      app.logger.error(f'Failed to Auto-Refresh expired access token with refresh token: {e}')
    
    response = make_response(redirect(
      f'/login?callbackURI={parse.quote(request.path)}',
      code = HTTPStatusCode.SEE_OTHER
    ))
    unset_refresh_cookies(response)
    unset_access_cookies(response)
    return response, HTTPStatusCode.SEE_OTHER
  
@jwt.token_in_blocklist_loader
def token_in_blocklist_loader(jwtHeader, jwtPayload) -> bool:
  jti = jwtPayload['jti']
  return JWTBlocklistModel.query.get(jti) is not None




# Routing
@app.route('/login', methods = ['Get', 'POST'])
def login():
  # Auto redirect to callbackURI
  if optional_jwt():
    flash(f'Welcome back!', 'success')
    callbackURI: str = parse.quote(request.args.get('callbackURI', '/home'))

    return redirect(callbackURI, code = HTTPStatusCode.PERMANENT_REDIRECT)
  
  form = LoginForm(request.form)
  validatedForm = form.validate_on_submit()

  if request.method == 'POST' and validatedForm:
    response = requests.post(
      f'{request.url_root}api/v1/login',
      headers = {'Content-Type': 'application/json'},
      json = {
        'email': form.email.data,
        'password': form.password.data,
        'remember_me': form.remember_me.data,
      }
    )
    body = LoginResponse(response)
    
    if response.status_code != HTTPStatusCode.OK:
      flash(body.message, 'danger')
    else:
      # Handle Login and cookie
      callbackURI: str = parse.quote(request.args.get('callbackURI', '/home'))
      successfulLogin = make_response(
        redirect(callbackURI, code = HTTPStatusCode.SEE_OTHER),
        HTTPStatusCode.SEE_OTHER
      )

      set_access_cookies(successfulLogin, body.data.access_token)
      set_refresh_cookies(successfulLogin, body.data.access_token)
      flash('Welcome back!', 'success')

      return successfulLogin
    
  elif request.method == 'POST':
    flash('Failed to log in', 'danger')
    
  return render_template('(auth)/login.html', form = form, url = request.host_url)


@app.route('/logout', methods = ['GET', 'POST'])
def logout():
  successfulLogout = make_response(
    redirect('/', code = HTTPStatusCode.SEE_OTHER),
    HTTPStatusCode.SEE_OTHER
  )

  # Not logged in
  if (
    not request.cookies.get('access_token_cookie')
    and not request.cookies.get('refresh_token_cookie')
  ):
    return successfulLogout, HTTPStatusCode.SEE_OTHER
  
  # Logged in
  if request.method == 'POST':
    try:
      accesss_token = request.cookies.get('access_token_cookie')
      refresh_token = request.cookies.get('refresh_token_cookie')

      if not accesss_token or not refresh_token:
        raise Exception('No cookies')
      
      decoded_access = decode_token(accesss_token)
      decoded_refresh = decode_token(refresh_token)

      if decoded_access.get('jti'): db.session.add(JWTBlocklistModel(str(decoded_access.get('jti')), 'access'))
      if decoded_refresh.get('jti'): db.session.add(JWTBlocklistModel(str(decoded_refresh.get('jti')), 'refresh'))
      db.session.commit()

      flash('Successfully logged out', 'info')

    except Exception as e:
      app.logger.exception(f'Failed to logout: {e}')
    
    finally:
      unset_refresh_cookies(successfulLogout)
      unset_access_cookies(successfulLogout)
      unset_jwt_cookies(successfulLogout)

      app.logger.warning('Unset cookies on logout')
      return successfulLogout, HTTPStatusCode.SEE_OTHER
    
  return render_template('(auth)/logout.html', form = LogoutForm())


@app.route('/register', methods = ['GET', 'POST'])
@jwt_required(optional = True)
def register():
  # Redirect to callbackURI or home if logged in
  if get_jwt_identity():
    callbackURI: str = parse.quote(request.args.get('callbackURI', '/home'))
    return redirect(callbackURI, code = HTTPStatusCode.SEE_OTHER), HTTPStatusCode.SEE_OTHER
  
  form = RegisterForm(request.form)
  if request.method == 'POST' and form.validate_on_submit():
    response = requests.post(
      f'{request.url_root}api/v1/register',
      headers = {'Content-Type': 'application/json'},
      json = {
        'email': form.email.data,
        'username': form.username.data,
        'password': form.password.data
      }
    )
    body = GenericResponse(response)

    if response.status_code != HTTPStatusCode.OK:
      flash(body.message, 'danger')
    else:
      flash(body.message, 'success')

      callbackURI: str = parse.quote(request.args.get('callbackURI', '/login'))
      return redirect(callbackURI, code = HTTPStatusCode.FOUND), HTTPStatusCode.FOUND
  elif request.method == 'POST':
    flash(f'Failed to create user account: {form.errors}', 'danger')

  return render_template('(auth)/register.html', form = form)
