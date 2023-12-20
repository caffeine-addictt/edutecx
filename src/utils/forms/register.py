from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, SubmitField, StringField
from wtforms.validators import DataRequired, Email, Length, EqualTo

from typing import Optional

class RegisterForm(FlaskForm):
  """Register Form"""

  username    = StringField('Username', validators = [DataRequired(), Length(1, 20)])
  email       = StringField('Email', validators = [DataRequired(), Length(1, 64), Email('Invalid Email', check_deliverability = True)])
  password    = PasswordField('Password', validators = [DataRequired(), Length(1, 20), EqualTo('confirm', 'Passwords do not match')])
  confirm     = PasswordField('Confirm Password', validators = [DataRequired(), Length(1, 20)])
  agree       = BooleanField('I agree to the <a href="/">privacy policy</a>', validators = [DataRequired()])
  submit      = SubmitField('Log In')

  def validate(self, *args, **kwargs) -> bool:
    field_validation = super().validate(*args, **kwargs)
    if not field_validation: return False

    # Import at runtime to prevent circular imports
    from src.database import UserModel

    user: Optional['UserModel'] = UserModel.query.filter_by(username = self.username.data).first()
    if user:
      self.password.errors = ['Username already exists']
      return False
    
    user: Optional[UserModel] = UserModel.query.filter_by(email = self.email.data).first()
    if user:
      self.password.errors = ['Email already exists']
      return False
    
    return True
