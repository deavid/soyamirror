# -*- indent-tabs-mode: t -*-


cdef class RaypickData:
	cdef int       option
	cdef Chunk*    raypicked
	cdef Chunk*    raypick_data
	cdef float     root_data[7], normal[3], result, root_result
	cdef CoordSyst result_coordsyst
	

cdef class RaypickContext:
	cdef Chunk* _items
	cdef _World _root

