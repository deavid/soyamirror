# -*- indent-tabs-mode: t -*-
#cdef class _Geom
cdef class _Space(_Geom):
	cdef _World   _world
	cdef readonly geoms
	
	#cdef void _create(self, _Space space)
	
cdef class SimpleSpace(_Space):
	pass
	#cdef void _create(self, _Space space)
