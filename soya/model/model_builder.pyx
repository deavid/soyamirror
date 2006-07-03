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

def _is_static_light(item):
	return isinstance(item, _Light) and item.static


cdef class ModelBuilder(_CObj):
	cdef _Model _to_model(self, _World world):
		pass


cdef class SimpleModelBuilder(ModelBuilder):
	"""SimpleModelBuilder

ModelBuilder for simple / normal / regular Model. The SimpleModelBuilder attributes allows to
customize the World -> Model computation.

Attributes are :

 - shadow (default 0) : enable shadows

 - max_face_angle (default 80.0) : if the angle (in degree) between 2 faces is less than
	 this value, vertices of the two faces can be merged if they are enough close. Set it
	 to 180.0 or more to disable this feature."""
	#cdef int   _shadow
	#cdef float _max_face_angle
	
	property shadow:
		def __get__(self):
			return self._shadow
		def __set__(self, int x):
			self._shadow = x
			
	property max_face_angle:
		def __get__(self):
			return self._max_face_angle
		def __set__(self, float x):
			self._max_face_angle = x
			
	def __init__(self, int shadow = 0, float max_face_angle = 80.0):
		"""SimpleModelBuilder(**attributes) -> SimpleModelBuilder

See SimpleModelBuilder.__doc__ for more info."""
		self._shadow         = shadow
		self._max_face_angle = max_face_angle
		
	cdef __getcstate__(self):
		return self._shadow, self._max_face_angle
	
	cdef void __setcstate__(self, cstate):
		self._shadow, self._max_face_angle = cstate
		
	cdef _Model _to_model(self, _World world):
		cdef _SimpleModel model
		cdef int          option
		cdef              ligths
		option = 0
		if self._shadow: option = option | MODEL_PLANE_EQUATION | MODEL_SIMPLE_NEIGHBORS | MODEL_SHADOW
		model = SimpleModel(world, self._max_face_angle, option, world.search_all(_is_static_light))
		model._build_sphere()
		model._build_display_list()
		return model

	
cdef class SolidModelBuilder(SimpleModelBuilder):
	"""SolidModelBuilder
"""
	cdef _Model _to_model(self, _World world):
		cdef _SolidModel model
		cdef int         option
		cdef             ligths
		option = 0
		if self._shadow: option = option | MODEL_PLANE_EQUATION | MODEL_SIMPLE_NEIGHBORS | MODEL_SHADOW
		model = SolidModel(world, self._max_face_angle, option, world.search_all(_is_static_light))
		model._build_sphere()
		model._build_display_list()
		return model
	
	
cdef class TreeModelBuilder(SimpleModelBuilder):
	"""TreeModelBuilder

ModelBuilder for tree-based Model. Yields a TreeModel instead of a SimpleModel.
TreeModel are optimized for big model with lots of faces, espescially if all the faces
are not visible at the same time (e.g. a game level). Both rendering and raypicking
are optimized.
Internally, the model is broken down into several hierarchinal nodes, each node grouping
close faces.

Attributes are :

 - shadow (default 0) : NOT IMPLEMENTED YET for tree

 - collapsing_distance (default 0.9) : this parameter tunes how many nodes are created.
	 If a child node's radius > parent node's radius X collapsing_distance, the child
	 and parent nodes are merged.

 - quality (default 0) : set to 1 to compute a slower but slightly more performant tree.

 - max_child_radius (default 0.5) : the maximum children node's radius, expressed in ratio
	 of the parent node's radius. Meaningfull only when quality == 0"""
	#cdef float _collapsing_distance
	#cdef int   _quality
	#cdef float _max_child_radius
	
	property collapsing_distance:
		def __get__(self):
			return self._collapsing_distance
		def __set__(self, float x):
			self._collapsing_distance = x
			
	property quality:
		def __get__(self):
			return self._quality
		def __set__(self, int x):
			self._quality = x
	
	property max_child_radius:
		def __get__(self):
			return self._max_child_radius
		def __set__(self, float x):
			self._max_child_radius = x
			
	def __init__(self, int shadow = 0, float max_face_angle = 200.0, float collapsing_distance = 0.9, int quality = 0, float max_child_radius = 0.5):
		"""TreeModelBuilder(**attributes) -> TreeModelBuilder

See TreeModelBuilder.__doc__ for more info."""
		SimpleModelBuilder.__init__(self, shadow, max_face_angle)
		self._collapsing_distance = collapsing_distance
		self._quality             = quality
		self._max_child_radius    = max_child_radius
		
	cdef __getcstate__(self):
		return self._shadow, self._max_face_angle, self._collapsing_distance, self._quality, self._max_child_radius
	
	cdef void __setcstate__(self, cstate):
		self._shadow, self._max_face_angle, self._collapsing_distance, self._quality, self._max_child_radius = cstate
		
	cdef _Model _to_model(self, _World world):
		cdef _TreeModel model
		cdef int        option
		option = 0
		if self._shadow: option = option | MODEL_PLANE_EQUATION | MODEL_SIMPLE_NEIGHBORS | MODEL_SHADOW
		model = TreeModel(world, self._max_face_angle, option, world.search_all(_is_static_light))
		model._build_tree()
		model._optimize_tree(self._collapsing_distance, self._quality, self._max_child_radius)
		return model
	
		
