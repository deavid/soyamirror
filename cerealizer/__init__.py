# Cerealizer
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

"""
Cerealizer -- A secure pickle-like module

The interface of the Cerealizer module is similar to Pickle. It aims to be secure and it
have no known vulnerabilities, though of course I cannot garanteed it is 100% secure.

Compared to Pickle, Cerealizer is much more secure, because it loads only a given set of
classes, and because the code is entirely in Python and much smaller (and so have
probably less bugs).

Compared to Jelly, Cerealizer is more happy with object cycles, C-defined types and tuples.
Jelly does handle them, but tuples and objects in a cycle are first created as _Tuple or
_Dereference objects ; this works for Python classes, but not with C-defined types which
expects a precise type (e.g. tuple and not _Tuple).

By default, Cerealizer support int, float, string, unicode, tuple, list, set and dict.
You can add support to any user-defined classes or data-less C-defined types, by calling
register_class(YourClass), or write custom Handler for other C-defined types.

Notice that you don't have to modify your classes to make them cerealizable.
Moreover, Cerealizer can use __getstate__ and __setstate__ methods.


IMPLEMENTATION DETAILS

Cerealizer format is quite verbose. It looks like that :

  <id of the 'root' object>
  <number of objects>
  <id of object #1>
  <classname of object #1>
  <optional data for creating object #1 (usually nothing except for tuples)>
  <id of object #2>
  <classname of object #2>
  <optional data for creating object #2 (usually nothing except for tuples)>
  [...]
  <id of object #1>
  <data of object #1 (format depend of the class of object #1)>
  <id of object #2>
  <data of object #2 (format depend of the class of object #1)>
  [...]

As you can see, the information for a given object is splitted in two parts, the first one
for object's class, and the second one for the object's data.

To avoid problems, the order of the objects is the following:

  <list, dict, set>
  <object, instance>
  <tuple, sorted by depth (max number of folded tuples)>

Objects are put after basic types (list,...), since object's __setstate__ might rely on
a list, and thus the list must be fully loaded BEFORE calling the object's __setstate__.
"""

from cStringIO import StringIO
from new       import instance

VERSION = "0.1"


def _priority_sorter(a, b): return cmp(a[0], b[0])

class Dumper(object):
  def __init__(self):
    self.objs            = []
    self.objs_id         = set()
    self.id2obj          = {}
    self.priorities_objs = [] # [(priority1, obj1), (priority2, obj2),...]
    self.obj2state       = {}
    
  def dump(self, obj, s = None):
    if not s: s = StringIO()
    
    self.collect(obj)
    self.priorities_objs.sort(_priority_sorter)
    self.objs.extend([o for (priority, o) in self.priorities_objs])
    
    print >> s, id(obj)
    print >> s, len(self.objs)
    for obj in self.objs: self.dump_obj (obj, s)
    for obj in self.objs: self.dump_data(obj, s)
    return s.getvalue()
    
  def undump(self, s):
    if isinstance(s, basestring): s = StringIO(s)
    
    first = int(s.readline())
    nb    = int(s.readline())
    for i in range(nb):
      objid = int(s.readline())
      classname = s.readline()[:-1]
      self.id2obj[objid] = HANDLERS[classname].undump_obj(classname, self, s)
      
    for i in range(nb):
      obj = self.id2obj[int(s.readline())]
      HANDLERS["%s.%s" % (obj.__class__.__module__, obj.__class__.__name__)].undump_data(obj, self, s)
      
    return self.id2obj[first]
  
  def collect(self, obj):
    """Dumper.collect(OBJ) -> bool

Collects OBJ for serialization. Returns false is OBJ is already collected; else returns true."""
    return HANDLERS["%s.%s" % (obj.__class__.__module__, obj.__class__.__name__)].collect(obj, self)
  
  def dump_obj (self, obj, s):
    HANDLERS["%s.%s" % (obj.__class__.__module__, obj.__class__.__name__)].dump_obj (obj, self, s)
    
  def dump_data(self, obj, s):
    HANDLERS["%s.%s" % (obj.__class__.__module__, obj.__class__.__name__)].dump_data(obj, self, s)
    
  def dump_ref (self, obj, s):
    """Dumper.dump_ref(OBJ, S)

Writes a reference to OBJ in file S."""
    HANDLERS["%s.%s" % (obj.__class__.__module__, obj.__class__.__name__)].dump_ref (obj, self, s)
  
  def undump_ref(self, s):
    """Dumper.undump_ref(S) -> obj

Reads a reference from file S."""
    c = s.read(1)
    if   c == "i": return int  (s.readline())
    elif c == "f": return float(s.readline())
    elif c == "s": r = s.read(int(s.readline())); s.read(1); return r
    elif c == "u": r = s.read(int(s.readline())).decode("utf8"); s.read(1); return r
    elif c == "r": return self.id2obj[int(s.readline())]
    elif c == "n": s.read(1); return None
    elif c == "b": return bool(int(s.readline()))
    else: raise ValueError("Unknown ref code '%s'!" % c)
    
    
