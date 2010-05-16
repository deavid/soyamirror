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

cdef _Material _PARTICLE_DEFAULT_MATERIAL
def _set_particle_default_material(_Material material):
	global _PARTICLE_DEFAULT_MATERIAL
	_PARTICLE_DEFAULT_MATERIAL = material


cdef class _Particles(CoordSyst):
	#cdef _Material _material
	#cdef CoordSyst _particle_coordsyst
	#cdef int       _nb_particles, _nb_max_particles, _particle_size # range from 11 to 20 float
	#cdef float*    _particles # life, max_life, position, speed, acceleration, [color], [size], [direction]
														# life, max_life, x/y/z, u/v/w, a/b/c, [r/g/b/a], [w/h], [m/n/o]
	#cdef float     _delta_time
	#cdef int       _nb_colors, _nb_sizes
	#cdef float*    _fading_colors, *_sizes # fading colors and size gain
	#cdef int       _nb_creatable_particles, _max_particles_per_round
	
	cdef __getcstate__(self):
		cdef Chunk* chunk
		chunk = get_chunk()
		chunk_add_int_endian_safe   (chunk, self._option)
		chunk_add_floats_endian_safe(chunk, self._matrix, 19)
		chunk_add_int_endian_safe   (chunk, self._nb_particles)
		chunk_add_int_endian_safe   (chunk, self._nb_max_particles)
		chunk_add_int_endian_safe   (chunk, self._particle_size)
		chunk_add_int_endian_safe   (chunk, self._nb_colors)
		chunk_add_int_endian_safe   (chunk, self._nb_sizes)
		chunk_add_int_endian_safe   (chunk, self._max_particles_per_round)
		chunk_add_floats_endian_safe(chunk, self._particles, self._nb_particles * self._particle_size)
		if self._nb_colors:
			chunk_add_floats_endian_safe(chunk, self._fading_colors, 4 * self._nb_colors)
		if self._nb_sizes:
			chunk_add_floats_endian_safe(chunk, self._sizes, 2 * self._nb_sizes)
			
		return drop_chunk_to_string(chunk), self._material, self._particle_coordsyst
	
	cdef void __setcstate__(self, cstate):
		cdef Chunk* chunk
		cstate2, self._material, self._particle_coordsyst = cstate
		chunk = string_to_chunk(cstate2)
		chunk_get_int_endian_safe(chunk, &self._option)
		chunk_get_floats_endian_safe(chunk, self._matrix, 19)
		chunk_get_int_endian_safe(chunk, &self._nb_particles)
		chunk_get_int_endian_safe(chunk, &self._nb_max_particles)
		chunk_get_int_endian_safe(chunk, &self._particle_size)
		chunk_get_int_endian_safe(chunk, &self._nb_colors)
		chunk_get_int_endian_safe(chunk, &self._nb_sizes)
		chunk_get_int_endian_safe(chunk, &self._max_particles_per_round)
		
		self._particles = <float*> malloc(self._nb_max_particles * self._particle_size * sizeof(float))
		chunk_get_floats_endian_safe(chunk, self._particles, self._nb_particles * self._particle_size)
		if self._nb_colors:
			self._fading_colors = <float*> malloc(4 * self._nb_colors * sizeof(float))
			chunk_get_floats_endian_safe(chunk, self._fading_colors, 4 * self._nb_colors)
		if self._nb_sizes:
			self._sizes = <float*> malloc(2 * self._nb_colors * sizeof(float))
			chunk_get_floats_endian_safe(chunk, self._sizes, 2 * self._nb_sizes)
		
		drop_chunk(chunk)
		self._validity = COORDSYS_INVALID
		
	property material:
		def __get__(self):
			return self._material
		def __set__(self, _Material x not None):
			self._material = x
			self._compute_alpha()
			
	property particle_coordsyst:
		def __get__(self):
			return self._particle_coordsyst
		def __set__(self, CoordSyst x):
			self._particle_coordsyst = x
	
	property nb_particles:
		def __get__(self):
			return self._nb_particles
		def __set__(self, int x):
			self._nb_particles = x
	
	property nb_max_particles:
		def __get__(self):
			return self._nb_max_particles
		def __set__(self, int x):
			self._nb_max_particles = x
			self._reinit()
			
	property lit:
		def __get__(self):
			return not(self._option & SPRITE_NEVER_LIT)
		def __set__(self, int x):
			if x: self._option = self._option & ~SPRITE_NEVER_LIT
			else: self._option = self._option |  SPRITE_NEVER_LIT

	property auto_generate_particle:
		def __get__(self):
			return self._option & PARTICLES_AUTO_GENERATE
		def __set__(self, int x):
			if x:
				self._option = self._option |  PARTICLES_AUTO_GENERATE
				self._nb_creatable_particles = self._max_particles_per_round
			else:
				self._option = self._option & ~PARTICLES_AUTO_GENERATE
				self._nb_creatable_particles = 0
				
	property removable:
		def __get__(self):
			return self._option & PARTICLES_REMOVABLE
		def __set__(self, int x):
			if x: self._option = self._option |  PARTICLES_REMOVABLE
			else: self._option = self._option & ~PARTICLES_REMOVABLE
			
	property max_particles_per_round:
		def __get__(self):
			return self._max_particles_per_round
		def __set__(self, int x):
			self._max_particles_per_round = x
			if self._option & PARTICLES_AUTO_GENERATE: self._nb_creatable_particles = x
			
	def __init__(self, _World parent = None, _Material material = None, int nb_max_particles = 50, int removable = 0):
		CoordSyst.__init__(self, parent)
		if material is None:
			self._material            = _PARTICLE_DEFAULT_MATERIAL
		else:
			self._material            = material
		self._particle_size           = 11
		self._nb_sizes                = 1
		self._sizes                   = <float*> malloc(2 * sizeof(float))
		self._sizes[0]                = self._sizes[1] = 1.0
		self._max_particles_per_round = 1000000
		self._nb_creatable_particles  = nb_max_particles
		self._nb_max_particles        = nb_max_particles
		self._fading_colors           = NULL
		self._particles               = <float*> malloc(self._nb_max_particles * self._particle_size * sizeof(float))
		
		if removable != 0: self._option = self._option | PARTICLES_REMOVABLE
		
	cdef void _reinit(self):
		cdef int size
		self._particle_size = 11
		if self._option & PARTICLES_MULTI_COLOR: self._particle_size = self._particle_size + 4
		if self._option & PARTICLES_MULTI_SIZE:  self._particle_size = self._particle_size + 2
		if self._option & PARTICLES_CYLINDER:    self._particle_size = self._particle_size + 3
		size = self._nb_max_particles * self._particle_size
		if size == 0:
			size = 1
		self._particles = <float*> realloc(self._particles, size * sizeof(float))
		if self._nb_particles > self._nb_max_particles:
			self._nb_particles = self._nb_max_particles
		
	def __dealloc__(self):
		free(self._particles)
		free(self._sizes)
		if self._fading_colors != NULL: free(self._fading_colors)
		
	def regenerate(self, int nb_particle = -1):
		cdef int i, max, nb
		if nb_particle == -1: nb_particle = self._max_particles_per_round
		nb  = 0
		max = self._nb_particles + nb_particle
		if max > self._nb_max_particles: max = self._nb_max_particles
		for i from self._nb_particles <= i < max: self.generate(i)
		
	def begin_round(self):
		if self._option & PARTICLES_AUTO_GENERATE and (self._nb_creatable_particles < self._max_particles_per_round):
			self._nb_creatable_particles = self._max_particles_per_round
		if self._nb_creatable_particles > (self._nb_max_particles - self._nb_particles):
			self._nb_creatable_particles = self._nb_max_particles - self._nb_particles
		#print self._nb_creatable_particles, self._nb_max_particles, self._nb_particles
			
	def advance_time(self, float proportion):
		self._delta_time = self._delta_time + proportion
		
	cdef void _advance(self, float proportion):
		cdef float* particle
		cdef float  decay
		cdef int    i
		decay = - 0.05 * proportion
		particle = self._particles
		i = 0
		#nb = self._nb_particles
		#if nb > self._nb_max_particles:
		#	self._nb_particles = self._nb_max_particles
		#	nb = self._nb_max_particles
		while i < self._nb_particles:
			particle[0] = particle[0] + decay
			if particle[0] < 0.0: # particle is dead
				#if (not(self._option & PARTICLES_AUTO_GENERATE)) or (self.generator(i) == 1): # remove the particle
				if (self._nb_creatable_particles > 0) and (self.generate(i) != 1): # Replace the dead particle by a new one
					self._nb_creatable_particles = self._nb_creatable_particles - 1
				else: # Delete particle
					self._nb_particles = self._nb_particles - 1
					
					memcpy(self._particles + i                  * self._particle_size, 
								 self._particles + self._nb_particles * self._particle_size, 
								 self._particle_size * sizeof(float))
					continue
				
			else: # advance position
				particle[5] = particle[5] + (particle[ 8] * proportion) # speed += acceleration * proportion
				particle[6] = particle[6] + (particle[ 9] * proportion)
				particle[7] = particle[7] + (particle[10] * proportion)
				particle[2] = particle[2] + (particle[ 5] * proportion) # position = speed * proportion
				particle[3] = particle[3] + (particle[ 6] * proportion)
				particle[4] = particle[4] + (particle[ 7] * proportion)
				# advance color
				if (self._nb_colors > 0) and (self._option & PARTICLES_MULTI_COLOR):
					self._get_fading_color(particle[0], particle[1], particle + 11)
					
				# advance size
				if self._option & PARTICLES_MULTI_SIZE:
					if self._option & PARTICLES_MULTI_COLOR: self._get_size(particle[0], particle[1], particle + 15)
					else:                                    self._get_size(particle[0], particle[1], particle + 11)
					
				# advance direction
				if self._option & PARTICLES_CYLINDER:
					pass # XXX TO DO
				
			particle = particle + self._particle_size
			i = i + 1
			
		if (self._nb_particles < self._nb_max_particles) and (self._nb_creatable_particles > 0):
			
			self.regenerate(self._nb_creatable_particles)
			self._nb_creatable_particles = 0
			
		if (self._option & PARTICLES_REMOVABLE) and (self._nb_particles == 0):
			#self.remove()
			from soya import MAIN_LOOP
			MAIN_LOOP.next_round_tasks.append(self.remove)
			
	def remove(self):
		if self._parent: self._parent.remove(self)
		
	cdef void _batch(self, CoordSyst coordsyst):
		if self._option & HIDDEN: return
		# XXX TO DO usefull ?
		# P3_multiply_matrix(p->render_matrix, renderer->c_camera->render_matrix, P3_coordsys_get_root_matrix ((P3_coordsys*) p))
		
		self._advance(self._delta_time)
		if not self._parent is None: # Else, _advance has removed the Particles system.
			renderer._batch(renderer.alpha,    self, coordsyst, NULL)
		self._delta_time = 0.0
		
		#if self._option & SPRITE_RECEIVE_SHADOW:
		#  if self._option & SPRITE_ALPHA: renderer._batch(renderer.alpha,    self, coordsyst, -1)
		#  else:                           renderer._batch(renderer.opaque,   self, coordsyst, -1)
		#else:                             renderer._batch(renderer.specials, self, coordsyst, -1)
		
	cdef void _render(self, CoordSyst coordsyst):
		cdef float* particle, *m
		cdef float  posi[3], w, h
		cdef int    i
		self._material._activate()
		
		glDisable(GL_CULL_FACE)
		if self._option & SPRITE_NEVER_LIT: glDisable(GL_LIGHTING)
		if self._option & SPRITE_COLORED: glColor4fv(self._fading_colors)
		if self._option & PARTICLES_MULTI_SIZE: w = h = 1.0
		else:
			w = self._sizes[0]
			h = self._sizes[1]
			
		glLoadIdentity()
		#if self._particle_coordsyst is None: m = renderer.current_camera._render_matrix
		if self._particle_coordsyst is None: m = self._get_root()._render_matrix
		else:                                m = self._particle_coordsyst._render_matrix
		particle = self._particles
		
		glBegin(GL_QUADS)
		#nb = self._nb_particles
		#if nb > self._nb_max_particles:
		#	nb = self._nb_max_particles
		for i from 0 <= i < self._nb_particles:
			if self._option & PARTICLES_MULTI_COLOR:
				glColor4fv(particle + 11)
				
				if self._option & PARTICLES_MULTI_SIZE:
					w = particle[15]
					h = particle[16]
			elif self._option & PARTICLES_MULTI_SIZE:
				w = particle[11]
				h = particle[12]
				
			posi[0] = particle[2] * m[0] + particle[3] * m[4] + particle[4] * m[ 8] + m[12]
			posi[1] = particle[2] * m[1] + particle[3] * m[5] + particle[4] * m[ 9] + m[13]
			posi[2] = particle[2] * m[2] + particle[3] * m[6] + particle[4] * m[10] + m[14]
			glTexCoord2f(0.0, 0.0); glVertex3f(posi[0] - w, posi[1] - h, posi[2])
			glTexCoord2f(1.0, 0.0); glVertex3f(posi[0] + w, posi[1] - h, posi[2])
			glTexCoord2f(1.0, 1.0); glVertex3f(posi[0] + w, posi[1] + h, posi[2])
			glTexCoord2f(0.0, 1.0); glVertex3f(posi[0] - w, posi[1] + h, posi[2])
			particle = particle + self._particle_size
			
		glEnd()
		if self._option & SPRITE_NEVER_LIT: glEnable(GL_LIGHTING)
		glEnable(GL_CULL_FACE)
		

	cdef void _compute_alpha(self):
		if (self._material._option & (MATERIAL_ALPHA | MATERIAL_MASK)) or ((self._option & SPRITE_COLORED) and (self._fading_colors[3] < 1.0)) or (self._option & PARTICLES_MULTI_COLOR):
			self._option = self._option |  SPRITE_ALPHA
		else:
			self._option = self._option & ~SPRITE_ALPHA
			
	cdef void _get_fading_color(self, float life, float max_life, float* returned_color):
		cdef int    i
		cdef float  f1, f2
		cdef float* c1, *c2
		if   life <= 0.0:      memcpy(returned_color, self._fading_colors + 4 * (self._nb_colors - 1), 4 * sizeof (float))
		elif life >= max_life: memcpy(returned_color, self._fading_colors, 4 * sizeof(float))
		else:
			life = (1.0 - (life / max_life)) * (self._nb_colors - 1)
			i    = <int> life
			c1   = self._fading_colors + 4 *  i
			c2   = self._fading_colors + 4 * (i + 1)
			f2   = life - i
			f1   = 1.0 - f2
			returned_color[0] = c1[0] * f1 + c2[0] * f2
			returned_color[1] = c1[1] * f1 + c2[1] * f2
			returned_color[2] = c1[2] * f1 + c2[2] * f2
			returned_color[3] = c1[3] * f1 + c2[3] * f2
			
	cdef void _get_size(self, float life, float max_life, float* returned_size):
		cdef int    i
		cdef float  f1, f2
		cdef float* c1, *c2
		if   life <= 0.0:      memcpy(returned_size, self._sizes + 2 * (self._nb_sizes - 1), 2 * sizeof(float))
		elif life >= max_life: memcpy(returned_size, self._sizes, 2 * sizeof(float))
		else:
			life = (1.0 - (life / max_life)) * (self._nb_sizes - 1)
			i    = <int> life
			c1   = self._sizes + 2 *  i
			c2   = self._sizes + 2 * (i + 1)
			f2   = life - i
			f1   = 1.0 - f2
			returned_size[0] = c1[0] * f1 + c2[0] * f2
			returned_size[1] = c1[1] * f1 + c2[1] * f2
	
	cdef float* _generate(self, int index, float life):
		cdef float* particle
		particle = self._particles + index * self._particle_size
		particle[0] = particle[1] = life
		if self._parent is None: memcpy (particle + 2, &self._matrix[0] + 12, 3 * sizeof(float))
		else: point_by_matrix_copy(particle + 2, &self._matrix[0] + 12, self._parent._root_matrix())
		if not self._particle_coordsyst is None: point_by_matrix(particle + 2, self._particle_coordsyst._inverted_root_matrix())
		
		if self._option & PARTICLES_MULTI_COLOR:
			memcpy(particle + 11, self._fading_colors, 4 * sizeof(float))
			if self._option & PARTICLES_MULTI_SIZE: memcpy(particle + 15, self._sizes, 2 * sizeof(float))
		elif self._option & PARTICLES_MULTI_SIZE: memcpy(particle + 11, self._sizes, 2 * sizeof(float))
		
		if self._nb_particles <= index: self._nb_particles = index + 1
		return self._particles + self._particle_size * index
	
	def generate(self, int i):
		pass
	
	def set_particle(self, int index, float life, float speed_x, float speed_y, float speed_z, float accel_x, float accel_y, float accel_z, float dir_x = 0.0, float dir_y = 0.0, float dir_z = 0.0):
		"""args are: (index, life, speed x, y, z, acceleration x, y, z, [direction x, y, z])"""
		cdef int    i
		cdef float* particle
		particle = self._generate(index, life)
		particle[ 5] = speed_x
		particle[ 6] = speed_y
		particle[ 7] = speed_z
		particle[ 8] = accel_x
		particle[ 9] = accel_y
		particle[10] = accel_z
		if self._option & PARTICLES_CYLINDER:
			i = 11
			if self._option & PARTICLES_MULTI_COLOR: i = i + 4
			if self._option & PARTICLES_MULTI_SIZE:  i = i + 2
			particle[i    ] = dir_x
			particle[i + 1] = dir_y
			particle[i + 2] = dir_z
		
	def set_particle2(self, int index, float life, float x, float y, float z, float speed_x, float speed_y, float speed_z, float accel_x, float accel_y, float accel_z, float dir_x = 0.0, float dir_y = 0.0, float dir_z = 0.0):
		"""args are: (index, life, position x, y, z, speed x, y, z, acceleration x, y, z, [direction x, y, z])"""
		cdef int    i
		cdef float* particle
		particle = self._particles + index * self._particle_size
		particle[0] = life
		particle[1] = particle[0]
		if self._option & PARTICLES_MULTI_COLOR:
			memcpy(particle + 11, self._fading_colors, 4 * sizeof(float))
			if self._option & PARTICLES_MULTI_SIZE: memcpy(particle + 15, self._sizes, 2 * sizeof(float))
		if self._option & PARTICLES_MULTI_SIZE: memcpy(particle + 11, self._sizes, 2 * sizeof(float))
		if self._nb_particles <= index: self._nb_particles = index + 1
		
		particle[ 2] = x
		particle[ 3] = y
		particle[ 4] = z
		particle[ 5] = speed_x
		particle[ 6] = speed_y
		particle[ 7] = speed_z
		particle[ 8] = accel_x
		particle[ 9] = accel_y
		particle[10] = accel_z
		if self._option & PARTICLES_CYLINDER:
			i = 11
			if self._option & PARTICLES_MULTI_COLOR: i = i + 4
			if self._option & PARTICLES_MULTI_SIZE:  i = i + 2
			particle[i    ] = dir_x
			particle[i + 1] = dir_y
			particle[i + 2] = dir_z
			
	def get_particle_position(self, int index):
		cdef float* particle
		particle = self._particles + index * self._particle_size
		return particle[2], particle[3], particle[4]
	
	def set_particle_position(self, int index, float x, float y, float z):
		cdef float* particle
		particle = self._particles + index * self._particle_size
		particle[2] = x
		particle[3] = y
		particle[4] = z
		
	def set_colors(self, *colors):
		cdef int i, j
		
		self._nb_colors = len(colors)
		if self._nb_colors != 0:
			self._fading_colors = <float*> realloc(self._fading_colors, self._nb_colors * 4 * sizeof(float))
			for i from 0 <= i < self._nb_colors:
				color = colors[i]
				self._fading_colors[i * 4    ] = color[0]
				self._fading_colors[i * 4 + 1] = color[1]
				self._fading_colors[i * 4 + 2] = color[2]
				self._fading_colors[i * 4 + 3] = color[3]
			self._option = self._option | SPRITE_COLORED
			if self._nb_colors == 1: self._option = self._option & ~PARTICLES_MULTI_COLOR
			else:                    self._option = self._option |  PARTICLES_MULTI_COLOR
		else:
			if self._fading_colors != NULL:
				free(self._fading_colors)
				self._fading_colors = NULL
			self._option = self._option & ((~SPRITE_COLORED) | (~PARTICLES_MULTI_COLOR))
		self._compute_alpha()
		self._reinit()
		
	def set_sizes(self, *sizes):
		cdef int i
		if sizes:
			self._nb_sizes = len(sizes)
			self._sizes = <float*> realloc(self._sizes, self._nb_sizes * 2 * sizeof(float))
			for i from 0 <= i < self._nb_sizes:
				size = sizes[i]
				self._sizes[i * 2    ] = size[0]
				self._sizes[i * 2 + 1] = size[1]
			if self._nb_sizes == 1: self._option = self._option & ~PARTICLES_MULTI_SIZE
			else:                   self._option = self._option |  PARTICLES_MULTI_SIZE
		else:
			self._nb_sizes = 1
			self._sizes = <float*> realloc(self._sizes, 2 * sizeof(float))
			self._sizes[0] = self._sizes[1] = 1.0
			self._option = self._option & ~PARTICLES_MULTI_SIZE
		self._reinit()


