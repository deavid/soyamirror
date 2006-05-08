cdef class _CellShadingShape(_SimpleShape):
  cdef _Material _shader
  cdef float     _outline_color[4]
  cdef float     _outline_width, _outline_attenuation
  
  cdef __getcstate__(self)
  cdef void __setcstate__(self, cstate)
  cdef void _build_cellshading(self, _Material shader, outline_color, float outline_width, float outline_attenuation)
  cdef void _batch(self, CoordSyst coordsyst)
  cdef void _render(self, CoordSyst coordsyst)
  cdef void _render_outline(self, Frustum* frustum)
  cdef void _prepare_cellshading_shades(self, float* shades, lights)
  cdef void _prepare_cellshading(self, CoordSyst coordsyst, float* shades)
  cdef float _vertex_compute_cellshading(self, float* coord, float* normal, lights, float shade)
  cdef void _render_triangle_cellshading(self, ShapeFace* face, float* shades)
  cdef void _render_quad_cellshading(self, ShapeFace* face, float* shades)
  cdef void _render_vertex_cellshading_smoothlit (self, int index, int face_option, float* shades)
  cdef void _render_vertex_cellshading(self, int index, int face_option, float* fnormal)
  