class Handler(object):
  """Handler

A customized handler for serialization and deserialization.
You can subclass it to extend cerealization support to new object.
See also ObjHandler and InstanceHandler."""
  
  def collect(self, obj, dumper):
    """Handler.collect(obj, dumper) -> bool

Collects all the objects referenced by OBJ.
For each objects referenced by OBJ, DUMPER.collect(REFERENCED_OBJ) is called.
Returns false if OBJ is already referenced (and thus no collection should occur); else returns true.
"""
    if not id(obj) in dumper.objs_id:
      dumper.objs.append(obj)
      dumper.objs_id.add(id(obj))
      return 1
    
  def dump_obj (self, obj, dumper, s):
    """Handler.dump_obj(obj, dumper, s)

Dumps OBJ classname in file S."""
    print >> s, "%s" % id(obj)
    print >> s, "%s.%s" % (obj.__class__.__module__, obj.__class__.__name__)
    
  def dump_data(self, obj, dumper, s):
    """Handler.dump_data(obj, dumper, s)

Dumps OBJ data in file S.
If you override undump_data, you should use DUMPER.dump_ref(S) to write a referenced
object or a basic type (a string, an int,...)."""
    print >> s, "%s" % id(obj)
    
  def dump_ref (self, obj, dumper, s):
    """Handler.dump_ref(obj, dumper, s)

Write a reference to OBJ in file S.
You should not override dump_ref, since they is no corresponding 'undump_ref' that you
can override."""
    print >> s, "r%s" % id(obj)
  
  def undump_obj(self, classname, dumper, s):
    """Handler.undump_obj(classname, dumper, s)

Returns a new uninitialized (=no __init__'ed) instance of the class named CLASSNAME.
If you override undump_obj, DUMPER and file S can be used to read additional data
saved by Handler.dump_obj()."""
    
  def undump_data(self, obj, dumper, s):
    """Handler.undump_data(obj, dumper, s)

Reads the data for OBJ, from DUMPER and file S.
If you override undump_data, you should use DUMPER.undump_ref(REFERENCED_OBJ, S) to
read a reference or a basic type (=a string, an int,...)."""
  
    
class RefHandler(object):
  def collect  (self, obj, dumper)   : pass
  def dump_obj (self, obj, dumper, s): pass
  def dump_data(self, obj, dumper, s): pass
  
class NoneHandler(RefHandler):
  def dump_ref (self, obj, dumper, s): print >> s, "n"
  
class StrHandler(RefHandler):
  def dump_ref (self, obj, dumper, s): print >> s, "s%s\n%s" % (len(obj), obj)
  
class UnicodeHandler(RefHandler):
  def dump_ref (self, obj, dumper, s):
    obj = obj.encode("utf8")
    print >> s, "u%s\n%s" % (len(obj), obj)
    
class BoolHandler(RefHandler):
  def dump_ref (self, obj, dumper, s): print >> s, "b%s" % int(obj)
  
class IntHandler(RefHandler):
  def dump_ref (self, obj, dumper, s): print >> s, "i%s" % obj
  
class FloatHandler(RefHandler):
  def dump_ref (self, obj, dumper, s): print >> s, "f%s" % obj
  

def tuple_depth(t):
  return max([0] + [tuple_depth(i) + 1 for i in t if isinstance(i, tuple)])

class TupleHandler(Handler):
  def collect(self, obj, dumper):
    if not id(obj) in dumper.objs_id:
      dumper.priorities_objs.append((tuple_depth(obj), obj))
      dumper.objs_id.add(id(obj))
      
      for i in obj: dumper.collect(i)
      return 1
    
  def dump_obj (self, obj, dumper, s):
    Handler.dump_obj(self, obj, dumper, s)
    print >> s, len(obj)
    for i in obj: dumper.dump_ref(i, s)
    
  def undump_obj(self, classname, dumper, s):
    nb = int(s.readline())
    return tuple([dumper.undump_ref(s) for i in range(nb)])
  
  
class ListHandler(Handler):
  def collect(self, obj, dumper):
    if Handler.collect(self, obj, dumper):
      for i in obj: dumper.collect(i)
      return 1
    
  def dump_data(self, obj, dumper, s):
    Handler.dump_data(self, obj, dumper, s)
    print >> s, len(obj)
    for i in obj: dumper.dump_ref(i, s)
      
  def undump_obj(self, classname, dumper, s): return []
  
  def undump_data(self, obj, dumper, s):
    nb = int(s.readline())
    for i in range(nb): obj.append(dumper.undump_ref(s))
    
class SetHandler(Handler):
  def collect(self, obj, dumper):
    if Handler.collect(self, obj, dumper):
      for i in obj: dumper.collect(i)
      return 1
    
  def dump_data(self, obj, dumper, s):
    Handler.dump_data(self, obj, dumper, s)
    print >> s, len(obj)
    for i in obj: dumper.dump_ref(i, s)
      
  def undump_obj(self, classname, dumper, s): return set()
  
  def undump_data(self, obj, dumper, s):
    nb = int(s.readline())
    for i in range(nb): obj.add(dumper.undump_ref(s))
    
