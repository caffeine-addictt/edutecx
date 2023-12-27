from flask_wtf import FlaskForm
from wtforms import SubmitField

class LogoutForm(FlaskForm):
  """Logout Form"""

  submit = SubmitField('Log Out')
