"""
Testing for database models
"""

from flask import Flask
from flask.testing import FlaskClient

def test_userModel(app: Flask):
  """
  Testing for User models writing to database
  """
  from src import db
  from src.database import UserModel

  with app.app_context():
    userNew = UserModel(
      email = 'user_test_user@example.com',
      username = 'user_test_user',
      password = '<PASSWORD>',
      privilege = 'User'
    )
    db.session.add(userNew)

    foundUser: UserModel | None = UserModel.query.filter(UserModel.username == 'user_test_user').first()
    isSame: bool = (foundUser is not None) and (foundUser.id == userNew.id)

    UserModel.query.filter(UserModel.id == userNew.id).delete()
    assert isSame, f'Found User is {foundUser}'

  

def test_token_User_Relationship(app: Flask):
  """
  Testing for Token-User DB Schema relationships & Token model writing to database
  """
  from src import db
  from src.database import UserModel, TokenModel

  with app.app_context():
    userNew = UserModel(
      email = 'token_test_user@example.com',
      username = 'token_test_user',
      password = '<PASSWORD>',
      privilege = 'User'
    )
    db.session.add(userNew)
    db.session.commit()

    tokenNew = TokenModel(
      user = userNew,
      token_type = 'Verification'
    )
    db.session.add(tokenNew)
    db.session.commit()


    searchedUser: UserModel | None = UserModel.query.filter(UserModel.username == 'token_test_user').first()
    searchedToken: TokenModel | None = TokenModel.query.filter(TokenModel.id == userNew.id).first()

    log = []

    # Logic
    if searchedUser is None: log.append('Unable to locate userModel after adding to session')
    if searchedToken is None: log.append('Unable to locate tokenModel after adding to session')

    if searchedUser and searchedUser.token is not None:
      if searchedUser.token.id != userNew.id: log.append('Token mapped to userModel has incorrect id')
    else:
      log.append('Token was not mapped to userModel')

    if searchedToken and searchedToken.user is not None:
      if searchedToken.user.id != tokenNew.id: log.append('User mapped to tokenModel has incorrect id')
    else:
      log.append('User was not mapped to tokenModel')


    # Cleanup
    TokenModel.query.filter(TokenModel.id == tokenNew.id).delete()
    UserModel.query.filter(UserModel.id == userNew.id).delete()
    db.session.commit()

    # Assertion
    assert len(log) == 0, '\n'.join(log)





