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

ctypedef struct TerrainVertex:
	float texcoord[2]
	float normal  [3]
	float coord   [3]
	Pack* pack

cdef struct _TerrainTri

cdef struct _TerrainPatch:
	float     sphere[4]
	char      level # precision level for rendering
	_TerrainTri* tri_top
	_TerrainTri* tri_left
	_TerrainTri* tri_right
	_TerrainTri* tri_bottom
	int       visible
ctypedef _TerrainPatch TerrainPatch

cdef struct _TerrainTri:
	char        level
	float       normal[3]
	float       sphere[4]
	# 3 vertices that determine the triangle. turn right to left (CCW)
	TerrainVertex* v1 # apex vertex
	TerrainVertex* v2 # right vertex for the apex
	TerrainVertex* v3 # left vertex for the apex
	_TerrainTri*   parent
	_TerrainTri*   left_child
	_TerrainTri*   right_child
	_TerrainTri*   left_neighbor
	_TerrainTri*   right_neighbor
	_TerrainTri*   base_neighbor
	Pack*       pack
	TerrainPatch*  patch
	int         texcoord_type # 0: use terrainvertex texcoord, 1, 2, 3, 4: the tri use a texture generated (from blend_material), and the texcoord are (0.0, 0.0) - (1.0, 1.0)
ctypedef _TerrainTri TerrainTri

ctypedef void (*terrain_drawColor_FUNC   )(float*)
ctypedef void (*terrain_disableColor_FUNC)()
ctypedef void (*terrain_enableColor_FUNC )()

cdef class _Terrain(CoordSyst):
	cdef             _materials
	cdef TerrainVertex* _vertices
	cdef char*       _vertex_options
	cdef int*        _vertex_colors
	cdef float*      _vertex_geos # Geomorph Y coordinate
	cdef float*      _normals # full LOD triangles normals
	cdef int         _nb_colors
	cdef float*      _colors # vertices colors
	cdef int         _nb_vertex_width # size_width and size_depth must be (2^n) + 1
	cdef int         _nb_vertex_depth # or I don't know what happen (crash?)
	cdef int         _patch_size
	cdef int         _max_level
	cdef float       _texture_factor # a factor that multiply the texture coordinates
	cdef float       _scale_factor # a factor to decide when the triangle must split (higher value means more accuracy)
	cdef float       _split_factor
	cdef int         _nb_patchs
	cdef int         _nb_patch_width
	cdef int         _nb_patch_depth
	cdef TerrainPatch*  _patchs

	cdef TerrainVertex* _get_vertex(self, int x, int z)
	cdef void _check_size(self)
	cdef void _free_patchs(self)
	cdef void _add_material(self, _Material material)
	cdef float _get_height(self, int x, int z)
	cdef void _set_height (self, int x, int z, float height)
	cdef void _init(self)
	cdef void _compute_normal(self, int x, int y)
	cdef void _compute_normals(self)
	cdef void _compute_coords(self)
	cdef void _create_patch(self, TerrainPatch* patch, int x, int z, int patch_size)
	cdef void _create_patchs(self)
	cdef int _register_color(self, float color[4])
	cdef void _tri_split(self, TerrainTri* tri)
	cdef int _tri_merge_child(self, TerrainTri* tri)
	cdef void _tri_set_level(self, TerrainTri* tri, char level)
	cdef void _patch_set_level(self, TerrainPatch* patch, char level)
	cdef int _patch_update(self, TerrainPatch* patch, Frustum* frustum, float* frustum_box)
	cdef void _tri_force_presence(self, TerrainTri* tri, TerrainVertex* v)
	cdef void _force_presence(self)
	cdef void _tri_batch(self, TerrainTri* tri, Frustum* frustum)
	cdef void _patch_batch(self, TerrainPatch* patch, Frustum* frustum)
	cdef void _batch(self, CoordSyst coordsyst)
	cdef void _tri_render_middle(self, TerrainTri* tri)
	cdef void _tri_render_secondpass(self, TerrainTri* tri)
	cdef void _render(self, CoordSyst coordsyst)
	cdef void _tri_raypick(self, TerrainTri* tri, float* raydata, RaypickData data)
	cdef int _tri_raypick_b(self, TerrainTri* tri, float* raydata, int option)
	cdef void _full_raypick(self, TerrainVertex* v1, TerrainVertex* v2, TerrainVertex* v3, float* normal, float* raydata, RaypickData data)
	cdef void _full_raypick_rect(self, int x1, int z1, int x2, int z2, float* raydata, RaypickData data)
	cdef void _raypick(self, RaypickData raypick_data, CoordSyst raypickable, int category)
	cdef int _full_raypick_b(self, TerrainVertex* v1, TerrainVertex* v2, TerrainVertex* v3, float* normal, float* raydata, int option)
	cdef int _full_raypick_rect_b(self, int x1, int z1, int x2, int z2, float* raydata, int option)
	cdef int _raypick_b(self, RaypickData raypick_data, CoordSyst raypickable, int category)
	cdef void _collect_raypickables(self, Chunk* items, float* rsphere, float* sphere, int category)
	cdef __getcstate__(self)
	cdef void __setcstate__(self, object cstate)
	cdef void _check_vertex_options(self)
	cdef int _check_color(self, float* color)
	
	# For Blam terrain
	cdef void _vertex_render_special(self, TerrainVertex* vertex)
	
	### ODE collision
	cdef _GeomTerrain _geom

	

