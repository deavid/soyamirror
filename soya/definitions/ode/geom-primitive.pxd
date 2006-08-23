cdef class _PrimitiveGeom(_PlaceableGeom)
cdef class GeomSphere(_PrimitiveGeom)
cdef class GeomBox(_PrimitiveGeom)
cdef class GeomCCylinder(_PrimitiveGeom)


#cdef class GeomPlan(_Geom):
#	cdef GLfloat[3] point_a
#	cdef GLfloat[3] point_b
#	cdef GLfloat[3] point_c