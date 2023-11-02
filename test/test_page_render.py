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
    

def test_routesExist(app: Flask, client: FlaskClient):
  """
  Testing that all routes are added properly
  """
  with app.app_context():
    passed = set()
    failed = set()

    for route in [
      # Normal routes
      '/',
      '/home',
      
      # Purchasing routes
      '/store',
      '/cart',
      '/checkout',

      # Auth routes
      '/login',
      '/logout',
      '/register',

      # user routes
      '/textbooks',
      '/classrooms',
      '/assignments',
      '/submissions',

      # Legal
      '/privacy-policy',
      '/contact-us',
      '/terms-of-service',

      # Admin routes
      '/dashboard',
      '/dashboard/users',
      '/dashboard/sales'
    ]:
      response = client.get(route)

      if response.status_code == 404:
        failed.add(f'{route}: {response.status_code}')
      else:
        passed.add(f'{route}: {response.status_code}')

    assert len(failed) == 0, (
      f'\n\nLog:\n\nFailed [{len(failed)}]\n>>>>>>>>>>\n%s\n<<<<<<<<<<\n\nPassed [{len(passed)}]\n>>>>>>>>>>\n%s\n<<<<<<<<<<\n'
      % ('\n'.join(failed), '\n'.join(passed))
    )
