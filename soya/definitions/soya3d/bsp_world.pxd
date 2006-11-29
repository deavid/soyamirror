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


cdef struct _BSPLeaf:
	int   cluster
	int   face_group
	float sphere[4]
	float box[6]

cdef struct _BSPNode:
	int   front
	int   back
	float plane[4]

cdef struct _BSPCluster:
	int* leafs
	int  nb_leafs

cdef class _BSPWorld(_World):
	cdef _BSPNode*      _nodes
	cdef int            _nb_node
	cdef _BSPLeaf*      _leafs
	cdef int            _nb_leaf
	cdef _BSPCluster*   _clusters
	cdef object         _movable_lists
	cdef int            _nb_cluster
	cdef int            _row_length
	cdef unsigned char* _vis_data
	cdef object         _batched_children
	
	cdef float _distance_to(self, float* coords, int node)
	cdef int   _is_visible_from(self, int _from, int _to)
	cdef void  _locate_child(self, _Body child)
	cdef void  _locate_sphere(self, _Body movable, float* sphere, int node)
	cdef void  _locate_movable(self, _Body movable)
	cdef       __getcstate__(self)
	cdef void  __setcstate__(self, object cstate)
	cdef void  _batch(self, CoordSyst coordsyst)
	cdef void  _raypick(self, RaypickData raypick_data, CoordSyst raypickable, int category)
	cdef int   _raypick_b(self, RaypickData raypick_data, CoordSyst raypickable, int category)
	cdef void  _collect_raypickables(self, Chunk* items, float* rsphere, float* sphere, int category)





