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

cdef object LIGHTS, LAST_LIGHTS
LIGHTS      = []
LAST_LIGHTS = []

import weakref

cdef class _Light(CoordSyst):
	#cdef public float radius
	#cdef float _w, _constant, _linear, _quadratic, _angle, _exponent
	#cdef float _colors[16] # ambient + diffuse + specular + shadow colors
	#cdef float _data[3] # used by cell-shading and shadow
	#cdef readonly int _id
	#cdef int _gl_id_enabled
	##cdef int _used
	#cdef _static_shadow_displaylists
	
	def __cinit__(self, *args, **kargs):
		self.__raypick_data              = -1
		self._id                         = -1
		self._static_shadow_displaylists = weakref.WeakKeyDictionary()

	def __dealloc__(self):
		cdef int displaylist
		if self._static_shadow_displaylists:
			for displaylist in self._static_shadow_displaylists.values():
				glDeleteLists(displaylist, 1)
				
	def __init__(self, _World parent = None):
		CoordSyst.__init__(self, parent)
		self._w          = 1.0
		self._constant   = 1.0
		self._angle      = 180.0
		self._colors[ 0] = 0.0 # ambient color
		self._colors[ 1] = 0.0 # ambient color
		self._colors[ 2] = 0.0 # ambient color
		self._colors[ 3] = 0.0 # ambient color
		self._colors[ 4] = 1.0 # diffuse color
		self._colors[ 5] = 1.0
		self._colors[ 6] = 1.0
		self._colors[ 7] = 1.0
		self._colors[ 8] = 1.0 # specular color
		self._colors[ 9] = 1.0
		self._colors[10] = 1.0
		self._colors[11] = 1.0
		self._colors[12] = 0.0 # shadow color
		self._colors[13] = 0.0
		self._colors[14] = 0.0
		self._colors[15] = 0.5
		self._option     = self._option | LIGHT_STATIC
		self.radius      = -1.0
		
	cdef __getcstate__(self):
		cdef Chunk* chunk
		chunk = get_chunk()
		chunk_add_int_endian_safe   (chunk, self._option)
		chunk_add_floats_endian_safe(chunk, self._matrix, 19)
		chunk_add_float_endian_safe (chunk, self.radius)
		chunk_add_float_endian_safe (chunk, self._angle)
		chunk_add_float_endian_safe (chunk, self._exponent)
		chunk_add_float_endian_safe (chunk, self._linear)
		chunk_add_float_endian_safe (chunk, self._constant)
		chunk_add_float_endian_safe (chunk, self._quadratic)
		chunk_add_float_endian_safe (chunk, self._w)
		chunk_add_floats_endian_safe(chunk, self._colors, 16)
		return drop_chunk_to_string (chunk)
	
	cdef void __setcstate__(self, cstate):
		self._validity = COORDSYS_INVALID
		cdef Chunk* chunk
		chunk = string_to_chunk(cstate)
		chunk_get_int_endian_safe   (chunk, &self._option)
		chunk_get_floats_endian_safe(chunk,  self._matrix, 19)
		chunk_get_float_endian_safe (chunk, &self.radius)
		chunk_get_float_endian_safe (chunk, &self._angle)
		chunk_get_float_endian_safe (chunk, &self._exponent)
		chunk_get_float_endian_safe (chunk, &self._linear)
		chunk_get_float_endian_safe (chunk, &self._constant)
		chunk_get_float_endian_safe (chunk, &self._quadratic)
		chunk_get_float_endian_safe (chunk, &self._w)
		chunk_get_floats_endian_safe(chunk,  self._colors, 16)
		drop_chunk(chunk)
		
		if self._option & LIGHT_STATIC:
			self._option = self._option & ~LIGHT_STATIC
			self._option = self._option |  COORDSYS_STATIC
		
	property angle:
		def __get__(self):
			return self._angle
		def __set__(self, float x):
			self._angle = x
			self._option = self._option | LIGHT_INVALID
			
	property exponent:
		def __get__(self):
			return self._exponent
		def __set__(self, float x):
			self._exponent = x
			self._option = self._option | LIGHT_INVALID
			
	property directional:
		def __get__(self):
			return self._w == 0.0
		def __set__(self, int x):
			if x: self._w = 0.0
			else: self._w = 1.0
			
	property constant:
		def __get__(self):
			return self._constant
		def __set__(self, float x):
			self._constant = x
			self._compute_radius()
			self._option = self._option | LIGHT_INVALID
			
	property linear:
		def __get__(self):
			return self._linear
		def __set__(self, float x):
			self._linear = x
			self._compute_radius()
			self._option = self._option | LIGHT_INVALID
			
	property quadratic:
		def __get__(self):
			return self._quadratic
		def __set__(self, float x):
			self._quadratic = x
			self._compute_radius()
			self._option = self._option | LIGHT_INVALID
			
	property cast_shadow:
		def __get__(self):
			return self._option & LIGHT_NO_SHADOW == 0
		def __set__(self, int x):
			if x: self._option = self._option & ~LIGHT_NO_SHADOW
			else: self._option = self._option |  LIGHT_NO_SHADOW
			
	property top_level:
		def __get__(self):
			return self._option & LIGHT_TOP_LEVEL != 0
		def __set__(self, int x):
			if x: self._option = self._option |  LIGHT_TOP_LEVEL
			else: self._option = self._option & ~LIGHT_TOP_LEVEL
			
	property ambient:
		def __get__(self):
			return self._colors[0], self._colors[1], self._colors[2], self._colors[3]
		def __set__(self, color):
			self._colors[0], self._colors[1], self._colors[2], self._colors[3] = color
			self._option = self._option | LIGHT_INVALID
			
	property diffuse:
		def __get__(self):
			return self._colors[4], self._colors[5], self._colors[6], self._colors[7]
		def __set__(self, color):
			self._colors[4], self._colors[5], self._colors[6], self._colors[7] = color
			self._option = self._option | LIGHT_INVALID
			
	property specular:
		def __get__(self):
			return self._colors[8], self._colors[9], self._colors[10], self._colors[11]
		def __set__(self, color):
			self._colors[8], self._colors[9], self._colors[10], self._colors[11] = color
			self._option = self._option | LIGHT_INVALID
			
	property shadow_color:
		def __get__(self):
			return self._colors[12], self._colors[13], self._colors[14], self._colors[15]
		def __set__(self, color):
			self._colors[12], self._colors[13], self._colors[14], self._colors[15] = color
			
	cdef int _shadow_at(self, float position[3]):
		cdef _World root
		cdef RaypickData data
		cdef float* rdata
		root  = self._get_root()
		if root is None: return 0
		data  = RaypickData()
		rdata = data.root_data
		if self._w == 0.0:
			rdata[3] =  0.0
			rdata[4] =  0.0
			rdata[5] = -1.0
			vector_by_matrix(rdata + 3, self._root_matrix())
			vector_normalize(rdata + 3)
			rdata[6] = 100.0
			point_by_matrix_copy(rdata, position, self._parent._root_matrix())
			rdata[0] = rdata[0] - rdata[3] * rdata[6]
			rdata[1] = rdata[1] - rdata[4] * rdata[6]
			rdata[2] = rdata[2] - rdata[5] * rdata[6]
			rdata[6] = rdata[6] - 1.0
		else:
			vector_from_points(rdata + 3, &self._matrix[0] + 12, position)
			if self._parent is None:
				memcpy(rdata, &self._matrix[0] + 12, 3 * sizeof(GLfloat))
			else:
				point_by_matrix_copy(rdata, &self._matrix[0] + 12, self._parent._root_matrix())
				vector_by_matrix(rdata + 2, self._parent._root_matrix())
			rdata[6] = vector_length(rdata + 3) - 1.0
			vector_normalize(rdata + 3)
		data.option = RAYPICK_HALF_LINE
		return root._raypick_b(data, None, 1)
	
	cdef float _spotlight_at(self, float position[3]):
		cdef float v[3], w[3]
		cdef float m
		if (fabs(self._angle - 180.0) < EPSILON) or (self._w == 0.0):
			return 1.0 # point or directional light
		v[0] = position[0] - self._matrix[12]
		v[1] = position[1] - self._matrix[13]
		v[2] = position[2] - self._matrix[14]
		w[0] = -self._matrix[ 8] # front is -Z
		w[1] = -self._matrix[ 9]
		w[2] = -self._matrix[10]
		m = vector_dot_product(v, w)
		if m < 0.0: m = 0.0
		if m <= cos(self._angle): return 0.0 # position is out of cone
		else: return pow(m, <int>self._exponent)
		
	cdef float _attenuation_at(self, float position[3]):
		cdef float d
		if self._w == 0.0: return 1.0 # directional light
		d = point_distance_to(&self._matrix[0] + 12, position)
		return 1.0 / (self._constant + self._linear * d + self._quadratic * d * d)

	cdef void _static_light_at(self, float* position, float* normal, int shadow, float* result):
		cdef float f, g, angle, attenuation, spotlight
		cdef float v[3], n[3]
		attenuation = self._attenuation_at(position)
		spotlight   = self._spotlight_at  (position)
		f           = attenuation * spotlight
		
		if f == 0.0: return
		if shadow and self._shadow_at(position): g = 0.0
		else:
			if (normal == NULL): angle = 1.0
			else:
				memcpy(&n[0], normal, sizeof(n))
				vector_normalize(n)
				if self._w == 0.0: # directional light
					v[0] =  0.0
					v[1] =  0.0
					v[2] =  1.0 # XXX should be -1, but works only with 1...???
					vector_by_matrix(v, self._matrix)
				else:
					vector_from_points(v, &self._matrix[0] + 12, position)
					vector_normalize(v)
				angle = vector_dot_product(n, v)
				
				if angle > 0.0: angle = 0.0
				else:           angle = -angle
			g = angle
			
		result[0] = result[0] + f * (self._colors[0] + g * self._colors[4])
		result[1] = result[1] + f * (self._colors[1] + g * self._colors[5])
		result[2] = result[2] + f * (self._colors[2] + g * self._colors[6])
		#result[3] = result[3] + f * (self._colors[3] + g * self._colors[7])
		
	cdef void _cast_into(self, CoordSyst coordsyst):
		if self._w == 0.0: # convert light direction in coordsyst
			self._data[0] = -self._matrix[ 8] # light direction is -Z
			self._data[1] = -self._matrix[ 9]
			self._data[2] = -self._matrix[10]
			if (not self.parent is None) and (not self.parent is coordsyst):
				vector_by_matrix(self._data, self._parent._root_matrix())
				vector_by_matrix(self._data, coordsyst._inverted_root_matrix())
				vector_normalize(self._data)
		else: # convert light position in coordsys
			if (self.parent is None) or (self.parent is coordsyst):
				memcpy (&self._data[0], &self._matrix[0] + 12, sizeof(self._data))
			else:
				point_by_matrix_copy(self._data, &self._matrix[0] + 12, self._parent._root_matrix())
				point_by_matrix     (self._data, coordsyst._inverted_root_matrix())
				
	cdef void _batch(self, CoordSyst coordsyst):
