# -*- indent-tabs-mode: t -*-

# Soya 3D
# Copyright (C) 2003 Jean-Baptiste LAMY -- jiba@tuxfamily.org
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

cdef class Position(_CObj):
	"""A 3D position.

In Soya 3D, a position is defined by 3 coordinates (x, y, z) AND the
coordinates system in which the coordinates are defined (sometime
called the "parent").

Points and Vectors are used for math computation; my own experiences in 3D
have convinced me that ANY complicated 3D computation can be heavily
simplified by the use of coordinates system conversions. As Soya 3D
associates the coordinates system along with the coordinates values, it
performs coordinates system conversion automagically !"""
	
	#cdef CoordSyst _parent
	
	def __init__(self):
		raise ValueError("Position is an abstract class. Use Point instead.")
	
	cdef void _into(self, CoordSyst coordsyst, float* result):
		pass
	
	cdef void _out(self, float* result):
		pass
	
	def __mod__(Position self, CoordSyst coordsyst):
		"""Position % coordsyst -> Point

Converts a Position to the coordinate system COORDSYST and returns the result.
The returned value may be the same Point if its coordinate system is
already COORDSYST, so you should be careful if you modify it."""
		cdef _Point p
		if (self._parent is None) or (coordsyst is None) or (self._parent is coordsyst): return self
		p = Point(coordsyst)
		self._into(coordsyst, p._matrix)
		return p
	
	def position(self):
		"""Position.position() -> Point

Returns the position of this Position (a Point or a Vector, whatever Position is)."""
		pass


