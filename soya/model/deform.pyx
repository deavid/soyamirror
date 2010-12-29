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

cdef class _BaseDeform(_ModelData):
	#cdef _Model _model
	#cdef _Model _data
	#cdef int    _option
	#cdef float  _time
	#cdef float  _time_speed
	
	def __init__(self):
		self._time       = 0.0
		self._time_speed = 1.0
		
	property time:
		def __get__(self):
			return self._time
		def __set__(self, float x):
			self._time = x
			
	cdef _set_model(self, _Model model):
		if model is None:
			self._model = None
			self._data  = None
			
		else:
			self._model = model
			self._data  = model
			
	cdef _Model _create_deformed_data(self): return self._data._create_deformed_data()
	
	cdef void _batch               (self, _Body body):
		if self._model is None: raise ValueError
		self._data._batch (body)
	cdef void _render              (self, _Body body):
		if self._model is None: raise ValueError
		self._data._render(body)
	cdef int  _shadow              (self, CoordSyst coord_syst, _Light light): return self._data._shadow(coord_syst, light)
	cdef void _get_box             (self, float* box, float* matrix): self._data._get_box(box, matrix)
	cdef void _raypick             (self, RaypickData raypick_data, CoordSyst raypickable):        self._data._raypick  (raypick_data, raypickable)
	cdef int  _raypick_b           (self, RaypickData raypick_data, CoordSyst raypickable): return self._data._raypick_b(raypick_data, raypickable)
	cdef void _collect_raypickables(self, Chunk* items, float* rsphere, float* sphere, CoordSyst parent): self._data._collect_raypickables(items, rsphere, sphere, parent)
	
	def __repr__(self):
		return "<%s deforming %s>" % (self.__class__.__name__, self._model)
	
	cdef void _begin_round(self):
		self._model._begin_round()
		
	cdef void _advance_time(self, float proportion):
		self._model._advance_time(proportion)
		
		self._time = self._time + self._time_speed * proportion
		
		
		
		
cdef class _Deform(_BaseDeform):
	cdef _set_model(self, _Model model):
		if model is None:
			self._model = None
			self._data  = None
			
		else:
			self._model = model
			self._data  = model._create_deformed_data()
			
	cdef __getcstate__(self):
		cdef Chunk* chunk
		chunk = get_chunk()
		chunk_add_int_endian_safe  (chunk, self._option)
		chunk_add_float_endian_safe(chunk, self._time)
		chunk_add_float_endian_safe(chunk, self._time_speed)
		return self._model, drop_chunk_to_string(chunk)
	
	cdef void __setcstate__(self, cstate):
		self._set_model(cstate[0])
		cdef Chunk* chunk
		chunk = string_to_chunk(cstate)
		chunk_get_int_endian_safe  (chunk, &self._option)
		chunk_get_float_endian_safe(chunk, &self._time)
		chunk_get_float_endian_safe(chunk, &self._time_speed)
		drop_chunk(chunk)
		
	cdef _deform_points(self, float* coords, float* r, int nb):
		cdef int i
		for i from 0 <= i < nb:
			self._deform_point(coords + 3 * i, r + 3 * i)
			
	cdef _deform_point(self, float* coord, float* r):
		r[0] = coord[0]
		r[1] = coord[1]
		r[2] = coord[2]
		
	cdef void _advance_time(self, float proportion):
		self._model._advance_time(proportion)
		
		self._time = self._time + self._time_speed * proportion
		
		cdef _Model       base
		cdef _BaseDeform  deform
		cdef _SimpleModel simple_model, simple_data
		
		if isinstance(self._model, _BaseDeform):
			deform = self._model
			base = deform._data
		else: base = self._model
		
		if isinstance(base, _SimpleModel):
			simple_model = base
			simple_data  = self._data
			self._deform_points(simple_model._coords, simple_data._coords, simple_model._nb_coords)
			
		else:
			raise ValueError("Cannot deform %s!" % base)
			
			

		
cdef class PythonDeform(_Deform):
	cdef _deform_point(self, float* coord, float* r):
		r[0], r[1], r[2] = self.deform_point(coord[0], coord[1], coord[2])
		
	def deform_point(self, x, y, z):
		return x, y, z



cdef class _ShaderDeform(_BaseDeform):
	#cdef _ShaderProgram _shader
	
	def __init__(self, _ARBShaderProgram shader = None, **kargs):
		"""ShaderDeform(shader_program, local1 = ..., local2 = ..., ...)

Create a Shader deform, based on SHADER_PROGRAM ShaderProgram (vertex of fragment shader).
Additional shader parameters can be set, name "localX" where X is the local shader parameter index.
Remember that by default, parameter 0 is time (and is handled by Soya automatically).
"""
		
		self._shader     = shader
		self._params     = {}
		self._time       = 0.0
		self._time_speed = 1.0
		
		for key, val in kargs.iteritems():
			self._params[int(key[5:])] = val
			
	cdef void _render(self, _Body body):
		if self._model is None: raise ValueError
		self._shader._activate()
		self._shader._set_local_parameter(0, self._time, 0.0, 0.0, 0.0)
		for index, values in self._params.iteritems():
			self._shader.set_local_parameter(index, *values)
		self._data._render(body)
		self._shader._inactivate()
		
	property params:
		def __get__(self):
			return self._params
