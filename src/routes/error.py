"""
Handling errors
"""

from src.utils.http import HTTPStatusCode
from werkzeug.exceptions import HTTPException

import traceback
from typing import Union

from dataclasses import dataclass
from flask import (
  request,
  redirect,
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
  if request.path.startswith('/api'):
    app.logger.error(f'API error {request.path}: %s' % str(error))
    app.logger.error(traceback.format_exc())

    return {
      'message': (isHTTPException and error.description) or HTTPStatusCode.getNameFromCode(500),
      'status': (isHTTPException and error.code) or HTTPStatusCode.INTERNAL_SERVER_ERROR,
    }, (isHTTPException and error.code) or HTTPStatusCode.INTERNAL_SERVER_ERROR
  

  app.logger.error(f'Non-API error {request.path}: %s' % str(error))
  if (isHTTPException and (error.code != HTTPStatusCode.NOT_FOUND)):
    app.logger.error(traceback.format_exc())

  match (isHTTPException and error.code):
    case HTTPStatusCode.NOT_FOUND:
      # Check for URL with extra /
      if request.path.endswith('/'):
        return redirect(
          request.path[:-1],
          code = HTTPStatusCode.SEE_OTHER
        ), HTTPStatusCode.SEE_OTHER

      return render_template('error.html', params = ErrorPageVariables(
        page_title = '404 Page not found',
        header1 = '404',
        header2 = 'Looks like you\'re lost!'
      )), HTTPStatusCode.NOT_FOUND
    
    case HTTPStatusCode.UNAUTHORIZED:
      return render_template('error.html', params = ErrorPageVariables(
        page_title = '401 Unauthorized',
        header1 = 'Unauthorized!',
        header2 = 'You are not allowed to access this page!'
      )), HTTPStatusCode.UNAUTHORIZED
    
    case HTTPStatusCode.TOO_MANY_REQUESTS:
      return render_template('error.html', params = ErrorPageVariables(
        page_title = '429 Rate Limited',
        header1 = 'Too Many Requests!',
        header2 = 'Let\'s take a chill pill'
      ))
    
    case _:
      return render_template('error.html', params = ErrorPageVariables(
        page_title = '500 Oops!',
        header1 = 'Oops!',
        header2 = 'Looks like something went wrong!'
      )), (isHTTPException and error.code or HTTPStatusCode.INTERNAL_SERVER_ERROR)
