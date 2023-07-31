from flask import Flask, request
from markupsafe import escape


app = Flask(__name__)

@app.route('/')
def hello(): ...


if __name__ == '__main__':
  app.run()