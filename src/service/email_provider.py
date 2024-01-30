"""
Email Provider
"""

import re
import resend
import email_validator

from src.utils.api import _APIBase
from flask import render_template
from dataclasses import dataclass

from functools import wraps
from typing import Literal, TypeVar, ParamSpec, Callable, Concatenate


EmailSender: str = 'contact@edutecx.ngjx.org'
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
def send_email(email: str, emailType: EmailType, data: 'VerificationEmailData') -> bool:
  """
  Send email

  Parameters
  ----------
  `email: str`
  `emailType: Verification`
  `data: VerificationEmailData`
  """
  try:
    match emailType:
      case 'Verification':
        resend.Emails.send({
          'from': f'EduTecX Team <{EmailSender}>',
          'to': [email],
          'subject': 'Email Verification',
          'text': f'Dear {data.username},\n\nThank you for registering with EduTecX! Please click the following link to verify your account:\n\n{data.cta_link}\n\nIf you did not register with EduTecX, please ignore this email.\n\nBest regards,\nThe EduTecX Team',
          'html': render_template('email/verification.html', **data.to_dict()),
        })
    return True
  except Exception:
    return False




# Email DATA #
@dataclass
class VerificationEmailData(_APIBase):
  """
  Verification Email Data

  Paramters
  ---------
  title: Fills the `<title />` tag in `<head />`
  preheader: Some customers will see this as a preview text
  username: Username of the user
  pre_cta: Text to be shown before the CTA
  cta_link: CTA link
  cta_text: CTA text
  post_cta: Text to be shown after the CTA
  salutation: The salutation
  footer_one: First Footer text
  footer_two_a: Second Footer text
  footer_two_link: Second Footer link
  footer_two_b: Second Footer text wrapped in `<a />`
  footer_three: Third Footer text wrapped in `<a />`
  footer_three_link: Third Footer link
  """
  username: str
  title: str = 'Verify Your EduTecX Email'
  preheader: str = 'Welcome to EduTecX, verify your email to get started!'
  pre_cta: str = 'Thank you for registering with EduTecX! Please click the following link to verify your account:'
  cta_link: str = 'https://edutecx.ngjx.org/verify/'
  cta_text: str = 'Verify Here'
  post_cta: str = 'If you did not register with EduTecX, please ignore this email.'
  salutation: str = 'Welcome aboard! - The EduTecX Team'
  footer_one: str = '© 2024 EduTecX. All rights reserved.'
  footer_two_a: str = 'Wish to learn more?'
  footer_two_link: str = 'https://edutecx.ngjx.org'
  footer_two_b: str = 'Visit our website.'
  footer_three: str = 'Powered by EduTecX.'
  footer_three_link: str = 'https://edutecx.ngjx.org'
