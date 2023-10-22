from flask import (
  jsonify,
  current_app as app
)


@app.route('/api/v1/')
def root():
  return jsonify({
   'message': 'Hello World!'
  })