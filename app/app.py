from flask import Flask, request, render_template
# from flask_bootstrap import Bootstrap5
from markupsafe import escape


app = Flask(
  import_name = __name__,
  template_folder = 'pages'
)
# bootstrap = Bootstrap5(app)

@app.route('/')
def home():
  return render_template('home/index.html')#, bootstrap = bootstrap)


if __name__ == '__main__':
  app.run(host = 'localhost', debug = True)