import random

# Hint :
# The free Linux driver for ati radeon 7500 has problem for rendering transparency
# => as particles system usually use additive blending, you should avoid using alpha
# for fading colors.
# E.g. :
#   Particles.set_colors((1.0, 1.0, 1.0, 0.5), (1.0, 1.0, 1.0, 1.0), (1.0, 1.0, 1.0, 0.0))
# and
#   Particles.set_colors((0.5, 0.5, 0.5, 1.0), (1.0, 1.0, 1.0, 1.0), (0.0, 0.0, 0.0, 1.0))
# are equivalent with additive blending, but the last one doesn't bug on radeon 7500.


cdef class Fountain(_Particles):
	def __init__(self, _World parent = None, _Material material = None, int nb_particles = 12, int removable = 0):
		_Particles.__init__(self, parent, material, nb_particles, removable)
		#self.set_colors((0.3, 0.3, 0.3, 1.0), (0.3, 0.3, 0.3, 0.0))
		#self.set_colors((0.3, 0.3, 0.3, 1.0), (0.1, 0.1, 0.1, 0.0))
		self.set_colors((0.1, 0.1, 0.1, 1.0), (0.3, 0.3, 0.3, 1.0), (0.3, 0.3, 0.3, 1.0), (0.1, 0.1, 0.1, 1.0))
		self.set_sizes ((0.25, 0.25), (1.0, 1.0))
		
	def generate(self, int index):
		cdef float sx, sy, sz, l
		sx = random.random() - 0.5
		sy = random.random() + 1.0
		sz = random.random() - 0.5
		l  = (0.2 * (1.0 + random.random())) / sqrt(sx * sx + sy * sy + sz * sz) * 0.4 * self._matrix[16]
		self.set_particle(index, 1.0 + random.random(), sx * l, sy * l, sz * l, 0.0, 0.0, 0.0)

