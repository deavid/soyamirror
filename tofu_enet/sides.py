# TOFU
# Copyright (C) 2006 Jean-Baptiste LAMY
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

__all__ = ["server_side", "client_side", "single_side", "local_mobile", "remote_mobile", "Multisided", "set_mode"]

import sys, weakref

def _noop(*args, **kargs): pass

class SidesManager(object):
  def __init__(self, nb_sides):
    self.nb_sides      = nb_sides
    self.current_sides = [0]
    self.funcs         = {}
    self.func2locals   = {}
    self.class_funcs   = {}
    self.created       = weakref.WeakKeyDictionary()
    
  def Decorator(self, i):
    def decorator(f, locals = None, orig = None):
      if not locals: locals = sys._getframe(1).f_locals
      if not orig: orig = f
      
      self.func2locals[orig] = locals, orig.func_name
      
      funcs = self.funcs.get((orig.func_name, id(locals)))
      if not funcs:
        funcs = self.funcs[orig.func_name, id(locals)] = [[] for j in range(self.nb_sides)]
      funcs[i].append(f)
      return f
    return decorator
  
  def set_side(self, sides):
    self.current_sides = sides
    self._treat_class(Multisided)
    
  def _tag_sided_method(self, Class):
    Class.__multisided_methods__ = {}
    for attr, value in Class.__dict__.items():
      try: self.func2locals[value]
      except: continue
      locals, func_name = self.func2locals[value]
      Class.__multisided_methods__[attr] = self.funcs[func_name, id(locals)]
      
  def _treat_class(self, Class):
    for attr, value in Class.__dict__.items():
      try: self.func2locals[value]
      except: continue
      
      locals, func_name = self.func2locals[value]
      funcs = self.funcs[func_name, id(locals)]

      fs = [funcs[i] for i in self.current_sides]
      fs = [j for i in fs for j in i]
      
      if self.created.has_key(value): del self.func2locals[value]

      #if   len(fs) == 0: f = lambda *args, **kargs: None; self.created[f] = 1
      if   len(fs) == 0:
        f = lambda *args, **kargs: None
        if hasattr(Class, func_name): delattr(Class, func_name)
        attr = "_disabled_%s" % attr
      elif len(fs) == 1: f = fs[0]
      else:              f = self._create_multi_f(fs)
      
      self.func2locals[f] = locals, func_name
      setattr(Class, attr, f)
    for ChildClass in Class.__subclasses__(): self._treat_class(ChildClass)
    
  def _treat_class(self, Class):
    if not Class.__dict__.has_key("__multisided_methods__"): self._tag_sided_method(Class)
    
    for func_name, funcs in Class.__multisided_methods__.items():
      fs = [funcs[i] for i in self.current_sides]
      fs = [j for i in fs for j in i]
      
      if   len(fs) == 0:
        if Class.__dict__.has_key(func_name): delattr(Class, func_name)
      elif len(fs) == 1: f = fs[0]                   ; setattr(Class, func_name, f)
      else:              f = self._create_multi_f(fs); setattr(Class, func_name, f)
      
    for ChildClass in Class.__subclasses__(): self._treat_class(ChildClass)
    
  def _create_multi_f(self, fs):
    def f(*args, **kargs):
      for f1 in fs: r = f1(*args, **kargs)
      return r
    #self.created[f] = 1
    return f
  
_client_serveur_side = SidesManager(3)

server_side = _client_serveur_side.Decorator(0)
client_side = _client_serveur_side.Decorator(1)
single_side = _client_serveur_side.Decorator(2)


def set_mode(mode):
  global MODE
  MODE = mode
  _client_serveur_side.set_side({"server" : [0], "client" : [1], "single" : [2]}[mode])


def local_mobile(f):
  locals = sys._getframe(1).f_locals
  server_side(lambda self, *args, **kargs: self.bot and f(self, *args, **kargs), locals, f)
  client_side(lambda self, *args, **kargs: (not self.bot) and self.local and f(self, *args, **kargs), locals, f)
  single_side(f, locals)
  return f

def remote_mobile(f):
  locals = sys._getframe(1).f_locals
  server_side(lambda self, *args, **kargs: (not self.bot) and f(self, *args, **kargs), locals, f)
  client_side(lambda self, *args, **kargs: (self.bot or (not self.local)) and f(self, *args, **kargs), locals, f)
  return f

class Multisided(object): pass


if __name__ == "__main__":
  class C(Multisided):
    @server_side
    def test(self): print "server"
    
    @client_side
    def test(self): print "client"

  set_mode("server")
  
  print C.__multisided_methods__
  
  c = C()
  
  c.test()
