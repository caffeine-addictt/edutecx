"""
Manage User Cookies
"""

from flask import (
  render_template,
  current_app as app,
)

basePath: str = '/api/v1/auth'


@app.route(f'{basePath}/login')
def login():
  return render_template('login.html')