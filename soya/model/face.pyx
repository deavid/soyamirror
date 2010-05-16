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

cdef class _Vertex(_Point):
	#cdef float   _tex_x, _tex_y
	#cdef         _diffuse, _emissive
	#cdef _Face   _face
	#cdef _Vector _normal
	
	cdef __getcstate__(self):
		#return struct.pack("<fffff", self._matrix[0], self._matrix[1], self._matrix[2], self._tex_x, self._tex_y), self._parent, self._diffuse, self._emissive
		cdef Chunk* chunk
		chunk = get_chunk()
		chunk_add_floats_endian_safe(chunk, self._matrix, 3)
		#chunk_add_float_endian_safe (chunk, self._tex_x)
		#chunk_add_float_endian_safe (chunk, self._tex_y)
		chunk_add_floats_endian_safe (chunk, &self._tex_x, 1)
		chunk_add_floats_endian_safe (chunk, &self._tex_y, 1)
		return drop_chunk_to_string(chunk), self._parent, self._diffuse, self._emissive
	
	cdef void __setcstate__(self, cstate):
		cstate2, self._parent, self._diffuse, self._emissive = cstate
		#self._matrix[0], self._matrix[1], self._matrix[2], self._tex_x, self._tex_y = struct.unpack("<fffff", cstate2)
		
		# don't work ???
		cdef Chunk* chunk
		chunk = string_to_chunk(cstate2)
		chunk_get_floats_endian_safe(chunk, self._matrix, 3)
		#self._tex_x = chunk_get_float_endian_safe(chunk)
		#self._tex_y = chunk_get_float_endian_safe(chunk)
		chunk_get_float_endian_safe(chunk, &self._tex_x)
		chunk_get_float_endian_safe(chunk, &self._tex_y)
		drop_chunk(chunk)
		
#     cdef float* cstate_data
#     cstate_data = <float*> PyString_AS_STRING(cstate2)
#     self._matrix[0] = cstate_data[0]
#     self._matrix[1] = cstate_data[1]
#     self._matrix[2] = cstate_data[2]
#     self._tex_x     = cstate_data[3]
#     self._tex_y     = cstate_data[4]
		
	property tex_x:
		def __get__(self):
			return self._tex_x
		def __set__(self, float x):
			self._tex_x = x
	
	property tex_y:
		def __get__(self):
			return self._tex_y
		def __set__(self, float x):
			self._tex_y = x
	
	property color: # Compatibility, use rather diffuse
		def __get__(self):
			return self._diffuse
		def __set__(self, x):
			self._diffuse = x
			
	property diffuse:
		def __get__(self):
			return self._diffuse
		def __set__(self, x):
			self._diffuse = x
			
	property emissive:
		def __get__(self):
			return self._emissive
		def __set__(self, x):
			self._emissive = x
			
	property face:
		def __get__(self):
			return self._face
		
	def __init__(self, CoordSyst parent = None, float x = 0.0, float y = 0.0, float z = 0.0, float tex_x = 0.0, float tex_y = 0.0, diffuse = None, emissive = None):
		"""Vertex(parent = None, x = 0.0, y = 0.0, z = 0.0, tex_x = 0.0, tex_y = 0.0, diffuse = None, emissive = None)

Creates a new Vertex in coordinate systems PARENT, at position X, Y, Z, with texture
coordinates TEX_X and TEX_Y, and the given DIFFUSE and EMISSIVE colors."""
		Point.__init__(self, parent, x, y, z)
		self._tex_x    = tex_x
		self._tex_y    = tex_y
		self._diffuse  = diffuse
		self._emissive = emissive
		
	cdef void _render(self, CoordSyst coord_syst):
		cdef float coords[3], emissive[4]
		glTexCoord2f(self._tex_x, self._tex_y)
		if not self._diffuse  is None:
			# this call doesnt seem to work. model.pyx uses glColor so used again here 
			#glMaterialfv(GL_FRONT, GL_DIFFUSE, <float*> self._diffuse)
			# using glColor4fv(<float*>self._diffuse) doesnt work 
			glColor4f(self._diffuse[0], self._diffuse[1], self._diffuse[2], self._diffuse[3])
		if not self._emissive is None:
			emissive[0], emissive[1], emissive[2], emissive[3] = self._emissive
			glMaterialfv(GL_FRONT, GL_EMISSION, emissive)
		if coord_syst is None: glVertex3fv(self._matrix)
		else:
			self._into(coord_syst, coords)
			glVertex3fv(coords)
			
	cdef float _angle_at(self):
		cdef float u1[3], u2[3]
		cdef int index
		index = self._face._vertices.index(self)
		vector_from_points(u1, (<_Vertex> (self._face._vertices[(index + 1) % len(self._face._vertices)]))._matrix, self._matrix)
		vector_from_points(u2, (<_Vertex> (self._face._vertices[ index - 1                             ]))._matrix, self._matrix)
		return vector_angle(u1, u2)
	
	
