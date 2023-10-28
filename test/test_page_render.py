from flask import Flask
from flask.testing import FlaskClient

# ! Issue #23
def test_home(app: Flask, client: FlaskClient):
  """
  Testing page routing
  """
  with app.app_context():
    # Write routes loaded to a.txt
    # with open('a.txt', 'a') as f:
    #   f.write(', '.join(list(i.__str__() for i in app.url_map.iter_rules())))

    response = client.get('/')
    assert response.status_code == 200, response
    