from flask import Flask, request, render_template
from markupsafe import escape

# Registering blueprints
from api import api_handler

# Setup for merging native templates/ & static/
app = Flask(
  import_name = __name__,
  template_folder = 'pages',
  static_folder = 'pages',
  static_url_path = ''
)
app.register_blueprint(api_handler)


@app.route('/')
def home():
  return render_template('home/index.html')


if __name__ == '__main__':
  app.run(host = 'localhost', debug = True)