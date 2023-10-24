"""
Managing user login/logout
"""

from .. import loginManager
from ..util import HTTPStatusCode
from ..util.database import UserModel

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
def loadUser(userID: str) -> UserModel | None:
  # Placed in try-except block to prevent edge case of invalid formatting of userID
  try: return UserModel.query.get(userID)
  except Exception as e:
    print(f'Error loading user: {e}')
    return None



# Routing
@app.route('/login', methods = ['Get', 'POST'])
def login():
  # Auto redirect to callbackURI
  if g.user.is_authenticated():
    callbackURI: str = parse.quote(request.args.get('callbackURI', '/'))
    return redirect(callbackURI, code = HTTPStatusCode.PERMANENT_REDIRECT)
  
  # TODO: Form Logic
  form: None

  return render_template('(auth)/login/index.html')


@app.route('/logout', methods = ['GET', 'POST'])
def logout():
  if g.user.is_authenticated():
    logout_user()
    return redirect('/', code = HTTPStatusCode.PERMANENT_REDIRECT)
  
  return redirect(url_for(endpoint = 'login'), code = HTTPStatusCode.PERMANENT_REDIRECT)
