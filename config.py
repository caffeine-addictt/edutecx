"""
Setup Flask Environment Variables

.env - imported variables should only be private keys etc.
"""

import os
from typing import Literal, Union, Optional, Required

from dotenv import load_dotenv
load_dotenv()

class ConfigBase:
  """
  Base Config Class for Flask Environment
  Imports from .env

  Setup to favor development

  `SHOULD CONTAIN ALL ENV VARIABLES OF CHILD CLASSES`\n
  `SHOULD NEVER BE USED DIRECTLY`
  """

  # \\\\\\ General ////// #
  # Production ENV
  ENV: Literal['development', 'production'] = 'development'


  # \\\\\\ Flask ////// #
  # Docs https://flask.palletsprojects.com/en/3.0.x/config/
  DEBUG: Optional[bool] = True
  SECRET_KEY: str


  # \\\\\\ Session ////// #
  # Docs https://flask-session.readthedocs.io/en/latest/config.html
  SESSION_TYPE : Literal['filesystem', 'sqlalchemy']
  PERMANENT_SESSION_LIFETIME: int = 2 * 60 * 60 # 2h in seconds


  # \\\\\\ JWT ////// #
  # Docs https://flask-jwt-extended.readthedocs.io/en/3.0.0_release/options/
  JWT_SECRET_KEY: str = 'jwt-secret'
  JWT_TOKEN_LOCATION: list[str] = ['headers', 'cookies']
  JWT_ACCESS_TOKEN_EXPIRES: int = 1 * 60 # 1h in seconds
  JWT_REFRESH_TOKEN_EXPIRES: int = 30 * 24 * 60 * 60 #30 days in seconds
  PROPAGATE_EXCEPTIONS: bool = True


  # \\\\\\ Mail ////// #
  MAIL_PORT: int = 25
  MAIL_USE_TLS: bool = False
  MAIL_USE_SSL: bool = True
  MAIL_SERVER: Literal['localhost', 'smtp.google.com'] = 'smtp.google.com'


  # \\\\\\ SQL ////// #
  # Docs https://flask-sqlalchemy.palletsprojects.com/en/3.1.x/config/
  SQLALCHEMY_ECHO: Optional[bool] = True
  SQLALCHEMY_DATABASE_URI: Required[str] = 'sqlite:///testing.sqlite3'



# Configs to export
class DevelopmentConfig(ConfigBase):
  """
  Configurations for `Development`
  """

  ENV = 'development'

  SECRET_KEY = 'mysecretkey'

  SESSION_TYPE = 'sqlalchemy'



class ProductionConfig(ConfigBase):
  """
  Configurations for `Production`
  """

  ENV = 'production'
  DEBUG = False

  SECRET_KEY = 'L&>SdT@-Z*y[%(fxN6L>Us1PQ{WAp7&u'
  SESSION_TYPE = 'sqlalchemy'

  SQLALCHEMY_ECHO = False






def get_production_config() -> str:
  match os.getenv('PROD', 'development'):
    case 'development':
      return 'config.DevelopmentConfig'
    case 'production':
      return 'config.ProductionConfig'
    
  return 'config.DevelopmentConfig'