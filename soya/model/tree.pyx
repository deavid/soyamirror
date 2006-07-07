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

#cdef struct _Node:
#  int     nb_faces, nb_children
#  int*    faces # index in the TreeModel faces array
#  _Node** children
#  float   sphere[4]
#ctypedef _Node Node

cdef Node* node_new(int face_index, GLfloat* sphere):
	cdef Node* node
	node             = <Node*> malloc(sizeof(Node))
	node.nb_faces    = 1
	node.faces       = <int*> malloc(sizeof(int))
	node.faces[0]    = face_index
	node.nb_children = 0
	node.children    = NULL
	memcpy(node.sphere, sphere, 4 * sizeof(float))
	return node
	
cdef Node* node_register_face(Node* node, Node* parent, int face_index, float* sphere):
	cdef float d
	cdef Node* n
	d = point_distance_to(node.sphere, sphere)
	if   d + sphere[3] <= node.sphere[3]: node_register_inside_face(node, face_index, sphere) # face is inside node
	elif d + node.sphere[3] <= sphere[3]: # node is inside face
		n             = <Node*> malloc(sizeof(Node))
		n.nb_faces    = 1
		n.faces       = <int*> malloc(sizeof(int))
		n.faces[0]    = face_index
		n.nb_children = 1
		n.children    = <Node**> malloc(sizeof(Node*))
		n.children[0] = node
		memcpy(n.sphere, sphere, 4 * sizeof(float))
		return n
	else:
		if parent == NULL: # create a new node with no face
			n             = <Node*> malloc(sizeof(Node))
			n.nb_faces    = 0
			n.faces       = NULL
			n.nb_children = 2
			n.children    = <Node**> malloc(2 * sizeof(Node*))
			n.children[0] = node
			n.children[1] = node_new(face_index, sphere)
			sphere_from_2_spheres(n.sphere, node.sphere, sphere)
			return n
		else: node_add_face(parent, face_index, sphere)
	return node

cdef void node_register_inside_face(Node* node, int face_index, GLfloat* sphere):
	cdef float d
	cdef int   i
	for i from 0 <= i < node.nb_children: # recurse to children
		d = point_distance_to(node.children[i].sphere, sphere)
		if d + sphere[3] <= node.children[i].sphere[3]: # face is inside that child
			node_register_inside_face(node.children[i], face_index, sphere)
			return
	node_add_face(node, face_index, sphere) # no child found => face must be added to this node

cdef void node_register_node(Node* node, Node* add):
	cdef float d
	cdef int   i, added
	i = added = 0
	# test if former nodes can be put into the added node
	while i < node.nb_children:
		if node.children[i] == NULL:
			if added == 0:
				node.children[i] = add
				added = 1
			i = i + 1
		else:
			d = point_distance_to(add.sphere, node.children[i].sphere)
			if d + node.children[i].sphere[3] <= add.sphere[3]:
				# add child i into added node
				node_add_node(add, node.children[i])
				if added == 0:
					node.children[i] = add
					added = 1
					i = i + 1
				else:
					node.nb_children = node.nb_children - 1
					node.children[i] = node.children[node.nb_children]
					node.children[node.nb_children] = NULL
			else: i = i + 1
	if added == 0: node_add_node(node, add)

cdef void node_add_face(Node* node, int face_index, float* sphere):
	cdef Node* new
	# create a new node for face and add the new node to our node
	new = node_new(face_index, sphere)
	node_register_node(node, new)
	node.children = <Node**> realloc(node.children, node.nb_children * sizeof(Node*))
	
