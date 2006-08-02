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

cdef Frustum* frustum_coordsyst_into(Frustum* r, Frustum* f, float* old, float* new):
	cdef float scalefactor[3]
	cdef float scaling
	cdef int   i
	scalefactor[0] = scalefactor[1] = scalefactor[2] = 1.0
	if (r == NULL):
		# return a new frustum
		r = <Frustum*> malloc(sizeof(Frustum))
		
	# clone
	memcpy(r, f, sizeof(Frustum))
	if (new != old):
		# change position, points of coordsys
		if old != NULL:
			for i from 0 <= i < 8: point_by_matrix(r.points + 3 * i, old)
			scalefactor[0] = scalefactor[0] * old[16]
			scalefactor[1] = scalefactor[1] * old[17]
			scalefactor[2] = scalefactor[2] * old[18]
			point_by_matrix(r.position, old)
		
		if new != NULL:
			for i from 0 <= i < 8: point_by_matrix(r.points + 3 * i, new)
			scalefactor[0] = scalefactor[0] * new[16]
			scalefactor[1] = scalefactor[1] * new[17]
			scalefactor[2] = scalefactor[2] * new[18]
			point_by_matrix(r.position, new)
			
		# re-compute the normals
		scaling = scalefactor[0]
		if scalefactor[1] > scaling: scaling = scalefactor[1]
		if scalefactor[2] > scaling: scaling = scalefactor[2]
		face_normal(r.planes, r.points, r.points + 3, r.points + 9)
		vector_set_length(r.planes, scaling)
		face_normal(r.planes + 4, r.points + 12, r.points + 15, r.points)
		vector_set_length(r.planes + 4, scaling)
		face_normal(r.planes + 8, r.points + 9, r.points + 6, r.points + 21)
		vector_set_length(r.planes + 8, scaling)
		face_normal(r.planes + 12, r.points + 12, r.points, r.points + 21)
		vector_set_length(r.planes + 12, scaling)
		face_normal(r.planes + 16, r.points + 3, r.points + 15, r.points + 6)
		vector_set_length(r.planes + 16, scaling)
		face_normal(r.planes + 20, r.points + 15, r.points + 12, r.points + 18)
		vector_set_length(r.planes + 20, scaling)
		# re-compute the constants
		r.planes[ 3] = -(r.planes[ 0] * r.points[ 0] + r.planes[ 1] * r.points[ 1] + r.planes[ 2] * r.points[ 2])
		r.planes[ 7] = -(r.planes[ 4] * r.points[ 0] + r.planes[ 5] * r.points[ 1] + r.planes[ 6] * r.points[ 2])
		r.planes[11] = -(r.planes[ 8] * r.points[ 6] + r.planes[ 9] * r.points[ 7] + r.planes[10] * r.points[ 8])
		r.planes[15] = -(r.planes[12] * r.points[ 0] + r.planes[13] * r.points[ 1] + r.planes[14] * r.points[ 2])
		r.planes[19] = -(r.planes[16] * r.points[ 6] + r.planes[17] * r.points[ 7] + r.planes[18] * r.points[ 8])
		r.planes[23] = -(r.planes[20] * r.points[12] + r.planes[21] * r.points[13] + r.planes[22] * r.points[14])
	return r


cdef class CoordSyst(Position):
	#cdef float _matrix               [19]
	#cdef float __root_matrix         [19]
	#cdef float __inverted_root_matrix[19]
	#cdef float _render_matrix        [19]
	#cdef int _frustum_id
	#cdef int _validity
	#cdef int __raypick_data
	#cdef int _option
	#cdef int _auto_static_count
	
	def __new__(self, *args, **kargs):
		self.__raypick_data     = -1
		self._auto_static_count = 3
		
	def __init__(self, _World parent = None):
		"""CoordSyst(PARENT)

Creates a new CoordSyst in the World PARENT."""
		self._matrix[0] = self._matrix[5] = self._matrix[10] = self._matrix[15] = 1.0
		self._matrix[16] = self._matrix[17] = self._matrix[18] = 1.0
		if parent: parent.add(self)
		self._category_bitfield = 1
		
	cdef __getcstate__(self):
		#return struct.pack("<ifffffffffffffffffff", self._option, self._matrix[0], self._matrix[1], self._matrix[2], self._matrix[3], self._matrix[4], self._matrix[5], self._matrix[6], self._matrix[7], self._matrix[8], self._matrix[9], self._matrix[10], self._matrix[11], self._matrix[12], self._matrix[13], self._matrix[14], self._matrix[15], self._matrix[16], self._matrix[17], self._matrix[18])
		cdef Chunk* chunk
		chunk = get_chunk()
		chunk_add_int_endian_safe   (chunk, self._option)
		chunk_add_floats_endian_safe(chunk, self._matrix, 19)
		chunk_add_int_endian_safe   (chunk, self._category_bitfield)
		return drop_chunk_to_string(chunk)
	
	cdef void __setcstate__(self, cstate):
		self._validity = COORDSYS_INVALID
