"""
API v1 endpoint for user
"""

from flask import (
  jsonify,
  current_app as app,
)

basePath: str = '/api/v1/user'


@app.route(basePath, methods=['GET'])
def root():
  return jsonify()