"""
Extension for managing time
"""

import re
from typing import Union, Optional
from datetime import datetime

from .math_lib import isInteger, isFloat


def convertToTime(date : Union[str, int, float]) -> Union[int, float]:
  """
  Converts a `string 1y3mth7s`, `int 500` (read in seconds) or `float 30.6` (read in seconds) to the total number of seconds

  
  Parameters
  ----------
  `date: str | int | float`, required

  
  Returns
  -------
  `seconds: int | float`


  String Table
  ------------
  ```sh
  one_year   =   `1y`,    `1yr`,   `1year`,   `1years`
  one_month  = `1mth`, `1month`, `1months`
  one_week   =   `1w`,  `1week`,  `1weeks`
  one_day    =   `1d`,   `1day`,   `1days`
  one_hour   =   `1h`,  `1hour`,  `1hours`
  one_minute =   `1m`,   `1min`, `1minute`, `1minutes`
  one_second =    `1`,     `1s`,    `1sec`,  `1second`, `1seconds`
  ```
  """
  # We make sure int() or float() do not error for when date is the string representation of a number
  if isInteger(date) or isFloat(date):
    return float(date)
  else:
    date = str(date).lstrip().rstrip()
  
  data_table = [
    ['y', 'year', 'years', 'yr', 60*60*24*365],
    ['mth', 'month', 'months', 60*60*24*30],
    ['w', 'week', 'weeks', 60*60*24*7],
    ['d', 'day', 'days', 60*60*24],
    ['h', 'hour', 'hours', 60*60],
    ['m', 'minute', 'minutes', 'min', 60],
    ['s', 'second', 'seconds', 'sec', 1]
  ]
  
  current = False
  params = re.findall(r'\d*\D+', date.replace('_', '').strip())

  for param in params:
    param = param.lower()
    numbers = re.findall(r'\d', param)
    letters = re.findall(r'[a-zA-Z]+', param)

    if (len(numbers) < 1) or (len(letters) < 1): continue #make sure input has at least 1 letter and number

    multiplier = False
    for v in data_table:
      if letters[0] in v:
        multiplier = v[len(v) - 1]
        break
    
    if not multiplier: continue
    current = (current and (current + (int(''.join(numbers)) * multiplier))) or (int(''.join(numbers)) * multiplier)

  return current


def get() -> datetime:
  """
  Returns the current utc time

  
  Returns
  -------
  `utcnow: datetime`
  """
  return datetime.utcnow()

def skip(unixOrSec: Union[str, int, float], fromTime: Optional[datetime] = None) -> datetime:
  """
  Returns the utc time of the skipped amount

  
  Parameters
  ----------
  `unixOrSec: str | int | float`, required
    The amount of time to skip
  
  `fromTime: datetime`, optional (defaults to None)

    
  Returns
  -------
  `utcthen: datetime`
  """
  unixOrSec = convertToTime(unixOrSec)
  return datetime.fromtimestamp((fromTime or datetime.utcnow()).timestamp() + unixOrSec)

def unskip(unixOrSec: Union[str, int, float], fromTime: Optional[datetime] = None) -> datetime:
  """
  Returns the utc time of the unskipped amount

  
  Parameters
  ----------
  `unixOrSec: str | int | float`, required
    The amount of time to unskip
  
  `fromTime: datetime`, optional (defaults to None)

    
  Returns
  -------
  `utcthen: datetime`
  """
  unixOrSec = convertToTime(unixOrSec)
  return datetime.fromtimestamp((fromTime or datetime.utcnow()).timestamp() - unixOrSec)
