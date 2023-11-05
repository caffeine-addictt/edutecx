"""
Managing user login/logout

! Note to self: redirects from POST -> GET needs code 302/303 to change request body as 307/308 preserves the original body
"""

from src import jwt
from src.database import UserModel

from src.utils.ext import utc_time
from src.utils.http import HTTPStatusCode, APIResponse
from src.utils.forms import LoginForm, LogoutForm, RegisterForm
from src.service.auth_provider import optional_jwt, require_login

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
  get_jwt,
  jwt_required,
  get_jwt_identity,
  unset_jwt_cookies,
  set_access_cookies,
  set_refresh_cookies,
  create_access_token,
)


# Config
@jwt.user_identity_loader
def user_identity_loader(user: 'UserModel'):
  return user.id

@jwt.user_lookup_loader
def user_lookup_loader(jwtHeader, jwtPayload):
  identity = jwtPayload["sub"]
  return UserModel.query.filter(UserModel.id == identity).first()

@app.after_request
def refresh_token(response):
  try:
    exp = get_jwt()['exp']
    if utc_time.skip('30minutes').timestamp() > exp:
      access_token = create_access_token(identity = get_jwt_identity())
      set_access_cookies(response, access_token)

    return response
  except Exception:
    return response


# Error handling
@jwt.unauthorized_loader
def unauthorized_loader(msg: str):
  if request.method == 'POST':
    return {
      'message': msg,
      'status': HTTPStatusCode.UNAUTHORIZED
    }, HTTPStatusCode.UNAUTHORIZED
  else:
    return redirect(
      f'/login?callbackURI={parse.quote(request.path)}',
      code = HTTPStatusCode.TEMPORARY_REDIRECT
    ), HTTPStatusCode.TEMPORARY_REDIRECT

@jwt.invalid_token_loader
def invalid_token_loader(msg: str):
  if request.method == 'POST':
    return {
      'message': msg,
      'status': HTTPStatusCode.UNPROCESSABLE_ENTITY
    }, HTTPStatusCode.UNPROCESSABLE_ENTITY
  else:
    response = make_response(redirect(
      f'/login?callbackURI={parse.quote(request.path)}',
      code = HTTPStatusCode.SEE_OTHER
    ))
    unset_jwt_cookies(response)
    return response, HTTPStatusCode.SEE_OTHER

@jwt.expired_token_loader
def expired_token_loader(jwtHeader, jwtPayload):
  if request.method == 'POST':
    return {
      'message': 'Token has expired',
      'status': HTTPStatusCode.UNAUTHORIZED
    }, HTTPStatusCode.UNAUTHORIZED
  else:
    response = make_response(redirect(
      f'/login?callbackURI={parse.quote(request.path)}',
      code = HTTPStatusCode.SEE_OTHER
    ))
    unset_jwt_cookies(response)
    return response, HTTPStatusCode.SEE_OTHER




# Routing
@app.route('/login', methods = ['Get', 'POST'])
def login():
  # Auto redirect to callbackURI
  if optional_jwt():
    flash(f'Welcome back!', 'success')
    callbackURI: str = parse.quote(request.args.get('callbackURI', '/home'))

    return redirect(callbackURI, code = HTTPStatusCode.PERMANENT_REDIRECT)
  
  form = LoginForm(request.form)

  if request.method == 'POST' and form.validate_on_submit():
    response = requests.post(
      f'{request.url_root}api/v1/login',
      headers = {'Content-Type': 'application/json'},
      json = {
        'email': form.email.data,
        'password': form.password.data
      }
    )
    body: APIResponse = response.json()
    
    if response.status_code != HTTPStatusCode.OK:
      flash(body.get('message'), 'danger')
    else:
      # Handle Login and cookie
      callbackURI: str = parse.quote(request.args.get('callbackURI', '/home'))
      successfulLogin = make_response(
        redirect(callbackURI, code = HTTPStatusCode.SEE_OTHER),
        HTTPStatusCode.SEE_OTHER
      )

      set_access_cookies(successfulLogin, str((body.get('data') or {}).get('access_token')))
      set_refresh_cookies(successfulLogin, str((body.get('data') or {}).get('refresh_token')))
      flash('Welcome back!', 'success')

      return successfulLogin
    
  elif request.method == 'POST':
    flash('Failed to log in', 'danger')
    
  return render_template('(auth)/login.html', form = form, url = request.host_url)


@app.route('/logout', methods = ['GET', 'POST'])
@require_login
def logout(user: UserModel):
  form = LogoutForm(request.form)
  if request.method == 'POST' and form.validate_on_submit():
    successfulLogout = make_response(
      redirect('/', code = HTTPStatusCode.SEE_OTHER),
      HTTPStatusCode.SEE_OTHER
    )
    unset_jwt_cookies(successfulLogout)
    # TODO: Add to token blocklist

    flash('Successfully logged out', 'info')
    return successfulLogout
  return render_template('(auth)/logout.html')


@app.route('/register', methods = ['GET', 'POST'])
@jwt_required(optional = True)
def register():
  # Redirect to callbackURI or home if logged in
  if get_jwt_identity():
    callbackURI: str = parse.quote(request.args.get('callbackURI', '/home'))
    return redirect(callbackURI, code = HTTPStatusCode.PERMANENT_REDIRECT), HTTPStatusCode.PERMANENT_REDIRECT
  
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
    body: APIResponse = response.json()

    if response.status_code != HTTPStatusCode.OK:
      flash(body.get('message'), 'danger')
    else:
      flash(body.get('message'), 'success')

      callbackURI: str = parse.quote(request.args.get('callbackURI', '/login'))
      return redirect(callbackURI, code = HTTPStatusCode.PERMANENT_REDIRECT), HTTPStatusCode.PERMANENT_REDIRECT
  elif request.method == 'POST':
    flash('Failed to create user account', 'danger')

  return render_template('(auth)/register.html', code = HTTPStatusCode.OK), HTTPStatusCode.OK
