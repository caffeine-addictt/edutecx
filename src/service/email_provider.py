"""
Email Provider
"""

import re
import email_validator

from functools import wraps
from typing import Literal, TypeVar, ParamSpec, Callable, Concatenate


EmailSender: str = 'edutecx@ngjx.org'
EmailType = Literal['Verification']


T = TypeVar('T')
P = ParamSpec('P')
def _enforce_email(func: Callable[Concatenate[str, P], T]) -> Callable[Concatenate[str, P], T]:
  """
  Decorator to enforce email format with RegEx

  Email must be first argument
  """
  @wraps(func)
  def wrapper(email: str, *args: P.args, **kwargs: P.kwargs) -> T:
    regex = re.compile(r'(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)')
    if not regex.fullmatch(email):
      raise ValueError('Invalid email')
    return func(email, *args, **kwargs)
  return wrapper




@_enforce_email
def dns_check(email: str) -> bool:
  """
  Check if email is reachable

  Parameters
  ----------
  `email: str`
  """
  try:
    email_validator.validate_email(email, check_deliverability = True)
  except Exception:
    return False
  return True




@_enforce_email
def send_email(email: str, emailType: EmailType, data: dict) -> bool:
  ...
