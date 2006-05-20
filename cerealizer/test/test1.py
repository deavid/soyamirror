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

import time
import psyco
psyco.full()

class O(object):
  def __init__(self):
    self.x = 1
    self.s = "jiba"
    self.o = None

register(O)
freeze_configuration()

l = []
for i in range(2000):
  o = O()
  if l: o.o = l[-1]
  l.append(o)

t = time.time()
s = dumps(l)
print time.time() - t

print len(s)

t = time.time()
l2 = loads(s)
print time.time() - t

print l2[0]
print l2[0].x
print l2[0].s
print l2[1].o



from cPickle import *

t = time.time()
s = dumps(l)
print time.time() - t

print len(s)

t = time.time()
l2 = loads(s)
print time.time() - t


