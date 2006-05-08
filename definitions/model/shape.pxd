cdef class _Shape(_CObj):
  cdef public _filename
  cdef void _batch(self, CoordSyst coord_syst)
  cdef void _render(self, CoordSyst coord_syst)
  cdef int _shadow(self, CoordSyst coord_syst, _Light light)
  cdef void _get_box(self, float* box, float* matrix)
  cdef void _raypick(self, RaypickData raypick_data, CoordSyst raypickable)
  cdef int _raypick_b(self, RaypickData raypick_data, CoordSyst raypickable)
  cdef void _collect_raypickables(self, Chunk* items, float* rsphere, float* sphere, CoordSyst parent)
  

ctypedef struct DisplayList:
  int    option
  int    id
  int    material_id #Material* material
  int*   faces_id
  Chunk* chunk # Only used for initialization of the DisplayList
  

ctypedef struct DisplayLists:
  int nb_opaque_list
  int nb_alpha_list
  DisplayList* display_lists
  

ctypedef struct ShapeFace:
  int      option
  Pack*    pack
  int      normal
  int      v[4] # v[3] is optional (only for quad, unused for triangle)
  

cdef class _SimpleShape(_Shape):
  cdef int           _option
  cdef               _materials
  cdef int           _nb_faces, _nb_vertices, _nb_coords, _nb_vnormals, _nb_colors, _nb_values
  cdef float*        _coords, *_vnormals, *_colors, *_values
  cdef int*          _vertex_coords, *_vertex_texcoords, *_vertex_diffuses, *_vertex_emissives
  cdef char*         _vertex_options
  cdef ShapeFace*    _faces
  cdef int*          _neighbors, *_simple_neighbors
  cdef signed char*  _neighbors_side, *_simple_neighbors_side
  cdef DisplayLists* _display_lists
  cdef float*        _sphere
  
  cdef __getcstate__(self)
  cdef void __setcstate_data__(self, cstate)
  cdef void __setcstate__(self, cstate)
  cdef void _register_material(self, _Material material)
  cdef void _add_coord(self, _Vertex vertex)
  cdef int _register_value(self, float* value, int nb)
  cdef int _register_color(self, float color[4])
  cdef void _add_face(self, _Face face, vertex2ivertex, ivertex2index, lights, int static_shadow)
  cdef int _add_vertex(self, _Vertex vertex, vertex2ivertex, ivertex2index, lights, int static_shadow)
  cdef object _identify_vertices(self, faces, float angle)
  cdef void _compute_face_normals(self, faces)
  cdef void _compute_vertex_normals(self, faces, vertex2ivertex, ivertex2vertices)
  cdef void _compute_face_neighbors(self, faces, vertex2ivertex, ivertex2vertices, int* neighbor, signed char* neighbor_side)
  cdef void _build_sphere(self)
  cdef void _build_display_list(self)
  cdef void _init_display_list(self)
  cdef void _batch(self, CoordSyst coordsyst)
  cdef void _batch_face(self, ShapeFace* face)
  cdef void _render(self, CoordSyst instance)
  cdef void _raypick(self, RaypickData data, CoordSyst parent)
  cdef int _raypick_b(self, RaypickData data, CoordSyst parent)
  cdef void _face_raypick(self, ShapeFace* face, float* raydata, RaypickData data, CoordSyst parent)
  cdef int _face_raypick_b(self, ShapeFace* face, float* raydata, RaypickData data)
  cdef void _collect_raypickables(self, Chunk* items, float* rsphere, float* sphere, CoordSyst parent)
  cdef void _render_triangle(self, ShapeFace* face)
  cdef void _render_quad(self, ShapeFace* face)
  cdef void _render_vertex(self, int index, int face_option)
  cdef int _shadow(self, CoordSyst coord_syst, _Light light)
  cdef void _get_box(self, float* box, float* matrix)

