# TOFU
# Copyright (C) 2005 Jean-Baptiste LAMY
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

import cPickle as pickle, sets
from StringIO import StringIO

SAFE_CLASSES = set([
  "copy_reg._reconstructor",
  "__builtin__.set",
  "__builtin__.object",
  ])

def safe_classes(*class_names):
  SAFE_CLASSES.update(set(class_names))
  
def find_global(module_name, class_name):
  
  if "%s.%s" % (module_name, class_name) in SAFE_CLASSES:
    return getattr(__import__(module_name, None, None, [""]), class_name)
  else:
    raise pickle.UnpicklingError("Unsecure object for unpickling: %s.%s" % (module_name, class_name))
  
def loads(data):
  u = pickle.Unpickler(StringIO(data))
  u.find_global = find_global
  return u.load()

def load(f):
  u = pickle.Unpickler(f)
  u.find_global = find_global
  return u.load()

from cPickle import dump, dumps


def dump_class_of_module(*modules):
  class D: pass
  class O(object): pass
  
  s = set()
  
  for module in modules:
    for c in module.__dict__.values():
      if isinstance(c, type(D)) or  isinstance(c, type(O)): s.add(c)
      

  l = ['  "%s.%s",' % (c.__module__, c.__name__) for c in s]
  l.sort()
  for i in l:
    print i
      
      
if __name__ == "__main__":
  import cPickle as pickle
  s = pickle.dumps(set())
  
  print loads(s)
