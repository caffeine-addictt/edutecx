"""
Managing Admin-Only routes
"""

from src import db
from src.utils.http import Parser, escape_id
from src.utils.ext.login import admin_required

from src.database import (
  ReceiptModel
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
@admin_required()
def dashboard():
  
  return render_template('(admin)/index.html', data = Parser(
    
  ))


# Users
@app.route(f'{basePath}/users')
@admin_required()
def dashboard_users():

  return render_template('(admin)/user_list.html', data = Parser(

  ))

@app.route(f'{basePath}/users/<string:id>')
@admin_required()
def dashboard_user(id: str):
  id = escape_id(id)

  return render_template('(admin)/user.html', data = Parser(
    id = id, typeof = type(id)
  ))


# Store
@app.route(f'{basePath}/sales')
@admin_required()
def dashboard_sales():

  return render_template('(admin)/store.html', data = Parser(

  ))

@app.route(f'{basePath}/sales/<string:id>')
@admin_required()
def dashboard_sale(id: str):
  id = escape_id(id)

  return render_template('(auth)/sale.html', data = Parser(
    
  ))
