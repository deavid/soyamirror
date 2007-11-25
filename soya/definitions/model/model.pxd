# -*- indent-tabs-mode: t -*-

cdef class _Model(_CObj):
	cdef public _filename
	cdef void _instanced(self, _Body body, opt)
	cdef void _batch(self, _Body body)
	cdef void _render(self, _Body body)
	cdef int  _shadow(self, CoordSyst coord_syst, _Light light)
	cdef void _get_box(self, float* box, float* matrix)
	cdef void _raypick(self, RaypickData raypick_data, CoordSyst raypickable)
	cdef int  _raypick_b(self, RaypickData raypick_data, CoordSyst raypickable)
	cdef void _raypick_part(self, RaypickData raypick_data, float* raydata, int part, CoordSyst parent)
	cdef int  _raypick_part_b(self, RaypickData raypick_data, float* raydata, int part)
	cdef void _collect_raypickables(self, Chunk* items, float* rsphere, float* sphere, CoordSyst parent)
	
	cdef _Model _create_deformed_data(self)
	
	cdef void _attach(self, mesh_names)
	cdef void _detach(self, mesh_names)
	cdef int  _is_attached(self, mesh_name)
	cdef void _attach_to_bone(self, CoordSyst coordsyst, bone_name)
	cdef void _detach_from_bone(self, CoordSyst coordsyst)
	cdef void _advance_time(self, float proportion)
	cdef void _begin_round(self)
	cdef      _get_attached_meshes    (self)
	cdef      _get_attached_coordsysts(self)
	cdef void _animate_blend_cycle   (self, animation_name, float weight, float fade_in)
	cdef void _animate_clear_cycle   (self, animation_name, float fade_out)
	cdef void _animate_execute_action(self, animation_name, float fade_in, float fade_out)
	cdef void _animate_reset(self)
	cdef void _set_lod_level(self, float lod_level)
	cdef void _begin_round  (self)
	cdef void _advance_time (self, float proportion)
	cdef void _batch_part(self, _Body body, int index)
	cdef void _batch_end(self, _Body body)
	
ctypedef struct DisplayList:
	int      option
	int      id
	intptr_t material_id # it is a pointer - should be long not to fail on AMD64
	int*     faces_id
	Chunk*   chunk # Only used for initialization of the DisplayList
	

ctypedef struct DisplayLists:
	int nb_opaque_list
	int nb_alpha_list
	DisplayList* display_lists
	

ctypedef struct ModelFace:
	int      option
	Pack*    pack
	int      normal
	int      v[4] # v[3] is optional (only for quad, unused for triangle)
	

cdef class _SimpleModel(_Model):
	cdef int           _option
	cdef               _materials
	cdef int           _nb_faces, _nb_vertices, _nb_coords, _nb_vnormals, _nb_colors, _nb_values
	cdef float*        _coords, *_vnormals, *_colors, *_values
	cdef int*          _vertex_coords, *_vertex_texcoords, *_vertex_diffuses, *_vertex_emissives
	cdef char*         _vertex_options
	cdef ModelFace*    _faces
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
	cdef void _batch(self, _Body body)
	cdef void _batch_face(self, ModelFace* face)
	cdef void _render(self, _Body body)
	cdef void _raypick(self, RaypickData data, CoordSyst parent)
	cdef int _raypick_b(self, RaypickData data, CoordSyst parent)
	cdef void _face_raypick(self, ModelFace* face, float* raydata, RaypickData data, CoordSyst parent)
	cdef int _face_raypick_b(self, ModelFace* face, float* raydata, RaypickData data)
	cdef void _collect_raypickables(self, Chunk* items, float* rsphere, float* sphere, CoordSyst parent)
	cdef void _render_triangle(self, ModelFace* face)
	cdef void _render_quad(self, ModelFace* face)
	cdef void _render_vertex(self, int index, int face_option)
	cdef int _shadow(self, CoordSyst coord_syst, _Light light)
	cdef int _build_shadow(self, CoordSyst coord_syst, _Light light, int camera_inside_shadow, int displaylist)
	cdef void _get_box(self, float* box, float* matrix)


cdef class _ModelData(_Model):
	pass