cdef class _Point(Position):
	#cdef float _matrix[3]
	
	def __deepcopy__(self, memo):
		cdef _Point clone
		# Do not clone the parent (except if already cloned before, in the memo) !
		if not id(self._parent) in memo.keys():
			parent = self._parent
			self._parent = None # XXX awfull HACK !!!!!
			clone = Position.__deepcopy__(self, memo)
			self._parent = clone._parent = parent
			return clone
		else: return Position.__deepcopy__(self, memo)
		
	def position(self):
		"""Position.position() -> Point

Returns the position of this Position (a Point or a Vector, whatever Position is)."""
		return self
		
	cdef void _into(self, CoordSyst coordsyst, float* result):
		memcpy(result, self._matrix, 3 * sizeof(float))
		if (not self._parent is None) and (not coordsyst is None) and (not self._parent is coordsyst):
			point_by_matrix(result, self._parent._root_matrix())
			point_by_matrix(result, coordsyst._inverted_root_matrix())
		
	cdef void _out(self, float* result):
		memcpy(result, self._matrix, 3 * sizeof(float))
		if not self._parent is None:
			point_by_matrix(result, self._parent._root_matrix())
		
	property parent:
		def __get__(self):
			return self._parent
		def __set__(self, CoordSyst parent):
			self._parent = parent
			
	def set_parent(self, CoordSyst parent):
		self._parent = parent
		
	property x:
		def __get__(self):
			return self._matrix[0]
		def __set__(self, float x):
			self._matrix[0] = x
	
	property y:
		def __get__(self):
			return self._matrix[1]
		def __set__(self, float x):
			self._matrix[1] = x
	
	property z:
		def __get__(self):
			return self._matrix[2]
		def __set__(self, float x):
			self._matrix[2] = x
			
	def __init__(self, CoordSyst parent = None, float x = 0.0, float y = 0.0, float z = 0.0):
		"""Point(parent = None, x = 0.0, y = 0.0, z = 0.0)

Creates a new Point, with coordinates X, Y and Z, defined in the coordinates
system PARENT.
"""
		self._parent    = parent
		self._matrix[0] = x
		self._matrix[1] = y
		self._matrix[2] = z
		
	def get_root(self):
		"""Position.get_root() -> World

Gets the root parent of a Position. The root parent is the root World of the
hierarchy (ofen called the "scene" object)."""
		if self._parent: return self._parent.get_root()
		
	def set_xyz(self, float x, float y, float z):
		"""Position.set_xyz(x, y, z)

Sets the coordinates of a Position to X, Y and Z."""
		self._matrix[0] = x
		self._matrix[1] = y
		self._matrix[2] = z
		
	def move(self, Position position not None):
		"""Position.move(position)

Moves a Position to POSITION.
Coordinates system conversion is performed if needed (=if the Position and
POSITION are not defined in the same coordinates system)."""
		position._into(self._parent, self._matrix)
		
	def __add__(_Point self, _Vector vector not None):
		"""Position + Vector -> Point

Translates a Position and returns the result (a new Point).
Coordinates system conversion is performed if needed (=if the Position and
VECTOR are not defined in the same coordinates system)."""
		#if vector is None: raise ValueError("None is not a valid position !")
		cdef float v[3]
		vector._into(self._parent, v)
		return Point(self._parent, self._matrix[0] + v[0], self._matrix[1] + v[1], self._matrix[2] + v[2])
	
	def __sub__(_Point self, _Vector vector not None):
		"""Position - Vector -> Point

Translates a Position and returns the result (a new Point).
Coordinates system conversion is performed if needed (=if the Position and
VECTOR are not defined in the same coordinates system)."""
		cdef float v[3]
		vector._into(self._parent, v)
		return Point(self._parent, self._matrix[0] - v[0], self._matrix[1] - v[1], self._matrix[2] - v[2])
	
	def add_xyz(self, float x, float y, float z):
		"""Position.add_xyz(x, y, z)

Translates the coordinates of a Position by X, Y and Z."""
		self._matrix[0] = self._matrix[0] + x
		self._matrix[1] = self._matrix[1] + y
		self._matrix[2] = self._matrix[2] + z
		
	def add_vector(self, _Vector vector not None):
		"""Position.add_vector(vector)

Translates a Position IN PLACE.
Coordinates system conversion is performed if needed (=if the Position and
VECTOR are not defined in the same coordinates system).

For Vector, add_vector means vectorial addition (translating a vector does
nothing !)."""
		cdef float v[3]
		vector._into(self._parent, v)
		self._matrix[0] = self._matrix[0] + v[0]
		self._matrix[1] = self._matrix[1] + v[1]
		self._matrix[2] = self._matrix[2] + v[2]
		return self
	
	def __iadd__(_Point self, _Vector vector not None):
		return self.add_vector(vector)
	
	def add_mul_vector(self, float k, _Vector vector not None):
		"""Position.add_mul_vector(k, vector)

Translates a Position IN PLACE, by K * VECTOR.
Coordinates system conversion is performed if needed (=if the Position and
VECTOR are not defined in the same coordinates system).

For Vector, add_mul_vector means vectorial addition (translating a vector does
nothing !)."""
		cdef float v[3]
		vector._into(self._parent, v)
		self._matrix[0] = self._matrix[0] + k * v[0]
		self._matrix[1] = self._matrix[1] + k * v[1]
		self._matrix[2] = self._matrix[2] + k * v[2]
		return self
	
	def distance_to(self, Position other not None):
		"""Position.distance_to(other) -> float

Gets the distance between a Position and anOTHER."""
		cdef float v[3]
		other._into(self._parent, v)
		return sqrt((self._matrix[0] - v[0]) * (self._matrix[0] - v[0]) + (self._matrix[1] - v[1]) * (self._matrix[1] - v[1]) + (self._matrix[2] - v[2]) * (self._matrix[2] - v[2]))
	
	def vector_to(self, Position other not None):
		"""Position.vector_to(other) -> Vector

Gets the vector that starts at a Position and ends at OTHER."""
		cdef float v[3]
		other._into(self._parent, v)
		return Vector(self._parent, v[0] - self._matrix[0], v[1] - self._matrix[1], v[2] - self._matrix[2])
	
	def __rshift__(_Point self, Position other not None):
		return self.vector_to(other)
	
	def __repr__(self):
		return "<%s %s, %s, %s in %s>" % (self.__class__.__name__, self._matrix[0], self._matrix[1], self._matrix[2], self._parent)
	
	cdef __getcstate__(self):
		cdef Chunk* chunk
		chunk = get_chunk()
		chunk_add_floats_endian_safe(chunk, self._matrix, 3)
		return drop_chunk_to_string(chunk), self.parent
		#return self._parent, self._matrix[0], self._matrix[1], self._matrix[2]
		#return PyString_FromStringAndSize(<char*> self._matrix, 3 * sizeof(float)), self._parent
	
	cdef void __setcstate__(self, cstate):
		cdef Chunk* chunk
		cstate2, self.parent = cstate
		chunk = string_to_chunk(cstate2)
		chunk_get_floats_endian_safe(chunk, self._matrix, 3)
		drop_chunk(chunk)
		#self._parent, self._matrix[0], self._matrix[1], self._matrix[2] = cstate
		#self._parent = cstate[1]
		#memcpy(self._matrix, PyString_AS_STRING(cstate[0]), 3 * sizeof(float))
		
	def convert_to(self, CoordSyst parent):
		"""Point.convert_to(parent)

Converts a Point to the coordinates system PARENT in place. The x, y and z
coordinates are modified, and the Point's parent is set to PARENT."""
		self._into(parent, self._matrix)
		self._parent = parent
		
	def __imod__(_Point self, CoordSyst parent):
		self.convert_to(parent)
		return self
	
	def copy(self):
		"""Point.copy() -> Point

Returns a copy of a Point."""
		return Point(self._parent, self._matrix[0], self._matrix[1], self._matrix[2])
	
	def clone(self, Position other not None):
		"""Point.clone(other)

Changes IN PLACE this point so as it is a clone of OTHER."""
		self._parent = other._parent
		other._into(None, self._matrix)
		
	# XXX cause trouble for using Vertex (who inherit from Point) as dict keys
	#def __cmp__(self, Position other):
	#  if (self._parent is other._parent) and (self._matrix[0] == other._matrix[0]) and (self._matrix[1] == other._matrix[1]) and (self._matrix[2] == other._matrix[2]): return 0
	#  return 1