#     cdef float data[4]
		if self._option & HIDDEN: return
		#multiply_matrix(self._render_matrix, renderer.current_camera._render_matrix, self._root_matrix())
		multiply_matrix(self._render_matrix, coordsyst._render_matrix, self._matrix)
#     if self.radius != -1.0: # frustum test
#       data[0] = self._matrix[12]
#       data[1] = self._matrix[13]
#       data[2] = self._matrix[14]
#       data[3] = self.radius
#       self._frustum_id = -1
#       if sphere_in_frustum(renderer._frustum(coordsyst), data) != 1: return
		if self._option & LIGHT_TOP_LEVEL: renderer.top_lights.append(self)
		else:                              renderer.current_context.lights.append(self)
		
	cdef void _activate(self):
		cdef int     id
		cdef _Light  light
		cdef GLfloat p[4]
		cdef GLfloat q[3]

		p[3] = self._w
		if not(self._option & HIDDEN):
			glLoadMatrixf(self._render_matrix)
			if self._id == -1:
				id = 0
				for light in LIGHTS:
					if light is None:
						self._id = id
						LIGHTS[id] = self
						break
					id = id + 1
				else:
					print "Too many lights!"
					#raise ValueError("Too many lights!")
					return
				
			id = GL_LIGHT0 + self._id

			if (self._option & LIGHT_INVALID) or (not self is LAST_LIGHTS[self._id]):
				self._option = self._option & ~LIGHT_INVALID
				LAST_LIGHTS[self._id] = self
				
				glLightf (id, GL_SPOT_EXPONENT,         self._exponent)
				glLightf (id, GL_SPOT_CUTOFF,           self._angle)
				glLightfv(id, GL_AMBIENT,               self._colors)
				glLightfv(id, GL_DIFFUSE,               &self._colors[0] + 4)
				glLightfv(id, GL_SPECULAR,              &self._colors[0] + 8)
				glLightf (id, GL_CONSTANT_ATTENUATION,  self._constant)
				glLightf (id, GL_LINEAR_ATTENUATION,    self._linear)
				glLightf (id, GL_QUADRATIC_ATTENUATION, self._quadratic)
				
			if self._w == 0.0:
				p[0] = p[1] = 0.0
				p[2] = 1.0 # XXX should be -1, but works only with 1...???
				glLightfv(id, GL_POSITION, p)
			else: # positional light
				p[0] = p[1] = p[2] = 0.0
				q[0] = q[1] = 0.0
				q[2] = -1.0
				glLightfv(id, GL_POSITION, p)
				glLightfv(id, GL_SPOT_DIRECTION, q)
			glEnable(id)
			self._gl_id_enabled = 1
			
			
	cdef void _compute_radius(self):
		if   self._w == 0.0:
			self.radius = -1.0
		elif (self._linear == 0.0) and (self._quadratic == 0.0): # point infinite light
			self.radius = -1.0
		elif (self._linear != 0.0) and (self._quadratic == 0.0):
			self.radius = ((1.0 / LIGHT_NULL_ATTENUATION) - self._constant) / self._linear
		else:
			# XXX sub optimal
			self.radius = ((1.0 / LIGHT_NULL_ATTENUATION) - self._constant) / (self._linear + self._quadratic)
			
			
