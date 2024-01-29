"""
Testing for database models
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from typing import Callable, Any

def withCleanup(app: Flask, db: SQLAlchemy, cleanup: None | Callable[[], None] = None) -> Callable[[Callable[..., Any]], Any]:
  """
  Wrapping decorator for testing database

  handles wrapping with app and db cleanup
  """
  def decorator(func: Callable[..., Any]) -> Callable[..., None]:
    def wrapper(*args: Any, **kwargs: Any) -> None:
      with app.app_context():
        try:
          func(*args, **kwargs)
        except Exception as e:
          db.session.reset()
          db.session.rollback()
          if cleanup: cleanup(); db.session.commit()
          raise e
        finally:
          db.session.reset()
          db.session.rollback()
          if cleanup: cleanup(); db.session.commit()
    return wrapper
  return decorator




def test_userModel(app: Flask):
  """
  Testing for User models writing to database
  """
  from src import db
  from src.database import UserModel

  @withCleanup(app, db)
  def run():
    userNew = UserModel(
      email = 'user_test_user@example.com',
      username = 'user_test_user',
      password = '<PASSWORD>',
      privilege = 'Student'
    )
    db.session.add(userNew)

    foundUser: UserModel | None = UserModel.query.filter(UserModel.username == 'user_test_user').first()
    isSame: bool = (foundUser is not None) and (foundUser.id == userNew.id)

    assert isSame, f'Found User is {foundUser}'

  run()


def test_token_User_Relationship(app: Flask):
  """
  Testing for Token-User DB Schema relationships & Token model writing to database
  """
  from src import db
  from src.database import UserModel, TokenModel

  @withCleanup(app, db)
  def run():
    userNew = UserModel(
      email = 'token_test_user@example.com',
      username = 'token_test_user',
      password = '<PASSWORD>',
      privilege = 'Educator'
    )
    db.session.add(userNew)

    tokenNew = TokenModel(
      user = userNew,
      token_type = 'Verification'
    )
    db.session.add(tokenNew)


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

    # Assertion
    assert len(log) == 0, '\n'.join(log)

  run()


def test_classroom_user_relationship(app: Flask):
  """
  Testing for User-Classroom DB Schema relationships & Classroom model writing to database
  """
  from src import db
  from src.database import UserModel, ClassroomModel

  def clean():
    UserModel.query.filter(UserModel.username == 'classroom_test_user').delete()
    UserModel.query.filter(UserModel.username == 'classroom_test2_user').delete()
    UserModel.query.filter(UserModel.username == 'classroom_test3_user').delete()
    ClassroomModel.query.filter(ClassroomModel.title == 'testing').delete()

  @withCleanup(app, db, clean)
  def run():
    userOne = UserModel(
      email = 'classroom_test_user@example.com',
      username = 'classroom_test_user',
      password = '<PASSWORD>',
      privilege = 'Student'
    )
    db.session.add(userOne)
    db.session.commit()

    userTwo = UserModel(
      email = 'classroom_test_user2@example.com',
      username = 'classroom_test2_user',
      password = '<PASSWORD>',
      privilege = 'Educator'
    )
    db.session.add(userTwo)
    db.session.commit()

    userThree = UserModel(
      email = 'classroom_test_user3@example.com',
      username = 'classroom_test3_user',
      password = '<PASSWORD>',
      privilege = 'Student'
    )
    db.session.add(userThree)
    db.session.commit()

    classNew = ClassroomModel(
      owner = userOne,
      title = 'testing',
      description = 'desc'
    )
    db.session.add(classNew)
    db.session.commit()

    classNew.add_educators(userTwo)
    classNew.add_students(userThree)
    db.session.commit()


    # Check
    foundClassroom: ClassroomModel | None = ClassroomModel.query.filter(ClassroomModel.id == classNew.id).first()

    assert isinstance(foundClassroom, ClassroomModel)

    assert foundClassroom.members
    assert len(foundClassroom.members) == 2

    assert foundClassroom.students
    assert len(foundClassroom.students) == 1

    assert foundClassroom.educators
    assert len(foundClassroom.educators) == 1

  run()

