"""
Setup Flask Environment Variables

.env - imported variables should only be private keys etc.
"""

import os
from typing import Literal, Optional, overload

from dotenv import load_dotenv
load_dotenv()




@overload
def getEnv(environmentName: str, *, strict: Literal[True]) -> str:
  ...

@overload
def getEnv(environmentName: str, defaultValue: str, *, strict: Optional[Literal[False]] = None) -> str:
  ...

@overload
def getEnv(environmentName: str, defaultValue: None = None, *, strict: Optional[Literal[False]] = None) -> Optional[str]:
  ...

def getEnv(environmentName: str, defaultValue: Optional[str] = None, *, strict: Optional[bool] = None) -> Optional[str]:
  """
  Get environment variable

  Parameters
  ----------
  `environmentName: str`, required
  `defaultValue: str`, optional (defaults to None)
  `strict: bool`, optional (defaults to None)

  Returns
  -------
  `value` or `defaultValue`

  Raises
  ------
  `ValueError` if `strict` is `True` and `variable` is not set
  """
  fetched = os.getenv(environmentName)

  if strict and (fetched is None) and (fetched != defaultValue):
    raise ValueError(
      f'Environment variable {environmentName} is not set!' \
      + f' Add it to .env file "{environmentName}=<value>" or set it to a default value "getEnv("{environmentName}", <value>)".'
    )

  return fetched or defaultValue




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
  ENV: Literal['development', 'production']
  UNLIMITED_TIER_PRICE: float = 49.99


  # \\\\\\ Stripe ////// #
  STRIPE_PUBLIC_KEY: str
  STRIPE_SECRET_KEY: str


  # \\\\\\ Flask ////// #
  # Docs https://flask.palletsprojects.com/en/3.0.x/config/
  DEBUG: Optional[bool] = True
  SECRET_KEY: str


  # \\\\\\ JWT ////// #
  # Docs https://flask-jwt-extended.readthedocs.io/en/3.0.0_release/options/
  JWT_SECRET_KEY: str
  JWT_TOKEN_LOCATION: list[str] = ['headers', 'cookies', 'json']
  JWT_ACCESS_TOKEN_EXPIRES: int = 60 * 60 # 1h in seconds
  JWT_REFRESH_TOKEN_EXPIRES: int = 30 * 24 * 60 * 60 #30 days in seconds
  PROPAGATE_EXCEPTIONS: bool = True


  # \\\\\\ Mail ////// #
  RESEND_API_KEY: str

  # \\\\\\ SQL ////// #
  # Docs https://flask-sqlalchemy.palletsprojects.com/en/3.1.x/config/
  SQLALCHEMY_ECHO: Optional[bool] = False
  SQLALCHEMY_DATABASE_URI: str



# Configs to export
class DevelopmentConfig(ConfigBase):
  """
  Configurations for `Development`
  """

  ENV = 'development'

  STRIPE_PUBLIC_KEY = getEnv('STRIPE_PUBLIC_KEY', '')
  STRIPE_SECRET_KEY = getEnv('STRIPE_SECRET_KEY', '')

  DEBUG = True
  SECRET_KEY = 'mysecretkey'

  JWT_SECRET_KEY = 'jwt-secret'

  RESEND_API_KEY = getEnv('RESEND_API_KEY', '')

  SQLALCHEMY_DATABASE_URI = 'sqlite:///testing.sqlite3'




class ProductionConfig(ConfigBase):
  """
  Configurations for `Production`
  """

  ENV = 'production'

  STRIPE_PUBLIC_KEY = getEnv('STRIPE_PUBLIC_KEY', strict = True)
  STRIPE_SECRET_KEY = getEnv('STRIPE_SECRET_KEY', strict = True)

  DEBUG = False
  SECRET_KEY = getEnv('SECRET_KEY', strict = True)

  JWT_SECRET_KEY = getEnv('JWT_SECRET_KEY', strict = True)

  RESEND_API_KEY = getEnv('RESEND_API_KEY', strict = True)

  SESSION_TYPE = 'sqlalchemy'

  SQLALCHEMY_ECHO = False
  SQLALCHEMY_DATABASE_URI = getEnv('SQLALCHEMY_DATABASE_URI', strict = True)







def get_production_config() -> str:
  match getEnv('PROD', strict = True):
    case 'development':
      return 'config.DevelopmentConfig'
    case 'production':
      return 'config.ProductionConfig'
    
  return 'config.DevelopmentConfig'