"""
Handles classroom routes
"""

from src.database import UserModel, ClassroomModel
from src.service import auth_provider

from src.utils.http import HTTPStatusCode
from src.utils.http import escape_id
from src.utils.forms import ClassroomCreateForm

from src.utils.api import ClassroomCreateResponse

import requests

from flask import (
  flash,
  request,
  redirect,
  make_response,
  render_template,
  current_app as app
)




@app.route('/classrooms', methods = ['GET'])
@auth_provider.require_login
def classrooms(user: UserModel):
  return render_template('(classroom)/classroom_list.html', user = user)


@app.route('/classrooms/<string:id>')
@auth_provider.require_login
def classroom(user: UserModel, id: str):
  id = escape_id(id)
  return render_template('(classroom)/classroom.html')


@app.route('/classrooms/new', methods = ['GET', 'POST'])
@auth_provider.require_educator
def classroom_new(user: UserModel):
  form = ClassroomCreateForm(request.form)
  app.logger.info(f'{request.url_root}api/v1/classroom/create')
  app.logger.info(request.cookies.get('access_token_cookie', ''))

  if request.method == 'POST' and form.validate_on_submit():
    response = ClassroomCreateResponse(requests.post(
      f'{request.url_root}api/v1/classroom/create',
      headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + request.cookies.get('access_token_cookie', '')
      },
      json = {
        'owner_id': user.id,
        'title': form.title.data,
        'description': form.description.data
      }
    ))
    
    if response.status != HTTPStatusCode.OK:
      flash(response.message, "danger")
    else:
      flash(response.message, "success")
      return make_response(redirect(
        f'/classrooms/{response.data.classroom_id}', 
        code = HTTPStatusCode.SEE_OTHER
      ), HTTPStatusCode.SEE_OTHER)

  return render_template('(classroom)/classroom_new.html', form = form)
