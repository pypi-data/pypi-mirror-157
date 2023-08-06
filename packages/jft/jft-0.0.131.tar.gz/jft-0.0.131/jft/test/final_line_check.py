from jft.directory.list_testables import f as list_testables
from jft.file.load import f as load
from jft.pf import f as pf
from jft.text_colours.danger import f as danger
from jft.text_colours.success import f as success

def f(_Pi=None):
  print('Checking final lines...', end='\r')
  _Pi = list_testables() or _Pi
  for _pi in _Pi:
    _lines = load(_pi).split('\n')
    _last_line_index = len(_lines)-1
    _line = _lines[_last_line_index]
    if _line != '': return pf(['', f'{_pi}:{_last_line_index}', danger([_line])])
  print(f"{success('PASS')} Final lines "+' '*20)

def t(): return True # TODO