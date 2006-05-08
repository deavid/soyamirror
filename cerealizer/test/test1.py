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

from cerealizer import *

s = dumps({"a" : 1})
print s

print loads(s)
print
print


class O(object):
  def __init__(self):
    self.x = 1
    self.self = self
    self.l = [1, 2, "e"]
    self.unic = u"abcdéf"
    self.s = set([1, 2, 2])
    self.none = None
  #def __getstate__(self): return self.__dict__
  #def __setstate__(self, state): self.__dict__ = state

register_class(O)

o = O()
s = dumps(o)
print s
o2 = loads(s)
print o2, o2.x, o2.self is o2, o2.l, o2.unic, o2.s

print
print

o1 = (1, 2, 3)
s = dumps(o1)
print s
r = loads(s)
print r

o1 = (1, (4, 5), 3)
s = dumps(o1)
print s
r = loads(s)
print r

t = (1, 2)
l = [t, (t, 3)]
s = dumps(l)
print s
r = loads(s)
print r