cdef void disable_all_lights():
	"""Disable all lights."""
	cdef _Light light
	for light in LIGHTS:
		if not light is None:
			if light._gl_id_enabled:
				glDisable(GL_LIGHT0 + light._id)
				light._gl_id_enabled = 0
			LIGHTS[light._id] = None
			light._id = -1
				
cdef void disable_static_lights():
	"""Disable all static lights. Static lights are disabled when rendering static lit
model (Soya assume the effect of static lights was already taken into account at the
model computation time)."""
	cdef _Light light
	for light in LIGHTS:
		if (not light is None) and (light._gl_id_enabled == 1) and (light._option & COORDSYS_STATIC):
			glDisable(GL_LIGHT0 + light._id)
			light._gl_id_enabled = 0
			
cdef void enable_static_lights():
	"""Enable all static lights. Static lights are disabled when rendering static lit
object (Soya assume the effect of static lights was already taken into account at the
model computation time)."""
	cdef _Light light
	for light in LIGHTS:
		if (not light is None) and (light._gl_id_enabled == 0) and (light._option & COORDSYS_STATIC):
			glEnable(GL_LIGHT0 + light._id)
			light._gl_id_enabled = 1
			
#U#cdef void disable_deep_lights():
#U#	"""Disable all non top level lights."""
#U#	cdef _Light light
#U#	for light in LIGHTS:
#U#		if (not light is None) and (light._option & LIGHT_TOP_LEVEL) and (light._gl_id_enabled == 1):
#U#			glDisable(GL_LIGHT0 + i)
#U#			light._gl_id_enabled = 0
			
