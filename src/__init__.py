"""
Initalizes Flask Application
"""

from flask import Flask
from flask_mail import Mail
from flask_migrate import Migrate
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from custom_lib.flask_login import LoginManager

from sqlalchemy import MetaData
from config import get_production_config


# Migrations naming convention setup
convention = {
  'ix': 'ix_%(column_0_label)s',
  'uq': 'uq_%(table_name)s_%(column_0_name)s',
  'ck': 'ck_%(table_name)s_%(constraint_name)s',
  'fk': 'fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s',
  'pk': 'pk_%(table_name)s'
}
metadata = MetaData(naming_convention = convention)


# Setup app init variables to be publically accessible
db = SQLAlchemy(metadata = metadata)
mail = Mail()
migrate = Migrate()
loginManager = LoginManager()

def init_app(testing: bool = False) -> Flask:
  """
  Initializes Flask Application

  Parameters
  ----------
  `testing: bool`, optional (defaults to False)
    For use when running test client with pytest
  """

  app = Flask(__name__)
  app.testing = testing
  app.config.from_object(get_production_config())

  print('\nImported environment variables')

  # Init DB
  db.init_app(app = app)

  # Init Login
  loginManager.init_app(app = app)

  # Init Session
  # app.config['SESSION_SQLALCHEMY'] = db
  # Session(app = app)

  # Init Mail
  mail.init_app(app = app)

  with app.app_context():
    # Import Database models
    from . import database

    # Import routes
    from . import routes

    db.create_all()
    migrate.init_app(app = app, db = db)

    return app