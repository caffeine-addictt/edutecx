import os
from src import init_app

app = init_app()

print()

# Need if statement to prevent gunicorn from attempting to run flask 2 times
if __name__ == '__main__':
  app.run(
    host = '127.0.0.1',
    port = int(os.getenv('FLASK_RUN_PORT', 8080)),
    debug = 'True' == os.getenv('FLASK_DEBUG', 'False')
  )