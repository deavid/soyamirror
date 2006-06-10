# -*- indent-tabs-mode: t -*-

# Soya 3D
# Copyright (C) 2004 Jean-Baptiste LAMY -- jiba@tuxfamily.org
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

cdef class _Atmosphere(_CObj):
	"""Atmosphere

An Atmosphere is an object that defines all the atmospheric attributes of a World, such
as fog, background or ambient lighting.

To apply an Atmosphere to a World, as well as everything inside the World, do :

		world.atmosphere = my_atmosphere

You can safely put several Worlds one inside the other, with different Atmospheres.

Attributes are :

- fog: true to activate fog, false to disable fog (default value).

- fog_color: the fog color (an (R, G, B, A) tuple of four floats). Defaults to black.

- fog_type: the type of fog. fog_type can take 3 different values :
	- 0, linear fog: the fog range from fog_start to fog_end (default value).
	- 1, exponentiel fog: the fog the fog increase exponentially to fog_density and the distance.
	- 2, exponentiel squared fog: the fog the fog increase exponentially to the square of fog_density and the distance.

- fog_start: the distance at which the fog begins, if fog_type == 0. Defaults to 10.0.

- fog_end: the distance at which the fog ends, if fog_type == 0. Defaults to 100.0.

- fog_density: the fog density, if fog_type > 0. Defaults to 1.0.

- ambient: the ambient lighting color (an (R, G, B, A) tuple of four floats). Defaults to (0.5, 0.5, 0.5, 1.0).

- bg_color: the background color of the scene (an (R, G, B, A) tuple of four floats). Defaults to black.
"""
	#cdef int       _option, _fog_type
	#cdef float     _fog_start, _fog_end, _fog_density
	#cdef float     _ambient[4], _bg_color[4], _fog_color[4]
	
	def __init__(self):
		"""Atmosphere()

Create a new Atmosphere."""
		self._ambient[0]  = self._ambient [1] = self._ambient  [2] = 0.5
		self._ambient[3]  = self._bg_color[3] = self._fog_color[3] = 1.0
		self._fog_type    = GL_LINEAR
		self._fog_start   = 10.0
		self._fog_end     = 100.0
		self._fog_density = 1.0

	cdef __getcstate__(self):
		#return (self._option, self._fog_type, self._fog_start, self._fog_end, self._fog_density, self._ambient[0], self._ambient[1], self._ambient[2], self._ambient[3], self._bg_color[0], self._bg_color[1], self._bg_color[2], self._bg_color[3], self._fog_color[0], self._fog_color[1], self._fog_color[2], self._fog_color[3])
		cdef Chunk* chunk
		chunk = get_chunk()
		chunk_add_int_endian_safe   (chunk, self._option)
		chunk_add_int_endian_safe   (chunk, self._fog_type)
		chunk_add_float_endian_safe (chunk, self._fog_start)
		chunk_add_float_endian_safe (chunk, self._fog_end)
		chunk_add_float_endian_safe (chunk, self._fog_density)
		chunk_add_floats_endian_safe(chunk, self._ambient  , 4)
		chunk_add_floats_endian_safe(chunk, self._bg_color , 4)
		chunk_add_floats_endian_safe(chunk, self._fog_color, 4)
		return drop_chunk_to_string (chunk)
	
	cdef void __setcstate__(self, cstate):
		#self._option, self._fog_type, self._fog_start, self._fog_end, self._fog_density, self._ambient[0], self._ambient[1], self._ambient[2], self._ambient[3], self._bg_color[0], self._bg_color[1], self._bg_color[2], self._bg_color[3], self._fog_color[0], self._fog_color[1], self._fog_color[2], self._fog_color[3] = cstate
		cdef Chunk* chunk
		chunk = string_to_chunk(cstate)
		chunk_get_int_endian_safe   (chunk, &self._option)
		chunk_get_int_endian_safe   (chunk, &self._fog_type)
		chunk_get_float_endian_safe (chunk, &self._fog_start)
		chunk_get_float_endian_safe (chunk, &self._fog_end)
		chunk_get_float_endian_safe (chunk, &self._fog_density)
		chunk_get_floats_endian_safe(chunk,  self._ambient  , 4)
		chunk_get_floats_endian_safe(chunk,  self._bg_color , 4)
		chunk_get_floats_endian_safe(chunk,  self._fog_color, 4)
		drop_chunk(chunk)
		
	property fog:
		def __get__(self):
			return self._option & ATMOSPHERE_FOG
		def __set__(self, x):
			if x: self._option = self._option |  ATMOSPHERE_FOG
			else: self._option = self._option & ~ATMOSPHERE_FOG
			
	property fog_type:
		def __get__(self):
			if self._fog_type == GL_LINEAR: return 0
			if self._fog_type == GL_EXP:    return 1
			if self._fog_type == GL_EXP2:   return 2
			
		def __set__(self, int x):
			if x == 0: self._fog_type = GL_LINEAR
			if x == 1: self._fog_type = GL_EXP
			if x == 2: self._fog_type = GL_EXP2
			
	property fog_start:
		def __get__(self):
			return self._fog_start
		def __set__(self, float x):
			self._fog_start = x
	
	property fog_end:
		def __get__(self):
			return self._fog_end
		def __set__(self, float x):
			self._fog_end = x
	
	property fog_density:
		def __get__(self):
			return self._fog_density
		def __set__(self, float x):
			self._fog_density = x
	
	property ambient:
		def __get__(self):
			return self._ambient[0], self._ambient[1], self._ambient[2], self._ambient[3]
		def __set__(self, x):
			self._ambient[0], self._ambient[1], self._ambient[2], self._ambient[3] = x
	
	property bg_color:
		def __get__(self):
			return self._bg_color[0], self._bg_color[1], self._bg_color[2], self._bg_color[3]
		def __set__(self, x):
			self._bg_color[0], self._bg_color[1], self._bg_color[2], self._bg_color[3] = x
	
	property fog_color:
		def __get__(self):
			return self._fog_color[0], self._fog_color[1], self._fog_color[2], self._fog_color[3]
		def __set__(self, x):
			self._fog_color[0], self._fog_color[1], self._fog_color[2], self._fog_color[3] = x
			
	cdef void _clear(self):
		renderer._clear_screen(self._bg_color)
		self._draw_bg()
		
	cdef void _draw_bg(self):
		pass
	
	cdef void _render(self):
		"""Apply fog and ambient."""
		glLightModelfv(GL_LIGHT_MODEL_AMBIENT, self._ambient)
		if self._option & ATMOSPHERE_FOG:
			glFogf(GL_FOG_MODE,    self._fog_type)
			glFogf(GL_FOG_START,   self._fog_start)
			glFogf(GL_FOG_END,     self._fog_end)
			glFogf(GL_FOG_DENSITY, self._fog_density)
			glFogfv(GL_FOG_COLOR,  self._fog_color)
			glEnable(GL_FOG)
		else: glDisable(GL_FOG)
	
	cdef float _fog_factor_at(self, float p[3]):
		cdef float z
		z = sqrt(p[0] * p[0] + p[1] * p[1] + p[2] * p[2])
		if   self._fog_type == GL_LINEAR: return <float> (1.0 - (self._fog_end - z) / (self._fog_end - self._fog_start))
		elif self._fog_type == GL_EXP:    return <float> (1.0 - exp(self._fog_density * z))
		elif self._fog_type == GL_EXP2:   return <float> (1.0 - exp(self._fog_density * self._fog_density * z * z))
		return 0.0

