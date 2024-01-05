"""
Handles classroom routes
"""

from src.database import UserModel, ClassroomModel
from src.service import auth_provider

from src.utils.http import HTTPStatusCode
from src.utils.http import escape_id
from src.utils.forms import ClassroomCreateForm

from src.utils.api import ClassroomCreateResponse, GenericResponse

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
@auth_provider.require_educator()
def classroom_new(user: UserModel):
  form = ClassroomCreateForm(request.form)
  return render_template('(classroom)/classroom_new.html', form = form)