cdef int node_gather(Node* node, int mode, float param):
	cdef int   best1, best2, i, j
	cdef float min_radius, radius
	cdef float sphere[4], best_sphere[4]
	cdef Node* n
	best1 = best2 = -1
	# return 0 if no more gather are possible
	# try different technics...
	if mode == 0: # take the smallest sphere
		min_radius = 100000.0
		radius     = param * node.sphere[3]
		n          = NULL
		for i from 0 <= i < node.nb_children:
			if (n == NULL) or (node.children[i].sphere[3] < min_radius):
				best1      = i
				n          = node.children[i]
				min_radius = n.sphere[3] 
		if min_radius >= radius: return 0
		else: # find the 1rst sphere to gather with that produce a sphere with a radius <= radius
			for i from 0 <= i < node.nb_children:
				if i != best1:
					sphere_from_2_spheres(best_sphere, n.sphere, node.children[i].sphere)
					if best_sphere[3] <= radius:
						best2 = i
						break
			return 0
	else:
		# compute the best tree possible but very slow
		# find the 2 children that produce the smallest sphere
		for i from 0 <= i < node.nb_children:
			n = node.children[i]
			if n != NULL:
				for j from i + 1 <= j < node.nb_children:
					if node.children[j] != NULL:
						sphere_from_2_spheres(sphere, n.sphere, node.children[j].sphere)
						if (best1 < 0) or (sphere[3] < best_sphere[3]):
							memcpy(best_sphere, sphere, 4 * sizeof(float))
							best1 = i
							best2 = j
	if (best_sphere[3] >= node.sphere[3]): return 0
	# gather best1 and best2
	n = <Node*> malloc (sizeof(Node))
	n.nb_faces    = 0
	n.faces       = NULL
	n.nb_children = 2
	n.children    = <Node**> malloc(2 * sizeof(Node*))
	n.children[0] = node.children[best1]
	n.children[1] = node.children[best2]
	memcpy(n.sphere, best_sphere, 4 * sizeof(float))
	node.nb_children = node.nb_children - 1
	node.children[best1] = n
	node.children[best2] = node.children[node.nb_children]
	node_added(node, n)
	return 1

cdef void node_added(Node* node, Node* new):
	cdef float d
	cdef int   i
	# test if ancient nodes can be contained into the new one
	i = 0
	while i < node.nb_children:
		if (node.children[i] != NULL) and (new != node.children[i]):
			d = point_distance_to(new.sphere, node.children[i].sphere)
			if d + node.children[i].sphere[3] <= new.sphere[3]:
				# add child i into new node
				node_add_node(new, node.children[i])
				node.nb_children = node.nb_children - 1
				node.children[i] = node.children[node.nb_children]
				node.children[node.nb_children] = NULL
			else: i = i + 1
		else: i = i + 1

cdef void node_add_node(Node* node, Node* add):
	node.children = <Node**> realloc(node.children, (node.nb_children + 1) * sizeof(Node*))
	node.children[node.nb_children] = add
	node.nb_children = node.nb_children + 1

cdef void node_collapse_with_child(Node* node, float collapse):
	cdef int i
	for i from 0 <= i < node.nb_children:
		if node.children[i].sphere[3] > collapse * node.sphere[3]:
			node_join(node, node.children[i])
			node.nb_children = node.nb_children - 1
			node.children[i] = node.children[node.nb_children]
			
cdef void node_join(Node* n1, Node* n2):
	cdef int i
	n1.faces = <int*> realloc(n1.faces, (n1.nb_faces + n2.nb_faces) * sizeof(int))
	for i from 0 <= i < n2.nb_faces: n1.faces[n1.nb_faces + i] = n2.faces[i]
	n1.nb_faces = n1.nb_faces + n2.nb_faces
	
	n1.children = <Node**> realloc(n1.children, (n1.nb_children + n2.nb_children) * sizeof(Node*))
	for i from 0 <= i < n2.nb_children: n1.children[n1.nb_children + i] = n2.children[i]
	n1.nb_children = n1.nb_children + n2.nb_children
	
cdef void node_optimize(Node* node, float collapse, int mode, float param):
	cdef int i
	while (node.nb_children > 2): # gather some children
		if node_gather(node, mode, param) == 0: break
	node_collapse_with_child(node, collapse)
	node.children = <Node**> realloc(node.children, node.nb_children * sizeof(Node*))
	for i from 0 <= i < node.nb_children: node_optimize(node.children[i], collapse, mode, param)
	
cdef int node_get_nb_level(Node* node):
	cdef int i, nb, n
	nb = 0
	for i from 0 <= i < node.nb_children:
		n = node_get_nb_level(node.children[i])
		if n > nb: nb = n
	return nb + 1

cdef int node_get_memory_size(Node* node):
	cdef int size, i
	size = 2 * sizeof(int) + 4 * sizeof(float) + (2 + node.nb_children + node.nb_faces) * sizeof(void*)
	for i from 0 <= i < node.nb_children: size = size + node_get_memory_size(node.children[i])
	return size


