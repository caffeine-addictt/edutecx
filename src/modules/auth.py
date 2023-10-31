"""
Managing user login/logout
"""

from src import db, loginManager
from src.database import UserModel

from src.utils.http import HTTPStatusCode
from src.utils.forms import LoginForm, RegisterForm
from src.utils.passwords import hash_password
from src.utils.ext.login import loggedin_required, not_loggedin_required

from typing import Optional

from urllib import parse
from custom_lib.flask_login import login_user, logout_user, current_user
from flask import (
  g,
  flash,
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
    callbackURI: str = parse.quote(request.args.get('callbackURI', '/home'))
    return redirect(callbackURI, code = HTTPStatusCode.PERMANENT_REDIRECT)
  
  form = LoginForm(request.form)

  if form.validate_on_submit():
    user: Optional['UserModel'] = UserModel.query.filter_by(email = form.email.data).first()

    if user is not None and user.verify_password(form.password.data):
      login_user(user)
      flash('Welcome, %s' % user.username, 'info')

      callbackURI: str = parse.quote(request.args.get('callbackURI', '/home'))
      return redirect(callbackURI, code = HTTPStatusCode.PERMANENT_REDIRECT)
    
  flash('hi', category = 'success')
  return render_template('(auth)/login.html', form = form)


@app.route('/logout', methods = ['GET', 'POST'])
@loggedin_required(login_uri = '/login')
def logout():
  logout_user()
  flash('Successfully logged out, cya soon!', 'message')
  return redirect('/', code = HTTPStatusCode.PERMANENT_REDIRECT)
  

@app.route('/register')
@not_loggedin_required(logout_uri = '/logout')
def register():

  form = RegisterForm()
  if form.validate_on_submit():
    assert form.email.data is not None   , 'Invalid email'
    assert form.username.data is not None, 'Invalid username'
    assert form.password.data is not None, 'Invalid password'

    newUser: 'UserModel' = UserModel(
      email     = form.email.data,
      username  = form.username.data,
      password  = str(hash_password(form.password.data)),
      privilege = 'User'
    )
    db.session.add(newUser)
    db.session.commit()

    flash('Created account, please log in!', 'info')
    return redirect('/login', code = HTTPStatusCode.PERMANENT_REDIRECT)

  return render_template('(auth)/register.html', form = form)
