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


	
cdef class _World(_Body):
	#cdef readonly         children
	#cdef _Atmosphere      _atmosphere
	#cdef public           _filename
	#cdef ModelBuilder        _model_builder
	
	property model_builder:
		def __get__(self):
			return self._model_builder
		def __set__(self, ModelBuilder arg):
			self._model_builder = arg
			
	property atmosphere:
		def __get__(self):
			return self._atmosphere
		def __set__(self, _Atmosphere atmosphere):
			self._atmosphere = atmosphere
			
	def __init__(self, _World parent = None, _Model model = None, opt = None):
		self.children = []
		_Body.__init__(self, parent, model, opt)
		
	cdef __getcstate__(self):
		return CoordSyst.__getcstate__(self), self._model, self._filename, self.children, self._atmosphere, self._model_builder, self._data
		
	cdef void __setcstate__(self, cstate):
		self._filename      = cstate[2]
		self.children       = cstate[3]
		self._atmosphere    = cstate[4]
		self._model_builder = cstate[5]
		
		if len(cstate) == 6: data = None
		else:                data = cstate[6]
		_Body.__setcstate__(self, (cstate[0], cstate[1], data))
		
		cdef CoordSyst child
		for child in self.children: child._parent = self
		
	def get_root(self):
		cdef _World root
		root = self
		while root._parent: root = root._parent
		return root
	
	cdef _World _get_root(self):
		cdef _World root
		root = self
		while root._parent: root = root._parent
		return root
	
	cdef void _invalidate(self):
		CoordSyst._invalidate(self)
		cdef CoordSyst child
		for child in self.children: child._invalidate()
		
	cdef void _batch(self, CoordSyst coordsyst):
		cdef Context   old_context
		cdef CoordSyst child
		old_context = renderer.current_context
		if self._option & HIDDEN: return
		#multiply_matrix(self._render_matrix, renderer.current_camera._render_matrix, self._root_matrix())
		if not coordsyst is None: multiply_matrix(self._render_matrix, coordsyst._render_matrix, self._matrix)
		self._frustum_id = -1
		# Atmosphere and context
		if not self._atmosphere is None:
			if renderer.root_atmosphere is None:
				renderer.current_context.atmosphere = renderer.root_atmosphere = self._atmosphere
			else:
				if not self._atmosphere is renderer.current_context.atmosphere:
					renderer.current_context = renderer._context()
					renderer.current_context.atmosphere = self._atmosphere
					renderer.current_context.lights.extend(old_context.lights)
		# Batch model
		if not self._model is None: self._model._batch(self)
		# Batch children
		for child in self.children: child._batch(self)
		
		renderer.current_context = old_context
		
	cdef int _shadow(self, CoordSyst coordsyst, _Light light):
		cdef CoordSyst child
		cdef int       result
		result = 0
		if not self._model is None: result = self._model._shadow(self, light)
		for child in self.children: result = result | child._shadow(self, light)
		return result
	
	
	cdef void _raypick(self, RaypickData raypick_data, CoordSyst raypickable, int category):
		cdef CoordSyst child
		#if self._option & NON_SOLID: return
		if not (self._category_bitfield & category): return
		if not self._model is None: self._model._raypick(raypick_data, self)
		for child in self.children: child._raypick(raypick_data, self, category)
		
	cdef int _raypick_b(self, RaypickData raypick_data, CoordSyst raypickable, int category):
		cdef CoordSyst child
		#if self._option & NON_SOLID: return 0
		if not (self._category_bitfield & category): return 0
		if (not self._model is None) and (self._model._raypick_b(raypick_data, self) == 1): return 1
		for child in self.children:
			if child._raypick_b(raypick_data, self, category) == 1: return 1
		return 0
	
	cdef int _contains(self, _CObj obj):
		cdef CoordSyst child
		if isinstance(obj, CoordSyst):
			child = obj
			while child:
				if child is self: return 1
				child = child._parent
		else:
			if self._model is obj: return 1
			for child in self.children:
				if child._contains(model): return 1
		return 0
	
	# XXX TODO (e.g. using sphere_from_spheres)
	#cdef void _get_sphere(self, float* sphere):
	#  sphere[0] = sphere[1] = sphere[2] = sphere[3] = 0.0
		
	cdef void _get_box(self, float* box, float* matrix):
		cdef float matrix2[19]
		if matrix == NULL: matrix_copy    (matrix2, self._matrix)
		else:              multiply_matrix(matrix2, matrix, self._matrix)
		
		if not self._model is None: self._model._get_box(box, matrix2)
			
		cdef CoordSyst child
		for child in self.children: child._get_box(box, matrix2)
		
	def raypick(self, Position origin not None, _Vector direction not None, float distance = -1.0, int half_line = 1, int cull_face = 1, _Point p = None, _Vector v = None, int category = 1):
		"""World.raypick(ORIGIN, DIRECTION, DISTANCE = -1.0, HALF_LINE = 1, CULL_FACE = 1, P = None, V = None, CATEGORY = 1) -> None or (Point, Vector)

Performs a raypicking, i.e. send an invisible ray and returns what the ray hits.
Raypicking is a collision detection method.
Only objects inside the World are taken into account ; raypick on the root World
if you want to raypick on the full scene.

ORIGIN and DIRECTION are a Position and a Vector that defines the ray.

DISTANCE is the maximum length of the ray, if DISTANCE == -1.0 (default value),
there is no length limitation. Shorter DISTANCEs give faster raypicks.

If HALF_LINE is true (default value), the ray starts at ORIGIN and goes toward DIRECTION.
If it is false, the ray is bidirectional : it starts at ORIGIN and goes both toward
DIRECTION and -DIRECTION.

If CULL_FACE is true (default value), non double-sided face are only raypicked on their
visible side. If false, both side are take into account.

P and V are a Point and a Vector that are re-used in the return value, if given (for speed up purpose).
By default, a new Point and a new Vector are created.

CATEGORY is a 32 bit wide bitfield identifying witch categories the methode should take into account (see "solid"  attribute). Only objects witch belong to these categories will be raypicked.

The return value is None if the ray hits nothing, or a (COLLISION, NORMAL) tuple.
COLLISION is a Point located where the collision occured, and COLLISION.parent is the
object hit.
NORMAL is the normal of the object at the impact point.
"""
		cdef RaypickData data
		cdef _World      root
		cdef CoordSyst   coordsyst
		cdef float*      d
		data = get_raypick_data()
		origin   ._out(data.root_data)
		direction._out(data.root_data + 3)
		vector_normalize(data.root_data + 3)
		data.root_data[6] = distance
		data.option       = RAYPICK_CULL_FACE * cull_face + RAYPICK_HALF_LINE * half_line
		
		self._raypick(data, None, category)
		if data.result_coordsyst is None: d = NULL
		else:                             d = data.result_coordsyst._raypick_data(data)
		
		cdef int max
		max = data.raypicked.nb
		data.raypicked.nb = 0
		while data.raypicked.nb < max:
			coordsyst = <CoordSyst> chunk_get_ptr(data.raypicked)
			coordsyst.__raypick_data = -1
		return make_raypick_result(d, data.result, data.normal, data.result_coordsyst, p, v)
	
	def raypick_b(self, Position origin not None, _Vector direction not None, float distance = -1.0, int half_line = 1, int cull_face = 1, int category = 1):
		"""World.raypick_b(ORIGIN, DIRECTION, DISTANCE = -1.0, HALF_LINE = 1, CULL_FACE = 1, CATEGORY = 1) -> bool

Performs a raypicking, i.e. send an invisible ray and returns true if something was hit.
Raypicking is a collision detection method.
This is a simpler but faster version of raypick ; if you want more information about
the collision, see raypick.
Only items inside the World are taken into account ; raypick on the root World
if you want to raypick on the full scene.

ORIGIN and DIRECTION are a Position and a Vector that defines the ray.

DISTANCE is the maximum length of the ray, if DISTANCE == -1.0 (default value),
there is no length limitation. Shorter DISTANCEs give faster raypicks.

If HALF_LINE is true (default value), the ray starts at ORIGIN and goes toward DIRECTION.
If it is false, the ray is bidirectional : it starts at ORIGIN and goes both toward
DIRECTION and -DIRECTION.

If CULL_FACE is true (default value), non double-sided face are only raypicked on their
visible side. If false, both side are take into account.

CATEGORY is a 32 bit wide bitfield identifying witch categories the methode should take into account (see "solid"  attribute). Only objects witch belong to these categories will be raypicked.
"""
		cdef RaypickData data
		cdef _World      root
		cdef CoordSyst   coordsyst
		cdef int         result
		data = get_raypick_data()
		origin   ._out(data.root_data)
		direction._out(data.root_data + 3)
		vector_normalize(data.root_data + 3)
		data.root_data[6] = distance
		data.option       = RAYPICK_CULL_FACE * cull_face + RAYPICK_HALF_LINE * half_line
		
		result = self._raypick_b(data, None, category)
		
		cdef int max
		max = data.raypicked.nb
		data.raypicked.nb = 0
		while data.raypicked.nb < max:
			coordsyst = <CoordSyst> chunk_get_ptr(data.raypicked)
			coordsyst.__raypick_data = -1
		return result
	
	def add(self, CoordSyst child not None):
		"""add(child)

Add a child to this World.

When the World is moved / rotated / scaled, all its children are moved / rotated / scaled
with it.
"""
		if isinstance(child, _World):
			if self.is_inside(child):	raise ValueError("Cyclic addition!")
			
		cdef float* m
		cdef float* p
		if not child._parent is None:
			if child._parent is self: return
			child._matrix_into(self, child._matrix)
			child._invalidate()
			child._parent.remove(child)
		self.children.append(child)
		child._invalidate()
		
		child.added_into(self)
		
	def append(self, CoordSyst child not None):
		"""append(child)

Same as add(child).
"""
		self.add(child)
	
	def __delitem__(self, index):
		self.children.pop(index)._parent = None
		
	def insert(self, int index, CoordSyst child not None):
		"""insert(index, child)

Insert child at INDEX.
"""
		child._parent = self
		self.children.insert(index, child)
		
	def remove(self, CoordSyst child not None):
		"""remove(child)

Remove a child.
"""
		self.children.remove(child)
		child.added_into(None)
		
	def recursive(self):
		"""World.recursive() -> list

Gets a recursive list of all the children elements in a World (=the World
children, + the children of its children and so on)."""
		cdef CoordSyst item
		recursive = self.children[:]
		for item in self.children:
			if isinstance(item, _World): recursive.extend((<_World> item).recursive())
		return recursive
	
	def __iter__(self):
		"""Iterate the children."""
		return iter(self.children)
	#def __contains__(self, item):
	#  return item in self.children
	def __getitem__(self, name):
		cdef CoordSyst item, i
		for item in self.children:
			if getattr(item, "name", "") == name: return item
		for item in self.children:
			if isinstance(item, _World):
				i = item[name]
				if i: return i
				
	def subitem(self, namepath):
		"""World.subitem(namepath) -> CoordSyst

Returns the CoordSyst denoted by NAMEPATH.
NAMEPATH is a string that contains elements' names, separated by ".", such as
"character.head.mouth"."""
		cdef CoordSyst item
		item = self
		for name in namepath.split("."): item = item[name]
		return item
	
	def search(self, predicat):
		"""World.search(predicate) -> CoordSyst

Searches (recursively) in a World for the first element that satisfies PREDICATE.
PREDICATE must be a callable of the form PREDICATE(CoordSyst) -> bool."""
		cdef CoordSyst item
		for item in self.children:
			if predicat(item): return item
			if isinstance(item, _World):
				subresult = item.search(predicat)
				if subresult: return subresult
		return None
	
	def search_name(self, name):
		"""World.search_name(name) -> CoordSyst

Searches (recursively) in a World for the first element named NAME."""
		return self[name]
	
	def search_all(self, predicat):
		"""World.search_all(predicate) -> [CoordSyst, CoordSyst, ...]

Searches (recursively) in a World all elements that satisfy PREDICATE.
PREDICATE must be a callable of the form PREDICATE(CoordSyst) -> bool."""
		result = []
		self._search_all(predicat, result)
		return result
	
	cdef void _search_all(self, predicat, result):
		cdef CoordSyst item
		for item in self.children:
			if predicat(item): result.append(item)
			if isinstance(item, _World): (<_World> (item))._search_all(predicat, result)
			
	def RaypickContext(self, Position center not None, float radius, RaypickContext rc = None, items = None, int category = 1):
		"""RaypickContext(center, radius, rc = None, items = None, category = 1) -> RaypickContext

Creates a RaypickContext. RaypickContext allows to raypick only on a subset of the items
that are inside the World.

The subset of items can be either directly given, using the ITEMS argument (a list of
CoordSyst), or computed as being the list of all items in a sphere. The sphere is defined
by the CENTER and RADIUS arguments.

RC is an optional RaypickContext that will be re-used if given (for speed up purpose).

CATEGORY is a 32 bit wide bitfield identifying witch categories the methode should take into account (see "solid"  attribute). Only objects witch belong to these categories will be listed inside the raypick context.

The returned RaypickContext has raypick and raypick_b method similar to the World's one.
"""
		cdef CoordSyst      coordsys
		cdef _World         root
		cdef float*         coord
		cdef float          sphere[4]
		cdef _CObj          item
		
		root = self._get_root()
		if rc is None: rc = RaypickContext(root)
		else:
			rc._items.nb = 0 # reset the chunk
			rc._root     = root
		center._into(root, sphere)
		sphere[3] = radius

		if items is None:
			self._collect_raypickables(rc._items, sphere, sphere, category)
		else:
			for item in items:
				chunk_add_ptr(rc._items, <void*> item)
				
		return rc
	
	cdef void _collect_raypickables(self, Chunk* items, float* rsphere, float* sphere, int category):
		#if self._option & NON_SOLID: return
		if not (self._category_bitfield & category): return
		
		cdef CoordSyst child
		cdef float* matrix
		cdef float  s[4]
		# transform sphere to my coordsys
		# XXX avoid using self._inverted_root_matrix() -- use rather the parent's result (=sphere ?) (faster)
		matrix = self._inverted_root_matrix()
		point_by_matrix_copy(s, rsphere, matrix)
		s[3] = length_by_matrix(rsphere[3], matrix)
		if not self._model is None: self._model._collect_raypickables(items, rsphere, s, self)
		for child in self.children:
			child._collect_raypickables(items, rsphere, s, category)
			
			
	def begin_round(self):
		"""World.begin_round()

Called (by the main_loop) when a new round begins; default implementation calls all children's begin_round."""
		
		# XXX copied from CoordSyst.begin_round and Body.begin_round
		
		if (self._option & COORDSYS_NON_AUTO_STATIC) == 0:
			if self._auto_static_count == 0:
				if not (self._option & COORDSYS_STATIC): self._go_static()
			else:
				self._auto_static_count = self._auto_static_count - 1
				
		if self._data: self._data._begin_round()
		
		cdef CoordSyst child
		for child in self.children: child.begin_round()
		
	def end_round(self):
		"""World.end_round()

Called (by the main_loop) when a round is finished; default implementation calls all children's end_round."""
		cdef CoordSyst child
		for child in self.children: child.end_round()
		
	def advance_time(self, float proportion):
		"""World.advance_time(proportion)

Called (by the main_loop) when a piece of a round is achieved; default implementation calls all children's advance_time.
PROPORTION is the proportion of the current round's time that has passed (1.0 for an entire round)."""
		cdef CoordSyst child
		
		# XXX copied from Body.begin_round
		
		if self._data: self._data._advance_time(proportion)
		
		for child in self.children: child.advance_time(proportion)
		
	def to_model(self):
		"""World.to_model() -> Model

Turns the world into a Model (a solid optimized / compiled model).
See World.model_builder and ModelBuilder if you want to customize this process (e.g. for using
trees, cell-shading or shadow)."""
		if self.model_builder is None: return _DEFAULT_MODEL_BUILDER._to_model(self)
		else:                      return self._model_builder   ._to_model(self)
