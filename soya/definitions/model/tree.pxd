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

cdef struct _Node:
	int     nb_faces, nb_children
	int*    faces # index in the TreeModel faces array
	_Node** children
	float   sphere[4]
ctypedef _Node Node

cdef class _TreeModel(_SimpleModel):
	cdef Node* _tree
	
	cdef __getcstate__(self)
	cdef void __setcstate__(self, object cstate)
	cdef _node2chunk(self, Node* node, Chunk* chunk)
	cdef Node* _chunk2node(self, Chunk* chunk)
	cdef void _build_tree(self)
	cdef void _optimize_tree(self, float collapse, int mode, float max_children_radius)
	cdef void compute_sphere(self, ModelFace* face, float* sphere)
	cdef void _batch (self, _Body body)
	cdef void _batch_node(self, Node* node, Frustum* frustum)
	cdef void _render(self, _Body body)
	cdef void _raypick(self, RaypickData data, CoordSyst parent)
	cdef int _raypick_b(self, RaypickData data, CoordSyst parent)
	cdef void _node_raypick(self, Node* node, float* raydata, RaypickData data, CoordSyst parent)
	cdef int _node_raypick_b(self, Node* node, float* raydata, RaypickData data)
	cdef void _collect_raypickables(self, Chunk* items, float* rsphere, float* sphere, CoordSyst parent)
	cdef void _raypick_from_context(self, RaypickData data, Chunk* items)
	cdef int _raypick_from_context_b(self, RaypickData data, Chunk* items)
		