#    self._option, self._matrix[0], self._matrix[1], self._matrix[2], self._matrix[3], self._matrix[4], self._matrix[5], self._matrix[6], self._matrix[7], self._matrix[8], self._matrix[9], self._matrix[10], self._matrix[11], self._matrix[12], self._matrix[13], self._matrix[14], self._matrix[15], self._matrix[16], self._matrix[17], self._matrix[18] = struct.unpack("<ifffffffffffffffffff", cstate)
		
		cdef Chunk* chunk
		chunk = string_to_chunk(cstate)
		chunk_get_int_endian_safe   (chunk, &self._option)
		chunk_get_floats_endian_safe(chunk,  self._matrix, 19)
		if len(cstate) >= 84: chunk_get_int_endian_safe(chunk, &self._category_bitfield)
		else:                 self._category_bitfield = 1 # For backward compatibility
		drop_chunk(chunk)
		
	cdef void _into(self, CoordSyst coordsyst, float* result):
		memcpy(result, self._matrix + 12, 12)
		if (not self._parent is None) and (not coordsyst is None) and (not self._parent is coordsyst):
			point_by_matrix(result, self._parent._root_matrix())
			point_by_matrix(result, coordsyst._inverted_root_matrix())
			
	cdef void _out(self, float* result):
		memcpy(result, self._matrix + 12, 12)
		if not self._parent is None:
			point_by_matrix(result, self._parent._root_matrix())
			
	cdef void _batch(self, CoordSyst coord_syst):
		pass
	
	cdef void _render(self, CoordSyst coord_syst):
		pass
	
	cdef int _shadow(self, CoordSyst coord_syst, _Light light):
		pass
	
	cdef void _raypick(self, RaypickData raypick_data, CoordSyst raypickable, int category):
		pass
	
	cdef int _raypick_b(self, RaypickData raypick_data, CoordSyst raypickable, int category):
		return 0
	
	cdef void _collect_raypickables(self, Chunk* items, float* rsphere, float* sphere, int category):
		pass
	
	cdef int _contains(self, _CObj obj):
		return 0
	
	def added_into(self, _World new_parent):
		"""CoordSyst.added_into(new_parent)

Called when the CoordSyst is added into NEW_PARENT, or removed from its previous parent
(in this case, NEW_PARENT is None)."""
		self._parent = new_parent
		if not(self._option & COORDSYS_NON_AUTO_STATIC) and (self._option & COORDSYS_STATIC):
			self._go_not_static()
		else:
			self._auto_static_count = 3
			
	cdef void _get_sphere(self, float* sphere):
		sphere[0] = sphere[1] = sphere[2] = sphere[3] = 0.0
		
	def get_sphere(self):
		"""CoordSyst.get_sphere() -> (Point, float)

Returns a sphere wrapping the given CoordSyst. The sphere is defined by the center
and the radius (a Point and a float value)."""
		cdef float sphere[4]
		self._get_sphere(sphere)
		return Point(self, sphere[0], sphere[1], sphere[2]), sphere[3]
	
	cdef void _get_box(self, float* box, float* matrix):
		pass
		
	def get_box(self):
		"""CoordSyst.get_box() -> (Point, Point)

Returns a box wrapping the given CoordSyst. The box is defined by 2 Point corresponding
to 2 opposite corners of the box, the box being aligned on the X, Y and Z axis."""
		cdef float box[6]
		box[0] = box[1] = box[2] =  10000000000000.0
		box[3] = box[4] = box[5] = -10000000000000.0
		self._get_box(box, NULL)
		return Point(self._parent, box[0], box[1], box[2]), Point(self._parent, box[3], box[4], box[5])
	
	def get_dimension(self):
		"""CoordSyst.get_dimension() -> (float, float, float)

Returns the dimension of a CoordSyst: a (width, height, depth) tuple.
For a World, this includes also all items inside the World."""
		cdef float box[6]
		box[0] = box[1] = box[2] =  10000000000000.0
		box[3] = box[4] = box[5] = -10000000000000.0
		self._get_box(box, NULL)
		return box[3] - box[0], box[4] - box[1], box[5] - box[2]
	
	def set_dimension(self, float width, float height, float depth):
		"""CoordSyst.set_dimension(width, height, depth)

Sets the dimension of a CoordSyst ; in other worlds, scale the coordsyst so as it has
the given dimensions."""
		cdef float box[6]
		box[0] = box[1] = box[2] =  10000000000000.0
		box[3] = box[4] = box[5] = -10000000000000.0
		self._get_box(box, NULL)
		self.scale(width / (box[3] - box[0]), height / (box[4] - box[1]), depth / (box[5] - box[2]))
		
		
	cdef float* _raypick_data(self, RaypickData data):
		cdef float* matrix, *rdata
		cdef float  f
		if (self.__raypick_data == -1):
			self.__raypick_data = chunk_register(data.raypick_data, 7 * sizeof(float))
			rdata = <float*> (data.raypick_data.content + self.__raypick_data)
			# transform origin and direction into the parent coordsys
			matrix = self._inverted_root_matrix()
			point_by_matrix_copy (rdata,     data.root_data,     matrix)
			vector_by_matrix_copy(rdata + 3, data.root_data + 3, matrix)
			
			if (matrix[16] != 1.0) or (matrix[17] != 1.0) or (matrix[18] != 1.0): vector_normalize(rdata + 3)

			if data.root_data[6] > 0.0:
				if matrix[16] > matrix[17]: f = matrix[16]
				else:                       f = matrix[17]
				if matrix[18] > f:          f = matrix[18]
				
				rdata[6] = data.root_data[6] * f
				
			else: rdata[6] = -1.0
			
			chunk_add_ptr(data.raypicked, <void*> self)
			return rdata
		else: return <float*> (data.raypick_data.content + self.__raypick_data)

	cdef float _distance_out(self, float distance):
		cdef float* matrix
		cdef float  f
		
		matrix = self._inverted_root_matrix()
		if matrix[16] > matrix[17]: f = matrix[16]
		else:                       f = matrix[17]
		if matrix[18] > f:          f = matrix[18]
		
		return distance / f
		
	def begin_round(self):
		"""CoordSyst.begin_round()

Called (by the MainLoop) when a new round begins; default implementation does nothing."""
		
		# XXX copied to Body.begin_round, World.begin_round
		
		if (self._option & COORDSYS_NON_AUTO_STATIC) == 0:
			if self._auto_static_count == 0:
				if not (self._option & COORDSYS_STATIC): self._go_static()
			else:
				self._auto_static_count = self._auto_static_count - 1
				
	def end_round(self):
		"""CoordSyst.end_round()

Called (by the MainLoop) when a round is finished; default implementation does nothing."""
		pass
	
	def advance_time(self, float proportion):
		"""CoordSyst.advance_time(proportion)

Called (by the MainLoop) when a piece of a round is achieved; default implementation does nothing.
PROPORTION is the proportion of the current round's time that has passed (1.0 for an entire round)."""
		pass
	
	property parent:
		def __get__(self):
			return self._parent
