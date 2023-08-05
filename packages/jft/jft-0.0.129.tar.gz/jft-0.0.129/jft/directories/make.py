from jft.directory.make import f as mkdirine
from jft.directory.remove import f as rmdirie
from os.path import exists

temp_root = './_dist_tars_remove'
temp_L = list('abc')

def setup(): mkdirine(temp_root)
def tear_down(): rmdirie(temp_root)

def t():
  setup()
  f(temp_L, temp_root)
  passed = all([exists(f'{temp_root}/{_l}') for _l in temp_L])
  tear_down()
  return passed

def f(_L, root='.'): [mkdirine(f'{temp_root}/{_l}') for _l in temp_L]