"""
Handles misc routing
"""

from src.database import UserModel
from src.service import auth_provider
from src.utils.forms import ContactForm, ProfileEditForm

from flask import (
  abort,
  flash,
  request,
  render_template,
  current_app as app
)




# General routes
@app.route('/')
def index():
  return render_template('(misc)/root.html')


@app.route('/home')
@auth_provider.require_login
def home(user: UserModel):
  return render_template('(misc)/home.html', user = user)


@app.route('/profile')
@auth_provider.require_login
def profile(user: UserModel):
  form = ProfileEditForm()
  form.email.data = user.email
  form.username.data = user.username
  return render_template('(misc)/profile.html', form = form)


@app.route('/privacy-policy')
def privacy_policy():
  return render_template('(misc)/privacy_policy.html')


@app.route('/terms-of-service')
def terms_of_service():
  return render_template('(misc)/terms_of_service.html')


@app.route('/contact-us')
@auth_provider.optional_login
def contact_us(user: UserModel | None):
  form = ContactForm(request.form)

  if form.email.data == '':
    form.email.data = (user and user.email) or ''

  if form.validate_on_submit():
    ...

  return render_template('(misc)/contact_us.html', form = form)


@app.route('/up')
def up():
  return { 'status': 200 }, 200
