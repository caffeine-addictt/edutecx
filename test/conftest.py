import pytest
from flask import Flask

from src import init_app
flaskApp = init_app(testing = True)

# testing app startup
@pytest.fixture()
def app():
  yield flaskApp

@pytest.fixture()
def client(app: Flask):
  return app.test_client()