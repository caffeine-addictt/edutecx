"""
API Parser
"""

import inspect
from typing import Any

from requests import Response as ReqResponse
from flask import Request, Response as FlaskResponse
from werkzeug.exceptions import BadRequest

from abc import abstractmethod
from dataclasses import dataclass




class _APIBase:
  """API Base Class"""

  @abstractmethod
  def __init__(self) -> None:
    ...

  def __str__(self) -> str:
    return str(self.__dict__)
        
  def to_dict(self) -> dict[str, Any]:
    return {
      i: (v if not isinstance(v, _APIBase) else v.to_dict())
      for i,v in self.__dict__.items()
    }
  
  def get(self, name: Any, default = None) -> Any | None:
    return self.__dict__.get(name, default)
  
class _APIParser(_APIBase):
  """
  API Parser

  Auto loads variables from json, dictionary or form
  """

  def __init__(self, req: Request | FlaskResponse | ReqResponse | dict[str, Any]) -> None:
    """
    Loads values from response object

    Raises
    ------
    BadRequest: code 400
    """

    for variableName, variableType in (
      self.__annotations__ if isinstance(req, (Request, FlaskResponse, ReqResponse))
      else req
    ).items():
      
      if isinstance(req, Request):
        variable = req.json.get(variableName, None) if req.json else req.form.get(variableName, None)
      elif isinstance(req, FlaskResponse):
        variable = req.json.get(variableName, None) if req.json else None
      elif isinstance(req, ReqResponse):
        variable = req.json().get(variableName, None) if req.json else None
      else:
        variable = req.get(variableName, None)

      self._interpret(variable, variableName, variableType)


  def _interpret(self, var: Any, varName: str, varType: Any) -> None:
    isClass = inspect.isclass(varType)

    if isClass and isinstance(var, varType):
      self.__dict__[varName] = var
      return
    
    else:
      try:
        interpreted = varType(var) if isClass else type(varType)(var)
        if isinstance(interpreted, varType if isClass else type(varType)):
          self.__dict__[varName] = interpreted
        else:
          raise Exception()
        
      except Exception:
        raise BadRequest('Invalid variable type')
      
    raise BadRequest('Invalid variable')




# Base classes
class _APIResponse(_APIParser):
  """
  API Response

  For interpreting api responses
  """

  message: str
  status: int


class _APIRequest(_APIParser):
  """
  API Request
  
  For interpreting API requests
  """


@dataclass
class _APIReply(_APIBase):
  """
  API Reply

  For replying to API requests
  """

  message: str
  status: int








# Data
@dataclass
class _TokenRefreshData(_APIBase):
  access_token: str

@dataclass
class _LoginData(_APIBase):
  access_token: str
  refresh_token: str




# API Responses
class GenericResponse(_APIResponse):
  """Generic Response"""
  
class TokenRefreshResponse(_APIResponse):
  """API Response for refreshing JWT access token"""
  data: _TokenRefreshData

class LoginResponse(_APIResponse):
  """API Response for login"""
  data: _LoginData





# API Requests
class LoginRequest(_APIRequest):
  """API Request for login"""
  email: str
  password: str
  remember_me: bool

class RegisterRequest(_APIRequest):
  """API Request for register"""
  email: str
  username: str
  password: str
  




# API Replies
class GenericReply(_APIReply):
  """Generic Reply"""

@dataclass
class TokenRefreshReply(_APIReply):
  """API Reply for refreshing JWT access token"""
  data: _TokenRefreshData

@dataclass
class LoginReply(_APIReply):
  """API Reply for login"""
  data: _LoginData
