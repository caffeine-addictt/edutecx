"""
Caching utils
"""

from functools import wraps
from typing import ParamSpec, TypeVar, Callable


_CacheP = ParamSpec('_CacheP')
_CacheT = TypeVar('_CacheT')
def customCache(func: Callable[_CacheP, _CacheT]) -> Callable[_CacheP, _CacheT]:
  _max = 128
  memory: dict[str, _CacheT] = {}
  
  @wraps(func)
  def wrapper(*args: _CacheP.args, **kwargs: _CacheP.kwargs) -> _CacheT:
    # Generate hash
    hash = str(''.join([
      str(i.__hash__())
      for i in (list(args) + list(
        (str(a.__hash__()) + str(b.__hash__()))
        for a,b in kwargs.items()
      ))
    ]).__hash__())

    if memory[hash]:
      return memory[hash]
    
    returnValue = func(*args, **kwargs)
    memory[hash] = returnValue

    # Enforce max memory
    keys = tuple(memory.keys())
    if len(keys) > _max:
      for index in range(0, len(keys) - _max):
        del memory[keys[index]]

    return returnValue
  return wrapper
