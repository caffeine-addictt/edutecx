"""
CDN manager for the app

Change to switch to an actual CDN upload if pushing to prod
"""

import io
import os
import re
import uuid
from cloudinary import uploader
from pypdf import PdfReader, PdfWriter

from typing import Literal, Optional, overload
from werkzeug.datastructures import FileStorage


# Setup
ENV = os.getenv('ENV', '')
Cloudinary_Folders = {
  'Image': 'image-uploads',
  'Textbook': 'textbook-uploads',
  'Submission': 'submission-uploads'
}

UploadBaseLocation = os.path.join(os.getcwd(), 'src', 'uploads')

CopyrightNoticeLocation = os.path.join(UploadBaseLocation, 'copyright.pdf')
SubmissionUpload = os.path.join(UploadBaseLocation, 'SubmissionUpload')
TextbookLocation = os.path.join(UploadBaseLocation, 'textbooks')
ImageLocation = os.path.join(UploadBaseLocation, 'images')

TextbookFileEXT = ['pdf']
ImageFileEXT = ['png', 'jpg', 'jpeg']
SubmissionFileEXT = ['pdf', 'txt', 'docx', 'doc', 'odt']

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
  if ENV == 'production': return

  if not os.path.isdir(UploadBaseLocation):
    os.mkdir(UploadBaseLocation)

  if not os.path.isdir(SubmissionUpload):
    os.mkdir(SubmissionUpload)

  if not os.path.isdir(TextbookLocation):
    os.mkdir(TextbookLocation)

  if not os.path.isdir(ImageLocation):
    os.mkdir(ImageLocation)




def _injectCopyright(file: PdfReader) -> PdfWriter:
  """Injects copyright notice"""

  writer = PdfWriter()
  writer.add_page(PdfReader(CopyrightNoticeLocation).pages[0])
  writer.append_pages_from_reader(file)
  return writer


@overload
def _get_unique_filename() -> str:
  """For production"""
  ...

@overload
def _get_unique_filename(dir: str, filename: str, extension: str) -> str:
  """Ensure edge case where file already exists (although unliekly as filename would be uuid, but doesn't hurt to be sure)"""
  ...

def _get_unique_filename(dir: Optional[str] = None, filename: Optional[str] = None, extension: Optional[str] = None) -> str:
  if ENV == 'production':
    return uuid.uuid4().hex
  
  if not dir or not filename or not extension:
    raise ValueError('dir, filename, and extension are required for development upload')

  regex = re.compile(r'[^a-zA-Z0-9-]')
  filename = regex.sub('', filename)
  while True:
    filename = f'{regex.sub("", filename)}.{extension}'

    if os.path.exists(os.path.join(dir, filename)):
      filename = uuid.uuid4().hex
    else: return filename




def _development_upload(
  fileType: Literal['Image', 'Textbook', 'Submission'],
  file: FileStorage,
  filename: str
):
  _dirCheck()
  if not file.filename:
    raise BadFileEXT('File does not have a name')
  
  ext = file.filename.split('.')[-1]

  # Upload the file
  match fileType:
    case 'Image':
      if ext not in ImageFileEXT:
        raise BadFileEXT(f'{ext} is not supported')
      
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

    case 'Textbook':
      if ext not in TextbookFileEXT:
        raise BadFileEXT()
      
      filename = _get_unique_filename(
        TextbookLocation,
        filename,
        ext
      )

      # Inject copyright notice
      writer = _injectCopyright(PdfReader(file.stream))

      location = os.path.join(TextbookLocation, filename)
      with open(location, 'wb') as out:
        writer.write(out)
        
      return location
    
    case 'Submission':
      if ext not in SubmissionFileEXT:
        raise BadFileEXT()
      
      filename = _get_unique_filename(
        SubmissionUpload,
        filename,
        ext
      )

      location = os.path.join(SubmissionUpload, filename)
      file.save(location)
      file.close()
      return location


def _production_upload(
  fileType: Literal['Image', 'Textbook', 'Submission'],
  file: FileStorage
):
  updatedFile = None

  file.filename = _get_unique_filename()

  if fileType == 'Textbook':
    updatedFile = io.BytesIO(file.stream.read())
    _injectCopyright(PdfReader(file.stream)).write_stream(updatedFile)

  res = uploader.upload(
    updatedFile or file,
    folder = Cloudinary_Folders[fileType],
    resource_type = 'image'
  )
  return res['public_id']




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
  return _production_upload('Textbook', file) if ENV == 'production' else _development_upload('Textbook', file, filename)

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
  return _production_upload('Image', file) if ENV == 'production' else _development_upload('Image', file, filename)

def uploadSubmission(file: FileStorage, filename: str) -> str:
  """
  Upload submission to CDN

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
  return _production_upload('Submission', file) if ENV == 'production' else _development_upload('Submission', file, filename)




def deleteImage(filename: str) -> None:
  _dirCheck()

  fileLocation = os.path.join(ImageLocation, filename)
  if os.path.exists(fileLocation):
    os.remove(fileLocation)




def deleteFile(fileLocation: str) -> None:
  """
  Delete file
  
  Parameters
  ----------
  `fileLocation: str`, required
    The iuri of the file to delete
  """
  _dirCheck()

  if not os.path.exists(fileLocation):
    raise FileDoesNotExistError()
  
  os.remove(fileLocation)
