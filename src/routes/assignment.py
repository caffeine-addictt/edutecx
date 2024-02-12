"""
Handles assignment routes
"""

from src.database import UserModel, AssignmentModel, ClassroomModel
from src.service import auth_provider
from src.utils.http import escape_id

from flask import request, render_template, current_app as app


@app.route('/assignments')
@auth_provider.require_login
def assignments(user: UserModel):
  return render_template('(assignment)/assignment_list.html')


@app.route('/assignments/<string:id>')
@auth_provider.require_login
def assignment(user: UserModel, id: str):
  id = escape_id(id)
  assignment = AssignmentModel.query.filter(AssignmentModel.id == id).first()

  if not isinstance(assignment, AssignmentModel):
    return render_template(
      '(assignment)/assignment_error.html', message='Assignment does not exist'
    )
  if (user.privilege != 'Admin') and not assignment.classroom.is_member(user):
    return render_template(
      '(assignment)/assignment_error.html',
      message='You do not have access to this assignment',
    )

  return render_template('(assignment)/assignment.html', assignment=assignment)


@app.route('/assignments/new', methods=['GET'])
@auth_provider.require_educator(unauthorized_redirect='/pricing')
def assignment_new(_: UserModel):
  classroomID = escape_id(request.args.get('classroomID', ''))
  if not classroomID:
    return render_template(
      '(assignment)/assignment_error.html',
      message='Classroom ID not specified. Create one from the <a href="/classrooms">classrooms page</a>.',
    )

  classroom = (
    classroomID
    and ClassroomModel.query.filter(ClassroomModel.id == classroomID).first()
  )
  if not isinstance(classroom, ClassroomModel):
    return render_template(
      '(assignment)/assignment_error.html', message='Classroom does not exist'
    )

  return render_template('(assignment)/assignment_new.html')