#    def __set__(self, _World parent):
#      self._parent = parent
			
	property visible:
		def __get__(self):
			return not(self._option & HIDDEN)
		def __set__(self, int x):
			if x: self._option = self._option & ~HIDDEN
			else: self._option = self._option |  HIDDEN
	
	property solid:
		def __get__(self):
			return self._category_bitfield
		def __set__(self, x):
			if isinstance(x, int):
				self._category_bitfield = x
			else:
				if x: self._category_bitfield = 1
				else: self._category_bitfield = 0
	
	property static:
		def __get__(self):
			return self._option & COORDSYS_STATIC
		def __set__(self, int x):
			#if x: self._option = self._option |  COORDSYS_STATIC
			#else: self._option = self._option & ~COORDSYS_STATIC
			if       (self._option & COORDSYS_STATIC) and not x: self._go_not_static()
			elif not (self._option & COORDSYS_STATIC) and     x: self._go_static()
			
	property auto_static:
		def __get__(self):
			return not(self._option & COORDSYS_NON_AUTO_STATIC)
		def __set__(self, int x):
			if x: self._option = self._option & ~COORDSYS_NON_AUTO_STATIC
			else: self._option = self._option |  COORDSYS_NON_AUTO_STATIC

	cdef void _go_static(self):
		self._option = self._option |  COORDSYS_STATIC
		
	cdef void _go_not_static(self):
		self._option = self._option & ~COORDSYS_STATIC
		self._auto_static_count = 3
		
	cdef void _invalidate(self):
		self._validity = COORDSYS_INVALID
		if not(self._option & COORDSYS_NON_AUTO_STATIC) and (self._option & COORDSYS_STATIC):
			self._go_not_static()
		else:
			self._auto_static_count = 3
			
			
			
	property x:
		def __get__(self):
			return self._matrix[12]
		def __set__(self, float x):
			self._matrix[12] = x
			self._invalidate()
			
	property y:
		def __get__(self):
			return self._matrix[13]
		def __set__(self, float x):
			self._matrix[13] = x
			self._invalidate()
			
	property z:
		def __get__(self):
			return self._matrix[14]
		def __set__(self, float x):
			self._matrix[14] = x
			self._invalidate()
			
	property matrix:
		def __get__(self):
			return self._matrix[0], self._matrix[1], self._matrix[2], self._matrix[3], self._matrix[4], self._matrix[5], self._matrix[6], self._matrix[7], self._matrix[8], self._matrix[9], self._matrix[10], self._matrix[11], self._matrix[12], self._matrix[13], self._matrix[14], self._matrix[15], self._matrix[16], self._matrix[17], self._matrix[18]
		def __set__(self, matrix):
			if len(matrix) == 16:
				self._matrix[0], self._matrix[1], self._matrix[2], self._matrix[3], self._matrix[4], self._matrix[5], self._matrix[6], self._matrix[7], self._matrix[8], self._matrix[9], self._matrix[10], self._matrix[11], self._matrix[12], self._matrix[13], self._matrix[14], self._matrix[15] = matrix
			else:
				self._matrix[0], self._matrix[1], self._matrix[2], self._matrix[3], self._matrix[4], self._matrix[5], self._matrix[6], self._matrix[7], self._matrix[8], self._matrix[9], self._matrix[10], self._matrix[11], self._matrix[12], self._matrix[13], self._matrix[14], self._matrix[15], self._matrix[16], self._matrix[17], self._matrix[18] = matrix
			self._invalidate()
			self._check_lefthanded()
			
	property root_matrix:
		def __get__(self):
			cdef float* m
			m = self._root_matrix()
			return m[0], m[1], m[2], m[3], m[4], m[5], m[6], m[7], m[8], m[9], m[10], m[11], m[12], m[13], m[14], m[15], m[16], m[17], m[18]
		
	property inverted_root_matrix:
		def __get__(self):
			cdef float* m
			m = self._inverted_root_matrix()
			return m[0], m[1], m[2], m[3], m[4], m[5], m[6], m[7], m[8], m[9], m[10], m[11], m[12], m[13], m[14], m[15], m[16], m[17], m[18]
		
	property lefthanded:
		def __get__(self):
			return (self._option & LEFTHANDED) != 0
			
	property scale_x:
		def __get__(self):
			return self._matrix[16]
		def __set__(self, float x):
			self.scale(x / self._matrix[16], 1.0, 1.0)
			
	property scale_y:
		def __get__(self):
			return self._matrix[17]
		def __set__(self, float x):
			self.scale(1.0, x / self._matrix[17], 1.0)
			
	property scale_z:
		def __get__(self):
			return self._matrix[18]
		def __set__(self, float x):
			self.scale(1.0, 1.0, x / self._matrix[18])
			
	def set_scale_factors(self, float scale_x, float scale_y, float scale_z):
		"""CoordSyst.set_scale_factors(SCALE_X, SCALE_Y, SCALE_Z)

Sets the scale factors in the X, Y and Z dimension."""
		self.scale(scale_x / self._matrix[16], scale_y / self._matrix[17], scale_z / self._matrix[18])
		
		
	cdef void _check_lefthanded(self):
		if self._matrix[16] * self._matrix[17] * self._matrix[18] < 0.0: self._option = self._option |  LEFTHANDED
		else:                                                            self._option = self._option & ~LEFTHANDED
		
	cdef float* _root_matrix(self):
		if not(self._validity & COORDSYS_ROOT_VALID):
			if self._parent is None: memcpy(self.__root_matrix, self._matrix, sizeof(self.__root_matrix))
			else: multiply_matrix(self.__root_matrix, self._parent._root_matrix(), self._matrix)
			self._validity = self._validity | COORDSYS_ROOT_VALID
		return self.__root_matrix
	
	cdef float* _inverted_root_matrix(self):
		if not(self._validity & COORDSYS_INVERTED_ROOT_VALID):
			matrix_invert(self.__inverted_root_matrix, self._root_matrix())
		return self.__inverted_root_matrix

	def get_root(self):
		"""CoordSyst.get_root() -> World

Returns the "root parent" of a coordsyst, i.e. the scene (= the parent world that has no parent)."""
		cdef _World root
		root = self._parent
		if root is None: return None
		while root._parent: root = root._parent
		return root

	cdef _World _get_root(self):
		cdef _World root
		root = self._parent
		if root is None: return None
		while root._parent: root = root._parent
		return root
	
	def is_inside(self, CoordSyst coordsyst):
		"""CoordSyst.is_inside(COORDSYST) -> bool

Returns true if self is inside COORDSYST, i.e. if COORDSYST is self, or self.parent, or
self.parent.parent or..."""
		cdef CoordSyst parent
		parent = self
		while parent:
			if parent is coordsyst: return 1
			parent = parent._parent
		return 0

	def set_xyz(self, float x, float y, float z):
		"""CoordSyst.set_xyz(x, y, z)

Moves a CoordSyst to X, Y and Z."""
		self._matrix[12] = x
		self._matrix[13] = y
		self._matrix[14] = z
		self._invalidate()
		
	def move(self, Position position not None):
		"""Position.move(position)

Moves a Position to POSITION.
Coordinates system conversion is performed if needed (=if the Position and
POSITION are not defined in the same coordinates system)."""
		position._into(self._parent, self._matrix + 12)
		self._invalidate()
		
	def add_xyz(self, float x, float y, float z):
		"""Position.add_xyz(x, y, z)

Translates a Position by X, Y and Z."""
		self._matrix[12] = self._matrix[12] + x
		self._matrix[13] = self._matrix[13] + y
		self._matrix[14] = self._matrix[14] + z
		self._invalidate()
		
	def shift(self, float x, float y, float z):
		"""CoordSyst.shift(x, y, z)

Translates a CoordSyst by X, Y and Z, given in CoordSyst space."""
		self._matrix[12] = self._matrix[12] + x * self._matrix[0] + y * self._matrix[4] + z * self._matrix[ 8]
		self._matrix[13] = self._matrix[13] + x * self._matrix[1] + y * self._matrix[5] + z * self._matrix[ 9]
		self._matrix[14] = self._matrix[14] + x * self._matrix[2] + y * self._matrix[6] + z * self._matrix[10]
		self._invalidate()
		
	def add_vector(self, _Vector vector not None):
		"""Position.add_vector(vector)

Translates a Position IN PLACE.
Coordinates system conversion is performed if needed (=if the Position and
VECTOR are not defined in the same coordinates system).

For Vector, add_vector means vectorial addition (translating a vector does
nothing !)."""
		cdef float v[3]
		vector._into(self._parent, v)
		self._matrix[12] = self._matrix[12] + v[0]
		self._matrix[13] = self._matrix[13] + v[1]
		self._matrix[14] = self._matrix[14] + v[2]
		self._invalidate()
		return self
	
	def __iadd__(self, _Vector vector not None):
		"""__iadd__(vec)

		Same as add_vector.
		"""
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
		self._matrix[12] = self._matrix[12] + k * v[0]
		self._matrix[13] = self._matrix[13] + k * v[1]
		self._matrix[14] = self._matrix[14] + k * v[2]
		self._invalidate()
		return self
		
	def scale(self, float x, float y, float z):
		"""CoordSyst.scale(x, y, z)

Scales a CoordSyst by X, Y and Z (Changes its dimensions).
Negative values are accepted."""
		matrix_scale(self._matrix, x, y, z)
		self._check_lefthanded()
		self._invalidate()
		
	def set_identity(self):
		"""CoordSyst.set_identity()

Resets a CoordSyst (moves it to 0,0,0 and removes any rotation or scaling)."""
		matrix_set_identity(self._matrix)
		self._invalidate()
		
	def position(self):
		"""Position.position() -> Point

Returns the position (a Point) at the same position than the Position."""
		return Point(self._parent, self._matrix[12], self._matrix[13], self._matrix[14])
	
	def __add__(CoordSyst self, _Vector vector not None):
		"""Position + Vector -> Point

Translates a Position and returns the result (a new Point).
Coordinates system conversion is performed if needed (=if the Position and
VECTOR are not defined in the same coordinates system)."""
		cdef float v[3]
		vector._into(self._parent, v)
		return Point(self._parent, self._matrix[12] + v[0], self._matrix[13] + v[1], self._matrix[14] + v[2])
	
	def __sub__(CoordSyst self, _Vector vector not None):
		"""Position - Vector -> Point

Translates a Position and returns the result (a new Point).
Coordinates system conversion is performed if needed (=if the Position and
VECTOR are not defined in the same coordinates system)."""
		cdef float v[3]
		vector._into(self._parent, v)
		return Point(self._parent, self._matrix[12] - v[0], self._matrix[13] - v[1], self._matrix[14] - v[2])
	
	def distance_to(self, Position other not None):
		"""Position.distance_to(other) -> float

Gets the distance between a Position and anOTHER."""
		cdef float v[3]
		other._into(self._parent, v)
		return sqrt((self._matrix[12] - v[0]) * (self._matrix[12] - v[0]) + (self._matrix[13] - v[1]) * (self._matrix[13] - v[1]) + (self._matrix[14] - v[2]) * (self._matrix[14] - v[2]))
	
	def vector_to(self, Position other not None):
		"""Position.vector_to(other) -> Vector

Gets the vector that starts at a Position and ends at OTHER."""
		cdef float v[3]
		other._into(self._parent, v)
		return Vector(self._parent, v[0] - self._matrix[12], v[1] - self._matrix[13], v[2] - self._matrix[14])
		
	def __rshift__(self, Position other not None):
		"""__rshift__(pos)

		Same as vector_to.
		"""
		return self.vector_to(other)
	
	def look_at(self, Position target not None):
		"""CoordSyst.look_at(target)

Rotate so that this CoordSyst's *negative*-Z points at target."""
		cdef float f[3]
		target._into(self._parent, f)
		if not isinstance(target, _Vector):
			f[0] = f[0] - self._matrix[12]
			f[1] = f[1] - self._matrix[13]
			f[2] = f[2] - self._matrix[14]
		matrix_look_to_Z(self._matrix, f)
		self._invalidate()
		
	def look_at_y(self, Position target not None):
		"""CoordSyst.look_at_y(target)

Rotate so that this object's positive-Y points at target."""
		cdef float f[3]
		target._into(self._parent, f)
		if not isinstance(target, _Vector):
			f[0] = f[0] - self._matrix[12]
			f[1] = f[1] - self._matrix[13]
			f[2] = f[2] - self._matrix[14]
		matrix_look_to_Y(self._matrix, f)
		self._invalidate()
		
	def look_at_x(self, Position target not None):
		"""CoordSyst.look_at_x(target)

Rotate so that this object's positive-X points at target."""
		cdef float f[3]
		target._into(self._parent, f)
		if not isinstance(target, _Vector):
			f[0] = f[0] - self._matrix[12]
			f[1] = f[1] - self._matrix[13]
			f[2] = f[2] - self._matrix[14]
		matrix_look_to_X(self._matrix, f)
		self._invalidate()
		
	def turn_y(self, float angle):
		"""CoordSyst.turn_y(angle)

Rotate about the *local* Y axis, in degrees."""
		matrix_turn_y(self._matrix, to_radians(angle))
		self._invalidate()
	
	def turn_x(self, float angle):
		"""CoordSyst.turn_x(angle)

Rotate about the *local* X axis, in degrees."""
		matrix_turn_x(self._matrix, to_radians(angle))
		self._invalidate()
	
	def turn_z(self, float angle):
		"""CoordSyst.turn_z(angle)

Rotate about the *local* Z axis, in degrees."""
		matrix_turn_z(self._matrix, to_radians(angle))
		self._invalidate()
	
	def turn_lateral(self, float angle):
		"""CoordSyst.turn_lateral(angle)

Same as turn_y."""
		matrix_turn_y(self._matrix, to_radians(angle))
		self._invalidate()
	
	def turn_vertical(self, float angle):
		"""CoordSyst.turn_vertical(angle)

Same as turn_x."""
		matrix_turn_x(self._matrix, to_radians(angle))
		self._invalidate()
	
	def turn_incline(self, float angle):
		"""CoordSyst.turn_incline(angle)

Same as turn_z."""
		matrix_turn_z(self._matrix, to_radians(angle))
		self._invalidate()
	
	def rotate_y(self, float angle):
		"""CoordSyst.rotate_y(angle)
		
Rotate about the *parent's* Y axis, in degrees.
e.g., If you are facing positive-Y with head to positive-Z, it
spins like a car's steering wheel."""
		matrix_rotate_y(self._matrix, to_radians(angle))
		self._invalidate()
	
	def rotate_x(self, float angle):
		"""CoordSyst.rotate_x(angle)

Rotate about the *parent's* X axis, in degrees.
e.g., If you are facing positive-Y with head to positive-Z, it
spins like a car's tire."""
		matrix_rotate_x(self._matrix, to_radians(angle))
		self._invalidate()
	
	def rotate_z(self, float angle):
		"""CoordSyst.rotate_z(angle)

Rotate about the *parent's* Z axis, in degrees.
e.g., If you are facing positive-Y with head to positive-Z, it
spins like a spinning top."""
		matrix_rotate_z(self._matrix, to_radians(angle))
		self._invalidate()
	
	def rotate_lateral(self, float angle):
		"""CoordSyst.rotate_lateral(angle)
		
Same as rotate_y."""
		matrix_rotate_y(self._matrix, to_radians(angle))
		self._invalidate()
	
	def rotate_vertical(self, float angle):
		"""CoordSyst.rotate_vertical(angle)

Same as rotate_x."""
		matrix_rotate_x(self._matrix, to_radians(angle))
		self._invalidate()
	
	def rotate_incline(self, float angle):
		"""CoordSyst.rotate_incline(angle)

Same as rotate_z."""
		matrix_rotate_z(self._matrix, to_radians(angle))
		self._invalidate()
	
	def rotate_axe(self, float angle, Position axe not None):
		"""Same as rotate_axis"""
		cdef float coords[3]
		memcpy(coords, self._matrix + 12, 3 * sizeof(float))
		cdef float f[3]
		axe._into(self._parent, f)
		matrix_rotate_axe(self._matrix, to_radians(angle), f[0], f[1], f[2])
		memcpy(self._matrix + 12, coords, 3 * sizeof(float))
		self._invalidate()
		
	def rotate_axe_xyz(self, float angle, float x, float y, float z):
		"""Same as rotate_axis_xyz"""
		cdef float coords[3]
		memcpy(coords, self._matrix + 12, 3 * sizeof(float))
		matrix_rotate_axe(self._matrix, to_radians(angle), x, y, z)
		memcpy(self._matrix + 12, coords, 3 * sizeof(float))
		self._invalidate()
		
	def rotate_axis(self, float angle, Position axe not None):
		"""CoordSyst.rotate_axis(ANGLE, AXE)

Rotate a CoordSyst about an axis, of ANGLE degrees.
The axis is defined by a Vector AXE, and pass through the origin (0, 0, 0)."""
		cdef float coords[3]
		memcpy(coords, self._matrix + 12, 3 * sizeof(float))
		cdef float f[3]
		axe._into(self._parent, f)
		matrix_rotate_axe(self._matrix, to_radians(angle), f[0], f[1], f[2])
		memcpy(self._matrix + 12, coords, 3 * sizeof(float))
		self._invalidate()
		
	def rotate_axis_xyz(self, float angle, float x, float y, float z):
		"""CoordSyst.rotate_axis_xyz(ANGLE, X, Y, Z)

Rotate a CoordSyst about an (X, Y, Z) axis, of ANGLE degrees."""
		cdef float coords[3]
		memcpy(coords, self._matrix + 12, 3 * sizeof(float))
		matrix_rotate_axe(self._matrix, to_radians(angle), x, y, z)
		memcpy(self._matrix + 12, coords, 3 * sizeof(float))
		self._invalidate()
		
	def rotate(self, float angle, Position a not None, Position b not None):
		"""CoordSyst.rotate(ANGLE, A, B)

Rotate a CoordSyst about an axis, of ANGLE degrees.
The axis is defined by a Position A, and another Position or a Vector B."""
		cdef float p1[3], p2[3]
		a._into(self._parent, p1)
		b._into(self._parent, p2)
		if not isinstance(b, _Vector):
			p2[0] = p2[0] - p1[0]
			p2[1] = p2[1] - p1[1]
			p2[2] = p2[2] - p1[2]
		matrix_rotate(self._matrix, to_radians(angle), p1, p2)
		self._invalidate()
		
	def rotate_xyz(self, float angle, float x1, float y1, float z1, float x2, float y2, float z2):
		"""CoordSyst.rotate_xyz(ANGLE, X1, Y1, Z1, X2, Y2, Z2)

Rotate a CoordSyst about an axis, of ANGLE degrees.
The axis is defined by a two point (X1, Y1, Z1) and (X2, Y2, Z2)."""
		cdef float coords[3]
		memcpy(coords, self._matrix + 12, 3 * sizeof(float))
		cdef float p1[3], p2[3]
		p1[0] = x1
		p1[1] = y1
		p1[2] = z1
		p2[0] = x2 - x1
		p2[1] = y2 - y2
		p2[2] = z2 - z2
		matrix_rotate(self._matrix, to_radians(angle), p1, p2)
		memcpy(self._matrix + 12, coords, 3 * sizeof(float))
		self._invalidate()
		
	def __repr__(self):
		return "<%s>" % self.__class__.__name__
	
	
	def transform(self, Position position not None):
		"""DEPRECATED"""
		cdef float p[3]
		position._into(self, p)
		return p[0], p[1], p[2]
	
	def transform_point(self, float x, float y, float z, CoordSyst from_parent):
		"""DEPRECATED"""
		cdef float p[3]
		p[0] = x
		p[1] = y
		p[2] = z
		if not from_parent is None: point_by_matrix(p, from_parent._root_matrix())
		point_by_matrix(p, self._inverted_root_matrix())
		return p[0], p[1], p[2]
	
	def transform_vector(self, float x, float y, float z, CoordSyst from_parent):
		"""DEPRECATED"""
		cdef float p[3]
		p[0] = x
		p[1] = y
		p[2] = z
		if not from_parent is None: vector_by_matrix(p, from_parent._root_matrix())
		vector_by_matrix(p, self._inverted_root_matrix())
		return p[0], p[1], p[2]
	
	
	def interpolate(self, CoordSystState state1, CoordSystState state2, float factor):
		"""CoordSyst.interpolate(state1, state2, factor)

Interpolates between STATE1 and STATE2. FACTOR determine the importance of the two
states(0.0 => STATE1, 1.0 => STATE2)."""
		cdef float q[4]
		cdef float factor1
		state1._check_state_validity()
		state2._check_state_validity()
		factor1 = 1.0 - factor
		
		quaternion_slerp(q, state1._quaternion, state2._quaternion, factor, factor1)
		
		matrix_from_quaternion(self._matrix, q)
		
		self._matrix[12] = factor1 * state1._matrix[12] + factor * state2._matrix[12]
		self._matrix[13] = factor1 * state1._matrix[13] + factor * state2._matrix[13]
		self._matrix[14] = factor1 * state1._matrix[14] + factor * state2._matrix[14]
		self._matrix[16] = factor1 * state1._matrix[16] + factor * state2._matrix[16]
		self._matrix[17] = factor1 * state1._matrix[17] + factor * state2._matrix[17]
		self._matrix[18] = factor1 * state1._matrix[18] + factor * state2._matrix[18]
		if (self._matrix[16] != 1.0) or (self._matrix[17] != 1.0) or (self._matrix[18] != 1.0):
			matrix_scale(self._matrix, self._matrix[16], self._matrix[17], self._matrix[18])
		self._invalidate()
		
