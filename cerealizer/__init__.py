# Cerealizer
# Copyright (C) 2005-2006 Jean-Baptiste LAMY
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

"""Cerealizer -- A secure Pickle-like module

The interface of the Cerealizer module is similar to Pickle, and it supports
__getstate__ and __setstate__.

Cerealizer supports int, float, string, unicode, tuple, list, set, dict, old-style and new-style
class instances. C-defined types are supported but saving the C-side data may require to write
a specific Handler or a __getstate__ and __setstate__ pair.

You have to register the class you want to serialize, by calling cerealizer.register(YourClass).
Cerealizer can be considered as secure AS LONG AS YourClass.__new__, YourClass.__getstate__,
YourClass.__setstate__ and YourClass.__del__ are secure. These methods are the only one Cerealizer
may call. For a higher security, Cerealizer maintains its own reference to __new__, __getstate__
and __setstate__ (__del__ can only be called indirectly).

Cerealizer doesn't aim at producing Human-readable files. About performances, Cerealizer is
really fast and, when powered by Psyco, it may even beat cPickle! Although Cerealizer is
implemented in less than 300 lines of pure-Python code (which is another reason for Cerealizer
to be secure, since less code means less bugs :-).

Compared to Pickle (cPickle):
 - Cerealizer is secure
 - Cerealizer achieves similar performances (using Psyco)
 - Cerealizer requires you to declare the serializable classes

Compared to Jelly (from TwistedMatrix):
 - Cerealizer is faster
 - Cerealizer generates smaller files
 - Cerealizer does a better job with object cycles, C-defined types and tuples (*)
 - Cerealizer files are not Human readable

(*) Jelly handles them, but tuples and objects in a cycle are first created as _Tuple or
_Dereference objects; this works for Python classes, but not with C-defined types which
expects a precise type (e.g. tuple and not _Tuple).



IMPLEMENTATION DETAILS

GENERAL FILE FORMAT STRUCTURE

Cerealizer format is simple but quite surprising. At is a "double flat list" format.
It looks like that :

  <magic code (currently cereal1)>\\n
  <number of objects>\\n
  <classname of object #0>\\n
  <optional data for creating object #0 (currently nothing except for tuples)>
  <classname of object #0>\\n
  <optional data for creating object #0 (currently nothing except for tuples)>
  [...]
  <data of object #0 (format depend of the type of object #1)>
  <data of object #0 (format depend of the type of object #1)>
  [...]
  <reference to the 'root' object>

As you can see, the information for a given object is splitted in two parts, the first one
for object's class, and the second one for the object's data.

To avoid problems, the order of the objects is the following:

  <list, dict, set>
  <object, instance>
  <tuple, sorted by depth (=max number of folded tuples)>

Objects are put after basic types (list,...), since object's __setstate__ might rely on
a list, and thus the list must be fully loaded BEFORE calling the object's __setstate__.


DATA (<data of object #n> above)

The part <data of object #n> saves the data of object #n. It may contains reference to other data
(see below, in Cerealizer references include reference to other objects but also raw data like int).

 - an object           is saved by :  <reference to the object state (the value returned by object.__getstate__() or object.__dict__)>
                                      e.g. 'r7\\n' (object #7 being e.g. the __dict__).

 - a  list or a set    is saved by :  <number of item>\\n
                                      <reference to item #0>
                                      <reference to item #1>
                                      [...]
                                      e.g. '3\\ni0\\ni1\\ni2\\n' for [0, 1, 2]

 - a  dict             is saved by :  <number of item>\\n
                                      <reference to value #0>
                                      <reference to key #0>
                                      <reference to value #1>
                                      <reference to key #1>
                                      [...]


REFERENCES (<reference to XXX> above)

In Cerealizer a reference can be either a reference to another object beign serialized in the
same file, or a raw value (e.g. an integer).
 - an int              is saved by e.g. 'i187\\n'
 - a  float            is saved by e.g. 'f1.07\\n'
 - a  bool             is saved by      'b0' or 'b1'
 - a  string           is saved by e.g. 's5\\nascii' (where 5 is the number of characters)
 - an unicode          is saved by e.g. 'u4\\nutf8'  (where 4 is the number of characters)
 - an object reference is saved by e.g. 'r3\\n'      (where 3 means reference to object #3)
 -    None             is saved by      'n'
"""

__alls__ = ["load", "dump", "loads", "dumps", "freeze_configuration", "register"]
VERSION = "0.2"

import logging
logger = logging.getLogger("cerealizer")
#logging.basicConfig(level=logging.INFO)

