from flask.testing import FlaskClient

def test_home(client: FlaskClient):
  """
  Testing page routing
  """
  response = client.get('/')
  assert response.status_code == 200, response