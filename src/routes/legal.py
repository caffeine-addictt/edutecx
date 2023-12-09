"""
Handles legal routes
"""

from src.service import auth_provider
from src.database import UserModel
from src.utils.forms import ContactForm

from typing import Optional
from flask import (
  flash,
  request,
  render_template,
  current_app as app
)

@app.route('/privacy-policy')
def privacy_policy():
  return render_template('(legal)/privacy_policy.html')

@app.route('/terms-of-service')
def terms_of_service():
  return render_template('(legal)/terms_of_service.html')

@app.route('/contact-us')
@auth_provider.optional_login
def contact_us(user: Optional[UserModel]):
  form = ContactForm(request.form)

  if form.email.data == '':
    form.email.data = (user and user.email) or ''

  if form.validate_on_submit():
    ...

  return render_template('(legal)/contact_us.html', form = form)
  