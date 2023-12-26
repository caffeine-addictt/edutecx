def test_exponentialBackoff_success():
  import src.utils.ext.exponential_backoff as s

  @s.exponentialBackoff(validate = (lambda x: x == 1))
  def func():
    return 1

  assert func() == 1


def test_exponentialBackoff_failure():
  import src.utils.ext.exponential_backoff as s

  @s.exponentialBackoff(retries = 0, validate = (lambda x: x == 1))
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


def test_forceTyping():
  import typing
  from src.utils.forcetype import recursiveValidation as forcetype


  # Testing single clause
  assert forcetype('hi', int) == None
  assert forcetype('hi', str) == 'hi'

  # Testing Union types
  assert forcetype(Exception(), typing.Union[int, str]) == None
  assert forcetype('hi', typing.Union[int, str]) == 'hi'
  assert forcetype('hi', typing.Optional[int]) == None
  assert forcetype('hi', typing.Optional[str]) == 'hi'

  # Testing Literal types
  assert forcetype('hi', typing.Literal['hi', 'bye']) == 'hi'
  assert forcetype(None, typing.Literal[True]) == None
  assert forcetype([], typing.Literal['']) == None

  # Testing sequence declared types
  assert forcetype('hi', list[str]) == None
  assert forcetype(['hi', Exception()], list[int]) == None
  assert forcetype(['hi'], list[str]) == ['hi']
  assert forcetype(['hi', 2], list[str]) == ['hi', '2']

  # Testing mapping declared types
  assert forcetype({'hi': 'bye'}, dict[str, str]) == {'hi': 'bye'}
  assert forcetype(None, dict[str, int]) == None
  assert forcetype({'a':'b', 'c':'d'}, dict[str, str]) == {'a':'b', 'c':'d'}
  assert forcetype({'a':'b', 'c':2}, dict[str, int]) == None

  # Testing default values
  assert forcetype(None, 9) == 9
  assert forcetype(Exception(), 4) == 4
