from __main__ import app # Import app from app.py

@app.route('/api')
def api_catchall():
  ...