# Password manager module
import bcrypt

"""
Password Handling Roadmap

Client enters plaintext
Encrypt with client's public key
Encrypted text is sent to the server
Encrypted text is decoded with clients private key to plaintext
Plaintext is then encoded to utf8 in  _encode()
Encoded text is then hashed
Hash is then stored

"""

def _encode(toEncode: str | bytes) -> bytes:
  """
  Encodes string for hashing/comparison
  Utilises utf8

  Parameters
  ----------
  toEncode : str | bytes, required
  
  Returns
  -------
  encoded : bytes
    Byte-string representation of the utf8 encoded input

  Raises
  ------
  TypeError
    If the toEncode parameter is not of a valid type
  """
  assert(isinstance(toEncode, (str, bytes)))

  encoded: bytes
  if (isinstance(toEncode, str)): encoded = toEncode.encode()
  else: encoded = toEncode
  
  return encoded





def hash_password(password: str | bytes) -> bytes:
  """
  Hashes Password
  Follows encryption conventions with sha256

  Parameters
  ----------
  password : str, required
    Should be in plaintext
  
    
  Returns
  -------
  HashedPassword : bytes
    Byte-string representation of the fully salted password


  Raises
  ------
  TypeError
    If the password parameter is of a valid type
  """
  assert(isinstance(password, (str, bytes)))
  
  encoded: bytes = _encode(password)
  return bcrypt.hashpw(
    password = encoded,
    salt = bcrypt.gensalt()
  )





def compare_password(password: str | bytes, hashed: bytes) -> bool:
  """
  Hashes Password
  Follows encryption conventions with sha256

  Parameters
  ----------
  password : str, required
    Should be in plaintext, will be encoded within the function.

  hashed : bytes, required
    Should be the byte representation of the hashed password to comapre against
  
    
  Returns
  -------
  Password is equal : bool
    Byte-string representation of the fully salted password


  Raises
  ------
  TypeError
    If the password or hashed parameter is of a valid type
  """
  assert(isinstance(password, (str, bytes)))
  assert(isinstance(hashed, bytes))

  encoded: bytes = _encode(password)
  return bcrypt.checkpw(
    password = encoded,
    hashed_password = hashed
  )