cdef class Smoke(_Particles):
	def __init__(self, _World parent = None, _Material material = None, int nb_particles = 12, int removable = 0):
		_Particles.__init__(self, parent, material, nb_particles, removable)
		#self.set_colors((0.3, 0.3, 0.3, 1.0), (0.3, 0.3, 0.3, 0.0))
		#self.set_colors((0.3, 0.3, 0.3, 1.0), (0.1, 0.1, 0.1, 0.0))
		self.set_colors((0.1, 0.1, 0.1, 1.0), (0.3, 0.3, 0.3, 1.0), (0.3, 0.3, 0.3, 1.0), (0.1, 0.1, 0.1, 1.0))
		self.set_sizes ((0.25, 0.25), (1.0, 1.0))
		self._life_base = 1.0
		self._life_function = random.random
		self._speed_factor = 1.0
		self._acceleration = 0.0
		
	def generate(self, int index):
		cdef float sx, sy, sz, l
		sx = random.random() - 0.5
		sy = random.random() - 0.5
		sz = random.random() - 0.5
		l  = self._speed_factor * (0.2 * (1.0 + random.random())) / sqrt(sx * sx + sy * sy + sz * sz) * 0.4 * self._matrix[16]
		lb  = self._life_base
		lf = self._life_function
		a = self._acceleration
		sx=sx*l
		sy=sy*l
		sz=sz*l
		self.set_particle(index, (1 + lf())*lb, sx, sy, sz, sx*a, sy*a, sz*a)
		
	property life:
		"""the life time of a particle (life of a particle = life*(1+life_function)"""
		def __get__(self):
			return self._life_base
		def __set__(self, float value):
			self._life_base = value
	property life_function:
		"""a function modify the life of a particle (life of a particle = (life_function+1)*life_base) default is 1"""
		def __get__(self):
			return self._life_function
		def __set__(self, float value):
			self._life_function = value
	property speed:
		"""a function modify the life of a particle (life of a particle = (life_function()+1)*life_base) default is random"""
		def __get__(self):
			return self._speed_factor
		def __set__(self, float value):
			self._speed_factor = value
	property acceleration:
		"""a function modify the life of a particle (life of a particle = (life_function()+1)*life_base) default is random"""
		def __get__(self):
			return self._acceleration
		def __set__(self, float value):
			self._acceleration = value
	
		