# 	def interpolate_add(self, CoordSystState state1, CoordSystState state2):
# 		"""CoordSyst.interpolate_add(state1, state2)

# """
# 		cdef float q [4]
# 		cdef float m [19]
# 		cdef float m2[19]
# 		cdef float factor1
# 		state1._check_state_validity()
# 		state2._check_state_validity()
# 		factor1 = 1.0 - factor
		
# 		#quaternion_slerp(q, state1._quaternion, state2._quaternion, factor, factor1)
# 		#matrix_from_quaternion(m, q)
# 		#matrix_copy(m2, self._matrix)
# 		#multiply_matrix(self._matrix, m, m2)
		
# 		self._matrix[12] = factor1 * state1._matrix[12] + factor * state2._matrix[12]
# 		self._matrix[13] = factor1 * state1._matrix[13] + factor * state2._matrix[13]
# 		self._matrix[14] = factor1 * state1._matrix[14] + factor * state2._matrix[14]
# 		self._matrix[16] = factor1 * state1._matrix[16] + factor * state2._matrix[16]
# 		self._matrix[17] = factor1 * state1._matrix[17] + factor * state2._matrix[17]
# 		self._matrix[18] = factor1 * state1._matrix[18] + factor * state2._matrix[18]
# 		if (self._matrix[16] != 1.0) or (self._matrix[17] != 1.0) or (self._matrix[18] != 1.0):
# 			matrix_scale(self._matrix, self._matrix[16], self._matrix[17], self._matrix[18])
# 		self._invalidate()
		
	def add_speed(self, CoordSystSpeed speed):
		"""CoordSyst.add_speed(speed)

"""
		cdef float m2[19]
		matrix_copy(m2, self._matrix)
		multiply_matrix(self._matrix, m2, speed._matrix)
		self._invalidate()
		
		
