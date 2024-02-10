"""
Email Provider
"""

import os
import re
import resend
import email_validator

from src.utils.api import _APIBase
from flask import render_template
from dataclasses import dataclass

from functools import wraps
from typing import Literal, Union, TypeVar, ParamSpec, Callable, Concatenate, overload


EmailSender: str = 'contact@edutecx.ngjx.org'
EmailType = Literal['Verification', 'Contact']


T = TypeVar('T')
P = ParamSpec('P')


def _enforce_email(
  func: Callable[Concatenate[str, P], T],
  ) -> Callable[Concatenate[str, P], T]:
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
    email_validator.validate_email(email, check_deliverability=True)
  except Exception:
    return False
  return True


@overload
def send_email(email: str, emailType: Literal['Verification'], data: 'VerificationEmailData') -> Literal[True] | tuple[Literal[False], str]:
  """
  Send verification email

  Parameters
  ----------
  `email: str`
  `emailType: Verification`
  `data: VerificationEmailData`
  """
  ...

@overload
def send_email(email: str, emailType: Literal['Contact'], data: 'ContactEmailData') -> Literal[True] | tuple[Literal[False], str]:
  """
  Send contact email

  Parameters
  ----------
  `email: str`
  `emailType: Contact`
  `data: ContactEmailData`
  """
  ...

@_enforce_email
def send_email(
  email: str, emailType: EmailType, data: Union['VerificationEmailData', 'ContactEmailData']
  ) -> Literal[True] | tuple[Literal[False], str]:
  try:
    match emailType:
      case 'Verification':
        assert isinstance(data, VerificationEmailData)

        if os.getenv('ENV') == 'development':
          from flask import current_app as app, request

          app.logger.info(
            'Emails are not sent in development.'
              + f' Go to {data.cta_link.replace("https://edutecx.ngjx.org/", request.root_url)} to verify your account'
          )
          return True

        resend.Emails.send(
          {
            'from': f'EduTecX Team <{EmailSender}>',
            'to': [email],
            'subject': 'Email Verification',
            'text': f'Dear {data.username},\n\nThank you for registering with EduTecX! Please click the following link to verify your account:\n\n{data.cta_link}\n\nIf you did not register with EduTecX, please ignore this email.\n\nBest regards,\nThe EduTecX Team',
            'html': render_template('email/verification.html', **data.to_dict()),
          }
        )
      
      case 'Contact':
        assert isinstance(data, ContactEmailData)

        # Escape html in text
        data.subject = data.subject.replace('<', '&lt;').replace('>', '&gt;')
        data.body = data.body.replace('<', '&lt;').replace('>', '&gt;')

        # if os.getenv('ENV') == 'development':
        #   from flask import current_app as app, request
        #   app.logger.info('Emails are not sent in development.')
        #   return True

        resend.Emails.send(
          {
            'from': 'Contact @ EduTecX <feedback@edutecx.ngjx.org>',
            'to': [EmailSender],
            'subject': f'{data.preheader}: {data.subject}',
            'text': data.body,
            'html': render_template('email/contact.html', **data.to_dict()),
          }
        )

      case _:
        raise ValueError('Invalid email type')

    return True
  except Exception as e:
    return False, str(e)


# Email DATA #
@dataclass
class VerificationEmailData(_APIBase):
  """
  Verification Email Data

  Parameters
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


@dataclass
class ContactEmailData(_APIBase):
  """
  Contact Email Data

  Parameters
  ---------
  response_type: Response type
  email: Email of the user
  subject: Subject of the email
  body: Body of the email
  preheader: str = 'Contact response: <TYPE>'
  cta_link: CTA link
  cta_text: CTA text
  footer_one: First Footer text
  footer_two_a: Second Footer text
  footer_two_link: Second Footer link
  footer_two_b: Second Footer text wrapped in `<a />`
  footer_three: Third Footer text wrapped in `<a />`
  footer_three_link: Third Footer link
  """

  response_type: Literal['General', 'Bug Report', 'Feature Request', 'Other']
  email: str
  subject: str
  body: str

  preheader: str = 'Contact response: <TYPE>'
  cta_link: str = 'mailto:'
  cta_text: str = 'Reply Here'

  footer_one: str = '© 2024 EduTecX. All rights reserved.'
  footer_two_a: str = 'Wish to learn more?'
  footer_two_link: str = 'https://edutecx.ngjx.org'
  footer_two_b: str = 'Visit our website.'
  footer_three: str = 'Powered by EduTecX.'
  footer_three_link: str = 'https://edutecx.ngjx.org'
