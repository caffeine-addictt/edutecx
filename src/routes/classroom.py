"""
Handles classroom routes
"""

from src.database import UserModel, ClassroomModel
from src.service import auth_provider

from src.utils.http import HTTPStatusCode
from src.utils.http import escape_id
from src.utils.forms import ClassroomCreateForm, ClassroomEditForm

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
  classroom = ClassroomModel.query.filter(ClassroomModel.id == id).first()

  if not isinstance(classroom, ClassroomModel):
    return render_template('(classroom)/classroom_error.html')
  
  if not classroom.is_member(user) and (user.privilege != 'Admin'):
    return render_template('(classroom)/classroom_error.html', message = 'You are not a member of this classroom!')

  return render_template('(classroom)/classroom.html', classroom = classroom)


@app.route('/classrooms/edit/<string:id>', methods = ['GET'])
@auth_provider.require_educator(unauthorized_redirect = '/pricing')
def classroom_edit(user: UserModel, id: str):
  id = escape_id(id)
  classroom = ClassroomModel.query.filter(ClassroomModel.id == id).first()
  app.logger.error(f'{classroom}')

  if not isinstance(classroom, ClassroomModel):
    return render_template('(classroom)/classroom_error.html')
  
  if (not classroom.is_owner(user)) and (user.privilege != 'Admin'):
    return render_template('(classroom)/classroom_error.html', message = 'You are not authorized to edit this classroom')

  form = ClassroomEditForm(request.form)
  form.title.data = classroom.title
  form.description.data = classroom.description
  form.inviteEnabled.data = classroom.invite_enabled
  classroom = ClassroomModel.query.filter(ClassroomModel.id == id).first()
  return render_template('(classroom)/classroom_edit.html', form = form, classroom = classroom)


@app.route('/classrooms/new', methods = ['GET'])
@auth_provider.require_educator(unauthorized_redirect = '/pricing')
def classroom_new(user: UserModel):
  form = ClassroomCreateForm(request.form)
  return render_template('(classroom)/classroom_new.html', form = form)

