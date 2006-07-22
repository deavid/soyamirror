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


# Some raypick stuff (including raypick context).
# Other raypick codes (e.g. raypick method) are in the objects themselves.

cdef object make_raypick_result(float* f, float z, float* normal, CoordSyst coordsyst, _Point p, _Vector v):
	if f == NULL: return None
	if p is None:
		p = Point (coordsyst, f[0] + f[3] * z, f[1] + f[4] * z, f[2] + f[5] * z)
		v = Vector(coordsyst)
		memcpy(v._matrix, normal, 3 * sizeof(float))
		return p, v
	else:
		p._parent = v._parent = coordsyst
		p._matrix[0] = f[0] + f[3] * z
		p._matrix[1] = f[1] + f[4] * z
		p._matrix[2] = f[2] + f[5] * z
		memcpy(v._matrix, normal, 3 * sizeof(float))
		return 1



cdef class RaypickData:
	#cdef int       option
	#cdef Chunk*    raypicked
	#cdef Chunk*    raypick_data
	#cdef float     root_data[7], normal[3], result, root_result
	#cdef CoordSyst result_coordsyst
	
	def __init__(self):
		self.raypicked    = get_chunk()
		self.raypick_data = get_chunk()
		
	def __dealloc__(self):
		drop_chunk(self.raypicked)
		drop_chunk(self.raypick_data)
		
cdef RaypickData raypick_data
raypick_data = RaypickData()

cdef RaypickData get_raypick_data():
	raypick_data.result_coordsyst = None
	raypick_data.raypicked   .nb = 0
	raypick_data.raypick_data.nb = 0
	return raypick_data


cdef class RaypickContext:
	#cdef Chunk* _items
	#cdef _World _root
	
	def __init__(self, _World root):
		self._items = get_chunk()
		self._root  = root
		
	def __dealloc__(self):
		drop_chunk(self._items)
		
	def raypick(self, Position origin not None, _Vector direction not None, float distance = -1.0, int half_line = 1, int cull_face = 1, _Point p = None, _Vector v = None, int category = 0xffffffff):
		"""raypick(origin, direction, distance = -1.0, half_line = 1, cull_face = 1, p = None, v = None, int category = 1) -> None or (Point, Vector)

See World.raypick"""
		cdef Chunk*      items
		items = self._items
		if items.nb == 0: return None
		
		cdef RaypickData data
		cdef _CObj       obj
		cdef CoordSyst   coordsyst
		cdef float*      d
		cdef int         max
		data = get_raypick_data()
		
		origin   ._out(data.root_data)
		direction._out(data.root_data + 3)
		vector_normalize(data.root_data + 3)
		data.root_data[6] = distance
		data.option       = RAYPICK_CULL_FACE * cull_face + RAYPICK_HALF_LINE * half_line
		
		max = items.nb
		items.nb = 0
		while items.nb < max:
			obj = <_CObj> chunk_get_ptr(items)
			if isinstance(obj, _TreeModel):
				(<_TreeModel> obj)._raypick_from_context(data, items)
			else:
				(<CoordSyst> obj)._raypick(data, (<CoordSyst> obj)._parent, category)
			
		if data.result_coordsyst is None: d = NULL
		else:                             d = data.result_coordsyst._raypick_data(data)
		
		max = data.raypicked.nb
		data.raypicked.nb = 0
		while data.raypicked.nb < max:
			coordsyst = <CoordSyst> chunk_get_ptr(data.raypicked)
			coordsyst.__raypick_data = -1
			
		return make_raypick_result(d, data.result, data.normal, data.result_coordsyst, p, v)
		
	def raypick_b(self, Position origin not None, _Vector direction not None, float distance = -1.0, int half_line = 1, int cull_face = 1, _Point p = None, _Vector v = None, int category = 0xffffffff):
		"""raypick_b(origin, direction, distance = -1.0, half_line = 1, cull_face = 1, p = None, v = None, category = 1) -> bool

See World.raypick_b"""
		cdef Chunk*      items
		items = self._items
		if items.nb == 0: return 0
		
		cdef RaypickData data
		cdef _CObj       obj
		cdef CoordSyst   coordsyst
		cdef int         result, max
		data = get_raypick_data()
		origin   ._out(data.root_data)
		direction._out(data.root_data + 3)
		vector_normalize(data.root_data + 3)
		data.root_data[6] = distance
		data.option       = RAYPICK_CULL_FACE * cull_face + RAYPICK_HALF_LINE * half_line
		
		max = items.nb
		items.nb = 0
		while items.nb < max:
			obj = <_CObj> chunk_get_ptr(items)
			if isinstance(obj, _TreeModel):
				if (<_TreeModel> obj)._raypick_from_context_b(data, items): result = 1; break
			else:
				if (<CoordSyst>  obj)._raypick_b(data, (<CoordSyst> obj)._parent, category): result = 1; break
		else: result = 0
		
		max = data.raypicked.nb
		data.raypicked.nb = 0
		while data.raypicked.nb < max:
			coordsyst = <CoordSyst> chunk_get_ptr(data.raypicked)
			coordsyst.__raypick_data = -1
			
		return result
	
	def get_items(self):
		"""Return a list of all items inside the raypick context"""
		cdef Chunk* items
		cdef _CObj obj
		cdef int max
		
		items = self._items
		if items.nb == 0:
			return None
		result = list()
		max = items.nb
		items.nb = 0
		while items.nb < max:
			obj = <_CObj> chunk_get_ptr(items)
			result.append(obj)
		return result
