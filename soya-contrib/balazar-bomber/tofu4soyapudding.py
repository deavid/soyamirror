# Soya 3D
# Copyright (C) 2005 Jean-Baptiste LAMY -- jiba@tuxfamily.org
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

"""soya.tofu4soya

Tofu is a practical high-level network game engine, based on Twisted.

This module integrate Tofu and Soya together, and thus make writing a
'no meat inside' game very easy :-)

Simply extend the classes provided by the module instead of Tofu's classes, and
then call soya.tofu4soya.init() with your classes.
"""

from twisted.internet import reactor
import soya, tofu
import pudding.idler


class Idler(soya.Idler):
  def __init__(self, scene = None):
    soya.Idler.__init__(self, scene)
    tofu.IDLER = self
    self.events = []
    
  def begin_round(self):
    reactor.iterate()
    soya.Idler.begin_round(self)
    tofu.Level.discard_inactives()
    self.events = pudding.process_event()
    
  def add_level(self, level): self.scenes[0].insert(0, level)
  
  def remove_level(self, level): self.scenes[0].remove(level)


class Level(soya.World, tofu.Level):
  def __init__(self):
    soya.World.__init__(self)
    tofu.Level.__init__(self)
    
  def add_mobile(self, mobile):
    self.add(mobile)
    tofu.Level.add_mobile(self, mobile)
    
  def remove_mobile(self, mobile):
    self.remove(mobile)
    tofu.Level.remove_mobile(self, mobile)
    
  def __reduce__(self):
    if (not tofu._SAVING is self) and (not soya._SAVING is self):
      return (soya._getter, (self.__class__, self.filename))
    return soya._CObj.__reduce__(self)

  def __reduce_ex__(self, i = 0):
    if (not tofu._SAVING is self) and (not soya._SAVING is self):
      return (soya._getter, (self.__class__, self.filename))
    #return object.__reduce_ex__(self, i)
    return soya._CObj.__reduce_ex__(self, i)

  def loaded(self):
    soya.World.loaded(self)
    tofu.Level.loaded(self)
    
  def begin_round(self):
    self.round += 1
    soya.World.begin_round(self)
    
    
class CoordSystState(soya.CoordSyst, tofu.State):
  """CoordSystState

A State that take care of CoordSyst position, rotation and scaling.

CoordSystState extend CoordSyst, and thus have similar method (e.g. set_xyz, rotate_*,
scale, ...)"""
  def __init__(self, mobile):
    """CoordSystState(mobile) -> CoordSystState

Creates a new CoordSystState, with the same position, rotation and scaling than MOBILE."""
    self.added_into(mobile.parent) # Hack !
    #mobile.parent.add(self)
    self.matrix = mobile.matrix


class Mobile(soya.World, tofu.Mobile):
  def __init__(self):
    soya.World .__init__(self)
    tofu.Mobile.__init__(self)
    self.current_move = soya.Vector()
    
  def begin_round(self):
    soya.World .begin_round(self)
    tofu.Mobile.begin_round(self)

  def set_state(self, state):
    """Mobile.set_state(state)

Set the current state of the Mobile. Default implementation take care of position,
rotation and scaling."""
    
    # XXX Smooth rotation and scaling too (by doing them in advance_time)
    
    x, y, z = self.x, self.y, self.z
    self.matrix = state.matrix
    self.set_xyz(x, y, z)
    self.current_move.set_xyz(state.x - x, state.y - y, state.z - z)
    
  def advance_time(self, proportion):
    """Mobile.advance_time(proportion)

This default implementation take care of position, rotation and scaling."""
    soya.World.advance_time(self, proportion)
    self.add_mul_vector(proportion, self.current_move)
    
  def loaded(self):
    soya.World .loaded(self)
    tofu.Mobile.loaded(self)


# The other Tofu classes doesn't need hacks currently :-)

from tofu import init, GameInterface, Unique, SavedInAPath, Player, Action, LocalController, RemoteController, LocalDoer, RemoteDoer

