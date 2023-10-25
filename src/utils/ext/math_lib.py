"""
Extensions for math library
"""

from typing import Any


def isInteger(value: Any) -> bool:
  """
  Checks if value is an integer without raising an exception

  Parameters
  ----------
  `value: Any`, required
    The value to check

  Returns
  -------
  `isInteger: bool`
    If the value is an integer
  """
  try:
    int(value)
    return True
  except Exception:
    return False


def isFloat(value: Any) -> bool:
  """
  Checks if value is a float without raising an exception

  Parameters
  ----------
  `value: Any`, required
    The value to check

  Returns
  -------
  `isFloat: bool`
    If the value is a float
  """
  try:
    float(value)
    return True
  except Exception:
    return False