cdef class _NoBackgroundAtmosphere(_Atmosphere):
	cdef void _clear(self):
		glClear(GL_DEPTH_BUFFER_BIT)
		

cdef class _SkyAtmosphere(_Atmosphere):
	#cdef float     _sky_color[4]
	#cdef float     _cloud_scale
	#cdef _Material _cloud
	#cdef           _sky_box
	
	def __init__(self):
		"""SkyAtmosphere()

Create a SkyAtmosphere"""
		self._ambient[0]  = self._ambient [1] = self._ambient  [2] = 0.5
		self._ambient[3]  = self._bg_color[3] = self._fog_color[3] = 1.0
		self._fog_type    = GL_LINEAR
		self._fog_start   = 10.0
		self._fog_end     = 100.0
		self._fog_density = 1.0
		self._sky_box     = ()
		self._cloud_scale = 1.0

	cdef __getcstate__(self):
		#return (self._option, self._fog_type, self._fog_start, self._fog_end, self._fog_density, self._ambient[0], self._ambient[1], self._ambient[2], self._ambient[3], self._bg_color[0], self._bg_color[1], self._bg_color[2], self._bg_color[3], self._fog_color[0], self._fog_color[1], self._fog_color[2], self._fog_color[3], self._sky_color[0], self._sky_color[1], self._sky_color[2], self._sky_color[3], self._cloud, self._sky_box)
		cdef Chunk* chunk
		chunk = get_chunk()
		chunk_add_int_endian_safe   (chunk, self._option)
		chunk_add_int_endian_safe   (chunk, self._fog_type)
		chunk_add_float_endian_safe (chunk, self._fog_start)
		chunk_add_float_endian_safe (chunk, self._fog_end)
		chunk_add_float_endian_safe (chunk, self._fog_density)
		chunk_add_floats_endian_safe(chunk, self._ambient  , 4)
		chunk_add_floats_endian_safe(chunk, self._bg_color , 4)
		chunk_add_floats_endian_safe(chunk, self._fog_color, 4)
		chunk_add_floats_endian_safe(chunk, self._sky_color, 4)
		chunk_add_float_endian_safe(chunk, self._cloud_scale)
		return drop_chunk_to_string (chunk), self._cloud, self._sky_box
	
	cdef void __setcstate__(self, cstate):
		#self._option, self._fog_type, self._fog_start, self._fog_end, self._fog_density, self._ambient[0], self._ambient[1], self._ambient[2], self._ambient[3], self._bg_color[0], self._bg_color[1], self._bg_color[2], self._bg_color[3], self._fog_color[0], self._fog_color[1], self._fog_color[2], self._fog_color[3], self._sky_color[0], self._sky_color[1], self._sky_color[2], self._sky_color[3], self._cloud, self._sky_box = cstate
		cstate2, self._cloud, self._sky_box = cstate
		cdef Chunk* chunk
		chunk = string_to_chunk(cstate2)
		chunk_get_int_endian_safe   (chunk, &self._option)
		chunk_get_int_endian_safe   (chunk, &self._fog_type)
		chunk_get_float_endian_safe (chunk, &self._fog_start)
		chunk_get_float_endian_safe (chunk, &self._fog_end)
		chunk_get_float_endian_safe (chunk, &self._fog_density)
		chunk_get_floats_endian_safe(chunk,  self._ambient  , 4)
		chunk_get_floats_endian_safe(chunk,  self._bg_color , 4)
		chunk_get_floats_endian_safe(chunk,  self._fog_color, 4)
		chunk_get_floats_endian_safe(chunk,  self._sky_color, 4)
		if len(cstate2) >= 88: # For compatibility with previous version of Soya
			chunk_get_float_endian_safe (chunk, &self._cloud_scale)
			
		drop_chunk(chunk)
		
	def set_sky_box(self, _Material front, _Material right, _Material back, _Material left, _Material bottom, _Material top = None):
		"""SkyAtmosphere.set_sky_box(FRONT, RIGHT, BACK, LEFT, BOTTOM, TOP = None)

Sets the sky box. The sky box is made of 6 materials that are displayed on the 6 faces of a cube.
The TOP material is optional.
"""
		if top is None: self._sky_box = front, right, back, left, bottom
		else:           self._sky_box = front, right, back, left, bottom, top
		
	property sky_box:
		def __get__(self):
			return self._sky_box
		def __set__(self, sky_box):
			if (len(sky_box) == 0) or (len(sky_box) == 5) or (len(sky_box) == 6):
				self._sky_box = front, right, back, left, bottom, top
			else: raise ValueError("Sky box must be a tuple of 5 or 6 materials")
			
	property sky_color:
		def __get__(self):
			return self._sky_color[0], self._sky_color[1], self._sky_color[2], self._sky_color[3]
		def __set__(self, x):
			self._sky_color[0], self._sky_color[1], self._sky_color[2], self._sky_color[3] = x
	
	property cloud:
		def __get__(self):
			return self._cloud
		def __set__(self, _Material x):
			self._cloud = x
	
	property cloud_scale:
		def __get__(self):
			return self._cloud_scale
		def __set__(self, float x):
			self._cloud_scale = x
	
	cdef void _draw_bg(self):
		glDisable(GL_LIGHTING)
		glDisable(GL_FOG)
		glDisable(GL_DEPTH_TEST)
		glDepthMask(GL_FALSE)
		glDisable(GL_CULL_FACE)
		if self._sky_color[3] != 0.0: self._draw_sky_plane()
		if self._sky_box:             self._draw_sky_box()
		glEnable(GL_LIGHTING)
		glEnable(GL_FOG)
		glEnable(GL_DEPTH_TEST)
		glDepthMask(GL_TRUE)
		glEnable(GL_CULL_FACE)
		
	cdef void _draw_sky_plane(self):
		cdef int    nb2, nb3, i
		cdef float  plane[4], face1[12], y, h, f, g
		cdef float* ptr, *face2, *face3

		glLoadMatrixf(renderer.current_camera._render_matrix)

		# draw gradient
		_DEFAULT_MATERIAL.activate()
		ptr = renderer.current_camera._frustum.points
		for i from 0 <= i < 12: face1[i] = ptr[12 + i] * 0.5
		
		ptr = renderer.current_camera._root_matrix()
		point_by_matrix(face1,     ptr)
		point_by_matrix(face1 + 3, ptr)
		point_by_matrix(face1 + 6, ptr)
		point_by_matrix(face1 + 9, ptr)
		
		y = renderer.current_camera._back * 0.5
		h = renderer.root_frustum.position[1]
		plane[0] =  0.0
		plane[1] = -1.0
		plane[2] =  0.0
		plane[3] =  h + y
		face_intersect_plane(face1, 4, plane, &face2, &nb2)
		if nb2 > 0:
			glColor4fv(self._sky_color)
			glBegin(GL_POLYGON)
			for i from 0 <= i < nb2: glVertex3fv(face2 + i * 3)
			glEnd()
		free(face2)
		
		plane[1] = 1.0
		plane[3] = -plane[3]
		face_intersect_plane(face1, 4, plane, &face3, &nb3)
		plane[1] = -1.0
		plane[3] = renderer.root_frustum.position[1]
		face_intersect_plane(face3, nb3, plane, &face2, &nb2)
		free(face3)
		if nb2 > 0:
			glBegin(GL_POLYGON)
			i = 0
			while i < nb2 * 3:
				f = (face2[i + 1] - h) / y
				g = 1.0 - f
				glColor4f(self._sky_color[0] * f + self._bg_color[0] * g, 
									self._sky_color[1] * f + self._bg_color[1] * g, 
									self._sky_color[2] * f + self._bg_color[2] * g, 
									self._sky_color[3] * f + self._bg_color[3] * g)
				glVertex3fv(face2 + i)
				i = i + 3
			glEnd()
		free(face2)

		# draw clouds
		if not self._cloud is None:
			plane[1] = renderer.root_frustum.position[1] + 5.0
			h = renderer.current_camera._back * 0.7
			glEnable(GL_BLEND)
			self._cloud.activate()

			ptr = renderer.root_frustum.position
			plane[0] = ptr[0] * 0.01 * self._cloud_scale
			plane[2] = ptr[2] * 0.01 * self._cloud_scale
			y = h * 0.1 * self._cloud_scale
			
			ptr = renderer.root_frustum.position
			glTranslatef(ptr[0], 0.0, ptr[2])

			glBegin(GL_TRIANGLE_FAN)

			glTexCoord2f(plane[0], plane[2])
			glVertex3f(0.0, plane[1], 0.0)

			ptr = self._cloud._diffuse
			glColor4f(ptr[0], ptr[1], ptr[2], 0.0)

			glTexCoord2f(plane[0] - y, plane[2] - y); glVertex3f(-h, plane[1], -h)
			glTexCoord2f(plane[0] + y, plane[2] - y); glVertex3f( h, plane[1], -h)
			glTexCoord2f(plane[0] + y, plane[2] + y); glVertex3f( h, plane[1],  h)
			glTexCoord2f(plane[0] - y, plane[2] + y); glVertex3f(-h, plane[1],  h)
			glTexCoord2f(plane[0] - y, plane[2] - y); glVertex3f(-h, plane[1], -h)

			glEnd()
			glDisable(GL_BLEND)

	cdef void _draw_sky_box(self):
		cdef int    nb
		cdef float* ptr
		cdef float  SKY_BOX_DISTANCE
		SKY_BOX_DISTANCE = 10.0
		nb  = len(self._sky_box)
		ptr = renderer.root_frustum.position
		glLoadMatrixf(renderer.current_camera._render_matrix)
		glTranslatef(ptr[0], ptr[1], ptr[2])
		if self._option & ATMOSPHERE_SKY_BOX_ALPHA: glEnable(GL_BLEND)
		# sky_box material order is: front, right, back, left, bottom, top
		# front
		self._sky_box[0].activate()
		glBegin(GL_QUADS)
		glTexCoord2f(0.0, 0.0); glVertex3f(-SKY_BOX_DISTANCE,  SKY_BOX_DISTANCE, SKY_BOX_DISTANCE)
		glTexCoord2f(1.0, 0.0); glVertex3f( SKY_BOX_DISTANCE,  SKY_BOX_DISTANCE, SKY_BOX_DISTANCE)
		glTexCoord2f(1.0, 1.0); glVertex3f( SKY_BOX_DISTANCE, -SKY_BOX_DISTANCE, SKY_BOX_DISTANCE)
		glTexCoord2f(0.0, 1.0); glVertex3f(-SKY_BOX_DISTANCE, -SKY_BOX_DISTANCE, SKY_BOX_DISTANCE)
		glEnd()
		
		if nb > 1:
			# right
			self._sky_box[1].activate()
			glBegin(GL_QUADS)
			glTexCoord2f(0.0, 0.0); glVertex3f(SKY_BOX_DISTANCE,  SKY_BOX_DISTANCE,  SKY_BOX_DISTANCE)
			glTexCoord2f(1.0, 0.0); glVertex3f(SKY_BOX_DISTANCE,  SKY_BOX_DISTANCE, -SKY_BOX_DISTANCE)
			glTexCoord2f(1.0, 1.0); glVertex3f(SKY_BOX_DISTANCE, -SKY_BOX_DISTANCE, -SKY_BOX_DISTANCE)
			glTexCoord2f(0.0, 1.0); glVertex3f(SKY_BOX_DISTANCE, -SKY_BOX_DISTANCE,  SKY_BOX_DISTANCE)
			glEnd()
			
			if nb > 2:
				# back
				self._sky_box[2].activate()
				glBegin(GL_QUADS)
				glTexCoord2f(0.0, 0.0); glVertex3f( SKY_BOX_DISTANCE,  SKY_BOX_DISTANCE, -SKY_BOX_DISTANCE)
				glTexCoord2f(1.0, 0.0); glVertex3f(-SKY_BOX_DISTANCE,  SKY_BOX_DISTANCE, -SKY_BOX_DISTANCE)
				glTexCoord2f(1.0, 1.0); glVertex3f(-SKY_BOX_DISTANCE, -SKY_BOX_DISTANCE, -SKY_BOX_DISTANCE)
				glTexCoord2f(0.0, 1.0); glVertex3f( SKY_BOX_DISTANCE, -SKY_BOX_DISTANCE, -SKY_BOX_DISTANCE)
				glEnd()
				
				if nb > 3:
					# left
					self._sky_box[3].activate()
					glBegin(GL_QUADS)
					glTexCoord2f(0.0, 0.0); glVertex3f(-SKY_BOX_DISTANCE,  SKY_BOX_DISTANCE, -SKY_BOX_DISTANCE)
					glTexCoord2f(1.0, 0.0); glVertex3f(-SKY_BOX_DISTANCE,  SKY_BOX_DISTANCE,  SKY_BOX_DISTANCE)
					glTexCoord2f(1.0, 1.0); glVertex3f(-SKY_BOX_DISTANCE, -SKY_BOX_DISTANCE,  SKY_BOX_DISTANCE)
					glTexCoord2f(0.0, 1.0); glVertex3f(-SKY_BOX_DISTANCE, -SKY_BOX_DISTANCE, -SKY_BOX_DISTANCE)
					glEnd()
					
					if nb > 4:
						# bottom
						self._sky_box[4].activate()
						glBegin(GL_QUADS)
						glTexCoord2f(0.0, 0.0); glVertex3f(-SKY_BOX_DISTANCE, -SKY_BOX_DISTANCE,  SKY_BOX_DISTANCE)
						glTexCoord2f(1.0, 0.0); glVertex3f( SKY_BOX_DISTANCE, -SKY_BOX_DISTANCE,  SKY_BOX_DISTANCE)
						glTexCoord2f(1.0, 1.0); glVertex3f( SKY_BOX_DISTANCE, -SKY_BOX_DISTANCE, -SKY_BOX_DISTANCE)
						glTexCoord2f(0.0, 1.0); glVertex3f(-SKY_BOX_DISTANCE, -SKY_BOX_DISTANCE, -SKY_BOX_DISTANCE)
						glEnd()
						
						if nb > 5:
							# top
							self._sky_box[5].activate()
							glBegin(GL_QUADS)
							glTexCoord2f(0.0, 0.0); glVertex3f(-SKY_BOX_DISTANCE, SKY_BOX_DISTANCE, -SKY_BOX_DISTANCE)
							glTexCoord2f(1.0, 0.0); glVertex3f( SKY_BOX_DISTANCE, SKY_BOX_DISTANCE, -SKY_BOX_DISTANCE)
							glTexCoord2f(1.0, 1.0); glVertex3f( SKY_BOX_DISTANCE, SKY_BOX_DISTANCE,  SKY_BOX_DISTANCE)
							glTexCoord2f(0.0, 1.0); glVertex3f(-SKY_BOX_DISTANCE, SKY_BOX_DISTANCE,  SKY_BOX_DISTANCE)
							glEnd()
		
		glDisable(GL_BLEND)


