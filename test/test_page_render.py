from flask import Flask
from flask.testing import FlaskClient


def test_appRoutes(app: Flask, client: FlaskClient):
  """
  Testing that all routes are added properly
  """
  passed = set()
  failed = set()

  def validatePassing(path: str, code: int) -> bool:
    return (
      (path.startswith('/public') and (code in [200, 404]))
      or (path.startswith('/static') and (code in [200, 404]))
      or (path.startswith('/api/v1') and (code in [200, 303, 400, 401]))
      or (path.startswith('/store/<') and (code in [200, 404]))
      or (code in [200, 303, 401])
    )

  for rule in app.url_map.iter_rules():
    
    if rule.methods and 'GET' in rule.methods:
      response = client.get(rule.rule)

      if validatePassing(rule.rule, response.status_code):
        passed.add(f'{rule.rule}: {response.status_code}')
      else:
        failed.add(f'{rule.rule}: {response.status_code}')

    if rule.methods and 'POST' in rule.methods:
      response = client.post(rule.rule)

      if validatePassing(rule.rule, response.status_code):
        passed.add(f'{rule.rule}: {response.status_code}')
      else:
        failed.add(f'{rule.rule}: {response.status_code}')

  assert len(failed) == 0, (
    f'\n\nLog:\n\nFailed [{len(failed)}]\n>>>>>>>>>>\n%s\n<<<<<<<<<<\n\nPassed [{len(passed)}]\n>>>>>>>>>>\n%s\n<<<<<<<<<<\n'
    % ('\n'.join(failed), '\n'.join(passed))
  )