from cStringIO import StringIO
from new       import instance

def _priority_sorter(a, b): return cmp(a[0], b[0])

class Dumper(object):
  def dump(self, root_obj, s):
    self.objs            = []
    self.objs_id         = set()
    self.priorities_objs = [] # [(priority1, obj1), (priority2, obj2),...]
    self.obj2state       = {}
    self.obj2newsargs    = {}
    self.id2id           = {}
    
    _HANDLERS_[root_obj.__class__].collect(root_obj, self)
    self.priorities_objs.sort(_priority_sorter)
    self.objs.extend([o for (priority, o) in self.priorities_objs])
    
    s.write("cereal1\n%s\n" % len(self.objs))
    
    i = 0
    for obj in self.objs:
      self.id2id[id(obj)] = i
      i += 1
    for obj in self.objs: _HANDLERS_[obj.__class__].dump_obj (obj, self, s)
    for obj in self.objs: _HANDLERS_[obj.__class__].dump_data(obj, self, s)
      
    _HANDLERS_[root_obj.__class__].dump_ref(root_obj, self, s)
    
  def undump(self, s):
    if s.read(8) != "cereal1\n": raise ValueError("Not a cerealizer file!")
    
    nb = int(s.readline())
    self.id2obj = [ None ] * nb  # DO NOT DO  self.id2obj = [comprehension list], since undump_ref may access id2obj during its construction
    for i in range(nb): self.id2obj[i] = _HANDLERS[s.readline()].undump_obj(self, s)
    for obj in self.id2obj: _HANDLERS_[obj.__class__].undump_data(obj, self, s)
    
    return self.undump_ref(s)
  
  def collect(self, obj):
    """Dumper.collect(OBJ) -> bool

Collects OBJ for serialization. Returns false is OBJ is already collected; else returns true."""
    return _HANDLERS_[obj.__class__].collect(obj, self)
  
  def dump_ref (self, obj, s):
    """Dumper.dump_ref(OBJ, S)

Writes a reference to OBJ in file S."""
    _HANDLERS_[obj.__class__].dump_ref(obj, self, s)
    
  def undump_ref(self, s):
    """Dumper.undump_ref(S) -> obj

Reads a reference from file S."""
    c = s.read(1)
    if   c == "i": return int  (s.readline())
    elif c == "f": return float(s.readline())
    elif c == "s": return s.read(int(s.readline()))
    elif c == "u": return s.read(int(s.readline())).decode("utf8")
    elif c == "r": return self.id2obj[int(s.readline())]
    elif c == "n": return None
    elif c == "b": return bool(int(s.read(1)))
    elif c == "c": return complex(s.readline())
    raise ValueError("Unknown ref code '%s'!" % c)
    
    
class Handler(object):
  """Handler

A customized handler for serialization and deserialization.
You can subclass it to extend cerealization support to new object.
See also ObjHandler."""
  
  def collect(self, obj, dumper):
    """Handler.collect(obj, dumper) -> bool

Collects all the objects referenced by OBJ.
For each objects ROBJ referenced by OBJ, calls collect method of the Handler for ROBJ's class,
i.e._HANDLERS_[ROBJ.__class__].collect(ROBJ, dumper).
Returns false if OBJ is already referenced (and thus no collection should occur); else returns true.
"""
    i = id(obj)
    if not i in dumper.objs_id:
      dumper.objs.append(obj)
      dumper.objs_id.add(i)
      return 1
    
  def dump_obj (self, obj, dumper, s):
    """Handler.dump_obj(obj, dumper, s)

Dumps OBJ classname in file S."""
    s.write(self.classname)
    
  def dump_data(self, obj, dumper, s):
    """Handler.dump_data(obj, dumper, s)

Dumps OBJ data in file S."""
    
  def dump_ref (self, obj, dumper, s):
    """Handler.dump_ref(obj, dumper, s)

Write a reference to OBJ in file S.
You should not override dump_ref, since they is no corresponding 'undump_ref' that you
can override."""
    s.write("r%s\n" % dumper.id2id[id(obj)])
  
  def undump_obj(self, dumper, s):
    """Handler.undump_obj(dumper, s)

Returns a new uninitialized (=no __init__'ed) instance of the class.
If you override undump_obj, DUMPER and file S can be used to read additional data
saved by Handler.dump_obj()."""
    
  def undump_data(self, obj, dumper, s):
    """Handler.undump_data(obj, dumper, s)

Reads the data for OBJ, from DUMPER and file S.
If you override undump_data, you should use DUMPER.undump_ref(S) to
read a reference or a basic type (=a string, an int,...)."""
  
    
class RefHandler(object):
  def collect  (self, obj, dumper)   : pass
  def dump_obj (self, obj, dumper, s): pass
  def dump_data(self, obj, dumper, s): pass
  
