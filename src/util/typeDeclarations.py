from dataclasses import dataclass
from uuid import uuid4


ID = str

@dataclass(init = False)
class Identifier():
  """
  # Identifier
  """

  def __init__(self) -> None:
    raise TypeError('Identifier class is not instantiable!')
  
  @staticmethod
  def _generate() -> ID:
    return ID(uuid4().hex)
  
  @staticmethod
  def new() -> ID:
    return Identifier._generate()
  
  @classmethod
  def from_string(cls, hex: str) -> ID:
    return ID(hex)