cdef class FlagSubFire(_Particles):
	def __init__(self, _World parent = None, _Material material = None, int nb_particles = 12, int removable = 0):
		_Particles.__init__(self, parent, material, nb_particles, removable)
		self.set_colors((1.0, 1.0, 1.0, 1.0), (0.2, 0.7, 0.8, 0.8), (0.2, 0.4, 0.8, 0.2))
		self.set_sizes ((0.25, 0.25), (1.0, 1.0))
		
	def generate(self, int index, float x = 0.0, float y = 0.0, float z = 0.0):
		#angle = random.random() * 3.1417
		#sx = math.cos(angle)
		#sy = 2.0 + math.sqrt(random.random() * 50.0)
		#sz = math.sin(angle)
		cdef float sx, sy, sz, l
		sx = random.random() - 0.5
		sy = random.random() + 1.0
		sz = random.random() - 0.5
		l  = (0.2 * (1.0 + random.random())) / sqrt(sx * sx + sy * sy + sz * sz) * self._matrix[16]
		self.set_particle2(index, 0.5 + random.random(), x, y, z, sx * l, sy * l, sz * l, 0.0, -0.03, 0.0)
		#if position:
		#  self.set_particle_all(index, 0.5 + random.random(), x, y, z, sx * l, sy * l, sz * l, 0.0, -0.03, 0.0)
		#else:
		#  self.set_particle(index, 0.5 + random.random(), sx * l, sy * l, sz * l, 0.0, -0.03, 0.0)



