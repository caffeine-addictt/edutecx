"""
Initalizes Flask Application
"""

from flask import Flask
from flask_migrate import Migrate
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from custom_lib.flask_login import LoginManager

from config import get_production_config

db = SQLAlchemy()
loginManager = LoginManager()

def init_app() -> Flask:
  """
  Initializes Flask Application
  """

  app = Flask(__name__)
  app.config.from_object(get_production_config())

  print('\nImported environment variables')

  # Init DB
  db.init_app(app = app)

  # Init Login
  loginManager.init_app(app = app)

  # Init Session
  app.config['SESSION_SQLALCHEMY'] = db
  Session(app = app)

  # Migrate DB
  migrate = Migrate(app = app, db = db)

  with app.app_context():
    # Import Database models
    from .util import database

    # Import modules
    from . import modules

    db.create_all()

    return app