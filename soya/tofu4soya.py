# -*- indent-tabs-mode: t -*-

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

DEPRECATED -- use now soya.tofu (tofu4soya corresponds to an old version of tofu)

"""

import twisted.internet.selectreactor
import soya

tofu = __import__("tofu")

class MainLoop(soya.MainLoop):
	def __init__(self, scene = None):
		soya.MainLoop.__init__(self, scene)
		tofu.MAIN_LOOP = self
		tofu.IDLER     = self
		
		twisted.internet.selectreactor.install()
		self.reactor = twisted.internet.reactor
		
	def begin_round(self):
		self.reactor.iterate()
		soya.MainLoop.begin_round(self)
		tofu.Level.discard_inactives()
		
	def add_level(self, level): self.scenes[0].insert(0, level)
	
	def remove_level(self, level): self.scenes[0].remove(level)

Idler = MainLoop

class Level(tofu.Level, soya.World):
	_reffed = tofu.Level.get
	
	def __init__(self):
		tofu.Level.__init__(self)
		soya.World.__init__(self)
		
	def add_mobile(self, mobile):
		if isinstance(mobile, soya.CoordSyst): self.add(mobile)
		tofu.Level.add_mobile(self, mobile)
		
	def remove_mobile(self, mobile):
		if isinstance(mobile, soya.CoordSyst) and mobile.parent is self: self.remove(mobile)
		tofu.Level.remove_mobile(self, mobile)
		
	def __reduce__(self):
		if not soya._SAVING is self:
			return (soya._getter, (self.__class__, self.filename))
		return soya._CObj.__reduce__(self)
	
	def __reduce_ex__(self, i = 0):
		if not soya._SAVING is self:
			return (soya._getter, (self.__class__, self.filename))
		return soya._CObj.__reduce_ex__(self, i)
	
	def dump(self):
		soya._SAVING = self
		try:     return tofu.Level.dump(self)
		finally: soya._SAVING = None

	def save(self, filename = None):
		soya._SAVING = self
		try:
			tofu.Level.save(self, filename)
		finally: soya._SAVING = None
		
	def loaded(self):
		tofu.Level.loaded(self)
		soya.World.loaded(self)
		
		for i in self:
			if isinstance(i, tofu.Unique) and not isinstance(i, tofu.Mobile): i.loaded()
			
	def received(self):
		tofu.Level.received(self)
		
		for i in self:
			if isinstance(i, tofu.Unique) and not isinstance(i, tofu.Mobile): i.received()
			
	def begin_round(self):
		if self.active:
			self.round += 1
			soya.World.begin_round(self)
			
	def advance_time(self, proportion):
		if self.active:
			soya.World.advance_time(self, proportion)
		

class CoordSystState(soya.CoordSystState, tofu.State):
	"""CoordSystState

A State that take care of CoordSyst position, rotation and scaling.

CoordSystState extend CoordSyst, and thus have similar method (e.g. set_xyz, rotate_*,
scale, ...)"""
	def __init__(self, mobile):
		soya.CoordSystState.__init__(self, mobile)
		tofu.State.__init__(self)
		
		if (mobile.level.round % DROPPED_STATE_RATIO) != 0: self.droppable = 1

tofu.QUEUE_LENGTH = 1


class Mobile(soya.World, tofu.Mobile):
	def __init__(self):
		soya.World .__init__(self)
		tofu.Mobile.__init__(self)
		
		self.state1 = None
		self.state2 = None
		self.interpolate_factor = 0.0
		
		# Old code, without interpolation
		#self.current_move = soya.Vector()
		
	def begin_round(self):
		soya.World .begin_round(self)
		tofu.Mobile.begin_round(self)
		
	def set_state(self, state):
		"""Mobile.set_state(state)

Set the current state of the Mobile. Default implementation take care of position,
rotation and scaling."""
		
		# Which one should be chosen? It seems that the second one give a smoother animation.
		
		#self.state1 = self.state2
		self.state1 = state.__class__(self)
		
		self.state2 = state
		self.interpolate_factor = 0.0
		
		# Old code, without interpolation
		#x, y, z = self.x, self.y, self.z
		#self.matrix = state.matrix
		#self.set_xyz(x, y, z)
		#self.current_move.set_xyz(state.x - x, state.y - y, state.z - z)
		
	def advance_time(self, proportion):
		"""Mobile.advance_time(proportion)

This default implementation take care of position, rotation and scaling."""
		soya.World.advance_time(self, proportion)
		
		self.interpolate_factor += self.doer.STATE_FACTOR * proportion
		
		y1 = (soya.Vector(self, 0.0, 1.0, 0.0) % self.parent).y
		
		if self.state1 and self.state2:
			self.interpolate(self.state1, self.state2, self.interpolate_factor)

		y2 = (soya.Vector(self, 0.0, 1.0, 0.0) % self.parent).y


		# Old code, without interpolation
		#self.add_mul_vector(proportion, self.current_move)
		
	def loaded(self):
		soya.World .loaded(self)
		tofu.Mobile.loaded(self)




# The other Tofu classes doesn't need hacks currently :-)

init = tofu.init
GameInterface = tofu.GameInterface
Unique = tofu.Unique
SavedInAPath = tofu.SavedInAPath
Player = tofu.Player
Action = tofu.Action
State = tofu.State
LocalController = tofu.LocalController
RemoteController = tofu.RemoteController
LocalDoer = tofu.LocalDoer
RemoteDoer = tofu.RemoteDoer

DROPPED_STATE_RATIO = 10
LocalDoer. STATE_FACTOR = 1.0
RemoteDoer.STATE_FACTOR = 0.1
def set_dropped_state_ratio(ratio):
	"""set_dropped_state_ratio(ratio)
Set how many states are dropped is client-server mode. The dropped states are interpolated
by the client. 1 state out of RATIO is not dropped, e.g. set_dropped_state_ratio(8)
means drop 7 states of 8. Default is 10.

Notice that states which have state.is_crucial() == True are never dropped."""
	global DROPPED_STATE_RATIO
	DROPPED_STATE_RATIO = ratio
	RemoteDoer.STATE_FACTOR = 1.0 / ratio

set_dropped_state_ratio(10)


