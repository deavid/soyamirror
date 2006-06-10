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

	cdef _build(self, _Cal3dShape shape, CalRenderer* cal_renderer, CalCoreModel* cal_core_model, CalCoreMesh* cal_core_mesh, int mesh, int submesh)
	cdef void _build_neighbors(self, cache_filename, float* coords)
		
		
cdef class _Cal3dShape(_Shape):
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
	
	cdef void _build_submeshes(self)
	cdef void _set_face_neighborhood(self, int index1, int index2, GLfloat* vertices)
	cdef void _set_cell_shading(self, _Material shader, GLfloat* color, GLfloat line_width_factor)
	cdef void _render(self, CoordSyst coordsyst)
	cdef void _prepare_cellshading(self, CoordSyst coordsyst, float* shades, int nb_vertices, float* coords, float* vnormals)
	cdef void _prepare_cellshading_shades(self, float* shades, lights, int nb_vertices, float* coords, float* vnormals)
	cdef void _render_outline(self, _Cal3dSubMesh submesh, Frustum* frustum, float* coords, float* vnormals, float* plane)
	cdef _Material _get_material_4_cal3d(self, image_filename, float diffuse_r, float diffuse_g, float diffuse_b, float diffuse_a, float specular_r, float specular_g, float specular_b, float specular_a, float shininess)
	cdef _Material _create_material_4_cal3d(self, image_filename, float diffuse_r, float diffuse_g, float diffuse_b, float diffuse_a, float specular_r, float specular_g, float specular_b, float specular_a, float shininess)
	cdef void _set_texture_from_model(self, _Material material, image_filename)
	cdef int _shadow(self, CoordSyst coordsyst, _Light light)
	cdef int _shadow2(self, _Cal3dSubMesh submesh, _Cal3dVolume volume, _Light light, float* coords, float* vnormals, float* plane)
	cdef void _build_vertices(self, _Cal3dVolume volume)




