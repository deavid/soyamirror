# -*- indent-tabs-mode: t -*-

# Souvarine souvarine@aliasrobotique.org
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

cdef struct _BSPPlane:
	float coords[4]
	int   signbits

cdef struct _BSPLeaf:
	int   cluster
	int   area
	int   model_part
	int   nb_brush
	int*  brushes
	float sphere[4]
	float box[6]

cdef struct _BSPNode:
	int front
	int back
	int plane

cdef struct _BSPBrush:
	int  nb_plane
	int* planes

cdef class _BSPWorld(_World):
	cdef _BSPPlane*     _planes
	cdef int            _nb_plane
	cdef _BSPNode*      _nodes
	cdef int            _nb_node
	cdef _BSPLeaf*      _leafs
	cdef int            _nb_leaf
	cdef int*           _clusters
	cdef int            _old_cluster
	cdef object         _movable_lists
	cdef int            _nb_cluster
	cdef _BSPBrush*     _brushes
	cdef int            _nb_brush
	cdef int            _row_length
	cdef unsigned char* _vis_data
	cdef int*           _areamask
	cdef int            _areamask_modified
	cdef object         _batched_children
	cdef object         _batched_clusters
	
	cdef float _distance_to(self, float* coords, int plane)
	cdef int   _is_visible_from(self, int _from, int _to)
	cdef float _ray_against_plane(self, float* start, float* vect, float length, int plane)
	cdef char  _box_against_plane(self, float* box, int plane)
	cdef char  _sphere_against_plane(self, float* sphere, int plane)
	cdef void  _locate_point(self, float* coords, int* cluster, int* area)
	cdef void  _locate_sphere(self, float* sphere, int node, leafs, areas)
	cdef void  _locate_box(self, float* box, int node, leafs, areas)
	cdef void  _locate_child(self, child, char world_locate, areas)
	cdef       __getcstate__(self)
	cdef void  __setcstate__(self, object cstate)
	cdef void  _batch_cluster(self, int index)
	cdef void  _batch(self, CoordSyst coordsyst)
	cdef int   _raypick_leaf(self, RaypickData data, float* raydata, int leaf, int category)
	cdef int   _raypick_leaf_b(self, RaypickData data, float* raydata, int leaf, int category)
	cdef int   _raypick_node(self, RaypickData data, float* raydata, float* start, float length, int node, int category)
	cdef void  _raypick(self, RaypickData raypick_data, CoordSyst raypickable, int category)
	cdef int   _raypick_b(self, RaypickData raypick_data, CoordSyst raypickable, int category)
	cdef void  _raypick_from_context(self, RaypickData data, Chunk* items, category)
	cdef int   _raypick_from_context_b(self, RaypickData data, Chunk* items, category)
	cdef void  _collect_raypickables(self, Chunk* items, float* rsphere, float* sphere, int category)





