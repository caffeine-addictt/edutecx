"""
CDN manager for the app

Change to switch to an actual CDN upload if pushing to prod
"""

import os
import re
import uuid
import shutil

from typing import Literal
from werkzeug.datastructures import FileStorage


# Setup
UploadBaseLocation = os.path.join(os.getcwd(), 'src', 'uploads')
TextbookLocation = os.path.join(UploadBaseLocation, 'textbooks')
ImageLocation = os.path.join(UploadBaseLocation, 'images')

TextbookFileEXT = ['.pdf']
ImageFileEXT = ['.png', '.jpg', 'jpeg', '.webp']

class BadFileEXT(Exception):
  """Raised when file extension is not supported"""
  def __init__(self, message: str = 'File extension is not supported', *args, **kwargs):
    super().__init__(message, *args, **kwargs)
class FileDoesNotExistError(Exception):
  """Raised when file does not exist"""
  def __init__(self, message: str = 'File does not exist', *args, **kwargs):
    super().__init__(message, *args, **kwargs)


def _dirCheck():
  """Ensure that the upload directories exist"""
  if not os.path.isdir(UploadBaseLocation):
    os.mkdir(UploadBaseLocation)

  if not os.path.isdir(TextbookLocation):
    os.mkdir(TextbookLocation)

  if not os.path.isdir(ImageLocation):
    os.mkdir(ImageLocation)

def _get_unique_filename(dir: str, filename: str, extension: str) -> str:
  """Ensure edge case where file already exists (although unliekly as filename would be uuid, but doesn't hurt to be sure)"""
  regex = re.compile(r'[^a-zA-Z0-9-]')
  filename = regex.sub('', filename)
  while True:
    filename = regex.sub('', filename) + extension

    if os.path.exists(os.path.join(dir, filename)):
      filename = uuid.uuid4().hex
    else: return filename

def _upload(
  fileType: Literal['Image', 'Textbook'],
  file: FileStorage,
  filename: str
):
  _dirCheck()
  if not file.filename:
    raise BadFileEXT('File does not have a name')


  # Upload the file
  if fileType == 'Image':
    ext = file.filename.split('.')[-1]
    if ext not in ImageFileEXT:
      raise BadFileEXT()
    
    filename = _get_unique_filename(
      ImageLocation,
      filename,
      ext
    )

    # Save the file
    location = os.path.join(ImageLocation, filename)
    file.save(location)
    file.close()
    return location

  elif fileType == 'Textbook':
    ext = file.filename[-1]
    if ext not in TextbookFileEXT:
      raise BadFileEXT()
    
    filename = _get_unique_filename(
      TextbookLocation,
      filename,
      ext
    )

    # Save the file
    location = os.path.join(TextbookLocation, filename)
    file.save(location)
    return location


def uploadTextbook(file: FileStorage, filename: str) -> str:
  """
  Upload a textbook file to CDN

  Parameters
  ----------
  `file: FileStorage`, required
    The file data to upload

  `filename: str`, required
    The filename of the uplaoded, will overwrite if invalid


  Returns
  -------
  `Interalpath: str`
    The interal path to access the uploaded content


  Raises
  ------
  `BadFileEXT`
    Raised when the file extension is not valid for a textbook
  """
  return _upload('Textbook', file, filename)

def uploadImage(file: FileStorage, filename: str) -> str:
  """
  Upload image to CDN

  Parameters
  ----------
  `file: FileStorage`, required
    The file data to upload

  `filename: str`, required
    The filename of the uplaoded, will overwrite if invalid


  Returns
  -------
  `Interalpath: str`
    The interal path to access the uploaded content


  Raises
  ------
  `BadFileEXT`
    Raised when the file extension is not valid for an image
  """
  return _upload('Image', file, filename)


# No delete textbook method
def deleteImage(filename: str) -> None:
  _dirCheck()

  fileLocation = os.path.join(ImageLocation, filename)
  if os.path.exists(fileLocation):
    os.remove(fileLocation)

def cloneTextbook(fileLocation: str, newfilename: str) -> str:
  """Clone a textbook upload"""
  _dirCheck()

  if not os.path.exists(fileLocation):
    raise FileDoesNotExistError()

  ext = fileLocation.split('.')[-1]
  if ext not in TextbookFileEXT:
    raise BadFileEXT()
  
  newfilename = _get_unique_filename(
    TextbookLocation,
    newfilename,
    ext
  )

  newfileLocation = os.path.join(TextbookLocation, newfilename)
  shutil.copy2(fileLocation, newfileLocation)
  return newfileLocation

def updateTextbook(fileLocation: str, file: FileStorage) -> None:
  """Replace current upload with new file"""
  _dirCheck()

  if not os.path.exists(fileLocation):
    raise FileDoesNotExistError()
  
  os.remove(fileLocation)
  file.save(fileLocation)
  file.close()
