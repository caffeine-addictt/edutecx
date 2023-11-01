"""
Handles misc routing
"""

from src.database import DocumentModel

from typing import List
from flask import (
  g,
  request,
  render_template,
  current_app as app
)

@app.route('/')
def index():
  return render_template('root.html')

# TODO: Add SQL sanitization and caching to all DB models
@app.route('/store')
def store():
  query = request.args.get('search', '')
  documents: List['DocumentModel'] = DocumentModel.query.all()

  return render_template('')




