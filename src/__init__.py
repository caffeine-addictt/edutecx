"""
Initalizes Flask Application
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from config import Config

db = SQLAlchemy()


def init_app() -> Flask:
  """
  Initializes Flask Application
  """

  app = Flask(__name__)
  app.config.from_object(Config)

  print('\nImported environment variables')

  db.init_app(app = app)

  with app.app_context():
    from . import modules

    db.create_all()

    return app