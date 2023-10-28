def test_exponentialBackoff_success():
  import src.utils.ext.exponential_backoff as s

  def check(x):
    return x == 1

  @s.exponentialBackoff(retries = 1, validate = check)
  def func():
    return 1

  assert func() == 1


def test_exponentialBackoff_failure():
  import src.utils.ext.exponential_backoff as s

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


def test_stringToTimeConversion():
  import src.utils.ext.utc_time as t

  assert float(t.convertToTime(3.5)) == float(3.5)
  assert float(t.convertToTime('5')) == float(5)
  assert float(t.convertToTime('5y7months9week4day8h9m2s')) == float(181642142)
