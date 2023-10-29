"""
Handling errors
"""

from src.utils.http import HTTPStatusCode

from flask import (
  redirect,
  render_template,
  current_app as app,
)

@app.errorhandler(HTTPStatusCode.ERROR_NOT_FOUND)
def handle_errorNotFound(exceptionClass):
  return redirect('/404', code = HTTPStatusCode.TEMPORARY_REDIRECT)






# handle error page routing
@app.route('/404')
def _404():
  return render_template('(error)/404.html')