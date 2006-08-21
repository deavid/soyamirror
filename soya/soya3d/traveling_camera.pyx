# -*- indent-tabs-mode: t -*-

# Soya 3D
# Copyright (C) 2003-2004 Jean-Baptiste LAMY -- jiba@tuxfamily.org
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

cdef class _TravelingCamera(_Camera):
	#cdef           _travelings
	#cdef Traveling _traveling
	#cdef float     _speed_value
	#cdef _Vector   _speed
	
	property traveling:
		def __get__(self): return self._traveling
	
	property travelings:
		def __get__(self): return self._travelings
	
	property speed:
		def __get__(self): return self._speed_value
		def __set__(self, float x): self._speed_value = x
		
	def __init__(self, parent = None):
		_Camera.__init__(self, parent)
		
		self._travelings  = []
		self._traveling   = None
		self._speed_value = 0.3
		self._speed       = Vector()
		
	def add_traveling(self, Traveling traveling):
		self._travelings.append(traveling)
		self._traveling = traveling
		self._traveling_changed()
		
	def pop_traveling(self):
		del self._travelings[-1]
		self._traveling = self._travelings[-1]
		self._traveling_changed()
		
	def remove_traveling(self, Traveling traveling):
		self._travelings.remove(traveling)
		if self._traveling is traveling:
			if self._travelings:
				self._traveling = self._travelings[-1]
				self._traveling_changed()
			else:
				self._traveling = None
				
	cdef void _traveling_changed(self):
		cdef float v[3], up[3]
		cdef float angle
		
		if self._traveling._incline_as is None:
			v[0] = 0.0
			v[1] = 1.0
			v[2] = 0.0
			vector_by_matrix(v, self._inverted_root_matrix())
			
			if (v[0] != 0.0) or (v[1] != 0.0):
				up[0] = 0.0
				up[1] = 1.0
				up[2] = 0.0
				v [2] = 0.0
				
				angle = vector_angle(up, v)
				if v[0] > 0: self.turn_incline(-angle)
				else:        self.turn_incline( angle)
				
	#def begin_round(self):
		#if self._traveling._smooth_move:
		#  self._speed.set_start_end(self, self._traveling.best_position(self))
		#  self._speed.__imul__(self._speed_value)
		
	def advance_time(self, float proportion):
		_Camera.advance_time(self, proportion)
		
		import soya
		if soya.MAIN_LOOP.will_render == 0:
			self._proportion = self._proportion + proportion
			return
		
		proportion = proportion + self._proportion
		
		cdef _Vector direction, current
		cdef float   v[3], up[3]
		cdef float   angle
		
		if self._traveling._smooth_move:
			while proportion > 1.0:
				self._speed.set_start_end(self, self._traveling.best_position(self))
				self.add_mul_vector(self._speed_value, self._speed)
				proportion = proportion - 1.0
				
			self._speed.set_start_end(self, self._traveling.best_position(self))
			self.add_mul_vector(proportion * self._speed_value, self._speed)
			
		else:
			self.move(self._traveling.best_position(self))
		
		if self._traveling._smooth_rotation:
			r = self._traveling.best_direction(self)
			if isinstance(r, _Vector): direction = r
			else:                      direction = self >> r
			direction.convert_to(self)
			direction.normalize()
			if   direction._matrix[0] < -0.02: direction._matrix[0] = -0.02
			elif direction._matrix[0] >  0.02: direction._matrix[0] =  0.02
			if   direction._matrix[1] < -0.02: direction._matrix[1] = -0.02
			elif direction._matrix[1] >  0.02: direction._matrix[1] =  0.02
			direction._matrix[2] = -1.0
			self.look_at(direction)
			
		else:
			self.look_at(self._traveling.best_direction(self))
			
