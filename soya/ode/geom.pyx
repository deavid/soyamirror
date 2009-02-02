cdef class _Geom:
	def __init__(self, _Space space=None):
		self._space = space
		if space is not None:
			space.geoms.append(self)
		self._create()
		dGeomSetData(self._OdeGeomID, <void *>self)
		self.bounce = 0
		self.grip = dInfinity
		
	
	cdef _create(self):
		raise NotImplemented("The _Geom can't be used directly")
	
	cdef float _point_depth(self, float x, float y, float z):
		raise NotImplementedError, "Cannot use GeomObject directly"
		
	def point_depth(self, pos): #XXX check it
		return self._point_depth(pos[0], pos[1], pos[2])
		
	def __dealloc__(self):
		if self._OdeGeomID != NULL:
			dGeomDestroy(self._OdeGeomID)
			self._OdeGeomID = NULL
			
	#XXXYYY make a python version using Vector
	cdef dReal* _getAABB(self):
		"""getAABB() -> 6-tuple

		Return an axis aligned bounding box that surrounds the geom.
		The return value is a 6-tuple (minx, maxx, miny, maxy, minz, maxz).
		"""
		cdef dReal aabb[6]
		
		dGeomGetAABB(self._OdeGeomID, aabb)
		return aabb
	def isSpace(self):
		"""isSpace() -> bool

		Return 1 if the given geom is a space, or 0 if not."""
		return False
		#return dGeomIsSpace(self._OdeGeomID)
	property space:
		def __get__(self):
			return self._space
		def __set__(self,_Space space):
			if space is not self._space:
				old_space = self._space
				self._space = space
				if old_space is not None:
					old_space.remove(self)
				if space is not None :
					space.add(self)
				
	property collide_bits:
		def __set__(self,bits):
			dGeomSetCollideBits(self._OdeGeomID, bits)
		def __get__(self):
			return dGeomGetCollideBits(self._OdeGeomID)

	property category_bits:
		def __set__(self,bits):
			dGeomSetCategoryBits(self._OdeGeomID, bits)
		def __get__(self):
			return dGeomGetCategoryBits(self._OdeGeomID)

	property enabled:
		def __set__(self, flag):
			if flag:
					dGeomEnable(self._OdeGeomID)
			else:
					dGeomDisable(self._OdeGeomID)

		def __get__(self):
			return dGeomIsEnabled(self._OdeGeomID)
	property bounce:
		def __get__(self):
			return self._bounce
		def __set__(self,float value):
			self._bounce = value
	property grip:
		def __get__(self):
			return self._grip
		def __set__(self,float value):
			self._grip = value
		
cdef class _PlaceableGeom(_Geom):
	def __init__(_PlaceableGeom self,_Body body):
		cdef _World parent
		if body is not None:
			parent = body._parent
			if parent._space is None:
				SimpleSpace(world=parent)
			space = parent._space
		else:
			space = None
		self._body = None
		_Geom.__init__(self,space)
		self.body = body
	property body:
		def __set__(self, _Body body):
			if self._body is not body:
				if self._body is not None and self._body.geom is self:
					self._body.geom = None
				self._body = body
				if body is None:
					dGeomSetBody(self._OdeGeomID,NULL)
				else:
					if not body._option & BODY_HAS_ODE:
						body._activate_ode_body()
					dGeomSetBody(self._OdeGeomID,body._OdeBodyID)
					body.geom = self
					if body.parent.space is None:
						SimpleSpace(world=body.parent)
					self.space=body.parent.space
				
			
		def __get__(self):
			return self._body
