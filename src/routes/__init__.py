"""
Import routes
"""

print('Importing routes...')

from . import (
  error,

  auth,
  misc,
  store,
  admin,

  cdn,
  legal,
)

print('Successfully imported routes')
