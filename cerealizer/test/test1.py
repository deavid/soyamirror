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

import cerealizer
import twisted.spread.jelly, twisted.spread.banana
import cPickle



import time
import psyco
psyco.full()

class O(twisted.spread.jelly.Jellyable):
  def __init__(self):
    self.x = 1
    self.s = "jiba"
    self.o = None
  
cerealizer.register(O)
cerealizer.freeze_configuration()


l = []
for i in range(10000):
  o = O()
  if l: o.o = l[-1]
  l.append(o)

print "cerealizer"
t = time.time()
s = cerealizer.dumps(l)
print "dumps in", time.time() - t, "s,",

print len(s), "bytes length"

t = time.time()
l2 = cerealizer.loads(s)
print "loads in", time.time() - t, "s"



print
print "cPickle"
t = time.time()
s = cPickle.dumps(l)
print "dumps in", time.time() - t, "s,",

print len(s), "bytes length"

t = time.time()
l2 = cPickle.loads(s)
print "loads in", time.time() - t, "s"


print
print "jelly + banana"
t = time.time()
s = twisted.spread.banana.encode(twisted.spread.jelly.jelly(l))
print "dumps in", time.time() - t, "s",

print len(s), "bytes length"

t = time.time()
l2 = twisted.spread.jelly.unjelly(twisted.spread.banana.decode(s))
print "loads in", time.time() - t, "s"


import twisted.spread.cBanana
twisted.spread.banana.cBanana = twisted.spread.cBanana
twisted.spread.cBanana.pyb1282int=twisted.spread.banana.b1282int
twisted.spread.cBanana.pyint2b128=twisted.spread.banana.int2b128
twisted.spread.banana._i = twisted.spread.banana.Canana()
twisted.spread.banana._i.connectionMade()
twisted.spread.banana._i._selectDialect("none")



print
print "jelly + cBanana"
t = time.time()
s = twisted.spread.banana.encode(twisted.spread.jelly.jelly(l))
print "dumps in", time.time() - t, "s",

print len(s), "bytes length"

t = time.time()
l2 = twisted.spread.jelly.unjelly(twisted.spread.banana.decode(s))
print "loads in", time.time() - t, "s"