#       if self._traveling._incline_as is None:
#         self.look_at(self._traveling.best_direction(self))
#       else:
#         # XXX optimizable
#         r = self.traveling.best_direction(self)
#         if isinstance(r, _Vector): direction = r
#         else:                      direction = self >> r
#         current = Vector(self, 0.0, 0.0, -1.0)
#         axe = current.cross_product(direction)
#         axe.convert_to(self.parent)
#         self.rotate_axe_xyz(current.angle_to(direction), axe.x, axe.y, axe.z)
				
		if not self._traveling._incline_as is None:
			v[0] = 0.0
			v[1] = 1.0
			v[2] = 0.0
			vector_by_matrix(v, self._traveling._incline_as._root_matrix())
			vector_by_matrix(v, self._inverted_root_matrix())
			
			if (v[0] != 0.0) or (v[1] != 0.0):
				up[0] = 0.0
				up[1] = 1.0
				up[2] = 0.0
				v [2] = 0.0
				
				angle = vector_angle(up, v)
				angle = min(2.0 * self._speed_value, angle) * proportion
				if v[0] > 0: self.turn_incline(-angle)
				else:        self.turn_incline( angle)
				
		self._proportion = 0.0

				
	def zap(self):
		self.move   (self._traveling.best_position (self))
		self.look_at(self._traveling.best_direction(self))
		
		
cdef class Traveling(_CObj):
	#cdef CoordSyst _incline_as
	#cdef int       _smooth_move, _smooth_rotation
	
	property incline_as:
		def __get__(self):
			return self._incline_as
		def __set__(self, CoordSyst x):
			self._incline_as = x
		
	property smooth_move:
		def __get__(self):
			return self._smooth_move
		def __set__(self, int x):
			self._smooth_move = x
		
	property smooth_rotation:
		def __get__(self):
			return self._smooth_rotation
		def __set__(self, int x):
			self._smooth_rotation = x
		
	def best_position (self, _TravelingCamera camera):
		raise NotImplementedError
	
	def best_direction(self, _TravelingCamera camera):
		raise NotImplementedError


cdef class _FixTraveling(Traveling):
	"""A fixed view traveling."""
	
	#cdef Position _target, _direction
	
	property target:
		def __get__(self):
			return self._target
		def __set__(self, Position x):
			self._target = x
		
	property direction:
		def __get__(self):
			return self._direction
		def __set__(self, Position x):
			self._direction = x
		
	def __init__(self, Position target, Position direction, int smooth_move = 1, int smooth_rotation = 0):
		"""FixTraveling(target, direction, smooth_move = 1, smooth_rotation = 0)
TARGET is the position of the camera, and DIRECTION the direction to look at.
SMOOTH_MOVE and SMOOTH_ROTATION defines wether the camera moves and rotates smoothly or
not."""
		
		self._target          = target
		self._direction       = direction or Vector(None, 0.0, 0.0, -1.0)
		self._smooth_move     = smooth_move
		self._smooth_rotation = smooth_rotation
		
	def best_position(self, _TravelingCamera camera):
		return self._target or camera
	
	def best_direction(self, _TravelingCamera camera):
		return self._direction


