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

import soya


cdef class _World(_Body):
	
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
	property space:
		def __get__(self):
			return self._space
			
	property has_space:
		def __get__(self):
			return self._space is not None
		def __set__(self,value):#
			print value
			if value  and self._space is None:
				print SimpleSpace(world=self)
				print self._space
			elif self._space is not None:
				raise NotImplementedError("There is currently no way to remove a space from a world")
			
	def __init__(self, _World parent = None, _Model model = None, opt = None):
		self.children = []
		self.ode_children = []
		_Body.__init__(self, parent, model, opt)
		self._space = None
		self._contact_group = _JointGroup()
		
	def __dealloc__(self):
		if self._option & WORLD_HAS_ODE:
			dWorldDestroy(self._OdeWorldID)
			for children in self.ode_children: #XXX add .values some day
				children._option = children._option &~BODY_HAS_ODE
				self.ode_parent = None
		
	cdef __getcstate__(self):
		#ode part
		cdef Chunk* ode_chunk
		cdef dVector3 vector
		if self._option & WORLD_HAS_ODE:
			ode_chunk = get_chunk()
			print "getting vector of %i"%(<int>self._OdeWorldID)
			dWorldGetGravity(self._OdeWorldID, vector)
			print "adding vector (%i,%i,%i)"%(vector[0],vector[1],vector[2])
			#chunk_add_floats_endian_safe(ode_chunk, vector, 3)
			chunk_add_float_endian_safe(ode_chunk, vector[0])
			chunk_add_float_endian_safe(ode_chunk, vector[1])
			chunk_add_float_endian_safe(ode_chunk, vector[2])
			print "adding ERP"
			chunk_add_float_endian_safe(ode_chunk, dWorldGetERP(self._OdeWorldID))
			print "adding CFM"
			chunk_add_float_endian_safe(ode_chunk, dWorldGetCFM(self._OdeWorldID))
			print "adding Auto Disable Flag"
			chunk_add_int_endian_safe(ode_chunk, dWorldGetAutoDisableFlag(self._OdeWorldID))
			print "adding Auto Disable Linear"
			chunk_add_float_endian_safe(ode_chunk, dWorldGetAutoDisableLinearThreshold(self._OdeWorldID))
			print "adding Auto Disable Angular"
			chunk_add_float_endian_safe(ode_chunk, dWorldGetAutoDisableAngularThreshold(self._OdeWorldID))
			print "adding Auto Disable Step"
			chunk_add_int_endian_safe(ode_chunk, dWorldGetAutoDisableSteps(self._OdeWorldID))
			print "adding Auto Disable Time"
			chunk_add_float_endian_safe(ode_chunk, dWorldGetAutoDisableTime(self._OdeWorldID))
			print "adding Num Step"
			chunk_add_int_endian_safe(ode_chunk, dWorldGetQuickStepNumIterations(self._OdeWorldID))
			print "adding Contact Max correcting Vel"
			chunk_add_float_endian_safe(ode_chunk, dWorldGetContactMaxCorrectingVel(self._OdeWorldID))
			print "adding Contact Surface Layer"
			chunk_add_float_endian_safe(ode_chunk, dWorldGetContactSurfaceLayer(self._OdeWorldID))
			ode_info = drop_chunk_to_string(ode_chunk)
		else:
			ode_info = None
		return CoordSyst.__getcstate__(self), self._model, self._filename, self.children, self._atmosphere, self._model_builder, self._data, ode_info, self.ode_children
		
	cdef void __setcstate__(self, cstate):
		cdef Chunk* ode_chunk
		cdef dVector3 vector
		cdef int i
		cdef float f
		cdef dWorldID wid
		self._filename      = cstate[2]
		self.children       = cstate[3]
		self._atmosphere    = cstate[4]
		self._model_builder = cstate[5]
		
		if len(cstate) == 6:
			data = None
		else:
			data = cstate[6]
		_Body.__setcstate__(self, (cstate[0], cstate[1], data))
		if self._option & WORLD_HAS_ODE:
			ode_chunk = string_to_chunk(cstate[7])
			wid = self._OdeWorldID = dWorldCreate()
			vector[0] = 0
			vector[1] = 0
			vector[2] = 56
			chunk_get_float_endian_safe(ode_chunk,&vector[0])
			chunk_get_float_endian_safe(ode_chunk,&vector[1])
			chunk_get_float_endian_safe(ode_chunk,&vector[2])
			#print "f =",f
			#vector[2]=f
			print "out the chunk vector is : (%i,%i,%i)"%(vector[0],vector[1],vector[2])
			dWorldSetGravity (wid, vector[0], vector[1], vector[2])
			chunk_get_float_endian_safe(ode_chunk,&f) #ERP
			dWorldSetERP(wid, f)
			chunk_get_float_endian_safe(ode_chunk,&f) #CFM
			dWorldSetCFM(wid, f)
			chunk_get_int_endian_safe(ode_chunk,&i) #Auto Disable Flag
			dWorldSetAutoDisableFlag(wid, i)
			chunk_get_float_endian_safe(ode_chunk,&f) #Auto Disable Linear Threshold
			dWorldSetAutoDisableLinearThreshold(wid, f)
			chunk_get_float_endian_safe(ode_chunk,&f) #Auto Disable Angular Threshold
			dWorldSetAutoDisableAngularThreshold(wid, f)
			chunk_get_int_endian_safe(ode_chunk,&i) #Auto Disable Step
			dWorldSetAutoDisableSteps(wid, i)
			chunk_get_float_endian_safe(ode_chunk,&f) #Auto Disable Time
			dWorldSetAutoDisableTime(wid, f)
			chunk_get_int_endian_safe(ode_chunk,&i) #Quick Step Num Iterations
			dWorldSetQuickStepNumIterations(wid, i)
			chunk_get_float_endian_safe(ode_chunk,&f) # Contact Max Correction Vel
			dWorldSetContactMaxCorrectingVel(wid, f)
			chunk_get_float_endian_safe(ode_chunk,&f) #Contact Surface layer
			dWorldSetContactSurfaceLayer(wid, f)
			drop_chunk(ode_chunk)
			self.ode_children = cstate[8]
		else:
			self.ode_children = []
		cdef CoordSyst child
		for child in self.children: child._parent = self
	def loaded(self):
		cdef _Body ode_child
		for ode_child in self.ode_children:
			ode_child._reactivate_ode_body(self)
			
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
				if child._contains(obj): return 1
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
		cdef void*       tmp_ptr
		data = get_raypick_data()
		origin   ._out(data.root_data)
		direction._out(&data.root_data[0] + 3)
		vector_normalize(&data.root_data[0] + 3)
		data.root_data[6] = distance
		data.option       = RAYPICK_CULL_FACE * cull_face + RAYPICK_HALF_LINE * half_line
		
		self._raypick(data, None, category)
		if data.result_coordsyst is None: d = NULL
		else:                             d = data.result_coordsyst._raypick_data(data)
		
		cdef int max
		max = data.raypicked.nb
		data.raypicked.nb = 0
		while data.raypicked.nb < max:
			tmp_ptr = chunk_get_ptr(data.raypicked)
			coordsyst = <CoordSyst> tmp_ptr
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
		cdef void*       tmp_ptr
		data = get_raypick_data()
		origin   ._out(data.root_data)
		direction._out(&data.root_data[0] + 3)
		vector_normalize(&data.root_data[0] + 3)
		data.root_data[6] = distance
		data.option       = RAYPICK_CULL_FACE * cull_face + RAYPICK_HALF_LINE * half_line
		
		result = self._raypick_b(data, None, category)
		
		cdef int max
		max = data.raypicked.nb
		data.raypicked.nb = 0
		while data.raypicked.nb < max:
			tmp_ptr = chunk_get_ptr(data.raypicked)
			coordsyst = <CoordSyst> tmp_ptr
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
		cdef object name_attr
		for item in self.children:
			try:
				name_attr = getattr(item, "name")
			except:
				name_attr = ""
			if name_attr == name:
				return item
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
		
		_Body.begin_round(self)
		
		cdef CoordSyst child
		for child in self.children:
			child.begin_round()
		
		if self._space is not None:
			#print "I'm a world, I will call collide"
			self._space.collide()
		if self._option & WORLD_HAS_ODE:
			#print "Gonna Step"
			#print len(self._contact_group), "contacts this round"
			if self._option & WORLD_ODE_USE_QUICKSTEP:
				dWorldQuickStep(self._OdeWorldID, soya.MAIN_LOOP.round_duration)
			else:
				dWorldStep(self._OdeWorldID, soya.MAIN_LOOP.round_duration)
			#print "Have  Step"
			self._contact_group.empty()
			#print "Have Clean"
			
	def end_round(self):
		"""World.end_round()

Called (by the main_loop) when a round is finished; default implementation calls all children's end_round."""
		cdef CoordSyst child
		for child in self.children:
			child.end_round()
		_Body.end_round(self)

		
	def advance_time(self, float proportion):
		"""World.advance_time(proportion)

Called (by the main_loop) when a piece of a round is achieved; default implementation calls all children's advance_time.
PROPORTION is the proportion of the current round's time that has passed (1.0 for an entire round)."""
		cdef CoordSyst child
		
		_Body.advance_time(self, proportion)
		
		
		for child in self.children:
			child.advance_time(proportion)
		
	def to_model(self):
		"""World.to_model() -> Model

Turns the world into a Model (a solid optimized / compiled model).
See World.model_builder and ModelBuilder if you want to customize this process (e.g. for using
trees, cell-shading or shadow)."""
		if self.model_builder is None: return _DEFAULT_MODEL_BUILDER._to_model(self)
		else:                          return self._model_builder   ._to_model(self)
		
		
	### ODE STUFF
	cdef void _activate_ode_world(self):
		if not (self._option & WORLD_HAS_ODE):
			self._OdeWorldID = dWorldCreate()
			self._option = self._option | WORLD_HAS_ODE | WORLD_ODE_USE_QUICKSTEP

	cdef void _deactivate_ode_world(self):
		if self._option & WORLD_HAS_ODE:
			dWorldDestroy(self._OdeWorldID)
			self._option = self._option & ~WORLD_HAS_ODE
			while self.ode_children:
				children = self.ode_children[-1]
				children.geom = None
				children._option = children._option &~BODY_HAS_ODE
				children._ode_parent = None
				self.ode_children.pop(-1)
		
	property odeWorld:
		def __get__(self):
			return self._option & WORLD_HAS_ODE
				
		def __set__(self,value):
			if value:
				self._activate_ode_world()
			else:
				self._deactivate_ode_world()
				
		
	property gravity:
		"""setGravity(gravity)

		Set the world's global gravity vector.

		@param gravity: Gravity vector
		@type gravity: 3-sequence of floats
		"""
		def __set__(self, _Vector gravity):
			cdef float g[3]
			if not (self._option & WORLD_HAS_ODE): self._activate_ode_world()
			gravity._into(self,g)
			dWorldSetGravity(self._OdeWorldID, g[0], g[1], g[2])

		def __get__(self):
			cdef dVector3 g
			if not (self._option & WORLD_HAS_ODE): return None		
			dWorldGetGravity(self._OdeWorldID, g)
			return Vector(self,g[0],g[1],g[2])

	property erp:
		"""setERP(erp)

		Set the global ERP value, that controls how much error
		correction is performed in each time step. Typical values are
		in the range 0.1-0.8. The default is 0.2.

		@param erp: Global ERP value
		@type erp: float
		"""
		def __set__(self, erp):
			if not (self._option & WORLD_HAS_ODE): self._activate_ode_world()
			dWorldSetERP(self._OdeWorldID, erp)

		def __get__(self):
			if not (self._option & WORLD_HAS_ODE): return None
			return dWorldGetERP(self._OdeWorldID)

	property cfm:
		"""setCFM(cfm)

		Set the global CFM (constraint force mixing) value. Typical
		values are in the range 10E-9 - 1. The default is 10E-5 if
		single precision is being used, or 10E-10 if double precision
		is being used.

		@param cfm: Constraint force mixing value
		@type cfm: float
		"""
		def __set__(self, cfm):
			if not (self._option & WORLD_HAS_ODE): self._activate_ode_world()
			dWorldSetCFM(self._OdeWorldID, cfm)

		def __get__(self):
			if not (self._option & WORLD_HAS_ODE): return None
			return dWorldGetCFM(self._OdeWorldID)
	
		
	property use_quickstep:
		"""Choose the use Standard or QuickStep resolution. Default to QuickStep

		QuickStep takes time on the order of m*N and memory on the order of
		m, where m is the total number of constraint rows and N is the number
		of iterations.

		Standard uses a "big matrix" method that takes time on the order of m^3
		and memory on the order of m^2, where m is the total number of
		constraint rows.
		"""
		def __set__(self, use_quickstep):
			if not (self._option & WORLD_HAS_ODE): self._activate_ode_world()
			if use_quickstep:
				self._option = self._option | WORLD_ODE_USE_QUICKSTEP
			else:
				self._option = self._option & ~WORLD_ODE_USE_QUICKSTEP

		def __get__(self):
			if not (self._option & WORLD_HAS_ODE): return None
			return self._option & WORLD_ODE_USE_QUICKSTEP
		
	property quickstep_num_iterations:
		"""setQuickStepNumIterations(num)
		
		Set the number of iterations that the QuickStep method
		performs per step. More iterations will give a more accurate
		solution, but will take longer to compute. The default is 20
		iterations.

		@param num: Number of iterations
		@type num: int
		"""
		def __set__(self, num):
			if not (self._option & WORLD_HAS_ODE): self._activate_ode_world()
			dWorldSetQuickStepNumIterations(self._OdeWorldID, num)
		def __get__(self):
			if not (self._option & WORLD_HAS_ODE): return None
			return dWorldGetQuickStepNumIterations(self._OdeWorldID)

	property contact_max_correcting_velocity:
		"""setContactMaxCorrectingVel(vel)

		Set the maximum correcting velocity that contacts are allowed
		to generate. The default value is infinity (i.e. no
		limit). Reducing this value can help prevent "popping" of
		deeply embedded objects.

		@param vel: Maximum correcting velocity
		@type vel: float
		"""
		def __set__(self, vel):
			if not (self._option & WORLD_HAS_ODE): self._activate_ode_world()
			dWorldSetContactMaxCorrectingVel(self._OdeWorldID, vel)

		def __get__(self):
			if not (self._option & WORLD_HAS_ODE): return None
			return dWorldGetContactMaxCorrectingVel(self._OdeWorldID)

	property contact_surface_layer:
		"""setContactSurfaceLayer(depth)

		Set the depth of the surface layer around all geometry
		objects. Contacts are allowed to sink into the surface layer
		up to the given depth before coming to rest. The default value
		is zero. Increasing this to some small value (e.g. 0.001) can
		help prevent jittering problems due to contacts being
		repeatedly made and broken.

		@param depth: Surface layer depth
		@type depth: float
		"""
		def __set__(self, depth):
			if not (self._option & WORLD_HAS_ODE): self._activate_ode_world()
			dWorldSetContactSurfaceLayer(self._OdeWorldID, depth)

		def __get__(self):
			if not (self._option & WORLD_HAS_ODE): return None
			return dWorldGetContactSurfaceLayer(self._OdeWorldID)

	property auto_disable:
		"""setAutoDisableFlag(flag)
		
		Set the default auto-disable flag for newly created bodies.

		@param flag: True = Do auto disable
		@type flag: bool
		"""
		def __set__(self, flag):
			if not (self._option & WORLD_HAS_ODE): self._activate_ode_world()
			dWorldSetAutoDisableFlag(self._OdeWorldID, flag)
		
		def __get__(self):
			if not (self._option & WORLD_HAS_ODE): return None
			return dWorldGetAutoDisableFlag(self._OdeWorldID)

	property auto_disable_linear_threshold:
		"""setAutoDisableLinearThreshold(threshold)
		
		Set the default auto-disable linear threshold for newly created
		bodies.

		@param threshold: Linear threshold
		@type threshold: float
		"""
		def __set__(self, threshold):
			if not (self._option & WORLD_HAS_ODE): self._activate_ode_world()
			dWorldSetAutoDisableLinearThreshold(self._OdeWorldID, threshold)

		def __get__(self):
			if not (self._option & WORLD_HAS_ODE): return None
			return dWorldGetAutoDisableLinearThreshold(self._OdeWorldID)

	property auto_disable_angular_threshold:
			"""setAutoDisableAngularThreshold(threshold)
			
			Set the default auto-disable angular threshold for newly created
			bodies.

			@param threshold: Angular threshold
			@type threshold: float
			"""
			def __set__(self, threshold):
				if not (self._option & WORLD_HAS_ODE): self._activate_ode_world()
				dWorldSetAutoDisableAngularThreshold(self._OdeWorldID, threshold)


			def __get__(self):
				if not (self._option & WORLD_HAS_ODE): return None
				return dWorldGetAutoDisableAngularThreshold(self._OdeWorldID)


	property auto_disable_steps:
		"""setAutoDisableSteps(steps)
		
		Set the default auto-disable steps for newly created bodies.

		@param steps: Auto disable steps
		@type steps: int
		"""
		def __set__(self, steps):
			if not (self._option & WORLD_HAS_ODE): self._activate_ode_world()
			dWorldSetAutoDisableSteps(self._OdeWorldID, steps)


		def __get__(self):
			if not (self._option & WORLD_HAS_ODE): return None
			return dWorldGetAutoDisableSteps(self._OdeWorldID)


	property auto_disable_time:
			"""setAutoDisableTime(time)
			
			Set the default auto-disable time for newly created bodies.

			@param time: Auto disable time
			@type time: float
			"""
			def __set__(self, time):
				if not (self._option & WORLD_HAS_ODE): self._activate_ode_world()
				dWorldSetAutoDisableTime(self._OdeWorldID, time)

			def __get__(self):
				if not (self._option & WORLD_HAS_ODE): return None
				return dWorldGetAutoDisableTime(self._OdeWorldID)

	# impulseToForce
	def impulse_to_force(self, stepsize, impulse):
			"""impulse_to_force(stepsize, impulse) -> 3-tuple

			If you want to apply a linear or angular impulse to a rigid
			body, instead of a force or a torque, then you can use this
			function to convert the desired impulse into a force/torque
			vector before calling the dBodyAdd... function.

			@param stepsize: Time step
			@param impulse: Impulse vector
			@type stepsize: float
			@type impulse: 3-tuple of floats
			"""
			cdef dVector3 force
			dWorldImpulseToForce(self._OdeWorldID, stepsize, impulse[0], impulse[1], impulse[2], force)
			return (force[0], force[1], force[2])
	
	#cdef _add_space(self):
	#	if self._space is None:
	#		# find the ode_root (or create it is None exist)
	#		way = []
	#		ode_root = self
	#		while not (ode_root._ or ode_root.parent is None):
	#			way.append(ode_root)
	#			ode_root = ode_root.parent
	#		if not ode_root._option & WORLD_HAS_ODE:
	#			ode_root._activate_ode_world()
	#		# create space
	#		way.append(ode_root)
	#		way.revert()
	#		for i in 
	#		if ode_root._space is None:
	#			SimpleSpace(world=ode_root)
	#		previous = ode_root
	#		while previous is not self:
