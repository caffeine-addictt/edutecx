"""
Setup Flask Environment Variables

.env - imported variables should only be private keys etc.
"""

import os
import inspect
from datetime import timedelta
from typing import Literal, Optional, Mapping, Callable, Any, overload

from dotenv import load_dotenv
load_dotenv()

SecretVar = str | Callable[[], str]


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

  if strict and (fetched is None):
    raise ValueError(
      f'Environment variable {environmentName} is not set!' \
      + f' Add it to .env file "{environmentName}=<value>" or set it to a default value "getEnv("{environmentName}", <value>)".'
    )
  
  if fetched is None:
    print(f'Environment variable {environmentName} is not set! Using default value "{defaultValue}".')

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
  STRIPE_PUBLIC_KEY: SecretVar
  STRIPE_SECRET_KEY: SecretVar


  # \\\\\\ Flask ////// #
  # Docs https://flask.palletsprojects.com/en/3.0.x/config/
  DEBUG: Optional[bool] = True
  SECRET_KEY: SecretVar


  # \\\\\\ JWT ////// #
  # Docs https://flask-jwt-extended.readthedocs.io/en/3.0.0_release/options/
  JWT_SECRET_KEY: SecretVar
  JWT_SESSION_COOKIE: bool = False
  JWT_COOKIE_SECURE: bool = False
  JWT_TOKEN_LOCATION: list[str] = ['headers', 'cookies', 'json']
  JWT_ACCESS_TOKEN_EXPIRES: int | timedelta = timedelta(minutes=15)
  JWT_REFRESH_TOKEN_EXPIRES: int | timedelta = timedelta(days=30)
  PROPAGATE_EXCEPTIONS: bool = True


  # \\\\\\ Mail ////// #
  RESEND_API_KEY: SecretVar


  # \\\\\\ SQL ////// #
  # Docs https://flask-sqlalchemy.palletsprojects.com/en/3.1.x/config/
  SQLALCHEMY_ECHO: Optional[bool] = False
  SQLALCHEMY_DATABASE_URI: SecretVar


  # \\\\\\ Cloudinary //// //
  CLOUDINARY_CLOUD_NAME: SecretVar
  CLOUDINARY_API_KEY: SecretVar
  CLOUDINARY_API_SECRET: SecretVar



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

  SQLALCHEMY_DATABASE_URI = 'sqlite:///testing.sqlite3'




class ProductionConfig(ConfigBase):
  """
  Configurations for `Production`
  """

  ENV = 'production'

  STRIPE_PUBLIC_KEY = lambda: getEnv('STRIPE_PUBLIC_KEY', strict = True)
  STRIPE_SECRET_KEY = lambda: getEnv('STRIPE_SECRET_KEY', strict = True)

  DEBUG = False
  SECRET_KEY = lambda: getEnv('SECRET_KEY', strict = True)

  JWT_COOKIE_SECURE = True
  JWT_SECRET_KEY = lambda: getEnv('JWT_SECRET_KEY', strict = True)

  RESEND_API_KEY = lambda: getEnv('RESEND_API_KEY', strict = True)

  SQLALCHEMY_ECHO = False
  SQLALCHEMY_DATABASE_URI = lambda: getEnv('SQLALCHEMY_DATABASE_URI', strict = True)

  CLOUDINARY_CLOUD_NAME = lambda: getEnv('CLOUDINARY_CLOUD_NAME', strict = True)
  CLOUDINARY_API_KEY = lambda: getEnv('CLOUDINARY_API_KEY', strict = True)
  CLOUDINARY_API_SECRET = lambda: getEnv('CLOUDINARY_API_SECRET', strict = True)




def fetch_attribute_tree(a: type[object]) -> list[tuple[str, Any]]:
  return [ i for i in inspect.getmembers(a) if not i[0].startswith('_')]

def get_environment_config() -> Mapping[str, Any]:
  config: list[tuple[str, Any]] = []

  match getEnv('ENV', strict = True):
    case 'development':
      config = fetch_attribute_tree(DevelopmentConfig)
    case 'production':
      config = fetch_attribute_tree(ProductionConfig)

  # Interpret env file values
  return {
    i[0]: i[1]() if callable(i[1]) else i[1]
    for i in config
  }
