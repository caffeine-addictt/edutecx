import pytest
from flask import Flask


# testing app startup
@pytest.fixture()
def app():
  from src.app import app
  yield app

@pytest.fixture()
def client(app: Flask):
  return app.test_client()