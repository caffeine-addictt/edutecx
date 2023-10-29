"""
Managing user login/logout
"""

from src import loginManager
from src.database import UserModel
from src.utils.http import HTTPStatusCode
from src.utils.forms import LoginForm, RegisterForm

from typing import Optional

from urllib import parse
from custom_lib.flask_login import login_user, logout_user, login_required, current_user
from flask import (
  g,
  request,
  url_for,
  redirect,
  render_template,
  current_app as app,
)


# Config
@app.before_request
def beforeRequest():
  g.user = current_user

@loginManager.user_loader
def loadUser(userID: str) -> Optional['UserModel']:
  # Placed in try-except block to prevent edge case of invalid formatting of userID
  try: return UserModel.query.get(userID)
  except Exception as e:
    print(f'Error loading user: {e}')
    return None



# Routing
@app.route('/login', methods = ['Get', 'POST'])
def login():
  # Auto redirect to callbackURI
  if g.user.is_authenticated:
    callbackURI: str = parse.quote(request.args.get('callbackURI', '/'))
    return redirect(callbackURI, code = HTTPStatusCode.PERMANENT_REDIRECT)
  
  form = LoginForm(request.form)

  if form.validate_on_submit():
    user: Optional['UserModel'] = UserModel.query.filter_by(email = form.email.data).first()

    if user is not None and user.verify_password(form.password.data):
      login_user(user)
      callbackURI: str = parse.quote(request.args.get('callbackURI', '/'))
      return redirect(callbackURI, code = HTTPStatusCode.PERMANENT_REDIRECT)

  return render_template('(auth)/login/index.html', form = form)


@app.route('/logout', methods = ['GET', 'POST'])
def logout():
  if g.user.is_authenticated:
    logout_user()
    return redirect('/', code = HTTPStatusCode.PERMANENT_REDIRECT)
  
  return redirect(url_for(endpoint = 'login'), code = HTTPStatusCode.PERMANENT_REDIRECT)
