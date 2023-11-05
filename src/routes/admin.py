"""
Managing Admin-Only routes
"""

from src import db
from src.utils.http import Parser, escape_id
from src.service.auth_provider import require_admin
from src.database import (
  ReceiptModel,
  UserModel
)

from flask import (
  g,
  request,
  render_template,
  current_app as app
)


# Routes
basePath: str = '/dashboard'

@app.route(basePath)
@require_admin
def dashboard(user: UserModel):
  
  return render_template('(admin)/index.html', data = Parser(
    
  ))


# Users
@app.route(f'{basePath}/users')
def dashboard_users():

  return render_template('(admin)/user_list.html', data = Parser(

  ))

@app.route(f'{basePath}/users/<string:id>')
def dashboard_user(id: str):
  id = escape_id(id)

  return render_template('(admin)/user.html', data = Parser(
    id = id, typeof = type(id)
  ))


# Store
@app.route(f'{basePath}/sales')
def dashboard_sales():

  return render_template('(admin)/sale_list.html', data = Parser(

  ))

@app.route(f'{basePath}/sales/<string:id>')
def dashboard_sale(id: str):
  id = escape_id(id)

  return render_template('(auth)/sale.html', data = Parser(

  ))
