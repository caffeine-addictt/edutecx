from flask import Flask

app = Flask(
  import_name = __name__,
  # template_folder = '/templates/',
  # static_folder = '/static/',
  # static_url_path = '/src/static/'
)

# Import modules
from . import modules