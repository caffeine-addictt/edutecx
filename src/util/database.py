import os, shelve
from contextlib import contextmanager
from dataclasses import dataclass, field
from collections.abc import Generator

from .typeDeclarations import Identifier
from typing import (
  Callable,
  Iterable,
  Literal,
  Union
)


@dataclass(frozen = True)
class User():
  """
  # User Object
  """

  id: Identifier

  # name

  # def __init__(self, )


@dataclass(frozen = True)
class Database:
  """
  # Python Shelve Wrapper Class
  (Non-Instantiable!)

  ### Variables
  ```py
  class Alias:
    USER_DATA: str
  ```

  ### Synchronous Functions
  ```py
  def openSession(...) -> Context Manager[Shelf[any]]: ...
  def extend(...) -> None: ...
  def append(arg, ...) -> None: self.extend( tuple(arg), ... )
  ```
  """

  @dataclass(frozen = True)
  class Alias:
    """
    Database Name Aliases
    """

    USER_DATA = 'users'

  # Stop Class from being initialized
  def __init__(self) -> None:
    raise TypeError('Database Class not instantiable!')


  # Private Functions
  @staticmethod
  def _urlFor(filename: str):
    """
    Converts filename to database path

    :param: filename: str

    :return: str
    """
    return os.path.join(
      os.getcwd(),
      'app', 'util', 'DBmodels', filename
    )
  

  @staticmethod
  @contextmanager
  def openSession(
    databaseName: str,
    flag: Literal['r', 'w', 'c', 'n', 'rf', 'wf', 'cf'] = 'c',
    protocol: int | None = None,
    writeback: bool = False
  ) -> Generator[shelve.Shelf, None, None]:
    """
    Context Manager connection to shelve.open()\n
    Automatically `closes` shelve connection and `syncs` if ```writeback = True```

    ```python
    with Database().openSession('Testing') as (shelveObj: shelve.Shelf[any]):
      ...
    ```

    :param: databaseName: str
    :param: flag: _TKFlag[str] | Literal['r', 'w', 'c', 'n', 'rf', 'wf', 'cf'] = 'c'
    :param: protocall: int | None = None
    :param: writeback: bool = Falses

    :return: ContextManager[shelve.Shelf, None, None]
    """
    Shelveinstance: shelve.Shelf = shelve.open(
      Database._urlFor(databaseName),
      flag = flag,
      protocol = protocol,
      writeback = writeback
    )
    yield Shelveinstance
    Shelveinstance.close()





  @staticmethod
  def extend(
    databaseName: str,
    listDir: Callable[[shelve.Shelf], list],
    arg: Iterable[str | int]
  ) -> None:
    """
    Invokes `Database.extend()`

    :param: databaseName: str
    :param: listDir: `Function (arg: shelve.Shelf) -> list[any]`
    :param: arg: `Iterable [Generator | list | tuple]`

    :return: None
    """
    try:
      with Database.openSession(databaseName, writeback = True) as data:
        to_extend: list | None = listDir(data)
        to_extend.extend(arg)

    except AttributeError as e: raise AttributeError(e)
    except Exception: raise LookupError('Unable to locate listDir')

  @staticmethod
  def append(
    databaseName: str,
    listDir: Callable[[shelve.Shelf], list],
    arg: Union[str, int]
  ) -> None:
    """
    Invokes `Database.extend()`

    :param: databaseName: str
    :param: listDir: `Function (arg: shelve.Shelf) -> list[any]`
    :param: arg: str | int | any

    :return: None
    """
    Database.extend(databaseName, listDir, list([arg]))


      








# Database testing
if __name__ == '__main__':
  with Database.openSession(Database.Alias.USER_DATA) as data:
    data['test'] = ['hi']
    