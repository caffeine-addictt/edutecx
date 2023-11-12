"""
Custom solution for threading processes and obtaining its result, which isnt supported by threading module
"""

import multiprocessing
from functools import wraps
from typing import Callable, Any, Literal, Optional, List

ThreadStatus = Literal['Idle', 'Running', 'Invoking hooks', 'Completed']


# Exceptions
class ThreadingError(Exception):
  """Base Exception class"""
  def __init__(self, message: Optional[str], *args, **kwargs) -> None:
    super().__init__(message, *args, **kwargs)

class AlreadyRunningError(ThreadingError):
  """Attempt to start a running thread"""
class StillRunningError(ThreadingError):
  """Attempt to get return value of a still running thread"""


# Main
class Thread:
  """
  Threading extension with a way to obtain its return value
  """

  thread: Optional[multiprocessing.Process]
  status: ThreadStatus
  data: Any
  hooks: List[Callable[..., None]]
  func: Callable[..., Any]

  def __init__(self, func: Callable[..., Any]) -> None:
    self.thread = None
    self.status = 'Idle'
    self.data   = None
    self.hooks  = list()
    self.func   = self._wrap_func(func)

  def _wrap_func(self, func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Wraps a function to thread
    """
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
      self.status = 'Running'
      self.data   = func(*args, **kwargs)
      self.status = 'Invoking hooks'
      self._invoke_hooks()
      self.status = 'Completed'

    return wrapper
  
  def _invoke_hooks(self) -> None:
    for hook in self.hooks:
      hook(self.data)


  @property
  def result(self) -> Any:
    if self.status in ['Completed', 'Invoking hooks']:
      return self.data
    else: raise StillRunningError('Thread is still running: %s' % self.status)

  def add_hook(self, func: Callable[..., None]) -> None:
    """
    Add hooks to run after the function has completed\n
    Will parse the returned value to it

    Examples
    --------
    ```py
    data = []
    def toThread(x, y) -> str: ...
    def update(z) -> None: data.append(z)

    a = Thread(toThread)
    a.add_hook(update)
    a.start('hi', ..., myKwarg = 'hi')
    ```
    """
    self.hooks.append(func)
  

  def start(self, *args: Any, **kwargs: Any) -> None:
    """
    Runs the thread

    Raises
    ------
    `AlreadyRunningError`
    """
    if self.thread is not None and self.thread.is_alive():
      raise AlreadyRunningError('Thread already running: %s' % self.status)
    
    self.data = None
    self.thread = multiprocessing.Process(
      target = self.func,
      args = args, 
      kwargs = kwargs,
      daemon = True
    )
    self.thread.start()
