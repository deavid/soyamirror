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


# author:
#	edited by Marmoute - Pierre-Yves David - marmoute@nekeme.net

#<<< Greg Ewing, Oct 2007: Turning debug messages on and off

cdef int debug_body_reactivate
cdef int debug_body_cm

debug_body_reactivate = 0
debug_body_cm = 0

def set_debug_body_reactivate(int value):
	global debug_body_reactivate
	debug_body_reactivate = value

def set_debug_body_cm(int value):
	global debug_body_cm
	debug_body_cm = value

#>>>

cdef class _Body(CoordSyst):
	#cdef _Model _model
	#cdef _Model _data
	
	def __init__(self, _World parent = None, _Model model = None, opt = None,_Mass mass=None):
		if not model is None:
			self._model = model
			model._instanced(self, opt)
		self._ode_parent = None
		self.__ode_data = None
		self.joints = []
		self._option = self._option | BODY_PUSHABLE
		CoordSyst.__init__(self, parent)
		if mass is not None:
			self.mass = mass
		
	def __del__(self):
		if self._option & BODY_HAS_ODE:
			self._option = self._option & ~ BODY_HAS_ODE
			dBodyDestroy(self._OdeBodyID)
		
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
		cdef Chunk* ode_chunk
		cdef dVector3 vector
		cdef dQuaternion q
		cdef dMass    mass
		cdef dBodyID  bid
		cdef dReal *  v
		ode_data = None
		if self._option & BODY_HAS_ODE:
			bid = self._OdeBodyID
			ode_chunk = get_chunk()
			# pos            vector (3)   # XXX ignored for the moment
			# quaternion     quaternion   # XXX use a self-relativ cordinate later
			# linear speed   vector (3)   # XXX idem
			v = <dReal*> dBodyGetLinearVel(bid) # Cast for const correction
			vector_by_matrix(vector, self._ode_parent._root_matrix())
			vector_by_matrix(vector, self._inverted_root_matrix())
			chunk_add_floats_endian_safe(ode_chunk,v,3)
			# angular speed  vector (3)   # XXX idem
			v = <dReal*> dBodyGetAngularVel(bid) # Cast for const correction
			vector_by_matrix(v, self._ode_parent._root_matrix())
			vector_by_matrix(v, self._inverted_root_matrix())
			chunk_add_floats_endian_safe(ode_chunk,v,3)
			chunk_add_int_endian_safe(ode_chunk, dBodyGetAutoDisableFlag(self._OdeBodyID))
			chunk_add_float_endian_safe(ode_chunk, dBodyGetAutoDisableLinearThreshold(self._OdeBodyID))
			chunk_add_float_endian_safe(ode_chunk, dBodyGetAutoDisableAngularThreshold(self._OdeBodyID))
			chunk_add_int_endian_safe(ode_chunk, dBodyGetAutoDisableSteps(self._OdeBodyID))
			chunk_add_float_endian_safe(ode_chunk, dBodyGetAutoDisableTime(self._OdeBodyID))
			# getting mass
			dBodyGetMass(self._OdeBodyID, &mass); 
			chunk_add_float_endian_safe(ode_chunk,mass.mass)
			chunk_add_floats_endian_safe(ode_chunk,mass.c,4)
			chunk_add_floats_endian_safe(ode_chunk,mass.I,12)
			ode_data = drop_chunk_to_string(ode_chunk)
			
		return CoordSyst.__getcstate__(self), self._model, self._data, ode_data, self.joints
	
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
			if len(cstate)>=4:
				if self._option & BODY_HAS_ODE:
					self.__ode_data = cstate[3]
					self.joints = cstate[4]
					#self._option & BODY_HAS_ODE
					self._option = self._option & ~BODY_HAS_ODE
				else:
					self.__ode_data = None
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
		
	cdef void _activate_ode_body(_Body self):
		if self.parent is None:
			raise ValueError("Orphan Body can't be ODE managed, it must ba added to a world first")
		self._activate_ode_body_with(self.parent)
	cdef void _activate_ode_body_with(_Body self,_World world):	
		assert world is not None
		if not self._option & BODY_HAS_ODE:
			world = _find_or_create_most_probable_ode_parent_from(world)
			self._OdeBodyID = dBodyCreate(world._OdeWorldID)
			dBodySetData(self._OdeBodyID,<void*> self) 
			self._option = self._option | BODY_HAS_ODE + BODY_ODE_INVALIDE_POS
			self._ode_parent = world
			world.ode_children.append(self)
	cdef void _reactivate_ode_body(_Body self,_World world):
		cdef Chunk * ode_chunk
		cdef int i
		cdef float f
		cdef dVector3 v
		cdef dBodyID bid
		cdef dMass   mass
		
		if debug_body_reactivate:
			print "Reactivated"
		
		if not (world._option & WORLD_HAS_ODE):
			raise TypeError("cant reactive on %s, %s is not and Ode Manager"%(self,world))
		bid = self._OdeBodyID = dBodyCreate(world._OdeWorldID)
		dBodySetData(self._OdeBodyID,<void*> self) 
		self._option = self._option | BODY_HAS_ODE + BODY_ODE_INVALIDE_POS
		self._ode_parent = world
		if self.__ode_data is None:
			raise ValueError("there is no ode_data stored")
		
		ode_chunk = string_to_chunk(self.__ode_data)
		# Auto Disable Flag
		chunk_get_floats_endian_safe(ode_chunk,v,3)
		vector_by_matrix(v, self._root_matrix())
		vector_by_matrix(v, self._ode_parent._inverted_root_matrix())
		dBodySetLinearVel(bid,v[0],v[1],v[2])
		chunk_get_floats_endian_safe(ode_chunk,v,3)
		vector_by_matrix(v, self._root_matrix())
		vector_by_matrix(v, self._ode_parent._inverted_root_matrix())
		dBodySetAngularVel(bid,v[0],v[1],v[2])
		chunk_get_int_endian_safe(ode_chunk,&i) #Auto Disable Flag
		dBodySetAutoDisableFlag(bid, i)
		chunk_get_float_endian_safe(ode_chunk,&f) #Auto Disable Linear Threshold
		dBodySetAutoDisableLinearThreshold(bid, f)
		chunk_get_float_endian_safe(ode_chunk,&f) #Auto Disable Angular Threshold
		dBodySetAutoDisableAngularThreshold(bid, f)
		chunk_get_int_endian_safe(ode_chunk,&i) #Auto Disable Step
		dBodySetAutoDisableSteps(bid, i)
		chunk_get_float_endian_safe(ode_chunk,&f) #Auto Disable Time
		dBodySetAutoDisableTime(bid, f)
		#mass
		chunk_get_float_endian_safe(ode_chunk,&mass.mass)
		chunk_get_floats_endian_safe(ode_chunk,mass.c,4)
		chunk_get_floats_endian_safe(ode_chunk,mass.I,12)
		dBodySetMass(self._OdeBodyID,&mass)
		drop_chunk(ode_chunk)
		
		
		
		self.__ode_data = None
			
		# Wake the joints up.
			
	cdef void _deactivate_ode_body(self):
		if self._option & BODY_HAS_ODE:
			dBodyDestroy(self._OdeBodyID)
			self._option = self._option &~BODY_HAS_ODE
			del self.ode_parent.ode_children[self]
			self._ode_parent = None
		else:
			raise RuntimeWarning("trying to Disable ODE support on a Body which is not ODE managed")
	cdef _World _find_or_create_most_probable_ode_parent(self):
		return self._find_or_create_most_probable_ode_parent_from(self._parent)
	
	property ode:
		def __get__(self):
			return self._option & BODY_HAS_ODE
		def __set__(self,mode):
			if mode:
				self._activate_ode_body()
			else:
				self._deactivate_ode_body()
	property pushable:
		def __get__(self):
				return self._option & BODY_PUSHABLE
		def __set__(self, value):
			if value:
				self._option = self._option | BODY_PUSHABLE
			else:
				self._option = self._option & ~BODY_PUSHABLE
			
	property ode_parent:
		def __get__(self):
			return self._ode_parent
		def __set__(self,_World ode_parent):
			if not self._option & BODY_HAS_ODE:
				if ode_parent is None:
					self._ode_parent = None
				else:
					if not ode_parent & WORLD_HAS_ODE:
						ode_parent._activate_ode_world()
					self._activate_ode_body_with(ode_parent)
			else:
				raise RuntimeError("Unable to reassign a new ODE parent")
	property geom:
		def __get__(self):
			return self._geom
		def __set__(self, _PlaceableGeom geom):
			if geom is not self._geom:
				old_geom = self._geom
				self._geom = geom
				if old_geom is not None:
					old_geom.body = None
				if geom is not None:
					if geom._body is not self:
						geom.body = self
		def __del__(self):
			self.geom=None
	def added_into(self, _World new_parent):
		CoordSyst.added_into(self,new_parent)
		if self._geom is not None:
			if self._parent is not None:
				if self._parent.space is None:
					type(self._geom._space)(self._parent)
				self._geom.space = self._parent.space
			else:
				self._geom.space = None
			
						
	cdef void _sync_ode_position(self):
		# Greg Ewing, March 2007 (greg.ewing@canterbury.ac.nz)
		# multiply_matrix was being passed an uninitialised pointer
		cdef GLfloat ma[19]
		cdef GLfloat *m
		cdef dMatrix3  R
		cdef dReal * q
		cdef GLfloat ode_pos[3] # Greg Ewing, Oct 2007 - Arbitrary centre of mass support
		
		if self.parent is self.ode_parent:
			m = self._matrix
		else:
			m = ma
			multiply_matrix(m, self._ode_parent._inverted_root_matrix(), self._root_matrix())
		R[0]  = m[0]
		R[1]  = m[4]
		R[2]  = m[8]
		R[3]  = 0.0
		R[4]  = m[1]
		R[5]  = m[5]
		R[6]  = m[9]
		R[7]  = 0.0
		R[8]  = m[2]
		R[9]  = m[6]
		R[10] = m[10]
		R[11] = 0.0

		# XXX Overriding the movement methods would be faster due to the fact
		# that we wouldn't have to copy the rotation matrix as well
		#<<< Greg Ewing, Oct 2007 - Arbitrary centre of mass support
		#dBodySetPosition(self._OdeBodyID, m[12], m[13], m[14])
		point_by_matrix_copy(ode_pos, self._cm, m)
		if debug_body_cm:
			print "Soya (%10g %10g %10g) + cm (%10g %10g %10g) --> ODE (%10g %10g %10g) + cm = (%10g %10g %10g)" % (
				self._matrix[12], self._matrix[13], self._matrix[14],
				self._cm[0], self._cm[1], self._cm[2],
				m[12], m[13], m[14],
				ode_pos[0], ode_pos[1], ode_pos[2])
		dBodySetPosition(self._OdeBodyID, ode_pos[0], ode_pos[1], ode_pos[2])
		#>>>
		dBodySetRotation(self._OdeBodyID, R)
		
		q = <dReal*> dBodyGetQuaternion(self._OdeBodyID) # Cast for const correction
		self._q[0] = q[1]
		self._q[1] = q[2]
		self._q[2] = q[3]
		self._q[3] = q[0]

		q = <dReal*> dBodyGetPosition(self._OdeBodyID) # Cast for const correction
		self._p[0] = q[0]
		self._p[1] = q[1]
		self._p[2] = q[2]
		

		# Mark the previous position and quaternion as valide
		self._option = self._option & ~BODY_ODE_INVALIDE_POS
		CoordSyst._invalidate(self)
			
	cdef void _invalidate(self):
		"""Set the ODE position as invalide after after invalidating the root and inverted
		root matrices. We do this here because all movement methods must
		call this."""
		CoordSyst._invalidate(self)
		self._option = self._option | BODY_ODE_INVALIDE_POS
	def begin_round(self):
		cdef dReal * q
		if self._option & BODY_HAS_ODE:
			self._t = 0
			if self._option & BODY_ODE_INVALIDE_POS:
				self._sync_ode_position()
			q = <dReal*> dBodyGetQuaternion(self._OdeBodyID) # Cast for const correction
			self._q[0] = q[1]
			self._q[1] = q[2]
			self._q[2] = q[3]
			self._q[3] = q[0]
	
			q = <dReal*> dBodyGetPosition(self._OdeBodyID) # Cast for const correction
			self._p[0] = q[0]
			self._p[1] = q[1]
			self._p[2] = q[2]

			
			
		#deformation stuff
		if (self._option & COORDSYS_NON_AUTO_STATIC) == 0:
			if self._auto_static_count == 0:
				if not (self._option & COORDSYS_STATIC): self._go_static()
			else:
				self._auto_static_count = self._auto_static_count - 1
				
		if self._data: self._data._begin_round()
		
		
		
	def advance_time(self, float proportion):
		"""Interpolate between the last two quaternions"""
		cdef GLfloat q[4]
		cdef dReal *r, *p
		cdef float t
		cdef float next_pos[19]
		cdef float tmp_pos[19]
		cdef float zoom[3]
		cdef GLfloat cm[3] # Greg Ewing, Oct 2007

		self._t = self._t + proportion
		if self._option & BODY_HAS_ODE: 
			if dBodyIsEnabled(self._OdeBodyID):
				if (self._option & BODY_ODE_INVALIDE_POS):
					self._sync_ode_position()
				else:
					#saving the scale of the object
					#XXX optimisable
					memcpy(&zoom[0],&self._matrix[16],3*sizeof(float))
					r = <dReal*> dBodyGetQuaternion(self._OdeBodyID) # Cast for const correction
					p = <dReal*> dBodyGetPosition(self._OdeBodyID) # Cast for const correction
					t = 1.0 - self._t
		
					# Linearly interpolate between the current quaternion and the last
					# one
					q[0] = t * self._q[0] + self._t * r[1]
					q[1] = t * self._q[1] + self._t * r[2]
					q[2] = t * self._q[2] + self._t * r[3]
					q[3] = t * self._q[3] + self._t * r[0]
				
					# Convert the quaternion to a matrix (also normalizes)
					matrix_from_quaternion(next_pos, q)
					#matrix_from_quaternion(self._matrix, q)
					
					# Interpolate the position, too
			
					
					next_pos[12] = t * self._p[0] + self._t * p[0]
					next_pos[13] = t * self._p[1] + self._t * p[1]
					next_pos[14] = t * self._p[2] + self._t * p[2]
					#self._matrix[12] = t * self._p[0] + self._t * p[0]
					#self._matrix[13] = t * self._p[1] + self._t * p[1]
					#self._matrix[14] = t * self._p[2] + self._t * p[2]
					
					
					# convert to the right CoordSyst
					if self.parent is not self.ode_parent:
						multiply_matrix(tmp_pos,self._ode_parent._root_matrix(),next_pos)
						multiply_matrix(self._matrix,self._parent._inverted_root_matrix(),tmp_pos)
					else:
						matrix_copy(self._matrix,next_pos)
					#<<< Greg Ewing, Oct 2007 - Arbitrary centre of mass support
					# Subtract centre of mass from position in parent coords
					vector_by_matrix_copy(cm, self._cm, self._matrix)
					self._matrix[12] = self._matrix[12] - cm[0]
					self._matrix[13] = self._matrix[13] - cm[1]
					self._matrix[14] = self._matrix[14] - cm[2]
					if debug_body_cm:
						print "Soya (%10g %10g %10g) + cm (%10g %10g %10g) <-- ODE (%10g %10g %10g)" % (
							self._matrix[12], self._matrix[13], self._matrix[14],
							cm[0], cm[1], cm[2],
							next_pos[12], next_pos[13], next_pos[14])
					#>>>
					
					matrix_scale(self._matrix,zoom[0],zoom[1],zoom[2])
					#memcpy(&self._matrix[16],zoom,3*sizeof(float))
					# Call _soya._World's _invalidate since we override _invalidate
					# to detect when the position is updated externally
					CoordSyst._invalidate(self)
	
			# Make sure advance_time is called on all our children
			CoordSyst.advance_time(self, proportion)


		#deformation stuff
		if self._data: self._data._advance_time(proportion)
			
	property linear_velocity:
		def __set__(self,_Vector vel):
			cdef float v[3]
			if not (self._option & BODY_HAS_ODE): self._activate_ode_body()
			if vel is None:
				dBodySetLinearVel(self._OdeBodyID, 0, 0, 0)
			else:
				vel._into(self._ode_parent, v)
				dBodySetLinearVel(self._OdeBodyID, v[0], v[1], v[2])


		def __get__(self):
			cdef dReal* p
			if not (self._option & BODY_HAS_ODE): return None
			p = <dReal*>dBodyGetLinearVel(self._OdeBodyID)
			return Vector(self._ode_parent,p[0], p[1], p[2])

	property angular_velocity:
		def __set__(self, _Vector vel):
			"""setAngularVel(vel)

			Set the angular velocity of the body.
	
			@param vel: New angular velocity
			@type vel: Vector
			"""
			cdef float v[3]
			if not (self._option & BODY_HAS_ODE):
				self._activate_ode_body()
			if vel is None:
				dBodySetAngularVel(self._OdeBodyID, 0, 0, 0)
			else:
				vel._into(self._ode_parent, v)
				dBodySetAngularVel(self._OdeBodyID, v[0], v[1], v[2])

		def __get__(self):
			"""getAngularVel() -> 3-tuple

			Get the current angular velocity of the body.
			"""
			cdef dReal* p
			if not (self._option & BODY_HAS_ODE): return None
			
			# The "const" in the original return value is cast away
			p = <dReal*>dBodyGetAngularVel(self._OdeBodyID)
			return Vector(self._ode_parent,p[0],p[1],p[2])
	
	property mass:
		def __set__(self, _Mass mass):
			"""setMass(mass)
	
			Set the mass properties of the body. The argument mass must be
			an instance of a Mass object.
	
			@param mass: Mass properties
			@type mass: Mass
			"""
			cdef dMass ode_mass # Greg Ewing, Oct 2007 - Arbitrary centre of mass support

			if not (self._option & BODY_HAS_ODE): self._activate_ode_body()
			
			#<<< Greg Ewing, Oct 2007 - Arbitrary centre of mass support
			#dBodySetMass(self._OdeBodyID, &mass._mass)
			ode_mass = mass._mass
			self._cm[0] = ode_mass.c[0]
			self._cm[1] = ode_mass.c[1]
			self._cm[2] = ode_mass.c[2]
			ode_mass.c[0] = 0
			ode_mass.c[1] = 0
			ode_mass.c[2] = 0
			dBodySetMass(self._OdeBodyID, &ode_mass)
			self._invalidate()
			#>>>
	
		def __get__(self):
			"""getMass() -> mass
	
			Return the mass properties as a Mass object.
			"""
			if not (self._option & BODY_HAS_ODE): return None
			cdef _Mass m
			m=Mass()
			dBodyGetMass(self._OdeBodyID, &m._mass)
			#<<< Greg Ewing, Oct 2007 - Arbitrary centre of mass support
			m._mass.c[0] = self._cm[0]
			m._mass.c[1] = self._cm[1]
			m._mass.c[2] = self._cm[2]
			#>>>
			return m

	# addForce
	def add_force(self,_Vector force,_Point pos=None):
		cdef float f[3]
		cdef float p[3]
		if not (self._option & BODY_HAS_ODE): self._activate_ode_body()
		force._into(self._ode_parent, f)
		if pos is None:
			dBodyAddForce(self._OdeBodyID, f[0], f[1], f[2])
		else:
			pos._into(self.ode_parent,p)
			dBodyAddForceAtPos(self._OdeBodyID,f[0],f[1],f[2],p[0],p[1],p[2])
	#def add_force_xyz(self, int x, int y, int z,int px=0, int py=0, int pz=0):
	#	if not (self._option & BODY_HAS_ODE):
	#		self._activate_ode_body()
	#	if px or py or pz:
	#		dBodyAddRelForceAtRelPos(self._OdeBodyID,x,y,z,px,py,pz)
	#	else:
	#		dBodyAddRelForce(self._OdeBodyID,x,y,z)
		
	# addTorque
	def add_torque(self,_Vector torque,_Point pos=None):
		"""addTorque(t)

		Add an external torque t given in absolute coordinates.

		@param t: Torque
		@type t: 3-sequence of floats
		"""
		cdef float t[3]
		cdef float p[3]
		if not (self._option & BODY_HAS_ODE): self._activate_ode_body()
		
		torque._into(self._ode_parent, t)
		if pos is None:
			dBodyAddTorque(self._OdeBodyID, t[0], t[1], t[2])
		else:
			pos._into(self.ode_parent,p)
			dBodyAddTorqueAtPos(t[0],t[1],t[2],p[0],p[1],p[2])

		#dBodyAddTorque(self._OdeBodyID, t[0], t[1], t[2])

	

	property force:
		# getForce
		def __get__(self):
			"""getForce() -> 3-tuple
	
			Return the current accumulated force.
			"""
			cdef dReal* f
			if not (self._option & BODY_HAS_ODE): return None
			# The "const" in the original return value is cast away
			f = <dReal*>dBodyGetForce(self._OdeBodyID)
			return Vector(self._ode_parent,f[0],f[1],f[2])
	
			
		# setForce
		def __set__(self,_Vector force):
			"""setForce(f)
	
			Set the body force accumulation vector.
	
			@param f: Force
			@type f: 3-tuple of floats
			"""
			cdef float f[3]
			if not (self._option & BODY_HAS_ODE):
				self._activate_ode_body()
			if force is None:
				dBodySetForce(self._OdeBodyID, 0, 0, 0)
			else:
				force._into(self._ode_parent, f)
				dBodySetForce(self._OdeBodyID, f[0], f[1], f[2])

	property torque:
	# getTorque
		def __get__(self):
			"""getTorque() -> 3-tuple
	
			Return the current accumulated torque.
			"""
			cdef dReal* f
			if not (self._option & BODY_HAS_ODE): return None
			# The "const" in the original return value is cast away
			f = <dReal*>dBodyGetTorque(self._OdeBodyID)
			return Vector(self._ode_parent,f[0],f[1],f[2])
			# setTorque
		def __set__(self,_Vector torque):
			"""setTorque(t)
		
			Set the body torque accumulation vector.
		
			@param t: Torque
			@type t: 3-tuple of floats
			"""
			cdef float t[3]
			if not (self._option & BODY_HAS_ODE):
				self._activate_ode_body()
			if torque is None:
				dBodySetTorque(self._OdeBodyID, 0, 0, 0)
			else:
				torque._into(self._ode_parent, t)
				dBodySetTorque(self._OdeBodyID, t[0], t[1], t[2])

	

	# getRelPointVel
	def get_point_vel(self, _Point pos):
		"""getRelPointVel(p) -> 3-tuple

		Utility function that takes a point p on a body and returns
		that point's velocity in global coordinates. The point p
		must be given in body relative coordinates.

		@param p: Body point (local coordinates)
		@type p: 3-sequence of floats
		"""
		if not (self._option & BODY_HAS_ODE): return None
		cdef dVector3 res 
		cdef dVector3 p
		pos._into(self,p)
		dBodyGetRelPointVel(self._OdeBodyID, p[0], p[1], p[2], res)
		return (res[0], res[1], res[2])


		
		
	property enabled:
		def __set__(self, flag):
			"""enable()
	
			Manually enable a body.
			"""
			if not (self._option & BODY_HAS_ODE): self._activate_ode_body()
			
			if flag:
				dBodyEnable(self._OdeBodyID)
			else:
				dBodyDisable(self._OdeBodyID)
			
		def __get__(self):
			"""isEnabled() -> bool
	
			Check if a body is currently enabled.
			"""
			if not (self._option & BODY_HAS_ODE): return None
			return dBodyIsEnabled(self._OdeBodyID)
			
	property finite_rotation_mode:
		def __set__(self, mode):
			"""setFiniteRotationMode(mode)
	
			This function controls the way a body's orientation is updated at
			each time step. The mode argument can be:
			
			 - 0: An "infinitesimal" orientation update is used. This is
				 fast to compute, but it can occasionally cause inaccuracies
				 for bodies that are rotating at high speed, especially when
				 those bodies are joined to other bodies. This is the default
				 for every new body that is created.
			
			 - 1: A "finite" orientation update is used. This is more
				 costly to compute, but will be more accurate for high speed
				 rotations. Note however that high speed rotations can result
				 in many types of error in a world, and this mode will
				 only fix one of those sources of error.
	
			@param mode: Rotation mode (0/1)
			@type mode: int
			"""
			if not (self._option & BODY_HAS_ODE): self.activate_ode_body()
			dBodySetFiniteRotationMode(self._OdeBodyID, mode)
		
		def __get__(self):
			"""getFiniteRotationMode() -> mode (0/1)
	
			Return the current finite rotation mode of a body (0 or 1).
			See setFiniteRotationMode().
			"""
			if not (self._option & BODY_HAS_ODE): return None
			return dBodyGetFiniteRotationMode(self._OdeBodyID)

	property finite_rotation_axis:
		def __set__(self, _Vector axis):
			"""setFiniteRotationAxis(a)

			Set the finite rotation axis of the body.  This axis only has a
			meaning when the finite rotation mode is set
			(see setFiniteRotationMode()).
			
			@param a: Axis
			@type a: Vector
			"""
			if not (self._option & BODY_HAS_ODE): self._activate_ode_body()
			cdef float a[3]
			axis._into(self._ode_parent,a)
			dBodySetFiniteRotationAxis(self._OdeBodyID, a[0], a[1], a[2])

		def __get__(self):
			"""getFiniteRotationAxis() -> 3-tuple
	
			Return the current finite rotation axis of the body.
			"""
			if not (self._option & BODY_HAS_ODE):
				#raise TypeError("This Body is not yet ODE managed. Use Body.activate_ode_body() to turn ODE management on.")
				return None
			cdef dVector3 p
			# The "const" in the original return value is cast away
			dBodyGetFiniteRotationAxis(self._OdeBodyID, p)
			return Vector(self.ode_parent,p[0],p[1],p[2])
		
	property num_joints:
		def __get__(self):
			"""getNumJoints() -> int

			Return the number of joints that are attached to this body.
			"""
			if not (self._option & BODY_HAS_ODE):
				#raise TypeError("This Body is not yet ODE managed. Use Body.activate_ode_body() to turn ODE management on.")
				return None
			return dBodyGetNumJoints(self._OdeBodyID)

	property gravity_mode:
		def __set__(self, mode):
			"""setGravityMode(mode)
	
			Set whether the body is influenced by the world's gravity
			or not. If mode is True it is, otherwise it isn't.
			Newly created bodies are always influenced by the world's gravity.
	
			@param mode: Gravity mode
			@type mode: bool
			"""
			if not (self._option & BODY_HAS_ODE): self._activate_ode_body()
			dBodySetGravityMode(self._OdeBodyID, mode)
		
		def __get__(self):
			"""getGravityMode() -> bool
	
			Return True if the body is influenced by the world's gravity.
			"""
			if not (self._option & BODY_HAS_ODE): return None
			return dBodyGetGravityMode(self._OdeBodyID)
			
	# why it is function ?
	cdef void _add_joint(self, _Joint joint):
		self.joints.append(joint)

	cdef void _remove_joint(self, _Joint joint):
		self.joints.remove(joint)
