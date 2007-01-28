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

cdef float _SPRITE_MATRIX[16]
_SPRITE_MATRIX[0] = _SPRITE_MATRIX[5] = _SPRITE_MATRIX[10] = _SPRITE_MATRIX[15] = 1.0
_SPRITE_MATRIX[1] = _SPRITE_MATRIX[2] = _SPRITE_MATRIX[3] = _SPRITE_MATRIX[4] = _SPRITE_MATRIX[6] = _SPRITE_MATRIX[7] = _SPRITE_MATRIX[8] = _SPRITE_MATRIX[9] = _SPRITE_MATRIX[11] = _SPRITE_MATRIX[12] = _SPRITE_MATRIX[13] = _SPRITE_MATRIX[14] = 0.0
cdef float _CYLINDER_SPRITE_MATRIX[16]
_CYLINDER_SPRITE_MATRIX[0] = _CYLINDER_SPRITE_MATRIX[5] = _CYLINDER_SPRITE_MATRIX[10] = _CYLINDER_SPRITE_MATRIX[15] = 1.0
_CYLINDER_SPRITE_MATRIX[1] = _CYLINDER_SPRITE_MATRIX[2] = _CYLINDER_SPRITE_MATRIX[3] = _CYLINDER_SPRITE_MATRIX[4] = _CYLINDER_SPRITE_MATRIX[6] = _CYLINDER_SPRITE_MATRIX[7] = _CYLINDER_SPRITE_MATRIX[8] = _CYLINDER_SPRITE_MATRIX[9] = _CYLINDER_SPRITE_MATRIX[11] = _CYLINDER_SPRITE_MATRIX[12] = _CYLINDER_SPRITE_MATRIX[13] = _CYLINDER_SPRITE_MATRIX[14] = 0.0

cdef class _Sprite(CoordSyst):
	#cdef float _width, _height
	#cdef float _color[4]
	#cdef _Material _material
	
	property width:
		def __get__(self):
			return self._width
		def __set__(self, float x):
			self._width = x
	
	property height:
		def __get__(self):
			return self._height
		def __set__(self, float x):
			self._height = x
	
	property color:
		def __get__(self):
			return self._color[0], self._color[1], self._color[2], self._color[3]
		def __set__(self, x):
			self._color[0], self._color[1], self._color[2], self._color[3] = x
	
	property material:
		def __get__(self):
			return self._material
		def __set__(self, _Material x not None):
			self._material = x
			
	property lit:
		def __get__(self):
			return not(self._option & SPRITE_NEVER_LIT)
		def __set__(self, int x):
			if x: self._option = self._option & ~SPRITE_NEVER_LIT
			else: self._option = self._option |  SPRITE_NEVER_LIT
			
	def __init__(self, _World parent = None, _Material material = None):
		CoordSyst.__init__(self, parent)
		self._material = material or _DEFAULT_MATERIAL
		self._color[0] = self._color[1] = self._color[2] = self._color[3] = 1.0
		self._width = self._height = 0.5
		
	cdef __getcstate__(self):
		#return struct.pack("<iifffffffffffffffffffiiffff", self._option, self._matrix[12], self._matrix[13], self._matrix[14], self._material, self._width, self._height, self._color[0], self._color[1], self._color[2], self._color[3]), self._material
		
		cdef Chunk* chunk
		chunk = get_chunk()
		chunk_add_int_endian_safe   (chunk, self._option)
		chunk_add_floats_endian_safe(chunk, self._matrix, 19)
		chunk_add_float_endian_safe   (chunk, self._width)
		chunk_add_float_endian_safe   (chunk, self._height)
		chunk_add_floats_endian_safe(chunk, self._color ,  4)
		return drop_chunk_to_string(chunk), self._material
	
	cdef void __setcstate__(self, cstate):
		self._validity = COORDSYS_INVALID
		#self._option, self._matrix[12], self._matrix[13], self._matrix[14], self._material, self._width, self._height, self._color[0], self._color[1], self._color[2], self._color[3] = struct.pack("<iifffffffffffffffffffiiffff")
		#self._material = cstate[1]
		
		cdef Chunk* chunk
		cstate2, self._material = cstate
		chunk = string_to_chunk(cstate2)
		chunk_get_int_endian_safe(chunk, &self._option)
		chunk_get_floats_endian_safe(chunk, self._matrix, 19)
		chunk_get_float_endian_safe(chunk, &self._width)
		chunk_get_float_endian_safe(chunk, &self._height)
		chunk_get_floats_endian_safe(chunk, self._color ,  4)
		drop_chunk(chunk)
		
	cdef void _batch(self, CoordSyst coordsyst):
		if self._option & HIDDEN: return
		if self._option & SPRITE_RECEIVE_SHADOW:
			if self.option & SPRITE_ALPHA: renderer._batch(renderer.alpha,    self, None, NULL)
			else:                          renderer._batch(renderer.opaque,   self, None, NULL)
		else:                            renderer._batch(renderer.specials, self, None, NULL)
		
	cdef void _render(self, CoordSyst coordsyst):
		cdef float* a, *b
		# compute render matrix
		b = self._parent._render_matrix
		a = &self._matrix[12]
		_SPRITE_MATRIX[12] = a[0] * b[0] + a[1] * b[4] + a[2] * b[ 8] + b[12]
		_SPRITE_MATRIX[13] = a[0] * b[1] + a[1] * b[5] + a[2] * b[ 9] + b[13]
		_SPRITE_MATRIX[14] = a[0] * b[2] + a[1] * b[6] + a[2] * b[10] + b[14]
		self._material._activate()
		glLoadMatrixf(_SPRITE_MATRIX)
		glDisable(GL_CULL_FACE)
		if self._option & SPRITE_NEVER_LIT: glDisable(GL_LIGHTING)
		else:
			glLightModeli(GL_LIGHT_MODEL_TWO_SIDE, GL_TRUE)
			glNormal3f(0.0, 0.0, -1.0)
		glColor4fv(self._color)
		
		glBegin(GL_QUADS)
		glTexCoord2f(0.0, 0.0); glVertex3f(- self._width, - self._height, 0.0)
		glTexCoord2f(1.0, 0.0); glVertex3f(  self._width, - self._height, 0.0)
		glTexCoord2f(1.0, 1.0); glVertex3f(  self._width,   self._height, 0.0)
		glTexCoord2f(0.0, 1.0); glVertex3f(- self._width,   self._height, 0.0)
		glEnd()
		glEnable(GL_CULL_FACE)
		if self._option & SPRITE_NEVER_LIT: glEnable(GL_LIGHTING)
		else: glLightModeli(GL_LIGHT_MODEL_TWO_SIDE, GL_FALSE)
		
	cdef void _compute_alpha(self):
		if self._material._option & (MATERIAL_ALPHA | MATERIAL_MASK):
			self._option = self._option | SPRITE_ALPHA
			return
		if self._color[3] < 1.0:
			self._option = self._option | SPRITE_ALPHA
			return
		self._option = self._option & ~SPRITE_ALPHA
		
		
