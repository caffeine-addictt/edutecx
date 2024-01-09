import re
from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField, StringField
from wtforms.validators import DataRequired, Email, Length, EqualTo



class ProfileEditForm(FlaskForm):
  """Profile form"""

  username = StringField(name = 'Username', validators = [DataRequired(), Length(5, 20)])
  email    = StringField(name = 'Email', validators = [DataRequired(), Length(1, 64), Email('Invalid Email')])
  password = PasswordField(name = 'Change Password', validators = [Length(8, 20), EqualTo('confirm', 'Passwords do not match')])
  confirm  = PasswordField(name = 'Confirm New Password', validators = [Length(1, 20)])
  submit   = SubmitField(name = 'Save Changes')
