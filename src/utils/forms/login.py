"""
Login form
"""

from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, SubmitField, StringField
from wtforms.validators import DataRequired, Email, Length

from typing import Optional

class LoginForm(FlaskForm):
  """
  Login Form
  """

  email       = StringField('Email', validators = [DataRequired(), Length(1, 64), Email()])
  password    = PasswordField('Password', validators = [DataRequired(), Length(1, 20)])
  remember_me = BooleanField('Keep me logged in')
  submit      = SubmitField('Log In')

  def validate(self) -> bool:
    field_validation = super().validate()
    if not field_validation: return False

    # Import at runtime to prevent circular imports
    from src.database import UserModel
    user: Optional['UserModel'] = UserModel.query.filter_by(email = self.email.data).first()

    if user is None:
      self.password.errors = ['Invalid email or password']
      return False
    
    if not user.verify_password(self.password.data):
      self.password.errors = ['Invalid email or password']
      return False
    
    return True