class NoneHandler(RefHandler):
  def dump_ref (self, obj, dumper, s): s.write("n")
  
class StrHandler(RefHandler):
  def dump_ref (self, obj, dumper, s): s.write("s%s\n%s" % (len(obj), obj))
  
class UnicodeHandler(RefHandler):
  def dump_ref (self, obj, dumper, s):
    obj = obj.encode("utf8")
    s.write("u%s\n%s" % (len(obj), obj))
    
class BoolHandler(RefHandler):
  def dump_ref (self, obj, dumper, s): s.write("b%s" % int(obj))

class IntHandler(RefHandler):
  def dump_ref (self, obj, dumper, s): s.write("i%s\n" % obj)
  
class FloatHandler(RefHandler):
  def dump_ref (self, obj, dumper, s): s.write("f%s\n" % obj)
  
class ComplexHandler(RefHandler):
  def dump_ref (self, obj, dumper, s):
    c = str(obj)
    if c.startswith("("): c = c[1:-1] # complex("(1+2j)") doesn't work
    s.write("c%s\n" % c)
    

def tuple_depth(t): return max([0] + [tuple_depth(i) + 1 for i in t if isinstance(i, tuple)])

class TupleHandler(Handler):
  classname = "tuple\n"
  def collect(self, obj, dumper):
    if not id(obj) in dumper.objs_id:
      dumper.priorities_objs.append((tuple_depth(obj), obj))
      dumper.objs_id.add(id(obj))
      
      for i in obj: _HANDLERS_[i.__class__].collect(i, dumper)
      return 1
    
  def dump_obj(self, obj, dumper, s):
    s.write("%s%s\n" % (self.classname, len(obj)))
    for i in obj: _HANDLERS_[i.__class__].dump_ref(i, dumper, s)
    
  def undump_obj(self, dumper, s):
    return tuple([dumper.undump_ref(s) for i in range(int(s.readline()))])
  
  
class ListHandler(Handler):
  classname = "list\n"
  def collect(self, obj, dumper):
    if Handler.collect(self, obj, dumper):
      for i in obj: _HANDLERS_[i.__class__].collect(i, dumper)
      return 1
    
  def dump_data(self, obj, dumper, s):
    s.write("%s\n" % len(obj))
    for i in obj: _HANDLERS_[i.__class__].dump_ref(i, dumper, s)
      
  def undump_obj(self, dumper, s): return []
  
  def undump_data(self, obj, dumper, s):
    for i in range(int(s.readline())): obj.append(dumper.undump_ref(s))
    
class SetHandler(Handler):
  classname = "set\n"
  def collect(self, obj, dumper):
    if Handler.collect(self, obj, dumper):
      for i in obj: _HANDLERS_[i.__class__].collect(i, dumper)
      return 1
    
  def dump_data(self, obj, dumper, s):
    s.write("%s\n" % len(obj))
    for i in obj: _HANDLERS_[i.__class__].dump_ref(i, dumper, s)
    
  def undump_obj(self, dumper, s): return set()
  
  def undump_data(self, obj, dumper, s):
    for i in range(int(s.readline())): obj.add(dumper.undump_ref(s))
    
class DictHandler(Handler):
  classname = "dict\n"
  def collect(self, obj, dumper):
    if Handler.collect(self, obj, dumper):
      for k, v in obj.iteritems():
        _HANDLERS_[v.__class__].collect(v, dumper)
        _HANDLERS_[k.__class__].collect(k, dumper)
      return 1
    
  def dump_data(self, obj, dumper, s):
    s.write("%s\n" % len(obj))
    for k, v in obj.iteritems():
      _HANDLERS_[v.__class__].dump_ref(v, dumper, s) # Value is saved fist
      _HANDLERS_[k.__class__].dump_ref(k, dumper, s)
      
  def undump_obj(self, dumper, s): return {}
  
  def undump_data(self, obj, dumper, s):
    for i in range(int(s.readline())):
      obj[dumper.undump_ref(s)] = dumper.undump_ref(s) # Value is read fist
      

