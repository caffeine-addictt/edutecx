import os
import pytest
from flask import Flask

from src import init_app
flaskApp = init_app(testing = True)

# testing app startup
@pytest.fixture()
def app():
  if os.getenv('ENV') == 'production':
    raise NotImplementedError('Cannot run tests in production environment')
  yield flaskApp

@pytest.fixture()
def client(app: Flask):
  if os.getenv('ENV') == 'production':
    raise NotImplementedError('Cannot run tests in production environment')
  return app.test_client()
