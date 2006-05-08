cdef class CoordSyst(Position):
  cdef float _matrix               [19]
  cdef float __root_matrix         [19]
  cdef float __inverted_root_matrix[19]
  cdef float _render_matrix        [19]
  cdef int _frustum_id
  cdef int _validity
  cdef int __raypick_data
  cdef int _option

  cdef __getcstate__(self)
  cdef void __setcstate__(self, cstate)
  cdef void _batch(self, CoordSyst coord_syst)
  cdef void _render(self, CoordSyst coord_syst)
  cdef int _shadow(self, CoordSyst coord_syst, _Light light)
  cdef void _raypick(self, RaypickData raypick_data, CoordSyst raypickable)
  cdef int _raypick_b(self, RaypickData raypick_data, CoordSyst raypickable)
  cdef void _collect_raypickables(self, Chunk* items, float* rsphere, float* sphere)
  cdef int _contains(self, _CObj obj)
  cdef float* _raypick_data(self, RaypickData data)
  cdef float _distance_out(self, float distance)
  cdef void _invalidate(self)
  cdef void check_lefthanded(self)
  cdef float* _root_matrix(self)
  cdef float* _inverted_root_matrix(self)
  cdef _World _get_root(self)
  cdef void _get_box(self, float* box, float* matrix)
  cdef void _get_sphere(self, float* sphere)
  
 
cdef class PythonCoordSyst(CoordSyst):
  cdef void _batch(self, CoordSyst parent)
  cdef void _render(self, CoordSyst coordsyst)
  cdef int _shadow(self, CoordSyst coordsyst, _Light light)


cdef class CoordSystState(CoordSyst):
  cdef float _quaternion[4]
  
  cdef void _check_state_validity(self)
  cdef void __setcstate__(self, object cstate)
  

