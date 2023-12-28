from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, SelectField
from wtforms.validators import DataRequired, Email, Length


class ContactForm(FlaskForm):
  """Contact Us Form"""

  form_type   = SelectField(name = 'Form Type', choices = [(1, 'Feedback'), (2, 'Bug Report'), (3, 'User Report')])
  email       = StringField(name = 'Email', validators = [DataRequired(), Length(1, 64), Email('Invalid Email', check_deliverability = True)])
  subject     = StringField(name = 'Title', validators = [DataRequired(), Length(1, 64)])
  message     = StringField(name = 'Message', validators = [DataRequired(), Length(1, 300)])
  submit      = SubmitField(name = 'Log In')

  def validate(self, *args, **kwargs) -> bool:
    field_validation = super().validate(*args, **kwargs)
    if not field_validation: return False
    
    return True
