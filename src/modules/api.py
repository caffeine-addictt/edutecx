from flask import jsonify

from ..app import app

@app.route('/api/v1/')
def root():
  return jsonify({
   'message': 'Hello World!'
  })