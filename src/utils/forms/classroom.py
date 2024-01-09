from flask_wtf import FlaskForm
from wtforms import BooleanField, SubmitField, StringField
from wtforms.validators import DataRequired, Length


class ClassroomCreateForm(FlaskForm):
  """Create classroom"""
  title         = StringField(name = 'Title', validators = [DataRequired(), Length(1, 64)])
  description   = StringField(name = 'Description', validators = [DataRequired(), Length(1, 300)])
  inviteEnabled = BooleanField(name = 'Invite Enabled', default = True)
  agreeToTOS    = BooleanField(name = 'I agree to the <a href="/">terms of service</a>', validators = [DataRequired()])
  submit        = SubmitField(name = 'Create')
  confirmchange = SubmitField(name = 'Confirm')

  def validate(self, *args, **kwargs) -> bool:
    field_validation = super().validate(*args, **kwargs)
    if not field_validation: return False

    # TODO: Validation
    return True


