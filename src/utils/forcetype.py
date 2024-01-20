import inspect
from typing import Any, Optional, Union, Literal, Sequence, Mapping, get_args, get_origin

def recursiveValidation(x: Any, type_: Any) -> Optional[Any]:
  """
  Recursive type forcing

  Supports nested types

  Parameters
  ----------
  `x: Any`, required
    The object to be validated
  
  `type_: Any`, required
    The type or default value
    The type of the default value is used if not a type

  Returns
  -------
  `returns: Any | None`: The forced type or None if any failed

  Use Case
  --------
  >>> recursiveValidation(Exception(), Union[int, str])   = None
  >>> recursiveValidation('hi', Union[int, str])          = 'hi'
  >>> recursiveValidation('hi', list[str])                = None
  >>> recursiveValidation(['hi', Exception()], list[int]) = None
  >>> recursiveValidation(['hi'], list[str])              = ['hi']
  >>> recursiveValidation(['hi', 2], list[str])           = ['hi', '2']
  >>> recursiveValidation('hi', int)                      = None
  >>> recursiveValidation('hi', str)                      = 'hi'
  >>> recursiveValidation(None, 9)                        = 9
  >>> recursiveValidation(Exception(), 4)                 = 4
  """

  # a: Union[int, str] => typing.Union
  # b: Optional[int] => typing.Union
  # c: list[str] => list
  # d: int => None
  # e = 'h' => None
  # f: MyClass => None
  origin = get_origin(type_)

  if origin is Union or origin is Literal:
    for t in get_args(type_):
      interpretated = recursiveValidation(x, t)

      isLiteral = origin is Literal
      isBool = t is bool

      if interpretated and ((not isLiteral) or (isLiteral and (interpretated == t or (isBool and isinstance(interpretated, bool))))):
        return interpretated
      
  elif origin:
    try:
      if isinstance(x, Sequence) and (not isinstance(x, str)):
        validatedX: Sequence = origin()
        for t in get_args(type_):
          for y in x:
            interpretated = recursiveValidation(y, t)
            if interpretated:
              validatedX = origin([*validatedX, interpretated])
            else:
              return None
        
        return validatedX

      elif isinstance(x, Mapping):
        mappedX: Mapping = origin()
        keyTypes, valueTypes = get_args(type_)

        for k,v in x.items():
          interpretatedKey = recursiveValidation(k, keyTypes)
          interpretatedValue = recursiveValidation(v, valueTypes)

          if (not interpretatedKey) or (not interpretatedValue):
            return None
          else:
            mappedX = origin(
              **mappedX,
              **{interpretatedKey: interpretatedValue},
            )
        
        return mappedX
      
      else:
        return x if isinstance(x, type_) else None

    except Exception:
      return None
    
  else:
    from .api import _APIBase
    isDefaultValue = not inspect.isclass(type_)

    try:
      try:
        if isDefaultValue:
          interpretated = type(type_)(x)
        
        elif issubclass(type_, _APIBase):
          interpretated = type_(**x)
        
        else:
          interpretated = type_(x)

      except Exception as e:
        raise e

      if isinstance(interpretated, (type(type_) if isDefaultValue is None else type_)):
        return interpretated
      elif isDefaultValue:
        return type_
    
    except Exception as e:
      return type_ if isDefaultValue else None
