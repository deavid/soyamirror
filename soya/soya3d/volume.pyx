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



cdef class _Volume(CoordSyst):
	#cdef _Shape _shape
	
	def __init__(self, _World parent = None, _Shape shape = None):
		self._shape = shape
		CoordSyst.__init__(self, parent)
		
	property shape:
		def __get__(self):
			return self._shape
		def __set__(self, _Shape shape):
			self._shape = shape
			
	def set_shape(self, _Shape shape):
		self._shape = shape
		
	cdef __getcstate__(self):
		return CoordSyst.__getcstate__(self), self._shape
	
	cdef void __setcstate__(self, cstate):
		CoordSyst.__setcstate__(self, cstate[0])
		self._shape = cstate[1]
		
	cdef void _batch(self, CoordSyst coordsyst):
		if self._option & HIDDEN: return
		#multiply_matrix(self._render_matrix, renderer.current_camera._render_matrix, self._root_matrix())
		multiply_matrix(self._render_matrix, coordsyst._render_matrix, self._matrix)
		self._frustum_id = -1
		if not self._shape is None: self._shape._batch(self)
		
	cdef int _shadow(self, CoordSyst coordsyst, _Light light):
		if not self._shape is None: return self._shape._shadow(self, light)
		return 0
	
	cdef void _raypick(self, RaypickData raypick_data, CoordSyst raypickable):
		if (self._shape is None) or (self._option & NON_SOLID): return
		self._shape._raypick(raypick_data, self)
		
	cdef int _raypick_b(self, RaypickData raypick_data, CoordSyst raypickable):
		if (self._shape is None) or (self._option & NON_SOLID): return 0
		return self._shape._raypick_b(raypick_data, self)
	
	cdef void _collect_raypickables(self, Chunk* items, float* rsphere, float* sphere):
		if self._option & NON_SOLID: return
		
		cdef float* matrix
		cdef float  s[4]
		# transform sphere to my coordsys
		# XXX avoid using self._inverted_root_matrix() -- use rather the parent's result (=sphere ?) (faster)
		matrix = self._inverted_root_matrix()
		point_by_matrix_copy(s, rsphere, matrix)
		s[3] = length_by_matrix(rsphere[3], matrix)
		if not self._shape is None: self._shape._collect_raypickables(items, rsphere, s, self)
		
	cdef int _contains(self, _CObj obj):
		if self._shape is obj: return 1
		return 0
	
	cdef void _get_box(self, float* box, float* matrix):
		cdef float matrix2[19]
		
		if not self._shape is None:
			if matrix == NULL: matrix_copy    (matrix2, self._matrix)
			else:              multiply_matrix(matrix2, matrix, self._matrix)
			self._shape._get_box(box, matrix2)
			
	cdef void _get_sphere(self, float* sphere):
		if self._shape and isinstance(self._shape, _SimpleShape) and ((<_SimpleShape> (self._shape))._option & SHAPE_HAS_SPHERE):
			memcpy(sphere, (<_SimpleShape> (self._shape))._sphere, 4 * sizeof(float))
		else:
			sphere[0] = sphere[1] = sphere[2] = sphere[3] = 0.0
			
	def __repr__(self):
		return "<%s, shape=%s>" % (self.__class__.__name__, self._shape)
	
		