cdef class _ThirdPersonTraveling(Traveling):
	"""A Tomb-Raider-like traveling.
TARGET is a point in the character (or world) to follow."""
	
	#cdef Position _target
	#cdef _Point   __target, _best, _result, __direction
	#cdef _Vector  _direction, __normal
	#cdef float _distance, _offset_y, _offset_y2, _lateral_angle, _top_view
	#cdef float _speed
	
	property speed:
		def __get__(self):
			return self._speed
		def __set__(self, float x):
			self._speed = x
		
	property target:
		def __get__(self):
			return self._target
		def __set__(self, Position x):
			self._target = x
		
	property direction:
		def __get__(self):
			return self._direction
		def __set__(self, _Vector x):
			self._direction = x
			
	property distance:
		def __get__(self):
			return self._distance
		def __set__(self, float x):
			self._distance = x
			
	property offset_y:
		def __get__(self):
			return self._offset_y
		def __set__(self, float x):
			self._offset_y = x
			
	property offset_y2:
		def __get__(self):
			return self._offset_y2
		def __set__(self, float x):
			self._offset_y2 = x
			
	property lateral_angle:
		def __get__(self):
			return self._lateral_angle
		def __set__(self, float x):
			self._lateral_angle = x
			
	property top_view:
		def __get__(self):
			return self._top_view
		def __set__(self,  x):
			self._top_view = x
			
	def __init__(self, Position target = None, _Vector direction = None, int smooth_move = 1, int smooth_rotation = 0):
		self._incline_as      = target
		self._target          = target
		self.__target         = Point()
		self._best            = Point()
		self._result          = Point()
		self._direction       = direction or Vector(None, 0.0, 1.0, 2.0)
		self.__direction      = Point()
		self.__normal         = Vector()
		self._smooth_move     = smooth_move
		self._smooth_rotation = smooth_rotation
		self._distance        = 5.0
		self._offset_y        = 1.5
		self._offset_y2       = 0.0
		self._lateral_angle   = 0.0
		self._top_view        = 0.0
		self._speed           = 1.0
		self._context         = None
		
	def best_position(self, _TravelingCamera camera):
		cdef _World  root
		cdef _Point  target, result, best
		cdef _Vector direction
		cdef int     i, j
		cdef float   best_dist, dist, px, py, pz, a, old_dirx, old_diry, c, s
		cdef int     lat, vert
		
		root      = camera._get_root()
		target    = self.__target
		result    = self._result
		best      = self._best
		direction = self._direction
		
		target._parent = self._target
		target._matrix[0] = 0.0
		target._matrix[1] = self._offset_y
		target._matrix[2] = 0.0
		target.convert_to(root)
		
		best.clone(target)
		best.add_mul_vector(0.5, direction)
		self._context = root.RaypickContext(best, self._distance * 0.6, self._context)
		
		px, py, pz = self._target.transform(camera)
		
		if self._lateral_angle:
			c  = cos(self._lateral_angle)
			s  = sin(self._lateral_angle)
			a  = px
			px = c * px + s * pz
			pz = c * pz - s * a
			
		py = py - self._top_view * self._distance
		
		if (fabs(px) < 1.0) and (pz > 0.0): lat = 0
		else:                               lat = -cmp(px, 0.0) # XXX optimizable
		if fabs(py - 3.0) < 1.0: vert = 0
		else:                    vert = -cmp(py, 3.0) # XXX optimizable
		
		best_dist = self._check(self._context, target, direction, result)
		if (best_dist > self._distance - 0.1) and (lat == 0) and (vert == 0): return result
		else: best.clone(result)
		
		direction.convert_to(camera)

		old_dirx = direction._matrix[0]
		old_diry = direction._matrix[1]


		direction._matrix[0] = old_dirx - 0.3 * self._speed
		dist = self._check(self._context, target, direction, result)
		if lat == -1: dist = dist + 0.1
		#dist = dist - 0.1 * lat
		if dist > best_dist: best.clone(result); best_dist = dist

		direction._matrix[0] = old_dirx + 0.3 * self._speed
		dist = self._check(self._context, target, direction, result)
		if lat == 1: dist = dist + 0.1
		#dist = dist + 0.1 * lat
		if dist > best_dist: best.clone(result); best_dist = dist
		
		#direction._matrix[0] = old_dirx
		direction._matrix[1] = old_diry - 0.2 * self._speed
		dist = self._check(self._context, target, direction, result)
		if vert == -1: dist = dist + 0.1
		#dist = dist - 0.1 * vert
		if dist > best_dist: best.clone(result); best_dist = dist
		
		direction._matrix[1] = old_diry + 0.2 * self._speed
		dist = self._check(self._context, target, direction, result)
		if vert == 1: dist = dist + 0.1
		#dist = dist + 0.1 * vert
		if dist > best_dist: best.clone(result); best_dist = dist
		
		direction.set_start_end(target, best)
		
		return best
	
	def best_direction(self, _TravelingCamera camera):
		#return self._target
		self.__direction.clone(self._target)
		self.__direction._matrix[1] = self.__direction._matrix[1] + self._offset_y + self._offset_y2
		return self.__direction
	
	
	cdef float _check(self, RaypickContext root, Position target, _Vector direction, _Point result):
		# XXX use raypick context ?
		if not root.raypick(target, direction, self._distance, 1, 0, result, self.__normal):
			direction.set_length(self._distance)
			result.clone(target)
			result.add_vector(direction)
			return self._distance
		
		return result.distance_to(target)
	