cdef class _Vector(_Point):
	cdef void _into(self, CoordSyst coordsyst, float* result):
		memcpy(result, self._matrix, 3 * sizeof(float))
		if (not self._parent is None) and (not coordsyst is None) and (not self._parent is coordsyst):
			vector_by_matrix(result, self._parent._root_matrix())
			vector_by_matrix(result, coordsyst._inverted_root_matrix())
			
	cdef void _out(self, float* result):
		memcpy(result, self._matrix, 3 * sizeof(float))
		if not self._parent is None:
			vector_by_matrix(result, self._parent._root_matrix())
			
	def copy(self):
		"""Vector.copy() -> Vector

Returns a copy of a Vector."""
		return Vector(self._parent, self._matrix[0], self._matrix[1], self._matrix[2])
	
	def cross_product(self, _Vector vector not None, _Vector result = None):
		"""Vector.cross_product(VECTOR, RESULT = None) -> Vector

Returns the cross product of a Vector with VECTOR."""
		cdef float v[3]
		vector._into(self._parent, v)
		if result is None:
			return Vector(self._parent,
										self._matrix[1] * v[2] - self._matrix[2] * v[1],
										self._matrix[2] * v[0] - self._matrix[0] * v[2],
										self._matrix[0] * v[1] - self._matrix[1] * v[0],
										)
		else:
			result.__init__(self._parent,
											self._matrix[1] * v[2] - self._matrix[2] * v[1],
											self._matrix[2] * v[0] - self._matrix[0] * v[2],
											self._matrix[0] * v[1] - self._matrix[1] * v[0],
											)
			return result
	
	def dot_product(self, _Vector vector not None):
		"""Vector.dot_product(VECTOR) -> float

Returns the dot product of a Vector with VECTOR."""
		cdef float v[3]
		vector._into(self._parent, v)
		return self._matrix[0] * v[0] + self._matrix[1] * v[1] + self._matrix[2] * v[2]
	
	def length(self):
		"""Vector.length() -> float

Gets the length of a Vector."""
		return sqrt(self._matrix[0] * self._matrix[0] + self._matrix[1] * self._matrix[1] + self._matrix[2] * self._matrix[2])
		
	def set_length(self, float new_length):
		"""Vector.set_length(new_length)

Sets the length of a Vector to NEW_LENGTH. The Vector's coordinates are
multiplied as needed."""
		cdef float f
		f = new_length / sqrt(self._matrix[0] * self._matrix[0] + self._matrix[1] * self._matrix[1] + self._matrix[2] * self._matrix[2])
		self._matrix[0] = self._matrix[0] * f
		self._matrix[1] = self._matrix[1] * f
		self._matrix[2] = self._matrix[2] * f
		
	def __mod__(_Vector self, CoordSyst coordsyst):
		"""Vector % coordsyst -> Vector

Converts a Vector to the coordinate system COORDSYST and returns the result.
The returned value may be the same Vector if its coordinate system is
already COORDSYST, so you should be carreful if you modify it."""
		cdef _Vector p
		if (self._parent is None) or (coordsyst is None) or (self._parent is coordsyst): return self
		p = Vector(coordsyst)
		self._into(coordsyst, p._matrix)
		return p
	
	def __add__(_Point self, _Vector vector not None):
		"""Vector + Vector -> Vector

Performs vectorial addition, and returns the result (a new Vector).
Coordinates system conversion is performed if needed (=if the Vector and
VECTOR are not defined in the same coordinates system)."""
		cdef float v[3]
		vector._into(self._parent, v)
		return Vector(self._parent, self._matrix[0] + v[0], self._matrix[1] + v[1], self._matrix[2] + v[2])
	
	def __mul__(_Vector self, float number):
		return Vector(self._parent, self._matrix[0] * number, self._matrix[1] * number, self._matrix[2] * number)
	
	def __div__(_Vector self, float number):
		return Vector(self._parent, self._matrix[0] / number, self._matrix[1] / number, self._matrix[2] / number)
	
	def __truediv__(_Vector self, float number):
		return self.__div__(number)
	
	def __imul__(_Vector self, float number):
		self._matrix[0] = self._matrix[0] * number
		self._matrix[1] = self._matrix[1] * number
		self._matrix[2] = self._matrix[2] * number
		return self
	
	def __idiv__(_Vector self, float number):
		self._matrix[0] = self._matrix[0] / number
		self._matrix[1] = self._matrix[1] / number
		self._matrix[2] = self._matrix[2] / number
		return self
		
	def __neg__(_Vector self):
		return Vector(self._parent, -self._matrix[0], -self._matrix[1], -self._matrix[2])
	
	def __abs__(_Vector self):
		return Vector(self._parent, abs(self._matrix[0]), abs(self._matrix[1]), abs(self._matrix[2]))
	
	def normalize(self):
		"""Vector.normalize()

Normalizes a Vector IN PLACE."""
		cdef float length
		length = self.length()
		self._matrix[0] = self._matrix[0] / length
		self._matrix[1] = self._matrix[1] / length
		self._matrix[2] = self._matrix[2] / length
		
	def set_start_end(self, Position start not None, Position end not None):
		"""Vector.set_start_end(start, end)

Sets this vector IN PLACE so as it correspond to the vector start->end."""
		cdef float s[3], e[3]
		self._parent = start._parent
		start._into(self._parent, s)
		end  ._into(self._parent, e)
		self._matrix[0] = e[0] - s[0]
		self._matrix[1] = e[1] - s[1]
		self._matrix[2] = e[2] - s[2]
		
	def angle_to(self, _Vector vector not None):
		"""Vector.angle_to(VECTOR) -> angle in degree

Computes the angle between this Vector and VECTOR."""
		cdef float v[3]
		vector._into(self._parent, v)
		return vector_angle(self._matrix, v) * 180.0 / pi
	

