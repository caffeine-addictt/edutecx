from flask import Blueprint, render_template
from util.database import Database

api_handler = Blueprint(
  name = 'api_handler',
  import_name = __name__
)

@api_handler.route('/api')
def api_catchall():
  return render_template('')