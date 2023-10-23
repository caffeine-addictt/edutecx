"""
Dynamically import modules

imports up to 1 directory deep if it contains __init__.py
"""

import os
import importlib

print('Importing modules...')

dirPath: str = os.path.dirname(os.path.abspath(__file__))

for fileName in os.listdir(dirPath):
  # Escape self import
  if fileName in ['__init__.py', '__pycache__']: continue
  
  absFilePath: str = os.path.join(dirPath, fileName)
  isDir: bool = os.path.isdir(absFilePath)

  if isDir and not os.path.isfile(os.path.join(absFilePath, '__init__.py')):
    print(f'{fileName} Not a Package, Skipping')
    continue

  # File/Directory is a python package, import it
  relativePath: str = '.'.join(absFilePath.split('/')[-3:])
  
  if not isDir:
    relativePath = relativePath[:-3]

  importlib.import_module(relativePath)
  print(f'{fileName} OK')

print('Successfully imported modules')