cdef class _CylinderSprite(_Sprite):
	cdef __getcstate__(self):
		#return struct.pack("<iifffffffffffffffffffiiffff", self._option, self._matrix[12], self._matrix[13], self._matrix[14], self._material, self._width, self._height, self._color[0], self._color[1], self._color[2], self._color[3]), self._material
		
		cdef Chunk* chunk
		chunk = get_chunk()
		chunk_add_int_endian_safe   (chunk, self._option)
		chunk_add_floats_endian_safe(chunk, self._matrix, 19)
		chunk_add_float_endian_safe   (chunk, self._width)
		chunk_add_float_endian_safe   (chunk, self._height)
		chunk_add_floats_endian_safe(chunk, self._color ,  4)
		return drop_chunk_to_string(chunk), self._material
	
	cdef void __setcstate__(self, cstate):
		self._validity = COORDSYS_INVALID
		#self._option, self._matrix[12], self._matrix[13], self._matrix[14], self._material, self._width, self._height, self._color[0], self._color[1], self._color[2], self._color[3] = struct.pack("<iifffffffffffffffffffiiffff")
		#self._material = cstate[1]
		
		cdef Chunk* chunk
		cstate2, self._material = cstate
		chunk = string_to_chunk(cstate2)
		chunk_get_int_endian_safe(chunk, &self._option)
		chunk_get_floats_endian_safe(chunk, self._matrix, 19)
		chunk_get_float_endian_safe(chunk, &self._width)
		chunk_get_float_endian_safe(chunk, &self._height)
		chunk_get_floats_endian_safe(chunk, self._color ,  4)
		drop_chunk(chunk)
		
	cdef void _render(self, CoordSyst coordsyst):
		cdef float  x, y, f
		cdef float* a, *m
		# compute render matrix
		m = self._parent._render_matrix
		a = &self._matrix[8]
		_CYLINDER_SPRITE_MATRIX[ 8] = a[0] * m[0] + a[1] * m[4] + a[2] * m[ 8]
		_CYLINDER_SPRITE_MATRIX[ 9] = a[0] * m[1] + a[1] * m[5] + a[2] * m[ 9]
		_CYLINDER_SPRITE_MATRIX[10] = a[0] * m[2] + a[1] * m[6] + a[2] * m[10]
		a = &self._matrix[12]
		_CYLINDER_SPRITE_MATRIX[12] = a[0] * m[0] + a[1] * m[4] + a[2] * m[ 8] + m[12]
		_CYLINDER_SPRITE_MATRIX[13] = a[0] * m[1] + a[1] * m[5] + a[2] * m[ 9] + m[13]
		_CYLINDER_SPRITE_MATRIX[14] = a[0] * m[2] + a[1] * m[6] + a[2] * m[10] + m[14]
		if _CYLINDER_SPRITE_MATRIX[10] == 0.0:
			x = _CYLINDER_SPRITE_MATRIX[8]
			y = _CYLINDER_SPRITE_MATRIX[9]
		else:
			f = _CYLINDER_SPRITE_MATRIX[14] / _CYLINDER_SPRITE_MATRIX[10]
			x = _CYLINDER_SPRITE_MATRIX[12] - f * _CYLINDER_SPRITE_MATRIX[8]
			y = _CYLINDER_SPRITE_MATRIX[13] - f * _CYLINDER_SPRITE_MATRIX[9]
			# sign of x, y ?
		if (x == 0.0) and (y == 0.0):
			_CYLINDER_SPRITE_MATRIX[4] = 0.0
			_CYLINDER_SPRITE_MATRIX[5] = 1.0
		else:
			f = <float> (1.0 / sqrt(x * x + y * y))
			_CYLINDER_SPRITE_MATRIX[5] = -x * f
			_CYLINDER_SPRITE_MATRIX[4] =  y * f
		_CYLINDER_SPRITE_MATRIX[0] =  _CYLINDER_SPRITE_MATRIX[5] * _CYLINDER_SPRITE_MATRIX[10] - _CYLINDER_SPRITE_MATRIX[6] * _CYLINDER_SPRITE_MATRIX[9]
		_CYLINDER_SPRITE_MATRIX[1] = -_CYLINDER_SPRITE_MATRIX[4] * _CYLINDER_SPRITE_MATRIX[10] + _CYLINDER_SPRITE_MATRIX[6] * _CYLINDER_SPRITE_MATRIX[8]
		_CYLINDER_SPRITE_MATRIX[2] =  _CYLINDER_SPRITE_MATRIX[4] * _CYLINDER_SPRITE_MATRIX[ 9] - _CYLINDER_SPRITE_MATRIX[5] * _CYLINDER_SPRITE_MATRIX[8]
		# render
		self._material._activate()
		glLoadMatrixf(_CYLINDER_SPRITE_MATRIX)
		glDisable(GL_CULL_FACE)
		if self._option & SPRITE_NEVER_LIT: glDisable(GL_LIGHTING)
		else:
			glLightModeli(GL_LIGHT_MODEL_TWO_SIDE, GL_TRUE)
			glNormal3f(1.0, 0.0, 0.0)
		glColor4fv(self._color)
		glBegin(GL_QUADS)
		glTexCoord2f(0.0, 0.0); glVertex3f(0.0, - self._height, - self._width)
		glTexCoord2f(1.0, 0.0); glVertex3f(0.0,   self._height, - self._width)
		glTexCoord2f(1.0, 1.0); glVertex3f(0.0,   self._height,   self._width)
		glTexCoord2f(0.0, 1.0); glVertex3f(0.0, - self._height,   self._width)
		glEnd()
		glEnable(GL_CULL_FACE)
		if self._option & SPRITE_NEVER_LIT: glEnable(GL_LIGHTING)
		else: glLightModeli(GL_LIGHT_MODEL_TWO_SIDE, GL_FALSE)


