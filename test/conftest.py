import pytest
from flask import Flask


# testing app startup
@pytest.fixture()
def app():
  from src import init_app
  yield init_app(testing = True)

@pytest.fixture()
def client(app: Flask):
  app.testing = True
  yield app.test_client()