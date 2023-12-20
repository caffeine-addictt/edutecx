"""
Editable Textbook Endpoint
"""

from src import db, limiter
from src.database import EditableTextbookModel
from flask_limiter import util
from flask import (
  request,
  current_app as app
)


# Routes
basePath: str = '/api/v1/editabletextbook'
auth_limit = limiter.shared_limit('100 per hour', scope = lambda _: request.host, key_func = util.get_remote_address)