cdef class FlagFirework(_Particles):
	#cdef _Particles _subgenerator
	#cdef int        _nb_sub_particles
	
	def __init__(self, _World parent = None, _Material material = None, int nb_particles = 6, int removable = 0, subgenerator = None, int nb_sub_particles = 8):
		_Particles.__init__(self, parent, material, nb_particles, removable)
		self._subgenerator = subgenerator or FlagSubFire(parent, nb_particles = nb_particles * nb_sub_particles)
		self._nb_sub_particles = nb_sub_particles
		self.set_colors((0.9, 0.7, 0.0, 0.4), (1.0, 1.0, 0.0, 1.0), (1.0, 1.0, 1.0, 1.0))
		self.set_sizes ((0.0, 0.0), (0.25, 0.25))
		self._option = self._option | PARTICLES_AUTO_GENERATE

	def remove(self):
		_Particles.remove(self)
		self._subgenerator.removable = 1
		
	def regenerate(self, int nb_particle = -1):
		cdef int i, nb
		if nb_particle == -1: nb_particle = self._max_particles_per_round
		nb = 0
		i  = self._nb_particles
		while i < self._nb_max_particles:
			self.mygenerate(i)
			i  = nb + 1
			nb = i  + 1
			if nb >= nb_particle: break
		#self.advance_time(1.0)
		
	def subgenerate(self, int index):
		cdef int        i
		cdef _Particles subg
		subg = self._subgenerator
		if not subg is None:
			if subg._nb_particles + self._nb_sub_particles > subg._nb_max_particles:
				# nb_max_particles and NOT _nb_max_particles (note the starting _) :
				# Changing the Python attribute nb_max_particles will realloc the memory as needed,
				# though a raw assignment to _nb_max_particles won't.
				subg.nb_max_particles = subg._nb_particles + self._nb_sub_particles
			p = self.get_particle_position(index)
			
			for i from subg._nb_particles <= i < subg._nb_particles + self._nb_sub_particles:
				subg.generate(i, p[0], p[1], p[2])
				#subg.set_particle_position(i, *p)
				
	def mygenerate(self, int index):
		cdef float sx, sy, sz, l
		sx = random.random() - 0.5
		sy = random.random() + 1.0
		sz = random.random() - 0.5
		l  = (0.2 * (1.8 + random.random())) / sqrt(sx * sx + sy * sy + sz * sz)
		self.set_particle(index, 0.5 + random.random(), sx * l, sy * l, sz * l, 0.0, -0.03, 0.0)
		
	def generate(self, int index):
		self.subgenerate(index)
		self.mygenerate(index)





