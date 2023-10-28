import pytest
from flask import Flask

# testing app startup
@pytest.fixture()
def app():
  from src import init_app
  return init_app(testing = True)

@pytest.fixture()
def client(app: Flask):
  with app.test_client() as client:
    yield client