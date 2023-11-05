import os
from src import init_app

app = init_app()

print()

# Need if statement to prevent gunicorn from attempting to run flask 2 times
if __name__ == '__main__':
  print('As login with JWT using internal api calling, you need to run flask with threading enabled', end='\n\n')
  print('You can use gunicorn [linux/macOS], command in ./.devcontainer/Dockerfile')
  print('or waitress [windows]: docs https://github.com/Pylons/waitress/blob/main/docs/usage.rst', end='\n\n')
  print('Do note that running gunicorn within the docker container would be best for windows users')
  exit(1)
  
  app.run(
    host = os.getenv('FLASK_RUN_HOST'),
    port = int(os.getenv('FLASK_RUN_PORT', 8080)),
  )