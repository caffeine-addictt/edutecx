"""
Initalizes Flask Application
"""

from flask import Flask
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy

from config import Config, DeploymentConfig

db = SQLAlchemy()

def init_app() -> Flask:
  """
  Initializes Flask Application
  """

  app = Flask(__name__)

  if Config.PRODUCTION == 'development':
    app.config.from_object(Config)
  else:
    app.config.from_object(DeploymentConfig)

  print('\nImported environment variables')

  # Init DB
  db.init_app(app = app)

  # Init Session
  app.config['SESSION_SQLALCHEMY'] = db
  Session(app = app)

  with app.app_context():
    # Import Database models
    from .util import database

    # Import modules
    from . import modules

    db.create_all()

    return app