# def draw_sprites(CoordSyst coordsyst, sprites):
#   # args : (coordsyst, [particules])
#   cdef CoordSyst root, parent
#   cdef float position[3], color[4], w, h
#   int i, nb
	
#   # TO DO coordsyst is useless...
#   sprites = PySequence_Fast_GET_ITEM (args, 1);
#   nb      = len(sprites)
#   root    = renderer.current_camera
#   glLoadIdentity()
#   glDisable(GL_CULL_FACE)
#   # use the current activated material :)
#   glBegin(GL_QUADS)
#   for i from 0 <= i < nb:
#     sprite = sprites[i]
#     parent = sprite.parent
#     position[0] = sprite.x
#     position[1] = sprite.y
#     position[2] = sprite.z
#     if not parent is root:
#       if not parent is None: point_by_matrix(position, parent._root_matrix())
#       point_by_matrix(position, root._inverted_root_matrix())
		
#     o = PyObject_GetAttrString (sprite, "color");
#     color[0] = (GLfloat) PyFloat_AS_DOUBLE (PySequence_Fast_GET_ITEM (o, 0));
#     color[1] = (GLfloat) PyFloat_AS_DOUBLE (PySequence_Fast_GET_ITEM (o, 1));
#     color[2] = (GLfloat) PyFloat_AS_DOUBLE (PySequence_Fast_GET_ITEM (o, 2));
#     color[3] = (GLfloat) PyFloat_AS_DOUBLE (PySequence_Fast_GET_ITEM (o, 3));
#     Py_DECREF (o);
#     o = PyObject_GetAttrString (sprite, "width");
#     w = (GLfloat) PyFloat_AS_DOUBLE (o);
#     Py_DECREF (o);
#     o = PyObject_GetAttrString (sprite, "height");
#     h = (GLfloat) PyFloat_AS_DOUBLE (o);
#     Py_DECREF (o);
#     /* draw */
#     glColor4fv (color);
#     glTexCoord2f (0.0, 0.0); 
#     glVertex3f (position[0] - w, position[1] - h, position[2]);
#     glTexCoord2f (1.0, 0.0); 
#     glVertex3f (position[0] + w, position[1] - h, position[2]);
#     glTexCoord2f (1.0, 1.0); 
#     glVertex3f (position[0] + w, position[1] + h, position[2]);
#     glTexCoord2f (0.0, 1.0); 
#     glVertex3f (position[0] - w, position[1] + h, position[2]);
#   }
#   glEnd ();
#   glEnable (GL_CULL_FACE);
#   Py_INCREF (Py_None);
#   return Py_None;
# }

