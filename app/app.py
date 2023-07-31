from flask import Flask, request, render_template
from markupsafe import escape


app = Flask(
  import_name = __name__,
  template_folder = 'pages'
)

@app.route('/')
def home():
  return render_template('home/index.html')


if __name__ == '__main__':
  app.run(host = 'localhost', debug = True)