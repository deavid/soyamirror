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



cdef class _Body(CoordSyst):
	#cdef _Model _model
	#cdef _Model _data
	
	def __init__(self, _World parent = None, _Model model = None, opt = None):
		if not model is None:
			self._model = model
			model._instanced(self, opt)
		CoordSyst.__init__(self, parent)
		
	property model:
		def __get__(self):
			return self._model
		def __set__(self, _Model model):
			self._model = model
			if model is None: self._data = None
			else:             model._instanced(self, None)
			
	def set_model(self, _Model model, opt = None):
		self._model = model
		if model is None: self._data = None
		else:             model._instanced(self, opt)
		
	cdef __getcstate__(self):
		return CoordSyst.__getcstate__(self), self._model, self._data
	
	cdef void __setcstate__(self, cstate):
		CoordSyst.__setcstate__(self, cstate[0])
		self._model = cstate[1]
		if len(cstate) > 2:
			if isinstance(cstate[2], list): # old (Soya < 0.12) Cal3DBody, now loaded as straight Body
				self._data = _AnimatedModelData.__new__(_AnimatedModelData)
				attached_coordsysts = []
				for coordsyst, bone_id in cstate[3]: attached_coordsysts.append((coordsyst, bone_id, 1))
				self._data.__setcstate__((self, self._model, cstate[2], attached_coordsysts))
				
			else: # New (Soya >= 0.12) Body
				self._data = cstate[2]
		if self._data is None: self._data = self._model
		
	cdef void _batch(self, CoordSyst coordsyst):
		#multiply_matrix(self._render_matrix, renderer.current_camera._render_matrix, self._root_matrix())
		multiply_matrix(self._render_matrix, coordsyst._render_matrix, self._matrix)
		self._frustum_id = -1
		#if not self._model is None: self._model._batch(self)
		if not self._data is None: self._data._batch(self)
		
	cdef int _shadow(self, CoordSyst coordsyst, _Light light):
		#if not self._model is None: return self._model._shadow(self, light)
		if not self._data is None: return self._data._shadow(self, light)
		return 0
	
	cdef void _raypick(self, RaypickData raypick_data, CoordSyst raypickable, int category):
		#if (self._data is None) or (self._option & NON_SOLID): return
		if (self._data is None) or not (self._category_bitfield & category): return
		self._data._raypick(raypick_data, self)
		
	cdef int _raypick_b(self, RaypickData raypick_data, CoordSyst raypickable, int category):
		#if (self._data is None) or (self._option & NON_SOLID): return 0
		if (self._data is None) or not (self._category_bitfield & category): return 0
		return self._data._raypick_b(raypick_data, self)
	
	cdef void _collect_raypickables(self, Chunk* items, float* rsphere, float* sphere, int category):
		#if (self._data is None) or (self._option & NON_SOLID): return
		if (self._data is None) or not (self._category_bitfield & category): return
		
		cdef float* matrix
		cdef float  s[4]
		# transform sphere to my coordsys
		# XXX avoid using self._inverted_root_matrix() -- use rather the parent's result (=sphere ?) (faster)
		matrix = self._inverted_root_matrix()
		point_by_matrix_copy(s, rsphere, matrix)
		s[3] = length_by_matrix(rsphere[3], matrix)
		
		#self._model._collect_raypickables(items, rsphere, s, self)
		self._data._collect_raypickables(items, rsphere, s, self)
		
	cdef int _contains(self, _CObj obj):
		if self._model is obj: return 1
		return 0
	
	cdef void _get_box(self, float* box, float* matrix):
		cdef float matrix2[19]
		
		#if not self._model is None:
		if not self._data is None:
			if matrix == NULL: matrix_copy    (matrix2, self._matrix)
			else:              multiply_matrix(matrix2, matrix, self._matrix)
			
			#self._model._get_box(box, matrix2)
			self._data._get_box(box, matrix2)
			
	cdef void _get_sphere(self, float* sphere):
		#if self._model and isinstance(self._model, _SimpleModel) and ((<_SimpleModel> (self._model))._option & MODEL_HAS_SPHERE):
			#memcpy(sphere, (<_SimpleModel> (self._model))._sphere, 4 * sizeof(float))
		if self._data and isinstance(self._data, _SimpleModel) and ((<_SimpleModel> (self._data))._option & MODEL_HAS_SPHERE):
			memcpy(sphere, (<_SimpleModel> (self._data))._sphere, 4 * sizeof(float))
		else:
			sphere[0] = sphere[1] = sphere[2] = sphere[3] = 0.0
			
	def __repr__(self):
		return "<%s, model=%s>" % (self.__class__.__name__, self._model)
	
	def add_deform(self, _Deform deform):
		if not deform._model is None:
			raise ValueError("This Deform object is already used by another Body! Please create a new Deform!")
		
		deform._set_model(self._data)
		self._data = deform
		
	def remove_deform(self, _Deform deform):
		cdef _Model model
		cdef _Deform previous
		
		if self._data is deform:
			self._data = deform._model
		else:
			model    = self._data
			previous = self._data
			while model and isinstance(model, _Deform):
				if model is deform:
					previous._set_model(deform._model)
					break
				
				previous = model
				model = previous._model
			else: raise ValueError("Cannot remove deform: this deform hasn't been added.")
			
		deform._set_model(None)
		
	property deforms:
		def __get__(self):
			deforms = []
			cdef _Model model
			cdef _Deform deform
			
			model = self._data
			while model and isinstance(model, _Deform):
				deform = model
				deforms.insert(0, deform)
				model = deform._model
			return deforms
		
		
		
	def attach(self, *mesh_names):
		"""Body.attach(mesh_name_1, ...)

Only for Body associated with a AnimatedModel.

Attaches new meshes named MESH_NAME_1, ... to the body.
See body.model.meshes to get the list of available mesh names.
Attaching several meshes at the same time can be faster."""
		if self._data: self._data._attach(mesh_names)
		else: raise TypeError("This type of model doesn't support attach!")
		
	def detach(self, *mesh_names):
		"""Cal3DBody.detach(mesh_name_1, ...)

Only for Body associated with a AnimatedModel.

Detaches meshes named MESH_NAME_1, ... to the body.
Detaching several meshes at the same time can be faster."""
		if self._data: self._data._detach(mesh_names)
		else: raise TypeError("This type of model doesn't support detach!")
		
	def is_attached(self, mesh_name):
		"""Cal3DBody.is_attached(mesh_name)

Only for Body associated with a AnimatedModel.

Checks if the mesh called MESH_NAME is attached to the body."""
		if self._data: return self._data._is_attached(mesh_names)
		return 0
		
	def attach_to_bone(self, CoordSyst coordsyst, bone_name):
		"""Cal3DBody.attach_to_bone(coordsyst, bone_name)

Only for Body associated with a AnimatedModel.

Attaches COORDSYST to the bone named BONE_NAME.
As the bone moved (because of animation), COORDSYST will be moved too.
See tutorial character-animation-2.py.

XXX this method should be moved to World.
XXX attaching a coordsyst X to bone of object Y will works well ONLY if Y is a world and X is a direct child of Y!"""
		if self._data: self._data._attach_to_bone(coordsyst, bone_name)
		else: raise TypeError("This type of model doesn't support attach_to_bone!")
		
	def detach_from_bone(self, CoordSyst coordsyst):
		"""Cal3DBody.detach_from_bone(coordsyst)

Only for Body associated with a AnimatedModel.

Detaches COORDSYST from the bone it has been attached to.

XXX this method should be moved to World."""
		if self._data: self._data._detach_from_bone(coordsyst)
		else: raise TypeError("This type of model doesn't support detach_from_bone!")
	
	property attached_meshes:
		def __get__(self):
			if self._data: return self._data._get_attached_meshes()
			return []
		
	property attached_coordsysts:
		def __get__(self):
			if self._data: return self._data._get_attached_coordsysts()
			return []

	def animate_blend_cycle(self, animation_name, float weight = 1.0, float fade_in = 0.2):
		"""Body.animate_blend_cycle(animation_name, weight = 1.0, fade_in = 0.2)

Only for Body associated with a AnimatedModel.

Plays animation ANIMATION_NAME in cycle.
See body.model.animations for the list of available animations.

WEIGHT is the weight of the animation (usefull is several animations are played
simultaneously), and FADE_IN is the time (in second) needed to reach this weight
(in order to avoid a brutal transition).

Notice that the animation will NOT start at its beginning, but at the current global
animation time, which is shared by all cycles (see animate_reset if you want to start
a cycle at its beginning)."""
		if self._data: self._data._animate_blend_cycle(animation_name, weight, fade_in)
		else: raise TypeError("This type of model doesn't support animation!")
			
	def animate_clear_cycle(self, animation_name, float fade_out = 0.2):
		"""Body.animate_clear_cycle(animation_name, fade_out = 0.2)

Only for Body associated with a AnimatedModel.

Stops playing animation ANIMATION_NAME in cycle.
FADE_OUT is the time (in second) needed to stop the animation (in order to avoid
a brutal transition)."""
		if self._data: self._data._animate_clear_cycle(animation_name, fade_out)
		else: raise TypeError("This type of model doesn't support animation!")
		
	def animate_execute_action(self, animation_name, float fade_in = 0.2, float fade_out = 0.2):
		"""Body.animate_execute_action(animation_name, fade_in = 0.2, fade_out = 0.2)

Only for Body associated with a AnimatedModel.

Plays animation ANIMATION_NAME once.
See body.model.animations for the list of available animations.
FADE_IN and FADE_OUT are the time (in second) needed to reach full weight, and to
stop the animation (in order to avoid brutal transitions)."""
		if self._data: self._data._animate_execute_action(animation_name, fade_in, fade_out)
		else: raise TypeError("This type of model doesn't support animation!")

	def animate_reset(self):
		"""Body.animate_reset()

Only for Body associated with a AnimatedModel.

Removes all animations (both cycle and action animation).
It also resets the cycle animation time : i.e. cycles will restart from their beginning."""
		if self._data: self._data._animate_reset()
		else: raise TypeError("This type of model doesn't support animation!")
		
	def set_lod_level(self, float lod_level):
		if self._data: self._data._set_lod_level(lod_level)
		else: raise TypeError("This type of model doesn't support LOD!")
		
	def begin_round(self):
		
		# XXX copied from CoordSyst.begin_round
		
		if (self._option & COORDSYS_NON_AUTO_STATIC) == 0:
			if self._auto_static_count == 0:
				if not (self._option & COORDSYS_STATIC): self._go_static()
			else:
				self._auto_static_count = self._auto_static_count - 1
				
		if self._data: self._data._begin_round()
		
	def advance_time(self, float proportion):
		if self._data: self._data._advance_time(proportion)
