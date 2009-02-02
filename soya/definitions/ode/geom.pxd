cdef class _Geom
cdef class _Space(_Geom)
cdef class _Geom:
	cdef dGeomID _OdeGeomID
	cdef _Space  _space
	#cdef _World  _ode_parent #XXX check it
	cdef float _bounce
	cdef float _grip
	
	cdef float _point_depth(self, float x, float y, float z)
	cdef _create(self)
	cdef dReal* _getAABB(self)
	
cdef class _PlaceableGeom(_Geom):
	cdef _Body  _body