cdef class CoordSystState(CoordSyst):
	"""CoordSystState

A State that take care of CoordSyst position, rotation and scaling.

CoordSystState extend CoordSyst, and thus have similar method (e.g. set_xyz, rotate_*,
scale, ...)"""
	
	#cdef float _quaternion[4]
	
	def __init__(self, CoordSyst coord_syst):
		"""CoordSystState(coord_syst) -> CoordSystState

Creates a new CoordSystState, with the same position, rotation and scaling than COORD_SYST."""
		if not coord_syst is None:
			self.added_into(coord_syst.parent) # Hack !
			matrix_copy(self._matrix, coord_syst._matrix)
			
	cdef void _invalidate(self):
		self._validity = COORDSYS_INVALID
		self._option   = self._option & ~COORDSYST_STATE_VALID
		
	cdef void _check_state_validity(self):
		if not(self._option & COORDSYST_STATE_VALID):
			self._option = self._option | COORDSYST_STATE_VALID
			quaternion_from_matrix(self._quaternion, self._matrix)
			
	cdef void __setcstate__(self, cstate):
		CoordSyst.__setcstate__(self, cstate)
		self._option = self._option & ~COORDSYST_STATE_VALID
		
	property quaternion:
		def __get__(self):
			self._check_state_validity()
			return self._quaternion[0], self._quaternion[1], self._quaternion[2], self._quaternion[3]
		def __set__(self, q):
			self._option = self._option | COORDSYST_STATE_VALID
			self._quaternion[0], self._quaternion[1], self._quaternion[2], self._quaternion[3] = q
			

