import os
from src import init_app

if __name__ == '__main__':
  app = init_app()
  app.run(
    host = '127.0.0.1',
    port = int(os.getenv('FLASK_RUN_PORT', 8080)),
    debug = 'True' == os.getenv('FLASK_DEBUG', 'False')
  )