# Sides -- 'side-oriented' programming for Python!
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

__all__ = ["side", "has_side", "get_side", "set_side", "Multisided"]

import sys

class Multisided(object): pass

class SidesManager(object):
  def __init__(self):
    self.current_sides = []
    self.funcs         = {}
    self.func2locals   = {}
    
  def Decorator(self, *sides):
    def decorator(f, locals = None, orig = None):
      if not locals: locals = sys._getframe(1).f_locals
      if not orig: orig = f
      
      self.func2locals[orig] = locals, orig.func_name
      funcs = self.funcs.get((orig.func_name, id(locals)))
      if not funcs: funcs = self.funcs[orig.func_name, id(locals)] = {}
      for side in sides:
        if not funcs.has_key(side): funcs[side] = []
        funcs[side].append(f)
      return f
    return decorator

  def get_side(self): return self.current_sides
  def has_side(self, *sides):
    for side in sides:
      if not side in self.current_sides: return 0
    return 1
  def set_side(self, *sides):
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
    if not Class.__dict__.has_key("__multisided_methods__"): self._tag_sided_method(Class)
    
    for func_name, funcs in Class.__multisided_methods__.items():
      fs = [funcs.get(side, ()) for side in self.current_sides]
      fs = [j for i in fs for j in i]
      
      if   len(fs) == 0:
        if Class.__dict__.has_key(func_name):          delattr(Class, func_name)
      elif len(fs) == 1: f = fs[0]                   ; setattr(Class, func_name, f)
      else:              f = self._create_multi_f(fs); setattr(Class, func_name, f)
      
    for ChildClass in Class.__subclasses__(): self._treat_class(ChildClass)
    
  def _create_multi_f(self, fs):
    def f(*args, **kargs):
      for f1 in fs: r = f1(*args, **kargs)
      return r
    return f
  
_side_manager = SidesManager()
get_side = _side_manager.get_side
has_side = _side_manager.has_side
set_side = _side_manager.set_side
side     = _side_manager.Decorator