class ObjHandler(Handler):
  """ObjHandler

A Cerealizer Handler that can support any new-style class instances, old-style class instances
as well as C-defined types (although it may not save the C-side data)."""
  def __init__(self, Class, classname = ""):
    self.Class          = Class
    self.Class_new      = getattr(Class, "__new__"     , instance)
    self.Class_getstate = getattr(Class, "__getstate__", None)  # Check for and store __getstate__ and __setstate__ now
    self.Class_setstate = getattr(Class, "__setstate__", None)  # so we are are they are not modified in the class or the object
    if classname: self.classname = "%s\n"    % classname
    else:         self.classname = "%s.%s\n" % (Class.__module__, Class.__name__)
    
  def collect(self, obj, dumper):
    i = id(obj)
    if not i in dumper.objs_id:
      dumper.priorities_objs.append((-1, obj))
      dumper.objs_id.add(i)
      
      if self.Class_getstate: state = self.Class_getstate(obj)
      else:                   state = obj.__dict__
      dumper.obj2state[i] = state
      _HANDLERS_[state.__class__].collect(state, dumper)
      return 1
    
  def dump_data(self, obj, dumper, s):
    i = dumper.obj2state[id(obj)]
    _HANDLERS_[i.__class__].dump_ref(i, dumper, s)
    
  def undump_obj(self, dumper, s): return self.Class_new(self.Class)
  
  def undump_data(self, obj, dumper, s):
    if self.Class_setstate: self.Class_setstate(obj, dumper.undump_ref(s))
    else:                   obj.__dict__ =           dumper.undump_ref(s)
    
class SlotedObjHandler(ObjHandler):
  """SlotedObjHandler

A Cerealizer Handler that can support new-style class instances with __slot__."""
  def __init__(self, Class, classname = ""):
    ObjHandler.__init__(self, Class, classname = "")
    self.Class_slots = Class.__slots__
    
  def collect(self, obj, dumper):
    i = id(obj)
    if not i in dumper.objs_id:
      dumper.priorities_objs.append((-1, obj))
      dumper.objs_id.add(i)
      
      if self.Class_getstate: state = self.Class_getstate(obj)
      else:                   state = dict([(slot, getattr(obj, slot, None)) for slot in self.Class_slots])
      dumper.obj2state[i] = state
      _HANDLERS_[state.__class__].collect(state, dumper)
      return 1
    
  def undump_data(self, obj, dumper, s):
    if self.Class_setstate: self.Class_setstate(obj, dumper.undump_ref(s))
    else:
      state = dumper.undump_ref(s)
      for slot in self.Class_slots: setattr(obj, slot, state[slot])
      
class InitArgsObjHandler(ObjHandler):
  """InitArgsObjHandler

A Cerealizer Handler that can support class instances with __getinitargs__."""
  def __init__(self, Class, classname = ""):
    ObjHandler.__init__(self, Class, classname = "")
    self.Class_getinitargs = Class.__getinitargs__
    self.Class_init        = Class.__init__
    
  def collect(self, obj, dumper):
    i = id(obj)
    if not i in dumper.objs_id:
      dumper.priorities_objs.append((-1, obj))
      dumper.objs_id.add(i)
      
      dumper.obj2state[i] = state = self.Class_getinitargs(obj)
      _HANDLERS_[state.__class__].collect(state, dumper)
      return 1
    
  def undump_data(self, obj, dumper, s):
    self.Class_init(obj, *dumper.undump_ref(s))
      
class NewArgsObjHandler(ObjHandler):
  """NewArgsObjHandler

A Cerealizer Handler that can support class instances with __getnewargs__.
Currently, it works ONLY if __getnewargs__() returns a tuple containing only strings, unicode,
numbers or None. However, the real problem is not in Cerealizer but in __getnewargs__ API:
what about the following:
  def __getnewargs__(self): return (self,)
Uisng this __getnewargs__, the object cannot be created before it exists,
which is an unsolvable problem..."""
  def __init__(self, Class, classname = ""):
    ObjHandler.__init__(self, Class, classname = "")
    self.Class_getnewargs = Class.__getnewargs__
    
  def collect(self, obj, dumper):
    i = id(obj)
    if not i in dumper.objs_id:
      dumper.priorities_objs.append((-1, obj))
      dumper.objs_id.add(i)
      
      if self.Class_getstate: state = self.Class_getstate(obj)
      else:                   state = obj.__dict__
      dumper.obj2state[i] = state
      _HANDLERS_[state.__class__].collect(state, dumper)
      return 1
    
  def dump_obj (self, obj, dumper, s):
    s.write(self.classname)
    newargs = self.Class_getnewargs(obj)
    
    s.write("%s\n" % len(newargs))
    for newarg in newargs:
      handler = _HANDLERS_[newarg.__class__]
      if not isinstance(handler, RefHandler): raise ValueError("Only string, unicode, numbers and None are supported in the return value of __getnewargs__!", newargs)
      handler.dump_ref(newarg, dumper, s)
      
  def undump_obj(self, dumper, s):
    return self.Class_new(self.Class, *tuple([dumper.undump_ref(s) for i in range(int(s.readline()))]))
  

