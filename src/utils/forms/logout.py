"""
Logout form
"""

from flask_wtf import FlaskForm
from wtforms import SubmitField

class LogoutForm(FlaskForm):
  """
  Logout Form
  """

  submit = SubmitField('Log Out')

  def validate(self, *args, **kwargs) -> bool:
    field_validation = super().validate(*args, **kwargs)
    if not field_validation: return False

    return True
