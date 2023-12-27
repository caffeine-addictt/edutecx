import re
from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, SubmitField, StringField
from wtforms.validators import DataRequired, Email, Length, EqualTo

class RegisterForm(FlaskForm):
  """Register Form"""

  username    = StringField('Username', validators = [DataRequired(), Length(5, 20)])
  email       = StringField('Email', validators = [DataRequired(), Length(1, 64), Email('Invalid Email')])
  password    = PasswordField('Password', validators = [DataRequired(), Length(8, 20), EqualTo('confirm', 'Passwords do not match')])
  confirm     = PasswordField('Confirm Password', validators = [DataRequired(), Length(1, 20)])
  agree       = BooleanField('I agree to the <a href="/">privacy policy</a>', validators = [DataRequired()])
  submit      = SubmitField('Register')

  def validate(self, *args, **kwargs) -> bool:
    field_validation = super().validate(*args, **kwargs)
    if not field_validation: return False

    # Username
    if not self.username.data: return False
    if not re.match(r'^[a-zA-Z]$', self.username.data[0]):
      self.username.errors = ['Username needs to start with letter']
      return False
    if not re.match(r'^.{5,20}$', self.username.data):
      self.username.errors = ['Username needs to be between 5 to 20 charcters long inclusive of 5 and 20']
      return False
    if not re.match(r'^[a-zA-Z0-9_-]+$', self.username.data):
      self.username.errors = ['Username can only contain letters, digits, _ and -']
      return False
    
    # Password
    if not self.password.data: return False
    if not re.match(r'.{8,20}', self.password.data):
      self.password.errors = ['Password needs to be between 8 to 20 characters long, inclusive of 8 and 20']
      return False
    if not re.match(r'^.*?[A-Z].*$', self.password.data):
      self.password.errors = ['Password needs to contain at least 1 upper case letter']
      return False
    if not re.match(r'^.*?[a-z].*$', self.password.data):
      self.password.errors = ['Password needs to contain at least 1 lower case letter']
      return False
    if not re.match(r'^.*?[0-9].*$', self.password.data):
      self.password.errors = ['Password needs to contain at least 1 digit']
      return False
    if not re.match(r'^.*?[?!@$%^#&*-].*$', self.password.data):
      self.password.errors = ['Password needs to contain at least 1 special character ?!@$%^#&*-']
      return False
    
    return True
