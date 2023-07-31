import shelve
from contextlib import contextmanager
from collections.abc import Generator

class Database:
  # Private Variables
  __databaseInstance: None | 'Database'
  __client: dict[str: str | int | float] = {
    'databaseName': 'Testing_0001'
  }

  def __new__(cls: 'Database', *args, **kwargs) -> 'Database':
    """
    Takes care of making sure only 1 class of Database can exist,
    and if instantiated again, returns the cached class
    """
    cls.__databaseInstance = cls.__databaseInstance or super().__new__(cls)
    return cls.__databaseInstance
  
  def __init__(self) -> None:
    pass





  @contextmanager
  def openSession(self, flag: str = 'c', protocol: int | None = None, writeback: bool = False ) -> Generator[shelve.Shelf, None, None]:
    """
    Context Manager connection to shelve.open()\n
    Automatically `closes` shelve connection and `syncs` if ```writeback = True```

    ```
    with Database().openSession() as (shelveObj: shelve.Shelf[any]) :
      ...
    ```

    :param: flag: _TKFlag[str] = 'c'
    :param: protocall: int | None = None
    :param: writeback: bool = Falses

    :return: ContextManager[shelve.Shelf, None, None]
    """
    Shelveinstance: shelve.Shelf = shelve.open(
      self.__client['databaseName'],
      flag = flag,
      protocol = protocol,
      writeback = writeback
    )
    yield Shelveinstance
    Shelveinstance.close()

  





# Database initial startup
Database()