from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, SubmitField, StringField
from wtforms.validators import DataRequired, Email, Length

from typing import Optional

class LoginForm(FlaskForm):
  """Login Form"""

  email       = StringField('Email', validators = [DataRequired(), Length(1, 64), Email()])
  password    = PasswordField('Password', validators = [DataRequired(), Length(1, 20)])
  remember_me = BooleanField('Keep me logged in')
  submit      = SubmitField('Log In')

  def validate(self, *args, **kwargs) -> bool:
    field_validation = super().validate(*args, **kwargs)
    if not field_validation: return False
    
    return True
