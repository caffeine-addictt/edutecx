"""
Handles misc routing
"""

from src.database import UserModel
from src.service import auth_provider, email_provider
from src.utils.forms import ProfileEditForm
from src.utils.api import ContactRequest, GenericReply
from src.utils.http import HTTPStatusCode

from flask import request, render_template, current_app as app


# General routes
@app.route('/')
@auth_provider.optional_login
def index(user: UserModel | None):
  return render_template('(misc)/root.html')


@app.route('/home')
@auth_provider.require_login
def home(user: UserModel):
  return render_template('(misc)/home.html', user=user)


@app.route('/profile')
@auth_provider.require_login
def profile(user: UserModel):
  form = ProfileEditForm()
  form.email.data = user.email
  form.username.data = user.username
  return render_template(
    '(misc)/profile.html',
    form=form,
    user_id=str(user.id),
    profile_uri=user.profile_image.uri if user.profile_image else '',
  )


@app.route('/privacy-policy')
@auth_provider.optional_login
def privacy_policy(user: UserModel | None):
  return render_template('(misc)/privacy_policy.html')


@app.route('/terms-of-service')
@auth_provider.optional_login
def terms_of_service(user: UserModel | None):
  return render_template('(misc)/terms_of_service.html')


@app.route('/contact-us', methods=['GET', 'POST'])
@auth_provider.optional_login
def contact_us(user: UserModel | None):
  if request.method == 'POST':
    req = ContactRequest(request)

    if req.email == 'None':
      return GenericReply(
        message='Missing email', status=HTTPStatusCode.BAD_REQUEST
      ).to_dict(), HTTPStatusCode.BAD_REQUEST

    if req.message == 'None':
      return GenericReply(
        message='Missing message', status=HTTPStatusCode.BAD_REQUEST
      ).to_dict(), HTTPStatusCode.BAD_REQUEST

    if not email_provider.dns_check(req.email):
      return GenericReply(
        message='Email is invalid and/or cannot be reached',
        status=HTTPStatusCode.BAD_REQUEST,
      ).to_dict(), HTTPStatusCode.BAD_REQUEST

    try:
      res = email_provider.send_email(
        req.email,
        emailType='Contact',
        data=email_provider.ContactEmailData(
          response_type=req.type,
          email=req.email,
          subject=req.subject,
          body=req.message,
          preheader=f'Contact response: {req.type}',
          cta_link=f'mailto:{req.email}',
        ),
      )

      if res is not True:
        raise Exception(res[1])

    except Exception as e:
      return GenericReply(
        message=str(e), status=HTTPStatusCode.INTERNAL_SERVER_ERROR
      ).to_dict(), HTTPStatusCode.INTERNAL_SERVER_ERROR

    return GenericReply(
      message='Successfully sent message', status=HTTPStatusCode.OK
    ).to_dict(), HTTPStatusCode.OK

  return render_template('(misc)/contact_us.html')


@app.route('/up')
@auth_provider.optional_login
def up(user: UserModel | None):
  return {'status': 200}, 200
