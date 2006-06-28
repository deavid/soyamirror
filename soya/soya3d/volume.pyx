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
	#cdef _Shape     _shape
	#cdef _ModelData _data
	
	def __init__(self, _World parent = None, _Shape shape = None, opt = None):
		if not shape is None:
			self._shape = shape
			shape._instanced(self, opt)
		CoordSyst.__init__(self, parent)
		
	property shape:
		def __get__(self):
			return self._shape
		def __set__(self, _Shape shape):
			self._shape = shape
			if shape is None: self._data = None
			else:             shape._instanced(self, None)
			
	def set_shape(self, _Shape shape, opt = None):
		self._shape = shape
		if shape is None: self._data = None
		else:             shape._instanced(self, opt)
		
	cdef __getcstate__(self):
		return CoordSyst.__getcstate__(self), self._shape, self._data
	
	cdef void __setcstate__(self, cstate):
		CoordSyst.__setcstate__(self, cstate[0])
		self._shape = cstate[1]
		if len(cstate) > 2:
			if isinstance(cstate[2], list): # old (Soya < 0.12) Cal3DVolume, now loaded as straight Volume
				self._data = _AnimatedModelData.__new__(_AnimatedModelData)
				attached_coordsysts = []
				for coordsyst, bone_id in cstate[3]: attached_coordsysts.append((coordsyst, bone_id, 1))
				self._data.__setcstate__((self, self._shape, cstate[2], attached_coordsysts))
				
			else: # New (Soya >= 12) Volume
				self._data = cstate[2]
				
	cdef void _batch(self, CoordSyst coordsyst):
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
	


		
		
	def attach(self, *mesh_names):
		"""Volume.attach(mesh_name_1, ...)

Only for Volume associated with a Cal3dShape.

Attaches new meshes named MESH_NAME_1, ... to the volume.
See volume.shape.meshes to get the list of available mesh names.
Attaching several meshes at the same time can be faster."""
		if self._data: self._data._attach(mesh_names)
		else: raise TypeError("This type of shape doesn't support attach!")
		
	def detach(self, *mesh_names):
		"""Cal3DVolume.detach(mesh_name_1, ...)

Only for Volume associated with a Cal3dShape.

Detaches meshes named MESH_NAME_1, ... to the volume.
Detaching several meshes at the same time can be faster."""
		if self._data: self._data._detach(mesh_names)
		else: raise TypeError("This type of shape doesn't support detach!")
		
	def is_attached(self, mesh_name):
		"""Cal3DVolume.is_attached(mesh_name)

Only for Volume associated with a Cal3dShape.

Checks if the mesh called MESH_NAME is attached to the volume."""
		if self._data: return self._data._is_attached(mesh_names)
		return 0
		
	def attach_to_bone(self, CoordSyst coordsyst, bone_name):
		"""Cal3DVolume.attach_to_bone(coordsyst, bone_name)

Only for Volume associated with a Cal3dShape.

Attaches COORDSYST to the bone named BONE_NAME.
As the bone moved (because of animation), COORDSYST will be moved too.
See tutorial character-animation-2.py.

XXX this method should be moved to World.
XXX attaching a coordsyst X to bone of object Y will works well ONLY if Y is a world and X is a direct child of Y!"""
		if self._data: self._data._attach_to_bone(coordsyst, bone_name)
		else: raise TypeError("This type of shape doesn't support attach_to_bone!")
		
	def detach_from_bone(self, CoordSyst coordsyst):
		"""Cal3DVolume.detach_from_bone(coordsyst)

Only for Volume associated with a Cal3dShape.

Detaches COORDSYST from the bone it has been attached to.

XXX this method should be moved to World."""
		if self._data: self._data._detach_from_bone(coordsyst)
		else: raise TypeError("This type of shape doesn't support detach_from_bone!")
	
	property attached_meshes:
		def __get__(self):
			if self._data: return self._data._get_attached_meshes()
			return []
		
	property attached_coordsysts:
		def __get__(self):
			if self._data: return self._data._get_attached_coordsysts()
			return []

	def animate_blend_cycle(self, animation_name, float weight = 1.0, float fade_in = 0.2):
		"""Volume.animate_blend_cycle(animation_name, weight = 1.0, fade_in = 0.2)

Only for Volume associated with a Cal3dShape.

Plays animation ANIMATION_NAME in cycle.
See volume.shape.animations for the list of available animations.

WEIGHT is the weight of the animation (usefull is several animations are played
simultaneously), and FADE_IN is the time (in second) needed to reach this weight
(in order to avoid a brutal transition).

Notice that the animation will NOT start at its beginning, but at the current global
animation time, which is shared by all cycles (see animate_reset if you want to start
a cycle at its beginning)."""
		if self._data: self._data._animate_blend_cycle(animation_name, weight, fade_in)
		else: raise TypeError("This type of shape doesn't support animation!")
			
	def animate_clear_cycle(self, animation_name, float fade_out = 0.2):
		"""Volume.animate_clear_cycle(animation_name, fade_out = 0.2)

Only for Volume associated with a Cal3dShape.

Stops playing animation ANIMATION_NAME in cycle.
FADE_OUT is the time (in second) needed to stop the animation (in order to avoid
a brutal transition)."""
		if self._data: self._data._animate_clear_cycle(animation_name, fade_out)
		else: raise TypeError("This type of shape doesn't support animation!")
		
	def animate_execute_action(self, animation_name, float fade_in = 0.2, float fade_out = 0.2):
		"""Volume.animate_execute_action(animation_name, fade_in = 0.2, fade_out = 0.2)

Only for Volume associated with a Cal3dShape.

Plays animation ANIMATION_NAME once.
See volume.shape.animations for the list of available animations.
FADE_IN and FADE_OUT are the time (in second) needed to reach full weight, and to
stop the animation (in order to avoid brutal transitions)."""
		if self._data: self._data._animate_execute_action(animation_name, fade_in, fade_out)
		else: raise TypeError("This type of shape doesn't support animation!")

	def animate_reset(self):
		"""Volume.animate_reset()

Only for Volume associated with a Cal3dShape.

Removes all animations (both cycle and action animation).
It also resets the cycle animation time : i.e. cycles will restart from their beginning."""
		if self._data: self._data._animate_reset()
		else: raise TypeError("This type of shape doesn't support animation!")
		
	def set_lod_level(self, float lod_level):
		if self._data: self._data._set_lod_level(lod_level)
		else: raise TypeError("This type of shape doesn't support LOD!")
		
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
