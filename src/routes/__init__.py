"""
Import routes
"""

print('Importing routes...')

from . import (
  error,
  cdn,

  auth,
  admin,

  misc,
  store,
  classroom,
  assignment,
  submission,
  textbook
)

print('Successfully imported routes')
