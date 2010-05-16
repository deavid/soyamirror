cdef class _PrimitiveGeom(_PlaceableGeom):
	pass
cdef class GeomSphere(_PrimitiveGeom):
	pass
cdef class GeomBox(_PrimitiveGeom):
	pass
cdef class GeomCapsule(_PrimitiveGeom):
	pass
cdef class GeomCylinder(_PrimitiveGeom):
	pass


#cdef class GeomPlan(_Geom):
#	cdef GLfloat[3] point_a
#	cdef GLfloat[3] point_b
#	cdef GLfloat[3] point_c
