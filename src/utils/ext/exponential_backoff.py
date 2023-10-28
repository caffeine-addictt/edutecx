"""
Exponential Backoff Implementation
"""

import time
import random
import traceback
from typing import (
  Callable,
  Union,
  Any,
)



class ExponentialBackoffError(Exception):
  """
  Exponential Backoff Error

  Raised when exponential backoff fails all attempts or validation
  """
  def __init__(self, message: Union[str, None] = None, *args, **kwargs) -> None:
    super().__init__(message, *args, **kwargs)


def exponentialBackoff(
  retries: int = 5,
  scale: int = 1,
  validate: Union[Callable[..., bool], None] = None
) -> Callable[[Callable[..., Any]], Any]:
  """
  Exponential Backoff Algorithm\n
  Best used for wrapping API calls

  Retries {retries} number of times after:
    `{scale} * 2**{attempt No.} + (random float between 0 - 1) seconds`

    
  Parameters
  ----------
  `retries : int`, optional (default is 5)
    The maximum number of times it will attempt to execute the function

  `scale   : int`, optional (default is 1)
    The scale factor of wait time, t, in the approximate exponential graph, y = tx^2

  `validate: (...) -> bool`, optional (default is None)
    The validation function to be called
    Arguments are parsed from the wrapped function

    
  Returns
  -------
  `function: (...) -> Any`
    Returns the decorator


  Raises
  ------
  `ExponentialBackoffError`
    If all retries are exhausted by errors or validation failures


  Examples
  --------
  ```py
    def check(returnedValue: Any) -> bool:
      return returnedValue == 1

    @exponentialBackoff(retries = 5, scale = 1, validate = check)
    def func1(arg1: int, arg2: int):
      return arg1 + arg2
  ```
  ```sh
  > func1(1, 2)
  3
  ```


  ```py
    @exponential_backoff(validate = lamda x: x==1)
    def func2(arg1: int, arg2: int):
      return arg1 / arg2
  ```
  ```sh
  > func2(2, 3)
  ExponentialBackoffError ...
  ```

  """
  def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorates a Function


    Parameters
    ----------
    `func   : (...) -> Any`, required
      The function to be decorated


    Returns
    -------
    `function: (...) -> Any`
      Returns wrapper function


    Raises
    ------
    `ExponentialBackoffError`
      If all retries are exhausted by errors or validation failures


    Examples
    --------
    >>> @decorator
    >>> def wrapMe() -> bool:
    >>>   return True
    """
    def wrapper(*args: Any, **kwargs: Any) -> Any:
      """
      Wraps a Function\n
      Retries {retries} number of times after:
        {scale} * 2**{attempt No.} + (random float between 0 - 1) seconds

        
      Parameters
      ----------
      `args   : tuple[Any]`    , optional (default is None)
        Value arguments that will be parsed to the wrapped function

      `kwargs : dict[Str: Any]`, optional (default is None)
        Key-Value pair arguments that will be parsed to the wrapped function

        
      Returns
      -------
      `value  : Any`
        What is returned by the wrapped function

        
      Raises
      ------
      `ExponentialBackoffError`
        If all retries are exhausted by errors or validation failures
      """
      log = [
        'Exponential Backoff attempt failed!',
        f'Function: {func.__name__}',
        ''
      ]

      count = 1
      while count <= retries:
        try:
          value = func(*args, **kwargs)

          if validate and not validate(value): raise Exception('Validation failed')
          else: return value
        except Exception as err:
          log.append(f'Try {count}: {err}')
        
        count += 1
        time.sleep((scale * 2**count) + random.uniform(0, 1))

      log.append('')
      traceback.print_exc()

      raise ExponentialBackoffError(message = '\n'.join(log))

    return wrapper
  return decorator
