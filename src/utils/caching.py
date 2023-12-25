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
    _hash = str(hash(''.join([
      str(hash(i))
      for i in (list(args) + list(
        (str(hash(a)) + str(hash(b)))
        for a,b in kwargs.items()
      ))
    ])))

    if memory.get(_hash):
      return memory[_hash]
    
    returnValue = func(*args, **kwargs)
    memory[_hash] = returnValue

    # Enforce max memory
    keys = tuple(memory.keys())
    if len(keys) > _max:
      for index in range(0, len(keys) - _max):
        del memory[keys[index]]

    return returnValue
  return wrapper