# PyObject* PyP3SpritesSphere_RenderOld (PyObject* module, PyObject* args) {
# //  P3_parent* coordsys;
#   P3_coordsys* root;
# //  P3_parent* root;
#   PyObject* sprites;
#   PyObject* sprite;
#   PyObject* old;
#   PyObject* o;
#   GLfloat position[3];
#   GLfloat color[4];
#   GLfloat w; GLfloat h; /* size of the sprite */
#   int i; int j;
#   int nb; int nb2;
#   GLfloat a_incr;
# // TO DO
#   /* args : (coordsys, [particules], alpha cste) */
# //  coordsys = (P3_parent*) PySequence_Fast_GET_ITEM (args, 0);
#   sprites = PySequence_Fast_GET_ITEM (args, 1);
#   nb = PySequence_Size (sprites);
# //  root = (P3_parent*) P3_coordsys_get_root ((P3_coordsys*) coordsys);
#   root = (P3_coordsys*) renderer->c_camera;
#   a_incr = (GLfloat) PyFloat_AS_DOUBLE (PySequence_Fast_GET_ITEM (args, 2));
#   glLoadIdentity ();
# //  glLoadMatrixf (root->render_matrix);
#   glDisable (GL_CULL_FACE);
#   /* use default activated material :) */
#   glBegin (GL_QUADS);
#   for (i = 0; i < nb; i++) {
#     sprite = PySequence_Fast_GET_ITEM (sprites, i);
#     o = PyObject_GetAttrString (sprite, "color");
#     color[0] = (GLfloat) PyFloat_AS_DOUBLE (PySequence_Fast_GET_ITEM (o, 0));
#     color[1] = (GLfloat) PyFloat_AS_DOUBLE (PySequence_Fast_GET_ITEM (o, 1));
#     color[2] = (GLfloat) PyFloat_AS_DOUBLE (PySequence_Fast_GET_ITEM (o, 2));
#     color[3] = (GLfloat) PyFloat_AS_DOUBLE (PySequence_Fast_GET_ITEM (o, 3));
#     Py_DECREF (o);
#     o = PyObject_GetAttrString (sprite, "width");
#     w = (GLfloat) PyFloat_AS_DOUBLE (o);
#     Py_DECREF (o);
#     o = PyObject_GetAttrString (sprite, "height");
#     h = (GLfloat) PyFloat_AS_DOUBLE (o);
#     Py_DECREF (o);
#     old = PyObject_GetAttrString (sprite, "old_pos");
#     nb2 = PySequence_Size (old);
#     for (j = 0; j < nb2; j++) {
#       sprite = PySequence_Fast_GET_ITEM (old, j);
#       o = PyObject_GetAttrString (sprite, "x");
#       position[0] = (GLfloat) PyFloat_AS_DOUBLE (o);
#       Py_DECREF (o);
#       o = PyObject_GetAttrString (sprite, "y");
#       position[1] = (GLfloat) PyFloat_AS_DOUBLE (o);
#       Py_DECREF (o);
#       o = PyObject_GetAttrString (sprite, "z");
#       position[2] = (GLfloat) PyFloat_AS_DOUBLE (o);
#       Py_DECREF (o);
#       o = PyObject_GetAttrString (sprite, "parent");
#       if (o != (PyObject*) root) {
#         if (o != Py_None) {
#           P3_point_by_matrix (position, P3_coordsys_get_root_matrix ((P3_coordsys*) o));
#         }
#         P3_point_by_matrix (position, P3_coordsys_get_inverted_root_matrix ((P3_coordsys*) root));
#       }
#       Py_DECREF (o);
#       glColor4fv (color);
#       glTexCoord2f (0.0, 0.0); 
#       glVertex3f (position[0] - w, position[1] - h, position[2]);
#       glTexCoord2f (1.0, 0.0); 
#       glVertex3f (position[0] + w, position[1] - h, position[2]);
#       glTexCoord2f (1.0, 1.0); 
#       glVertex3f (position[0] + w, position[1] + h, position[2]);
#       glTexCoord2f (0.0, 1.0); 
#       glVertex3f (position[0] - w, position[1] + h, position[2]);
#       color[3] += a_incr;
#     }
#     Py_DECREF (old);
#   }
#   glEnd ();
#   glEnable (GL_CULL_FACE);
#   Py_INCREF (Py_None);
#   return Py_None;
# }

# /*=========================*
#  * FADING COLORS FUNCTIONS *
#  *=========================*/

