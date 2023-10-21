# Dynamically import all files in this directory

import os
import importlib

print('\nImporting modules...')

modules = [
  filename for filename in os.listdir(os.path.dirname(os.path.abspath(__file__)))
  if filename.endswith('.py') and filename != '__init__.py'
]

for filename in modules:
  filepath = os.path.dirname(os.path.realpath(__file__))

  importlib.import_module(
    '.'.join(filepath.split('/')[-2:] + [filename[:-3]])
  )

  print(f'{filename} OK')

print('\nSuccessfully imported modules\n')