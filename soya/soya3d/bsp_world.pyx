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


cdef class _BSPWorld(_World):
	#_BSPNode*      _root_node
	#_BSPLeaf*      _leafs
	#_BSPCluster*   _clusters
	#int            _nb_cluster
	#int            _row_length
	#unsigned char* _vis_data
	
	property model_builder:
		def __get__(self):
			return None
		def __set__(self, ModelBuilder arg):
			raise TypeError("!")
	
	property model:
		def __get__(self):
			return self._model
		def __set__(self, _Model model):
			raise TypeError("!")
	
	cdef float _distance_to(self, float* coords, int node):
		return self._nodes[node].plane[0]*coords[0] + \
		       self._nodes[node].plane[1]*coords[1] + \
		       self._nodes[node].plane[2]*coords[2] - \
		       self._nodes[node].plane[3]
	
	cdef int _is_visible_from(self, int _from, int _to):
		# If you want to understant how this function works
		# read the quake 3 bsp file format specification :)
		return <int> (self._vis_data[_to*self._row_length + _from/8] & (1<<_from%8))
	
	cdef void _locate_child(self, _Body child):
		if not child._data is None:
			if (<_SimpleModel>(child._data))._option & MODEL_HAS_SPHERE and not child.static:
				self._locate_movable(child)
	
	cdef void _locate_sphere(self, _Body movable, float* sphere, int node):
		cdef float dist
		# If node is a node, test sphere with node's split plane
		if node >= 0:
			dist = self._distance_to(sphere, node)
			# Sphere in front of node's split plane
			if   dist > sphere[3] - EPSILON:
				self._locate_sphere(movable, sphere, self._nodes[node].front)
			# Sphere behind node's split plane
			elif dist < sphere[3] + EPSILON:
				self._locate_sphere(movable, sphere, self._nodes[node].back)
			# Sphere crossing node's split plane
			else:
				self._locate_sphere(movable, sphere, self._nodes[node].front)
				self._locate_sphere(movable, sphere, self._nodes[node].back)
		# If node is a leaf, add movable to leaf's cluster
		else:
			if self._leafs[-(node+1)].cluster >= 0:
				if not movable in self._movable_lists[self._leafs[-(node+1)].cluster]:
					self._movable_lists[self._leafs[-(node+1)].cluster].append(movable)
	
	cdef void _locate_movable(self, _Body movable):
		cdef float sphere[4]
		cdef float coords[3]
		cdef float radius
		cdef int   i
		# Remove movable from all clusters's lists
		for i from 0 <= i < self._nb_cluster:
			try:
				self._movable_lists[i].remove(movable)
			except: pass
		# Get movable bounding sphere and convert it to world coord system
		movable._get_sphere(sphere)
		point_by_matrix(sphere, movable._root_matrix())
		point_by_matrix(sphere, self._inverted_root_matrix())
		# Locate the sphere in the world
		self._locate_sphere(movable, sphere, 0)
	
	cdef __getcstate__(self):
		cdef Chunk* chunk
		cdef int    i
		
		chunk = get_chunk()
		chunk_add_int_endian_safe(chunk, self._nb_node)
		chunk_add_int_endian_safe(chunk, self._nb_leaf)
		chunk_add_int_endian_safe(chunk, self._nb_cluster)
		chunk_add_int_endian_safe(chunk, self._row_length)
		for i from 0 <= i < self._nb_node:
			chunk_add_int_endian_safe(chunk, self._nodes[i].front)
			chunk_add_int_endian_safe(chunk, self._nodes[i].back)
			chunk_add_floats_endian_safe(chunk, self._nodes[i].plane, 4)
		for i from 0 <= i < self._nb_leaf:
			chunk_add_int_endian_safe(chunk, self._leafs[i].cluster)
			chunk_add_int_endian_safe(chunk, self._leafs[i].face_group)
			chunk_add_floats_endian_safe(chunk, self._leafs[i].sphere, 4)
			chunk_add_floats_endian_safe(chunk, self._leafs[i].box, 6)
		for i from 0 <= i < self._nb_cluster:
			chunk_add_int_endian_safe(chunk, self._clusters[i].nb_leafs)
			print self._clusters[i].nb_leafs, "leaf for this cluster"
			chunk_add_ints_endian_safe(chunk, self._clusters[i].leafs, self._clusters[i].nb_leafs)
		chunk_add_chars_endian_safe(chunk, <char*> self._vis_data, self._nb_cluster*self._row_length)
		return _World.__getcstate__(self), drop_chunk_to_string(chunk)
	
	cdef void __setcstate__(self, object cstate):
		cdef Chunk* chunk
		cdef int    i
		
		_World.__setcstate__(self, cstate[0])
		chunk = string_to_chunk(cstate[1])
		chunk_get_int_endian_safe(chunk, &self._nb_node)
		chunk_get_int_endian_safe(chunk, &self._nb_leaf)
		chunk_get_int_endian_safe(chunk, &self._nb_cluster)
		chunk_get_int_endian_safe(chunk, &self._row_length)
		self._nodes         = <_BSPNode*>    malloc(self._nb_node    * sizeof(_BSPNode))
		self._leafs         = <_BSPLeaf*>    malloc(self._nb_leaf    * sizeof(_BSPLeaf))
		self._clusters      = <_BSPCluster*> malloc(self._nb_cluster * sizeof(_BSPCluster))
		for i from 0 <= i < self._nb_node:
			chunk_get_int_endian_safe   (chunk, &(self._nodes[i].front))
			chunk_get_int_endian_safe   (chunk, &(self._nodes[i].back))
			chunk_get_floats_endian_safe(chunk,  self._nodes[i].plane, 4)
		for i from 0 <= i < self._nb_leaf:
			chunk_get_int_endian_safe   (chunk, &(self._leafs[i].cluster))
			chunk_get_int_endian_safe   (chunk, &(self._leafs[i].face_group))
			chunk_get_floats_endian_safe(chunk,  self._leafs[i].sphere, 4)
			chunk_get_floats_endian_safe(chunk,  self._leafs[i].box, 6)
		self._movable_lists = []
		for i from 0 <= i < self._nb_cluster:
			chunk_get_int_endian_safe(chunk, &(self._clusters[i].nb_leafs))
			print self._clusters[i].nb_leafs, "leaf for this cluster"
			self._clusters[i].leafs = <int*> malloc(self._clusters[i].nb_leafs * sizeof(int))
			chunk_get_ints_endian_safe(chunk, self._clusters[i].leafs, self._clusters[i].nb_leafs)
			movable_list = []
			self._movable_lists.append(movable_list)
		self._movable_lists = tuple(self._movable_lists)
		self._vis_data = <unsigned char*> malloc(self._nb_cluster*self._row_length * sizeof(unsigned char))
		chunk_get_chars_endian_safe(chunk, <char*> self._vis_data, self._nb_cluster*self._row_length)
		drop_chunk(chunk)
	
	cdef void _batch(self, CoordSyst coordsyst):
		cdef Context   old_context
		cdef CoordSyst child
		cdef float     camera_coord[3]
		cdef float     box[3]
		cdef int       node, leaf, cam_cluster, i
		
		old_context = renderer.current_context
		if self._option & HIDDEN: return
		if not coordsyst is None: multiply_matrix(self._render_matrix, coordsyst._render_matrix, self._matrix)
		self._frustum_id = -1
		# Atmosphere and context
		if not self._atmosphere is None:
			if renderer.root_atmosphere is None:
				renderer.current_context.atmosphere = renderer.root_atmosphere = self._atmosphere
			else:
				if not self._atmosphere is renderer.current_context.atmosphere:
					renderer.current_context = renderer._context()
					renderer.current_context.atmosphere = self._atmosphere
					renderer.current_context.lights.extend(old_context.lights)
		# Find in witch leaf the camera is
		camera_coord[0] = renderer.root_frustum.position[0]
		camera_coord[1] = renderer.root_frustum.position[1]
		camera_coord[2] = renderer.root_frustum.position[2]
		point_by_matrix(camera_coord, renderer.root_object._root_matrix())
		point_by_matrix(camera_coord, self._inverted_root_matrix())
		# Start with the root node
		node = 0
		while(node >= 0):
			# Test camera position againt the node
			if self._distance_to(camera_coord, node) >= 0.:
				node = self._nodes[node].front
			else:
				node = self._nodes[node].back
		# Find leaf's cluster
		leaf = -(node + 1)
		cam_cluster = self._leafs[leaf].cluster
		if cam_cluster < 0:
			print "camera in invalid leaf !!!"
			return
		# Batch all visible leafs in clusters visible from this one
		for i from 0 <= i < self._nb_cluster:
			if self._is_visible_from(cam_cluster, i):
				for leaf from 0 <= leaf < self._clusters[i].nb_leafs:
					if self._leafs[self._clusters[i].leafs[leaf]].face_group >= 0:
						# test leaf's bounding box against frustum
						point_by_matrix_copy(box, self._leafs[self._clusters[i].leafs[leaf]].box, self._parent._root_matrix())
						point_by_matrix_copy(box+3, self._leafs[self._clusters[i].leafs[leaf]].box+3, self._parent._root_matrix())
						if box_in_frustum(renderer.root_frustum, box) > 0:
							self._model._batch_part(self, self._leafs[self._clusters[i].leafs[leaf]].face_group)
		self._model._batch_end(self)
		# Batch all visible childrens in clusters visible from this one
		self._batched_children = []
		for i from 0 <= i < self._nb_cluster:
			if self._is_visible_from(cam_cluster, i):
				for child in self._movable_lists[i]:
					if not child in self._batched_children:
						child._batch(self)
						self._batched_children.append(child)
		renderer.current_context = old_context
	
	cdef void _raypick(self, RaypickData raypick_data, CoordSyst raypickable, int category):
		pass
	
	cdef int _raypick_b(self, RaypickData raypick_data, CoordSyst raypickable, int category):
		pass
	
	cdef void _collect_raypickables(self, Chunk* items, float* rsphere, float* sphere, int category):
		pass
	
	def add(self, CoordSyst child not None):
		_World.add(self, child)
		self._locate_movable(child)
	
	def remove(self, CoordSyst child not None):
		_World.remove(self, child)
		cdef int i
		for i from 0 <= i < self._nb_cluster:
			try:
				self._movable_lists[i].remove(child)
			except: pass
	
	def insert(self, int index, CoordSyst child not None):
		_World.insert(self, index, child)
		self._locate_movable(child)
	
	def to_model(self):
		pass
	
	def begin_round(self):
		_World.begin_round(self)
		for child in self.children:
			self._locate_child(child)
	
	def __init__(self,_SplitedModel model, nodes, leafs, planes, leaf2facegroup, visdata, _World parent = None, opt = None):
		_World.__init__(self, parent, model, opt)
		# Build cluster list
		cluster_list     = []
		self._nb_cluster = visdata.nb_vector
		for i in range(0, self._nb_cluster):
			leaf_list = []
			for leaf in leafs:
				if leaf.cluster == i and leaf.nb_leaf_face > 0:
					leaf_list.append(leafs.index(leaf))
			cluster_list.append(leaf_list)
		# Register clusters and leafs in clusters
		self._clusters      = <_BSPCluster*> malloc(self._nb_cluster * sizeof(_BSPCluster))
		self._movable_lists = []
		for i in range(0, self._nb_cluster):
			self._clusters[i].nb_leafs = len(cluster_list[i])
			self._clusters[i].leafs    = <int*> malloc(self._clusters[i].nb_leafs * sizeof(int))
			for j in range(0, self._clusters[i].nb_leafs):
				self._clusters[i].leafs[j] = cluster_list[i][j]
		# Creat an empty list of movable objects for eatch cluster
		for i in range(0, self._nb_cluster):
			movable_list = []
			self._movable_lists.append(movable_list)
		self._movable_lists = tuple(self._movable_lists)
		# Register leafs
		self._nb_leaf = len(leafs)
		self._leafs   = <_BSPLeaf*> malloc(self._nb_leaf * sizeof(_BSPLeaf))
		for i in range(0, len(leafs)):
			self._leafs[i].cluster = leafs[i].cluster
			if leafs[i].nb_leaf_face > 0 and leafs[i].cluster >= 0:
				try:
					self._leafs[i].face_group = leaf2facegroup[leafs[i]]
				except KeyError:
					self._leafs[i].face_group = -1
				self._leafs[i].sphere[0] = leafs[i].sphere_x
				self._leafs[i].sphere[1] = leafs[i].sphere_y
				self._leafs[i].sphere[2] = leafs[i].sphere_z
				self._leafs[i].sphere[3] = leafs[i].sphere_r
				self._leafs[i].box[0]    = leafs[i].box_min_x
				self._leafs[i].box[1]    = leafs[i].box_min_y
				self._leafs[i].box[2]    = leafs[i].box_min_z
				self._leafs[i].box[3]    = leafs[i].box_max_x
				self._leafs[i].box[4]    = leafs[i].box_max_y
				self._leafs[i].box[5]    = leafs[i].box_max_z
			else:
				self._leafs[i].face_group = -1
				self._leafs[i].sphere[0]  = 0
				self._leafs[i].sphere[1]  = 0
				self._leafs[i].sphere[2]  = 0
				self._leafs[i].sphere[3]  = 0
				self._leafs[i].box[0]     = 0
				self._leafs[i].box[1]     = 0
				self._leafs[i].box[2]     = 0
				self._leafs[i].box[3]     = 0
				self._leafs[i].box[4]     = 0
				self._leafs[i].box[5]     = 0
		# Register nodes
		self._nb_node = len(nodes)
		self._nodes   = <_BSPNode*> malloc(self._nb_node * sizeof(_BSPNode))
		for i in range(0, len(nodes)):
			self._nodes[i].plane[0] = planes[nodes[i].plane].a
			self._nodes[i].plane[1] = planes[nodes[i].plane].b
			self._nodes[i].plane[2] = planes[nodes[i].plane].c
			self._nodes[i].plane[3] = planes[nodes[i].plane].d
			self._nodes[i].front    = nodes[i].front
			self._nodes[i].back     = nodes[i].back
		# Register visibility data
		self._row_length = visdata.vector_size
		self._vis_data   = <unsigned char*> malloc(len(visdata.data) * sizeof(unsigned char))
		for i in range(0, len(visdata.data)):
			self._vis_data[i] = visdata.data[i]
