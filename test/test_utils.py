def test_exponentialBackoff_success():
  import src.util.utils as s

  def check(x):
    return x == 1

  @s.exponentialBackoff(retries = 1, validate = check)
  def func():
    return 1

  assert func() == 1


def test_exponentialBackoff_failure():
  import src.util.utils as s

  def check(x):
    return x == 1

  @s.exponentialBackoff(retries = 1, validate = check)
  def func():
    return 2
  
  try:
    func()
    assert 1 == 0, 'Function did not raise an ExponentialBackoffError'
  except s.ExponentialBackoffError:
    assert 1 == 1