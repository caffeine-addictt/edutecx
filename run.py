import os


# Load .env variables
from dotenv import load_dotenv
load_dotenv()

print('\nImported environment variables')


from src.app import app

if __name__ == '__main__':
  app.run(
    host = '127.0.0.1',
    port = int(os.getenv('PORT', '8080')),
    debug = True
  )