"""
Initializes Flask Application
"""

from flask import Flask
from flask_limiter import Limiter, util
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

import resend
import stripe
import thread
import cloudinary
from logging import config
from sqlalchemy import MetaData
from config import get_environment_config


# Migrations naming convention setup
convention = {
  'ix': 'ix_%(column_0_label)s',
  'uq': 'uq_%(table_name)s_%(column_0_name)s',
  'ck': 'ck_%(table_name)s_%(constraint_name)s',
  'fk': 'fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s',
  'pk': 'pk_%(table_name)s',
}
metadata = MetaData(naming_convention=convention)


# Setup app init variables to be publicly accessible
thread.Settings.set_graceful_exit(False)

db = SQLAlchemy(metadata=metadata)
jwt = JWTManager()
limiter = Limiter(
  key_func=util.get_remote_address,
  default_limits=['10 per second'],
  storage_uri='memory://0.0.0.0:11211',
  storage_options={},
)


# Setup Logging
config.dictConfig(
  {
    'version': 1,
    'formatters': {
      'file_fmt': {
        'format': '%(asctime)s p%(process)s {%(pathname)s:%(lineno)d} [[%(levelname)s]] - %(message)s'
      },
      'console_fmt': {
        'format': '%(asctime)s p%(process)s {%(pathname)s:%(lineno)d} [[%(levelname)s]] - %(message)s'
      },
    },
    'handlers': {
      'error': {
        'class': 'logging.handlers.RotatingFileHandler',
        'filename': 'logs/error.log',
        'formatter': 'file_fmt',
        'level': 'ERROR',
      },
      'console': {
        'class': 'logging.StreamHandler',
        'formatter': 'console_fmt',
        'stream': 'ext://sys.stdout',
        'level': 'INFO',
      },
    },
    'root': {'level': 'DEBUG', 'handlers': ['error', 'console']},
  }
)


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
  app.config.from_mapping(get_environment_config())

  print('\nImported environment variables')

  # Init DB
  db.init_app(app=app)

  # Init Limiting
  limiter.init_app(app=app)

  # Init Email
  resend.api_key = app.config.get('RESEND_API_KEY')

  # Init JWT
  jwt.init_app(app=app)

  # Init Stripe
  stripe.api_key = app.config.get('STRIPE_SECRET_KEY')

  # Init cloudinary
  cloudinary.config(
    cloud_name=app.config.get('CLOUDINARY_CLOUD_NAME'),
    api_key=app.config.get('CLOUDINARY_API_KEY'),
    api_secret=app.config.get('CLOUDINARY_API_SECRET'),
    secure=app.config.get('ENV') == 'production',
  )

  with app.app_context():
    # Import Database models
    from . import database

    # Import routes
    from . import api
    from . import routes

    db.create_all()

    return app
