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

  # Flask
  FLASK_DEBUG = os.getenv('FLASK_DEBUG', False)
  FLASK_RUN_PORT = os.getenv('FLASK_RUN_PORT', 5000)

  # SQL
  SQLALCHEMY_ECHO = 'True' == os.getenv('SQLALCHEMY_ECHO', False)
  SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:///test.db')