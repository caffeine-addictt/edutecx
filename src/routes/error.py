"""
Handling errors
"""

from src.utils.http import HTTPStatusCode
from werkzeug.exceptions import HTTPException

from typing import Union

from dataclasses import dataclass
from flask import (
  request,
  render_template,
  current_app as app,
)


# Variables used by error.html
@dataclass
class ErrorPageVariables:
  page_title  : str
  header1     : str
  header2     : str
  description : str = 'A bug? <a href="/contact-us">Let us know!</a>'
  return_title: str = 'Return Home'
  return_route: str = '/'


# Route to error pages
@app.errorhandler(Exception)
def handle_errorNotFound(error: Union[Exception, HTTPException]):
  isHTTPException = isinstance(error, HTTPException)

  # Handle errors for API
  if request.method == 'POST':
    app.logger.error(error.__repr__())

    return {
      'message': (isHTTPException and error.description) or HTTPStatusCode.getNameFromCode(500),
      'status': (isHTTPException and error.code) or HTTPStatusCode.INTERNAL_SERVER_ERROR,
    }, (isHTTPException and error.code) or HTTPStatusCode.INTERNAL_SERVER_ERROR
  

  match (isHTTPException and error.code):
    case HTTPStatusCode.NOT_FOUND:
      return render_template('error.html', params = ErrorPageVariables(
        page_title = 'Page not found',
        header1 = '404',
        header2 = 'Looks like you\'re lost!'
      )), HTTPStatusCode.NOT_FOUND
    
    case HTTPStatusCode.UNAUTHORIZED:
      return render_template('error.html', params = ErrorPageVariables(
        page_title = 'Unauthorized',
        header1 = 'Unauthorized!',
        header2 = 'You are not allowed to access this page!'
      )), HTTPStatusCode.UNAUTHORIZED
    
    case _:
      return render_template('error.html', params = ErrorPageVariables(
        page_title = 'Oops!',
        header1 = 'Oops!',
        header2 = 'Looks like something went wrong!'
      )), (isHTTPException and error.code or HTTPStatusCode.INTERNAL_SERVER_ERROR)