cdef class _Bonus(CoordSyst):
	#cdef float _angle
	#cdef float _color[4]
	#cdef _Material _material, _halo
	
	cdef __getcstate__(self):
		#return struct.pack("<ifffffffffffffffffffffff", self._option, self._matrix[0], self._matrix[1], self._matrix[2], self._matrix[3], self._matrix[4], self._matrix[5], self._matrix[6], self._matrix[7], self._matrix[8], self._matrix[9], self._matrix[10], self._matrix[11], self._matrix[12], self._matrix[13], self._matrix[14], self._matrix[15], self._matrix[16], self._matrix[17], self._matrix[18], self._color[0], self._color[1], self._color[2], self._color[3]), self._material
	
		cdef Chunk* chunk
		chunk = get_chunk()
		chunk_add_int_endian_safe   (chunk, self._option)
		chunk_add_floats_endian_safe(chunk, self._matrix, 19)
		chunk_add_floats_endian_safe(chunk, self._color ,  4)
		return drop_chunk_to_string(chunk), self._material, self._halo
	
	cdef void __setcstate__(self, cstate):
		self._validity = COORDSYS_INVALID
		#self._option, self._matrix[0], self._matrix[1], self._matrix[2], self._matrix[3], self._matrix[4], self._matrix[5], self._matrix[6], self._matrix[7], self._matrix[8], self._matrix[9], self._matrix[10], self._matrix[11], self._matrix[12], self._matrix[13], self._matrix[14], self._matrix[15], self._matrix[16], self._matrix[17], self._matrix[18], self._color[0], self._color[1], self._color[2], self._color[3] = struct.unpack("<ifffffffffffffffffffffff", cstate[0])
		#self._material = cstate[1]
	
		cdef Chunk* chunk
		cstate2, self._material, self._halo = cstate
		chunk = string_to_chunk(cstate2)
		chunk_get_int_endian_safe(chunk, &self._option)
		chunk_get_floats_endian_safe(chunk, self._matrix, 19)
		chunk_get_floats_endian_safe(chunk, self._color ,  4)
		drop_chunk(chunk)
		
	property color:
		def __get__(self):
			return self._color[0], self._color[1], self._color[2], self._color[3]
		def __set__(self, x):
			self._color[0], self._color[1], self._color[2], self._color[3] = x
	
	property material:
		def __get__(self):
			return self._material
		def __set__(self, _Material x not None):
			self._material = x
	 
	property halo:
		def __get__(self):
			return self._halo
		def __set__(self, _Material x not None):
			self._halo = x
	 
	property lit:
		def __get__(self):
			return not(self._option & SPRITE_NEVER_LIT)
		def __set__(self, int x):
			if x: self._option = self._option & ~SPRITE_NEVER_LIT
			else: self._option = self._option |  SPRITE_NEVER_LIT
	
	def __init__(self, _World parent = None, _Material material = None, _Material halo = None):
		CoordSyst.__init__(self, parent)
		self._material = material or _DEFAULT_MATERIAL
		self._halo     = halo     or _DEFAULT_MATERIAL
		self._color[0] = self._color[1] = self._color[2] = self._color[3] = 1.0
		
	cdef void _batch(self, CoordSyst coordsyst):
		if self._option & HIDDEN: return
		if not(self._option & BONUS_BATCHED):
			# make the bonus rotate
			self._option = self._option | BONUS_BATCHED
			self._angle = self._angle + 4.0
			if self._angle >= 360.0: self._angle = self._angle - 360.0
		multiply_matrix(self._render_matrix, coordsyst._render_matrix, self._matrix)
		self._frustum_id = -1
		renderer._batch(renderer.alpha, self, self, NULL)
		
	cdef void _render(self, CoordSyst coordsyst):
		cdef float* m
		self._option = self._option & ~BONUS_BATCHED
		glDisable(GL_CULL_FACE)
		if self._option & SPRITE_NEVER_LIT: glDisable(GL_LIGHTING)
		else: glNormal3f(0.0, 0.0, -1.0)
		# draw halo
		#m = self._parent._render_matrix
		#_SPRITE_MATRIX[12] = m[12] + self._matrix[12]
		#_SPRITE_MATRIX[13] = m[13] + self._matrix[13] + 1.0
		#_SPRITE_MATRIX[14] = m[14] + self._matrix[14]
		#glLoadMatrixf(_SPRITE_MATRIX)
		m = self._render_matrix
		_SPRITE_MATRIX[12] = m[12]
		_SPRITE_MATRIX[13] = m[13] + 1.0
		_SPRITE_MATRIX[14] = m[14]
		glLoadMatrixf(_SPRITE_MATRIX)
		
		self._halo._activate()
		glColor4fv(self._color)
		glDisable(GL_LIGHTING)
		glBegin(GL_QUADS)
		glTexCoord2f(0.0, 1.0); glVertex3f(- 1.0, - 1.0, 0.0)
		glTexCoord2f(1.0, 1.0); glVertex3f(- 1.0,   1.0, 0.0)
		glTexCoord2f(1.0, 0.0); glVertex3f(  1.0,   1.0, 0.0)
		glTexCoord2f(0.0, 0.0); glVertex3f(  1.0, - 1.0, 0.0)
		glEnd()
		glEnable(GL_LIGHTING)
		# draw 2D square
		glRotatef(self._angle, 0.0, 1.0, 0.0)
		glLightModeli(GL_LIGHT_MODEL_TWO_SIDE, GL_TRUE)
		self._material._activate()
		glBegin(GL_QUADS)
		glTexCoord2f(0.0, 1.0); glVertex3f(- 0.5, -0.5, 0.0)
		glTexCoord2f(1.0, 1.0); glVertex3f(  0.5, -0.5, 0.0)
		glTexCoord2f(1.0, 0.0); glVertex3f(  0.5,  0.5, 0.0)
		glTexCoord2f(0.0, 0.0); glVertex3f(- 0.5,  0.5, 0.0)
		glEnd()
		glEnable(GL_CULL_FACE)
		glLightModeli(GL_LIGHT_MODEL_TWO_SIDE, GL_FALSE)
		if self._option & SPRITE_NEVER_LIT: glEnable(GL_LIGHTING)