cdef class CoordSystSpeed(CoordSyst):
	"""CoordSystSpeed

A Coordinate System "speed" / derivation, taking into account position, rotation and scaling.

CoordSystSpeed extend CoordSyst, and thus have similar method (e.g. set_xyz, rotate_*,
scale, ...)"""
	
	def __init__(self, CoordSyst coord_syst):
		"""CoordSystSpeed(coord_syst) -> CoordSystSpeed

Creates a new CoordSystSpeed, for the given COORD_SYST."""
		self._matrix[0] = self._matrix[5] = self._matrix[10] = self._matrix[15] = 1.0
		self._matrix[16] = self._matrix[17] = self._matrix[18] = 1.0
		if not coord_syst is None:
			self.added_into(coord_syst.parent) # Hack !

	def reset_orientation_scaling(self):
		self._matrix[1] = self._matrix[2] = self._matrix[3] = self._matrix[4] = 0.0
		self._matrix[6] = self._matrix[7] = self._matrix[8] = self._matrix[9] = 0.0
		self._matrix[11] = 0.0
		self._matrix[0] = self._matrix[5] = self._matrix[10] = self._matrix[15] = 1.0
		self._matrix[16] = self._matrix[17] = self._matrix[18] = 1.0
		self._invalidate()
		
		