cdef node_collect_raypickables(Node* node, Chunk* items, float* sphere):
	cdef int i
	if sphere_distance_sphere(sphere, node.sphere) < 0.0:
		# Add a face** (or a node*) instead ? (faster, less memory)
		chunk_add(items, node.faces, node.nb_faces * sizeof(int))
		for i from 0 <= i < node.nb_children: node_collect_raypickables(node.children[i], items, sphere)

cdef class _TreeModel(_SimpleModel):
	#cdef Node* _tree
	
	cdef __getcstate__(self):
		cdef Chunk* chunk
		chunk = get_chunk()
		self._node2chunk(self._tree, chunk)
		return _SimpleModel.__getcstate__(self), drop_chunk_to_string(chunk)
	
	cdef void __setcstate__(self, cstate):
		_SimpleModel.__setcstate_data__(self, cstate[0])
		
		cdef Chunk* chunk
		chunk = string_to_chunk(cstate[1])
		self._tree = self._chunk2node(chunk)
		drop_chunk(chunk)
		
	cdef _node2chunk(self, Node* node, Chunk* chunk):
		cdef int i
		chunk_add_int_endian_safe   (chunk, node.nb_faces)
		chunk_add_int_endian_safe   (chunk, node.nb_children)
		chunk_add_floats_endian_safe(chunk, node.sphere, 4)
		chunk_add_ints_endian_safe  (chunk, node.faces, node.nb_faces)
		for i from 0 <= i < node.nb_children: self._node2chunk(node.children[i], chunk)
		
	cdef Node* _chunk2node(self, Chunk* chunk):
		cdef int   i
		cdef Node* node
		node             = <Node*> malloc(sizeof(Node))
		chunk_get_int_endian_safe   (chunk, &node.nb_faces)
		chunk_get_int_endian_safe   (chunk, &node.nb_children)
		chunk_get_floats_endian_safe(chunk,  node.sphere, 4)
		node.faces       = <int*  > malloc(node.nb_faces    * sizeof(int  ))
		node.children    = <Node**> malloc(node.nb_children * sizeof(Node*))
		chunk_get_ints_endian_safe  (chunk, node.faces, node.nb_faces)
		for i from 0 <= i < node.nb_children: node.children[i] = self._chunk2node(chunk)
		return node
	
	cdef void _build_tree(self):
		cdef int   i
		cdef float sphere[4]
		cdef Node* tree
		tree = NULL
		
		for i from 0 <= i < self._nb_faces:
			self.compute_sphere(self._faces + i, sphere)
			if tree == NULL: tree = node_new(i, sphere)
			else:            tree = node_register_face(tree, NULL, i, sphere)
			
		self._tree = tree
		
		print "* Soya * Tree built,     %s levels, memory : %s bytes" % (node_get_nb_level(self._tree), node_get_memory_size(self._tree))
		
	cdef void _optimize_tree(self, float collapse, int mode, float max_children_radius):
		node_optimize(self._tree, collapse, mode, max_children_radius)
		
		print "* Soya * Tree optimized, %s levels, memory : %s bytes" % (node_get_nb_level(self._tree), node_get_memory_size(self._tree))
		
	cdef void compute_sphere(self, ModelFace* face, float* sphere):
		cdef float p[12]
		memcpy(p,     self._coords + self._vertex_coords[face.v[0]], 3 * sizeof(float))
		memcpy(p + 3, self._coords + self._vertex_coords[face.v[1]], 3 * sizeof(float))
		memcpy(p + 6, self._coords + self._vertex_coords[face.v[2]], 3 * sizeof(float))
		if   face.option & FACE_TRIANGLE: sphere_from_points(sphere, p, 3)
		elif face.option & FACE_QUAD:
			memcpy(p + 9, self._coords + self._vertex_coords[face.v[3]], 3 * sizeof(float))
			sphere_from_points(sphere, p, 4)
			
			
	cdef void _batch(self, _Body body):
		# XXX deforms: batched_object is ignored
		
		if body._option & HIDDEN: return
		
		cdef Frustum* frustum
		frustum = renderer._frustum(body)
		#batch_start(body)
		
		# batch each face
		self._batch_node(self._tree, frustum)
		pack_batch_end(self, body)
		#if self._option & MODEL_CELL_SHADING:
		#  renderer_batch(renderer.secondpass, mesh, inst, renderer.data.nb)
		#  mesh_batch_outline(mesh, inst, frustum)
		
	cdef void _batch_node(self, Node* node, Frustum* frustum):
		cdef int i
		if sphere_in_frustum(frustum, node.sphere) == 1: # frustum test
			for i from 0 <= i < node.nb_faces:    self._batch_face(self._faces + node.faces[i])
			for i from 0 <= i < node.nb_children: self._batch_node(node.children[i], frustum)
		
	cdef void _render(self, _Body instance):
		cdef Pack*      pack
		cdef ModelFace* face
		
		model_option_activate(self._option)
		
		pack = <Pack*> chunk_get_ptr(renderer.data)
		while pack:
			(<_Material> (pack.material_id))._activate()
			face_option_activate(pack.option)

			face = <ModelFace*> chunk_get_ptr(renderer.data)
			if   pack.option & FACE_TRIANGLE:
				glBegin(GL_TRIANGLES)
				while face:
					self._render_triangle(face)
					face = <ModelFace*> chunk_get_ptr(renderer.data)

			elif pack.option & FACE_QUAD:
				glBegin(GL_QUADS)
				while face:
					self._render_quad(face)
					face = <ModelFace*> chunk_get_ptr(renderer.data)

			glEnd()
			face_option_inactivate(pack.option)
			pack = <Pack*> chunk_get_ptr(renderer.data)
				
		model_option_inactivate(self._option)
		
	cdef void _raypick(self, RaypickData data, CoordSyst parent):
		cdef float* raydata
		raydata = parent._raypick_data(data)
		self._node_raypick(self._tree, raydata, data, parent)
		
	cdef int _raypick_b(self, RaypickData data, CoordSyst parent):
		cdef float* raydata
		raydata = parent._raypick_data(data)
		return self._node_raypick_b(self._tree, raydata, data)
		
	cdef void _node_raypick(self, Node* node, float* raydata, RaypickData data, CoordSyst parent):
		cdef int i
		if sphere_raypick(raydata, node.sphere) == 1:
			for i from 0 <= i < node.nb_faces:    self._face_raypick(self._faces + node.faces[i], raydata, data, parent)
			for i from 0 <= i < node.nb_children: self._node_raypick(node.children[i], raydata, data, parent)
			
	cdef int _node_raypick_b(self, Node* node, float* raydata, RaypickData data):
		cdef int i
		if sphere_raypick(raydata, node.sphere) == 1:
			for i from 0 <= i < node.nb_faces:
				if self._face_raypick_b(self._faces + node.faces[i], raydata, data): return 1
			for i from 0 <= i < node.nb_children:
				if self._node_raypick_b(node.children[i], raydata, data): return 1
		return 0

	cdef void _collect_raypickables(self, Chunk* items, float* rsphere, float* sphere, CoordSyst parent):
		chunk_add_ptr(items, <void*> self)
		chunk_add_ptr(items, <void*> parent)
		node_collect_raypickables(self._tree, items, sphere)
		chunk_add_int(items, -1)
		
	cdef void _raypick_from_context(self, RaypickData data, Chunk* items):
		cdef float*     raydata
		cdef int        face_index
		cdef CoordSyst  parent
		parent  = <CoordSyst> chunk_get_ptr(items)
		raydata = parent._raypick_data(data)
		face_index = chunk_get_int(items)
		while face_index != -1:
			self._face_raypick(self._faces + face_index, raydata, data, parent)
			face_index = chunk_get_int(items)
			
	cdef int _raypick_from_context_b(self, RaypickData data, Chunk* items):
		cdef float*     raydata
		cdef int        face_index
		cdef CoordSyst  parent
		parent  = <CoordSyst> chunk_get_ptr(items)
		raydata = parent._raypick_data(data)
		face_index = chunk_get_int(items)
		while face_index != -1:
			if self._face_raypick_b(self._faces + face_index, raydata, data): return 1
			face_index = chunk_get_int(items)
		return 0
		
		
