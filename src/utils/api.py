"""
API Parser
"""

import json
import inspect
from typing import Any

from requests import Response as ReqResponse
from flask import Request, Response as FlaskResponse, current_app as app
from werkzeug.exceptions import BadRequest


class _APIBase:
  """
  API Base Class

  Auto loads variables from json, dictionary or form
  """
  
  def __init__(self, req: Request | FlaskResponse | ReqResponse | dict[str, Any]) -> None:
    """
    Loads values from response object

    Raises
    ------
    BadRequest: code 400
    """
    # app.logger.info(req)
    for variableName, variableType in (self.__annotations__ if isinstance(req, (Request, FlaskResponse, ReqResponse)) else req).items():
      if isinstance(req, Request):
        variable = req.json.get(variableName, None) if req.json else req.form.get(variableName, None)
      elif isinstance(req, FlaskResponse):
        variable = req.json.get(variableName, None) if req.json else None
      elif isinstance(req, ReqResponse):
        variable = req.json().get(variableName, None) if req.json else None
      else:
        variable = req.get(variableName, None)

      self._interpret(variable, variableName, variableType)

  def __str__(self) -> str:
    return str(self._get_dict())
  
  def _get_dict(self) -> dict[str, Any]:
    """Returns a new dictionary from self.__dict__ without the private attributes"""
    return { i: v for i,v in self.__dict__.items() if not i.startswith('_') }
        
  def _interpret(self, var: Any, varName: str, varType: Any) -> None:
    if inspect.isclass(varType) and isinstance(var, varType):
      self.__dict__[varName] = var
    else:
      try:
        app.logger.info(f'{var, varName, varType}')
        interpreted = varType(var) if inspect.isclass(varType) else type(varType)(var)
        if isinstance(interpreted, varType if inspect.isclass(varType) else type(varType)):
          self.__dict__[varName] = interpreted
        else:
          raise Exception('Invalid variable')
      except Exception:
        raise BadRequest()
        
  def to_dict(self) -> dict[str, Any]:
    return self._get_dict()
  
  def get(self, name: Any, default = None) -> Any | None:
    return self._get_dict().get(name, default)




# Base classes
class _APIResponse(_APIBase):
  """
  API Response

  For use in routes. Validates response typing
  """


class _APIParser(_APIBase):
  """
  API Parser

  For use in api. Validates response typing
  """




# API Responses
class TokenRefreshResponse(_APIResponse):
  """API Response for refreshing JWT access token"""
  message: str
  status: int
  data: _APIBase




# API Parsers