_configurable = 1
_HANDLERS  = {}
_HANDLERS_ = {}
def register(Class, handler = None, classname = ""):
  """register(Class, handler = None)

Registers CLASS as a serializable and secure class.
By calling register, YOU ASSUME THAT CLASS.__new__, CLASS.__getstate__ and CLASS.__setstate__
ARE SECURE!

HANDLER is the Cerealizer Handler object that handles serialization and deserialization for Class.
If not given, Cerealizer create an instance of ObjHandler, which is suitable for old-style and
new_style Python class, and also C-defined types (although if it has some C-side data, you may
have to write a custom Handler or a __getstate__ and __setstate__ pair)."""
  if not _configurable: raise StandardError("Cannot register new classes after freeze_configuration has been called!")
  if "\n" in classname: raise ValueError("CLASSNAME cannot have \\n (Cerealizer automatically add a trailing \\n for performance reason)!")
  if not handler:
    if   hasattr(Class, "__getnewargs__" ): handler = NewArgsObjHandler (Class, classname)
    elif hasattr(Class, "__getinitargs__"): handler = InitArgsObjHandler(Class, classname)
    elif hasattr(Class, "__slots__"      ): handler = SlotedObjHandler  (Class, classname)
    else:                                   handler = ObjHandler        (Class, classname)
  if _HANDLERS_.has_key(Class): raise ValueError("Class %s has already been registred!" % Class)
  if not isinstance(handler, RefHandler):
    if _HANDLERS .has_key(handler.classname): raise ValueError("A class has already been registred under the name %s!" % handler.classname)
    _HANDLERS [handler.classname] = handler
    if handler.__class__ is ObjHandler:
      logger.info("Registring class %s as '%s'" % (Class, handler.classname[:-1]))
    else:
      logger.info("Registring class %s as '%s' (using %s)" % (Class, handler.classname[:-1], handler.__class__.__name__))
  else:
    logger.info("Registring reference '%s'" % Class)
    
  _HANDLERS_[Class] = handler

register_class = register # For backward compatibility

def freeze_configuration():
  """freeze_configuration()

Ends Cerealizer configuration. When freeze_configuration() is called, it is no longer possible
to register classes, using register().
Calling freeze_configuration() is not mandatory, but it may enforce security, by forbidding
unexpected calls to register()."""
  global _configurable
  _configurable = 0
  logger.info("Configuration frozen")
  
register(type(None), NoneHandler   ())
register(str       , StrHandler    ())
register(unicode   , UnicodeHandler())
register(bool      , BoolHandler   ())
register(int       , IntHandler    ())
register(float     , FloatHandler  ())
register(complex   , ComplexHandler())
register(dict      , DictHandler   ())
register(list      , ListHandler   ())
register(set       , SetHandler    ())
register(tuple     , TupleHandler  ())
 

def dump(obj, file, protocol = 0):
  """dump(obj, file, protocol = 0)

Serializes object OBJ in FILE.
PROTOCOL is unused, it exists only for compatibility with Pickle."""
  Dumper().dump(obj, file)
  
def load(file):
  """load(file) -> obj

De-serializes an object from FILE."""
  return Dumper().undump(file)

def dumps(obj, protocol = 0):
  """dumps(obj, protocol = 0) -> str

Serializes object OBJ and returns the serialized string.
PROTOCOL is unused, it exists only for compatibility with Pickle."""
  s = StringIO()
  Dumper().dump(obj, s)
  return s.getvalue()

def loads(string):
  """loads(file) -> obj

De-serializes an object from STRING."""
  return Dumper().undump(StringIO(string))


def dump_class_of_module(*modules):
  """dump_class_of_module(*modules)

Utility function; for each classes found in the given module, print the needed call to register."""
  class D: pass
  class O(object): pass
  s = set([c for module in modules for c in module.__dict__.values() if isinstance(c, type(D)) or  isinstance(c, type(O))])
  l = ['cerealizer.register(%s.%s)' % (c.__module__, c.__name__) for c in s]
  l.sort()
  for i in l: print i
  
