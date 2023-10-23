"""
Setup Flask Environment
"""

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
  """
  Containing environment variables from .env
  """

  # General
  PRODUCTION = os.getenv('PRODUCTION', 'development')

  # Flask
  # Docs https://flask.palletsprojects.com/en/3.0.x/config/
  SECRET_KEY = os.getenv('SECRET_KEY', 'mysecretkey')
  FLASK_DEBUG = 'True' == os.getenv('FLASK_DEBUG', 'False')
  FLASK_RUN_PORT = os.getenv('FLASK_RUN_PORT', 8000)

  # Session
  # Docs https://flask-session.readthedocs.io/en/latest/config.html
  SESSION_TYPE = os.getenv('SESSION_TYPE', 'filesystem')
  PERMANENT_SESSION_LIFETIME = int(os.getenv('PERMANENT_SESSION_LIFETIME', 2 * 60 * 60)) # 2h in Seconds

  # SQL
  # Docs https://flask-sqlalchemy.palletsprojects.com/en/3.1.x/config/
  SQLALCHEMY_ECHO = 'True' == os.getenv('SQLALCHEMY_ECHO', False)
  SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:///testing.sqlite3')


class DeploymentConfig(Config):
  SECRET_KEY = 'L&>SdT@-Z*y[%(fxN6L>Us1PQ{WAp7&u'
  FLASK_DEBUG = False