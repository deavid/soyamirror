# -*- indent-tabs-mode: t -*-

# Each geom object has to insert itself into the global dictionary
# _geom_c2py_lut (key:address - value:Python object).
# This lookup table is used in the near callback to translate the C
# pointers into corresponding Python wrapper objects.
#
# Additionally, each geom object must have a method _id() that returns
# the ODE geom id. This is used during collision detection.
# 
# ##########################
# # Obsolete:
# #
# # Each geom object has to register itself at its space as the
# # space keeps a dictionary that's used as lookup table to translate
# # C pointers into Python objects (this is used in the near callback).

cdef class GeomObject:
		cdef dGeomID gid
		cdef object space
		cdef object body
		cdef object attribs