cdef class CellShadingModelBuilder(SimpleModelBuilder):
	"""CellShadingModelBuilder

ModelBuilder for cell-shaded Model.

Attributes are :

 - shadow (default 0) : enable shadows

 - shader : the material used for cell-shading lighting

 - outline_color (default black) : the color of the outline

 - outline_width (default 4.0) : the maximum line width when the cell-shaded model
	 is very near the camera (set to 0.0 to disable outlines)

 - outline_attenuation (default : 0.3) : specify how much the distance affect the
	 outline_width
"""
	
	#cdef _Material _shader
	#cdef           _outline_color
	#cdef float     _outline_width, _outline_attenuation
	
	property shader:
		def __get__(self):
			return self._shader
		def __set__(self, _Material x):
			self._shader = x
			
	property outline_color:
		def __get__(self):
			return self._outline_color
		def __set__(self, x):
			self._outline_color = x
			
	property outline_width:
		def __get__(self):
			return self._outline_width
		def __set__(self, float x):
			self._outline_width = x
			
	property outline_attenuation:
		def __get__(self):
			return self._outline_attenuation
		def __set__(self, float x):
			self._outline_attenuation = x
			
	def __init__(self, int shadow = 0, float max_face_angle = 80.0, _Material shader = None, outline_color = BLACK, float outline_width = 4.0, float outline_attenuation = 0.3):
		"""CellShadingModelBuilder(**attributes) -> CellShadingModelBuilder

See CellShadingModelBuilder.__doc__ for more info."""
		SimpleModelBuilder.__init__(self, shadow, max_face_angle)
		self._shader              = shader or _SHADER_DEFAULT_MATERIAL
		self._outline_color       = outline_color
		self._outline_width       = outline_width
		self._outline_attenuation = outline_attenuation
		
	cdef __getcstate__(self):
		return self._shadow, self._max_face_angle, self._shader, self._outline_color, self._outline_width, self._outline_attenuation
	
	cdef void __setcstate__(self, cstate):
		self._shadow, self._max_face_angle, self._shader, self._outline_color, self._outline_width, self._outline_attenuation = cstate
		
	cdef _Model _to_model(self, _World world):
		cdef _CellShadingModel model
		cdef int               option
		option = 0
		if self._shadow: option = option | MODEL_PLANE_EQUATION | MODEL_SIMPLE_NEIGHBORS | MODEL_SHADOW
		model = CellShadingModel(world, self._max_face_angle, option | MODEL_PLANE_EQUATION | MODEL_NEIGHBORS | MODEL_CELLSHADING, world.search_all(_is_static_light))
		model._build_sphere()
		model._build_cellshading(self._shader, self._outline_color, self._outline_width, self._outline_attenuation)
		model._build_display_list()
		return model
		
	
cdef ModelBuilder _DEFAULT_MODEL_BUILDER
_DEFAULT_MODEL_BUILDER = SimpleModelBuilder()
def _set_default_model_builder(ModelBuilder model_builder):
	global _DEFAULT_MODEL_BUILDER
	_DEFAULT_MODEL_BUILDER = model_builder
	

