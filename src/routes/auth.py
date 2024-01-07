"""
Managing user login/logout

! Note to self: redirects from POST -> GET needs code 302/303 to change request body as 307/308 preserves the original body
"""

from src import db, jwt
from src.database import UserModel, JWTBlocklistModel

from src.utils.ext import utc_time
from src.utils.http import HTTPStatusCode
from src.utils.api import TokenRefreshResponse, LoginResponse
from src.utils.forms import LoginForm, RegisterForm
from src.service.auth_provider import optional_login, require_login, anonymous_required
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
      f'/login?callbackURI={parse.quote_plus(request.path)}',
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
      f'/login?callbackURI={parse.quote_plus(request.path)}',
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
      f'/login?callbackURI={parse.quote_plus(request.path)}',
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
@optional_login(ignore_locked = True)
def login(user: UserModel | None):

  # Check for locked account
  if user and user.status == 'Locked':
    return redirect('/logout', code = HTTPStatusCode.SEE_OTHER), HTTPStatusCode.SEE_OTHER

  # Auto redirect to callbackURI
  if user:
    flash(f'Welcome back!', 'success')
    callbackURI: str = parse.unquote_plus(request.args.get('callbackURI', '/home'))

    return redirect(callbackURI, code = HTTPStatusCode.PERMANENT_REDIRECT)
  
  form = LoginForm(request.form)
  if request.method == 'POST' and form.validate_on_submit():
    response = requests.post(
      f'{request.url_root}api/v1/login',
      headers = {'Content-Type': 'application/json'},
      json = {
        'email': form.email.data,
        'password': form.password.data,
        'remember_me': form.remember_me.data,
      }
    )
    
    if response.status_code != HTTPStatusCode.OK:
      flash(response.json().get('message'), 'danger')

    else:
      body = LoginResponse(response)

      # Handle Login and cookie
      callbackURI: str = parse.unquote_plus(request.args.get('callbackURI', '/home'))
      successfulLogin = make_response(
        redirect(callbackURI, code = HTTPStatusCode.SEE_OTHER),
        HTTPStatusCode.SEE_OTHER
      )

      set_access_cookies(successfulLogin, body.data.access_token)
      set_refresh_cookies(successfulLogin, body.data.refresh_token)
      flash('Welcome back!', 'success')

      return successfulLogin
  return render_template('(auth)/login.html', form = form)




@app.route('/logout', methods = ['GET', 'POST'])
@require_login(ignore_locked = True)
def logout(user: UserModel):
  successfulLogout = make_response(
    redirect('/', code = HTTPStatusCode.SEE_OTHER),
    HTTPStatusCode.SEE_OTHER
  )

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

    if user.status == 'Active':
      flash('Successfully logged out', 'info')
    else:
      flash('Your account has been locked, contact us at edutecx@ngjx.org for more information', 'danger')

  except Exception as e:
    app.logger.exception(f'Failed to logout: {e}')

  finally:
    unset_refresh_cookies(successfulLogout)
    unset_access_cookies(successfulLogout)
    unset_jwt_cookies(successfulLogout)

    app.logger.warning('Unset cookies on logout')
    return successfulLogout, HTTPStatusCode.SEE_OTHER




@app.route('/register', methods = ['GET', 'POST'])
@anonymous_required(use_path_callback = True, admin_override = False)
def register():
  form = RegisterForm(request.form)
  if request.method == 'POST' and form.validate_on_submit():
    response = requests.post(
      f'{request.url_root}api/v1/register',
      headers = {'Content-Type': 'application/json'},
      json = {
        'privilege': ['Student', 'Educator'][int(form.privilege.data)],
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

      callbackURI: str = parse.unquote_plus(request.args.get('callbackURI', '/login'))
      return redirect(callbackURI, code = HTTPStatusCode.FOUND), HTTPStatusCode.FOUND

  return render_template('(auth)/register.html', form = form)




@app.route('/verify', methods = ['GET'])
@app.route('/verify/<string:token>', methods = ['GET'])
@require_login(ignore_verification = True)
def verify(user: UserModel, token: str | None = None):
  if user.email_verified:
    flash('Email already verified', 'info')
    callbackURI = parse.unquote_plus(request.args.get('callbackURI', '/home'))
    return redirect(callbackURI, code = HTTPStatusCode.FOUND), HTTPStatusCode.FOUND
  
  if token:
    if not user.token or (user.token.token_type != 'Verification') or (user.token.token != token):
      flash('Invalid token', 'danger')
      newCallbackURI = parse.quote_plus(request.args.get('callbackURI', ''))
      return redirect('/verify?callbackURI=%s' % newCallbackURI, code = HTTPStatusCode.FOUND), HTTPStatusCode.FOUND
    
    if user.token.expires_at < utc_time.get():
      flash('Token expired', 'danger')
      newCallbackURI = parse.quote_plus(request.args.get('callbackURI', ''))
      return redirect('/verify?callbackURI=%s' % newCallbackURI, code = HTTPStatusCode.FOUND), HTTPStatusCode.FOUND
    
    user.email_verified = True
    user.token.delete()
    user.save()

    flash('Email verified', 'success')

    callbackURI = parse.unquote_plus(request.args.get('callbackURI', '/home'))
    return redirect(callbackURI, code = HTTPStatusCode.FOUND), HTTPStatusCode.FOUND

  return render_template('(auth)/verify.html')
