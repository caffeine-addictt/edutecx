"""
Managing Admin-Only routes
"""

from src.service.auth_provider import require_admin
from src.database import UserModel
from flask import (
  render_template,
  current_app as app,
)


# Config
basePath: str = '/dashboard'


# Routes
@app.route(basePath)
@require_admin
def dashboard(user: UserModel):
  return render_template('(admin)/index.html')


# Users
@app.route(f'{basePath}/users', methods = ['GET'])
@require_admin
def dashboard_users(user: UserModel):
  return render_template('(admin)/user.html')


# Revenue
@app.route(f'{basePath}/revenue', methods = ['GET'])
@require_admin
def dashboard_revenue(user: UserModel):
  return render_template('(admin)/revenue.html')


# Textbooks
@app.route(f'{basePath}/textbooks', methods = ['GET'])
@require_admin
def dashboard_textbooks(user: UserModel):
  return render_template('(admin)/textbook.html')
