from time import time
from jft.test.handle_pass import f as hp
from jft.dict.test_durations.to_tuple_list_sorted_by_duration import f as srt
from jft.directory.list_testables import f as list_testables
from os.path import getmtime
from jft.test.make_Π_to_test import f as make_Π_t
from jft.pickle.load_if_exists import f as load_pickle
from jft.file.remove import f as remove
from jft.pickle.save import f as save
from jft.strings.pyfiles.to_dict import f as pyfiles_to_dict
from jft.string.contains.function.test import f as has_t
from jft.string.contains.function.run import f as has_f
from jft.test.π_test_failed import f as π_test_failed
from jft.test.handle_fail import f as hf
from jft.text_colours.danger import f as danger
from jft.text_colours.warning import f as warn
def f(test_all=False, t_0=time()):
  Π = list_testables()
  try: prev = load_pickle('./last_modified.pickle') or set()
  except EOFError as eofe: remove('./last_modified.pickle'); prev = set()
  last_mods = {py_filename: getmtime(py_filename) for py_filename in Π}
  save(last_mods, './last_modified.pickle')
  Π_fail = set()
  _A = [_[0] for _ in srt(last_mods)[::-1]]
  _B = set(make_Π_t(Π, test_all, prev, last_mods) + list(Π_fail))
  Π_t = [a for a in _A if a in _B]
  pyfile_data = pyfiles_to_dict(Π_t)
  max_len = 0
  for π_index, π in enumerate(Π_t):
    content = pyfile_data[π]
    _m = ' '.join([
      f'[{(100*(π_index+1)/len(Π_t)):> 6.2f} % of',
      f'{π_index+1}/{len(Π_t)} files.] Checking {π}'
    ])
    max_len = max(max_len, len(_m))
    # print(f'{_m:<{max_len}}', end='\r')
    print(f'{_m:<{max_len}}')
    if not has_t(content): return hf(Π_fail, π, danger(" has no ")+warn('t()'))
    if not has_f(content): return hf(Π_fail, π, danger(" has no ")+warn('f()'))
    if π_test_failed(π): return hf(Π_fail, π, '')
  return hp(t_0, Π_t)
