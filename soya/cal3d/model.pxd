# -*- indent-tabs-mode: t -*-

# Soya 3D
# Copyright (C) 2004 Jean-Baptiste LAMY -- jiba@tuxfamily.org
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA


cdef class _Cal3dSubMesh:
	cdef int       _option, _mesh, _submesh
	cdef _Material _material
	
	cdef int       _nb_faces, _nb_vertices
	cdef int*      _faces
	cdef int*      _face_neighbors

	cdef _build(self, _AnimatedModel model, CalRenderer* cal_renderer, CalCoreModel* cal_core_model, CalCoreMesh* cal_core_mesh, int mesh, int submesh)
	cdef void _build_neighbors(self, full_filename, float* coords)
		
		
cdef class _AnimatedModel(_Model):
	cdef int   _option
	cdef int   _nb_faces, _nb_vertices
	cdef float _sphere[4]
	cdef _meshes, _animations, _materials, _submeshes
	cdef _full_filename
	
	cdef CalCoreModel* _core_model
	
	# Cellshading stuff
	cdef _Material _shader
	cdef float     _outline_color[4]
	cdef float     _outline_width, _outline_attenuation
	
	cdef void _instanced(self, _Body body, opt)
	cdef void _build_submeshes(self)
	cdef void _set_face_neighborhood(self, int index1, int index2, GLfloat* vertices)
	cdef void _set_cell_shading(self, _Material shader, GLfloat* color, GLfloat line_width_factor)
	cdef void _batch (self, _Body body)
	cdef void _render(self, _Body body)
	cdef void _prepare_cellshading(self, CoordSyst coordsyst, float* shades, int nb_vertices, float* coords, float* vnormals)
	cdef void _prepare_cellshading_shades(self, float* shades, lights, int nb_vertices, float* coords, float* vnormals)
	cdef void _render_outline(self, _Cal3dSubMesh submesh, Frustum* frustum, float* coords, float* vnormals, float* plane)
	cdef _Material _get_material_4_cal3d(self, image_filename, float diffuse_r, float diffuse_g, float diffuse_b, float diffuse_a, float specular_r, float specular_g, float specular_b, float specular_a, float shininess)
	cdef _Material _create_material_4_cal3d(self, image_filename, float diffuse_r, float diffuse_g, float diffuse_b, float diffuse_a, float specular_r, float specular_g, float specular_b, float specular_a, float shininess)
	cdef void _set_texture_from_model(self, _Material material, image_filename)
	cdef int _shadow(self, CoordSyst coordsyst, _Light light)
	cdef int _shadow2(self, _Cal3dSubMesh submesh, _Body body, _Light light, float* coords, float* vnormals, float* plane)
	cdef void _build_vertices(self, _AnimatedModelData data)




cdef class _AnimatedModelData(_ModelData):
	cdef _Body          _body
	cdef _AnimatedModel _model
	cdef                _attached_meshes, _attached_coordsysts
	cdef CalModel*      _cal_model
	cdef float          _delta_time
	cdef float*         _face_planes, *_coords, *_vnormals
	cdef int            _face_plane_ok, _vertex_ok
	
	cdef      __getcstate__(self)
	cdef void __setcstate__(self, cstate)
	
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
	
	cdef void _build_submeshes(self)
	cdef void _build_face_planes(self)
	cdef void _build_vertices(self, int vertices)
	cdef void _attach_all(self)
