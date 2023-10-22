import pytest
from flask import Flask


# testing app startup
@pytest.fixture()
def app():
  from src import init_app
  yield init_app()

@pytest.fixture()
def client(app: Flask):
  return app.test_client()