cdef class _Face(CoordSyst):
	#cdef object     _vertices
	#cdef _Material  _material
	#cdef _Vector    _normal
	
	property lit:
		def __get__(self):
			return self._option & FACE2_LIT
		def __set__(self, int x):
			if x: self._option = self._option |  FACE2_LIT
			else: self._option = self._option & ~FACE2_LIT
			
	property smooth_lit:
		def __get__(self):
			return self._option & FACE2_SMOOTH_LIT
		def __set__(self, int x):
			if x: self._option = self._option |  FACE2_SMOOTH_LIT
			else: self._option = self._option & ~FACE2_SMOOTH_LIT
			
	property static_lit:
		def __get__(self):
			return self._option & FACE2_STATIC_LIT
		def __set__(self, int x):
			if x: self._option = self._option |  FACE2_STATIC_LIT
			else: self._option = self._option & ~FACE2_STATIC_LIT
			
	property double_sided:
		def __get__(self):
			return self._option & FACE2_DOUBLE_SIDED
		def __set__(self, int x):
			if x: self._option = self._option |  FACE2_DOUBLE_SIDED
			else: self._option = self._option & ~FACE2_DOUBLE_SIDED
			
	property material:
		def __get__(self):
			return self._material
		def __set__(self, _Material x not None):
			self._material = x
			
	property vertices:
		def __get__(self):
			return self._vertices
		
	property normal:
		def __get__(self):
			self._compute_normal()
			return self._normal
		
	def __init__(self, _World parent = None, vertices = None, _Material material = None):
		"""Face(parent = None, vertices = None, material = None) -> Face

Creates a new Face in World PARENT, with the given list of VERTICES,
and the given Material."""
		cdef _Vertex vertex
		CoordSyst.__init__(self, parent)
		self._vertices     = vertices or []
		self._material     = material or _DEFAULT_MATERIAL
		self._option       = FACE2_LIT | FACE2_STATIC_LIT
		for vertex in self.vertices: vertex._face = self
		
	cdef __getcstate__(self):
		#return struct.pack("<ifffffffffffffffffffiiiii", self._option, self._matrix[0], self._matrix[1], self._matrix[2], self._matrix[3], self._matrix[4], self._matrix[5], self._matrix[6], self._matrix[7], self._matrix[8], self._matrix[9], self._matrix[10], self._matrix[11], self._matrix[12], self._matrix[13], self._matrix[14], self._matrix[15], self._matrix[16], self._matrix[17], self._matrix[18], self.double_sided, self.lit, self.static_lit, self.smooth_lit, self.solid), self._vertices, self._material
		cdef Chunk* chunk
		chunk = get_chunk()
		chunk_add_int_endian_safe   (chunk, self._option)
		chunk_add_floats_endian_safe(chunk, self._matrix, 19)
		return drop_chunk_to_string(chunk), self._vertices, self._material
	
	cdef void __setcstate__(self, cstate):
		cstate2, self._vertices, self._material = cstate
		#self._option, self._matrix[0], self._matrix[1], self._matrix[2], self._matrix[3], self._matrix[4], self._matrix[5], self._matrix[6], self._matrix[7], self._matrix[8], self._matrix[9], self._matrix[10], self._matrix[11], self._matrix[12], self._matrix[13], self._matrix[14], self._matrix[15], self._matrix[16], self._matrix[17], self._matrix[18], self.double_sided, self.lit, self.static_lit, self.smooth_lit, self.solid = struct.unpack("<ifffffffffffffffffffiiiii", cstate2)
		cdef _Vertex vertex
		for vertex in self._vertices: vertex._face = self
		
		cdef Chunk* chunk
		chunk = string_to_chunk(cstate2)
		chunk_get_int_endian_safe(chunk, &self._option)
		chunk_get_floats_endian_safe(chunk, self._matrix, 19)
		drop_chunk(chunk)
		self._validity = COORDSYS_INVALID
		
	def insert(self, int index, _Vertex vertex not None):
		"""Face.insert(index, vertex)

Inserts the given VERTEX to the Face at position INDEX."""
		vertex._face = self
		self._vertices.insert(index, vertex)
		
	def append(self, _Vertex vertex not None):
		"""Face.append(vertex)

Appends the given VERTEX to the Face."""
		vertex._face = self
		self._vertices.append(vertex)
		
	def add(self, _Vertex vertex not None):
		"""Face.add(vertex)

Appends the given VERTEX to the Face."""
		self.append(vertex)
		
	cdef void _compute_normal(self):
		# Computes the normal vector of the Face
		cdef float a[3], b[3], c[3]
		a[0] = a[1] = a[2] = b[0] = b[1] = b[2] = c[0] = c[1] = c[2] = 0.0
		if len(self._vertices) > 2:
			if self._normal is None: self._normal = Vector(self._parent)
			else:                    self._normal._parent = self._parent
			(<_Vertex> self._vertices[0])._into(self._parent, a)
			(<_Vertex> self._vertices[1])._into(self._parent, b)
			(<_Vertex> self._vertices[2])._into(self._parent, c)
			face_normal(self._normal._matrix, a, b, c)
			vector_normalize(self._normal._matrix)
		else: self._normal = None
		
	def is_coplanar(self, float threshold = 0.005):
		"""is_coplanar(threshold = 0.005) -> boolean

Returns true if the Face's vertices are all coplanar."""

		if len(self._vertices) < 4: return 1
		
		cdef _Vertex vertex
		cdef _Vector n1, n2
		self._compute_normal()
		n1 = self._normal
		n2 = Vector(self._parent)
		
		cdef float a[3], b[3], c[3]
		(<_Vertex> self._vertices[0])._into(self._parent, a)
		(<_Vertex> self._vertices[1])._into(self._parent, b)
		
		for vertex in self._vertices[2:]:
			vertex._into(self._parent, c)
			face_normal(n2._matrix, a, b, c)
			vector_normalize(n2._matrix)
			
			if n1.distance_to(n2) > threshold: return 0
		return 1
	
	def is_colored(self):
		"""is_colored() -> boolean

Returns true if the Face is colored, i.e. at least one of its Vertices is colored."""
		cdef _Vertex vertex
		for vertex in self._vertices:
			if not vertex._diffuse is None: return 1
		return 0
	
	def is_alpha(self):
		"""is_alpha() -> boolean

Returns true if the Face is alpha-blended."""
		return (self._material and self._material.is_alpha()) or self.has_alpha_vertex()
	
	def has_alpha_vertex(self):
		"""has_alpha_vertex() -> boolean

Returns true if the Face has at least one alpha blended Vertex."""
		cdef _Vertex vertex
		for vertex in self._vertices:
			if (not vertex._diffuse is None) and vertex._diffuse[3] < 1.0: return 1
		return 0
	
	cdef void _batch(self, CoordSyst coord_syst):
		if self.is_alpha(): renderer._batch(renderer.alpha , self, coord_syst, NULL)
		else:               renderer._batch(renderer.opaque, self, coord_syst, NULL)
		
	cdef void _render(self, CoordSyst coord_syst):
		cdef _Vertex vertex
		cdef _Vector at_camera
		cdef int    i
		i = len(self._vertices)
		if i == 0: return
		
		self._material._activate()
		
		if not(self._option & FACE2_LIT): glDisable(GL_LIGHTING)
		if self._option & FACE2_DOUBLE_SIDED:
			glLightModeli(GL_LIGHT_MODEL_TWO_SIDE, GL_TRUE)
			glDisable(GL_CULL_FACE)
			
		self._compute_normal()
		if self._normal is None:
			at_camera = Vector(renderer.current_camera, 0.0, 0.0, 1.0)
			at_camera.convert_to(self._parent)
			glNormal3fv(at_camera._matrix)
		else:
			glNormal3fv(self._normal._matrix)
			
		if   i == 1: glBegin(GL_POINTS)
		elif i == 2: glBegin(GL_LINES)
		elif i == 3: glBegin(GL_TRIANGLES)
		elif i == 4: glBegin(GL_QUADS)
		else:        glBegin(GL_POLYGON)
		
		for vertex in self._vertices: vertex._render(self._parent)
		glEnd()
		
		if self._option & FACE2_DOUBLE_SIDED:
			glLightModeli(GL_LIGHT_MODEL_TWO_SIDE, GL_FALSE)
			glEnable(GL_CULL_FACE)
			
		if not(self._option & FACE2_LIT): glEnable(GL_LIGHTING)
		
	def __iter__(self):
		return iter(self._vertices)
	def __getitem__(self, index):
		return self._vertices[index]
	# Pyrex does not like this one
	#def __contains__(self, vertex):
	#  return vertex in self._vertices
	def __len__(self):
		return len(self._vertices)
	
	def __repr__(self):
		cdef int i
		i = len(self._vertices)
		if   i == 1: r = "<Plot"
		elif i == 2: r = "<Line"
		elif i == 3: r = "<Triangle"
		elif i == 4: r = "<Quad"
		else:        r = "<Polygon"
		if not self._material is _DEFAULT_MATERIAL: r = r + ", material %s" % self._material.filename
		return r + ">"
	
	cdef void _get_box(self, float* box, float* matrix):
		cdef _Vertex vertex
		cdef float   coord[3]
		
		for vertex in self._vertices:
			if matrix == NULL: memcpy(&coord[0], &vertex._matrix[0], 3 * sizeof(float))
			else:              point_by_matrix_copy(coord, vertex._matrix, matrix)
			
			if coord[0] < box[0]: box[0] = coord[0]
			if coord[1] < box[1]: box[1] = coord[1]
			if coord[2] < box[2]: box[2] = coord[2]
			if coord[0] > box[3]: box[3] = coord[0]
			if coord[1] > box[4]: box[4] = coord[1]
			if coord[2] > box[5]: box[5] = coord[2]
			
	cdef void _raypick(self, RaypickData data, CoordSyst parent, int category):
		cdef float* p, r, root_r
		cdef float  normal[3]
		cdef int    nb_vertices, i, option
		nb_vertices = len(self._vertices)
		if nb_vertices < 3: return
		option = data.option
		if self.double_sided == 1: option = option & ~RAYPICK_CULL_FACE
		
		# get vertices coordinates
		p = <float*> malloc(nb_vertices * 3 * sizeof(float))
		for i from 0 <= i < nb_vertices: (<_Vertex> (self._vertices[i]))._into(self, p + 3 * i)
		
		face_normal(normal, p, p + 3, p + 6)
		vector_normalize(normal)
		if   nb_vertices == 3: i = triangle_raypick(self._raypick_data(data), p, p + 3, p + 6,        normal, option, &r)
		elif nb_vertices == 4: i = quad_raypick    (self._raypick_data(data), p, p + 3, p + 6, p + 9, normal, option, &r)
		else: raise ValueError("Raypicking on a face with more than 4 vertices is not supported yet.")
		
		if i != 0:
			root_r = self._distance_out(r)
			if (data.result_coordsyst is None) or (fabs(root_r) < fabs(data.root_result)):
				if   i == RAYPICK_DIRECT:
					data.result           = r
					data.root_result      = root_r
					data.result_coordsyst = self
					memcpy(&data.normal[0], &normal[0], 3 * sizeof(float))
				elif i == RAYPICK_INDIRECT:
					data.result           = r
					data.result_coordsyst = self
					if self.double_sided == 1:
						data.normal[0] = -normal[0]
						data.normal[1] = -normal[1]
						data.normal[2] = -normal[2]
					else: memcpy (&data.normal[0], &normal[0], 3 * sizeof(float))
					
		free(p)
		
	cdef int _raypick_b(self, RaypickData data, CoordSyst parent, int category):
		cdef float* p, r
		cdef float  normal[3]
		cdef int    nb_vertices, i, option
		
		nb_vertices = len(self._vertices)
		if nb_vertices < 3: return 0
		option = data.option
		if (option & RAYPICK_CULL_FACE) and (self.double_sided == 1): option = option & ~RAYPICK_CULL_FACE
		
		# get vertices coordinates
		p = <float*> malloc(nb_vertices * 3 * sizeof(float))
		for i from 0 <= i < nb_vertices: (<_Vertex> (self._vertices[i]))._into(self._parent, p + 3 * i)
		
		face_normal(normal, p, p + 3, p + 6)
		vector_normalize(normal)
		if   nb_vertices == 3: i = triangle_raypick(self._raypick_data(data), p, p + 3, p + 6,        normal, option, &r)
		elif nb_vertices == 4: i = quad_raypick    (self._raypick_data(data), p, p + 3, p + 6, p + 9, normal, option, &r)
		else: raise ValueError("Raypicking on a face with more than 4 vertices is not supported yet.")
		
		free(p)
		return i
	
	cdef void _collect_raypickables(self, Chunk* items, float* rsphere, float* sphere, int category):
		#if self._option & NON_SOLID: return
		if not (self._category_bitfield & category): return
		
		# XXX not really implemented -- no selection
		chunk_add_ptr(items, <void*> self)
		
		