class DictHandler(Handler):
  def collect(self, obj, dumper):
    if Handler.collect(self, obj, dumper):
      for k, v in obj.items():
        dumper.collect(k)
        dumper.collect(v)
      return 1
    
  def dump_data(self, obj, dumper, s):
    Handler.dump_data(self, obj, dumper, s)
    print >> s, len(obj)
    for k, v in obj.items():
      dumper.dump_ref(k, s)
      dumper.dump_ref(v, s)
      
  def undump_obj(self, classname, dumper, s): return {}
  
  def undump_data(self, obj, dumper, s):
    nb = int(s.readline())
    for i in range(nb):
      k = dumper.undump_ref(s)
      v = dumper.undump_ref(s)
      obj[k] = v


class ObjHandler(Handler):
  """InstanceHandler

A Cerealizer Handler that can support any type instance (=new-style class instances, as
well as C-defined types)."""
  def __init__(self, Class):
    self.Class = Class
    
  def collect(self, obj, dumper):
    if not id(obj) in dumper.objs_id:
      dumper.priorities_objs.append((-1, obj))
      dumper.objs_id.add(id(obj))
      
      if hasattr(obj, "__getstate__"): state = obj.__getstate__()
      else:                            state = obj.__dict__
      dumper.obj2state[id(obj)] = state
      dumper.collect(state)
      return 1
    
  def dump_data(self, obj, dumper, s):
    Handler.dump_data(self, obj, dumper, s)
    dumper.dump_ref(dumper.obj2state[id(obj)], s)
    
  def undump_obj(self, classname, dumper, s): return self.Class.__new__(self.Class)
  def undump_data(self, obj, dumper, s):
    if hasattr(obj, "__setstate__"): obj.__setstate__(dumper.undump_ref(s))
    else:                            obj.__dict__ = dumper.undump_ref(s)
  
class InstanceHandler(ObjHandler):
  """InstanceHandler

A Cerealizer Handler that can support any class instance (=old-style class instances)."""
  def undump_obj(self, classname, dumper, s): return instance(self.Class)


HANDLERS = {}
def register_handler(classname, handler):
  """register_handler(classname, handler)

Registers HANDLER as a handler for class named CLASSNAME."""
  HANDLERS[classname] = handler
  
def register_class(Class):
  """register_class(Class)

Registers CLASS as a serializable and secure for serialization class.
register_class automatically create a suitable Handler for it.
By default, CLASS must be either an old-style Python class, or a new-style class (a type).
C-defined types are accepted; though if it has some C-side data, you need to write a
custom Handler.

If CLASS.Handler does exist, it is used as a handler factory (=CLASS.Handler(CLASS) is
used as handler)."""
  if hasattr(Class, "Handler"):
    HANDLERS["%s.%s" % (Class.__module__, Class.__name__)] = Class.Handler(Class)
  else:
    if issubclass(Class, object): HANDLERS["%s.%s" % (Class.__module__, Class.__name__)] = ObjHandler     (Class)
    else:                         HANDLERS["%s.%s" % (Class.__module__, Class.__name__)] = InstanceHandler(Class)
    
register_handler("__builtin__.NoneType", NoneHandler   ())
register_handler("__builtin__.str"     , StrHandler    ())
register_handler("__builtin__.unicode" , UnicodeHandler())
register_handler("__builtin__.bool"    , BoolHandler   ())
register_handler("__builtin__.int"     , IntHandler    ())
register_handler("__builtin__.float"   , FloatHandler  ())
register_handler("__builtin__.dict"    , DictHandler   ())
register_handler("__builtin__.list"    , ListHandler   ())
register_handler("__builtin__.set"     , SetHandler    ())
register_handler("__builtin__.tuple"   , TupleHandler  ())


def dump(obj, file, protocol = 0):
  """dump(obj, file, protocol = 0)

Serializes object OBJ in FILE.
PROTOCOL is unused, it exists only for Pickle ompatibility."""
  Dumper().dump(obj, file)
  
def load(file):
  """load(file) -> obj

De-serializes an object from FILE."""
  return Dumper().undump(string)

def dumps(obj, protocol = 0):
  """dumps(obj, protocol = 0) -> str

Serializes object OBJ and returns the serialized string.
PROTOCOL is unused, it exists only for Pickle ompatibility."""
  return Dumper().dump(obj)

def loads(string):
  """loads(file) -> obj

De-serializes an object from STRING."""
  return Dumper().undump(string)


def dump_class_of_module(*modules):
  """For all classes found in the given module, print the needed call to register_class."""
  class D: pass
  class O(object): pass
  
  s = set()
  
  for module in modules:
    for c in module.__dict__.values():
      if isinstance(c, type(D)) or  isinstance(c, type(O)): s.add(c)
      

  l = ['cerealizer.register_class(%s.%s)' % (c.__module__, c.__name__) for c in s]
  l.sort()
  for i in l:
    print i
      
      
if __name__ == "__main__":
  import cPickle as pickle
  s = pickle.dumps(set())
  
  print loads(s)