cdef class PythonCoordSyst(CoordSyst):
	"""A CoordSyst whose rendering part is implemented in Python.
This class is destinated to be inherited.
You should override the batch and render methods.
"""
	cdef void _batch(self, CoordSyst parent):
		if self._option & HIDDEN: return
		self._frustum_id = -1
		cdef int       result
		cdef CoordSyst coordsyst
		cdef _Material material
		result, coordsyst, material = self.batch()
		if coordsyst is self:
			multiply_matrix(self._render_matrix, parent._render_matrix, self._matrix)
		#else:
		#  memcpy(self._render_matrix, coordsyst._render_matrix, sizeof(self._render_matrix))
			
		if   result == 1: renderer._batch(renderer.opaque,     self, coordsyst, -1)
		elif result == 2: renderer._batch(renderer.alpha,      self, coordsyst, -1)
		elif result == 3: renderer._batch(renderer.secondpass, self, coordsyst, -1)
		
	cdef void _render(self, CoordSyst coordsyst):
		self.render()
		
	cdef int _shadow(self, CoordSyst coordsyst, _Light light):
		return self.shadow(coordsyst, light)
	
	#cdef void _raypick(self, RaypickData raypick_data, CoordSyst raypickable):
	#  self._raypick(raypick_data, raypickable)
	
	#cdef int _raypick_b(self, RaypickData raypick_data, CoordSyst raypickable):
	#  return self._raypick_b(raypick_data, raypickable)
	
	def batch(self):
		"""PythonCoordSyst.batch()

Should return a tuple (TYPE, COORDSYST, MATERIAL), where type can be :
	0 if invisible / not drawn
	1 if drawn without alpha
	2 if drawn with alpha
COORDSYST is the coordinate system to use for rendering the object (usually self)."""
		return 0, self, None
	
	def render(self):
		"""PythonCoordSyst.render()

Should perform the rendering (e.g. by calling OpenGL operation)."""
		
	def shadow(self, CoordSyst coordsyst, _Light light):
		return 0
	
	#def raypick(self, raypick_data, raypickable):
	#  pass
	
	#def raypick_b(self, raypick_data, raypickable):
	#  pass