# PyObject* PyP3FadingColor_Advance (PyObject* module, PyObject* self) {
#   GLfloat life;
#   GLfloat max_life;
#   PyObject* colors;
#   PyObject* color;
#   PyObject* o;
#   colors = PyObject_GetAttrString (self, "colors");
#   color = PyObject_GetAttrString (self, "color");
#   o = PyObject_GetAttrString (self, "life");
#   life = (GLfloat) PyFloat_AS_DOUBLE (o);
#   Py_DECREF (o);
#   o = PyObject_GetAttrString (self, "max_life");
#   max_life = (GLfloat) PyFloat_AS_DOUBLE (o);
#   Py_DECREF (o);
#   /* maximum life of a particle is assumed to be 1.0 */
#   if (life <= 0.0) {
#     int i;
#     o = PySequence_Fast_GET_ITEM (colors, PySequence_Size (colors) - 1);
#     for (i = 0; i < 4; i++) {
#       PySequence_SetItem (color, i, PySequence_Fast_GET_ITEM (o, i));
#     }
#   } else if (life >= max_life) {
#     int i;
#     o = PySequence_Fast_GET_ITEM (colors, 0);
#     for (i = 0; i < 4; i++) {
#       PySequence_SetItem (color, i, PySequence_Fast_GET_ITEM (o, i));
#     }
#   } else {
#     int nb = PySequence_Size (colors);
#     int index;
#     int i;
#     GLfloat f1; GLfloat f2;
#     GLfloat c1[4]; GLfloat c2[4];
#     life = (1.0 - (life / max_life)) * (nb - 1);
#     index = (int) life;
#     o = PySequence_Fast_GET_ITEM (colors, index);
#     for (i = 0; i < 4; i++) {
#       c1[i] = (GLfloat) PyFloat_AS_DOUBLE (PySequence_Fast_GET_ITEM (o, i));
#     }
#     o = PySequence_Fast_GET_ITEM (colors, index + 1);
#     for (i = 0; i < 4; i++) {
#       c2[i] = (GLfloat) PyFloat_AS_DOUBLE (PySequence_Fast_GET_ITEM (o, i));
#     }
#     f2 = life - index;
#     f1 = 1.0 - f2;
#     o = PyFloat_FromDouble ((double) c1[0] * f1 + c2[0] * f2);
#     PySequence_SetItem (color, 0, o);
#     Py_DECREF (o);
#     o = PyFloat_FromDouble ((double) c1[1] * f1 + c2[1] * f2);
#     PySequence_SetItem (color, 1, o);
#     Py_DECREF (o);
#     o = PyFloat_FromDouble ((double) c1[2] * f1 + c2[2] * f2);
#     PySequence_SetItem (color, 2, o);
#     Py_DECREF (o);
#     o = PyFloat_FromDouble ((double) c1[3] * f1 + c2[3] * f2);
#     PySequence_SetItem (color, 3, o);
#     Py_DECREF (o);
#   }
#   Py_DECREF (colors);
#   Py_DECREF (color);
#   Py_INCREF (Py_None);
#   return Py_None;
# }

# /*========================*
#  * ACCELERATION FUNCTIONS *
#  *========================*/

# PyObject* PyP3Acceleration_Advance (PyObject* module, PyObject* args) {
#   PyObject* self;
#   PyObject* acc;
#   PyObject* speed;
#   PyObject* o;
#   double d;
#   double sx; double sy; double sz;
#   double proportion;
#   /* args are: (self, acceleration, proportion) */
#   self = PySequence_Fast_GET_ITEM (args, 0);
#   acc  = PySequence_Fast_GET_ITEM (args, 1);
#   proportion = PyFloat_AS_DOUBLE (PySequence_Fast_GET_ITEM (args, 2));
#   speed = PyObject_GetAttrString (self, "speed");
#   o = PyObject_GetAttrString (speed, "x");
#   d = PyFloat_AS_DOUBLE (o);
#   Py_DECREF (o);
#   sx = d + PyFloat_AS_DOUBLE (PySequence_Fast_GET_ITEM (acc, 0));
#   o = PyFloat_FromDouble (sx);
#   PyObject_SetAttrString (speed, "x", o);
#   Py_DECREF (o);
#   o = PyObject_GetAttrString (speed, "y");
#   d = PyFloat_AS_DOUBLE (o);
#   Py_DECREF (o);
#   sy = d + PyFloat_AS_DOUBLE (PySequence_Fast_GET_ITEM (acc, 1));
#   o = PyFloat_FromDouble (sy);
#   PyObject_SetAttrString (speed, "y", o);
#   Py_DECREF (o);
#   o = PyObject_GetAttrString (speed, "z");
#   d = PyFloat_AS_DOUBLE (o);
#   Py_DECREF (o);
#   sz = d + PyFloat_AS_DOUBLE (PySequence_Fast_GET_ITEM (acc, 2));
#   o = PyFloat_FromDouble (sz);
#   PyObject_SetAttrString (speed, "z", o);
#   Py_DECREF (o);
#   Py_DECREF (speed);
#   o = PyObject_GetAttrString (self, "x");
#   d = PyFloat_AS_DOUBLE (o);
#   Py_DECREF (o);
#   o = PyFloat_FromDouble (d + sx * proportion);
#   PyObject_SetAttrString (self, "x", o);
#   Py_DECREF (o);
#   o = PyObject_GetAttrString (self, "y");
#   d = PyFloat_AS_DOUBLE (o);
#   Py_DECREF (o);
#   o = PyFloat_FromDouble (d + sy * proportion);
#   PyObject_SetAttrString (self, "y", o);
#   Py_DECREF (o);
#   o = PyObject_GetAttrString (self, "z");
#   d = PyFloat_AS_DOUBLE (o);
#   Py_DECREF (o);
#   o = PyFloat_FromDouble (d + sz * proportion);
#   PyObject_SetAttrString (self, "z", o);
#   Py_DECREF (o);
#   Py_INCREF (Py_None);
#   return Py_None;
# }
