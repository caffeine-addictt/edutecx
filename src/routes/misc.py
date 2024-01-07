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
@auth_provider.optional_login
def index(user: UserModel | None):
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
  return render_template(
    '(misc)/profile.html',
    form = form,
    user_id = str(user.id),
    profile_uri = user.profile_image.uri if user.profile_image else ''
  )


@app.route('/privacy-policy')
@auth_provider.optional_login
def privacy_policy(user: UserModel | None):
  return render_template('(misc)/privacy_policy.html')


@app.route('/terms-of-service')
@auth_provider.optional_login
def terms_of_service(user: UserModel | None):
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
@auth_provider.optional_login
def up(user: UserModel | None):
  return { 'status': 200 }, 200
