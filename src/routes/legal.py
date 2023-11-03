"""
Handles legal routes
"""

from src.utils.forms import ContactForm
from flask import (
  g,
  flash,
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
def contact_us():
  user = g.current_user
  form = ContactForm()

  if form.email.data == '':
    form.email.data = (user.is_authenticated and user.email) or ''

  if form.validate_on_submit():
    ...

  return render_template('(legal)/contact_us.html', form = form)
  