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


#cdef struct _BSPLeaf:
	#int   cluster
	#int   area
	#int   model_part
	#int   nb_brush
	#int*  brushes
	#float sphere[4]
	#float box[6]


#cdef struct _BSPNode:
	#int front
	#int back
	#int plane


cdef class _BSPWorld(_World):
	#cdef float*         _planes
	#cdef int            _nb_plane
	#cdef _BSPNode*      _nodes
	#cdef int            _nb_node
	#cdef _BSPLeaf*      _leafs
	#cdef int            _nb_leaf
	#cdef int*           _clusters
	#cdef int            _old_cluster
	#cdef object         _movable_lists
	#cdef int            _nb_cluster
	#cdef int            _row_length
	#cdef unsigned char* _vis_data
	#cdef int*           _areamask
	#cdef int            _areamask_modified
	#cdef object         _batched_children
	#cdef object         _batched_clusters
	
	
	property model_builder:
		def __get__(self):
			return None
		def __set__(self, ModelBuilder arg):
			raise TypeError("BSPWorld does not implement model_builder property")
	
	
	property model:
		def __get__(self):
			return self._model
		def __set__(self, _Model model):
			raise TypeError("It's impossible to change the model of a BSPWorld")
	
	
	def add_shell(self, shell):
		raise TypeError("It's impossible to add a shell to a BSPWorld")
	
	
	# Return true if leaf _from is visible from leaf _to
	cdef int _is_visible_from(self, int _from, int _to):
	 # Test areas
	 # Sometime there can be valid leaf with area = -1. This happend near areaportal brushes.
		if self._leafs[_from].area < 0 or self._leafs[_to].area < 0 \
		or self._areamask[self._leafs[_to].area] & (1 << self._leafs[_from].area):
			# If area OK then test clusters
			return <int> (self._vis_data[(self._leafs[_to].cluster) * self._row_length + (self._leafs[_from].cluster) / 8] & (1 << (self._leafs[_from].cluster) % 8))
		else:
			return 0
	
	
	# Return the cluster and the area wich the given point belongs to
	cdef void _locate_point(self, float* coords, int* cluster, int* area):
		cdef int node
		# Start with the root node
		node = 0
		while(node >= 0):
			# Test camera position againt the node
			if point_distance_plane(coords, &(self._planes[self._nodes[node].plane])) >= 0.:
				node = self._nodes[node].front
			else:
				node = self._nodes[node].back
		# Find leaf's cluster and area
		leaf = -(node + 1)
		cluster[0] = self._leafs[leaf].cluster
		area[0]    = self._leafs[leaf].area
	
	
	# Find in wich leaves and areas the given sphere is
	cdef void _locate_sphere(self, float* sphere, int node, leafs, areas):
		cdef char sides
		# If node is a node, test sphere with node's split plane
		if node >= 0:
			sides = sphere_side_plane(sphere, &(self._planes[self._nodes[node].plane]))
			# Sphere in front of the plane
			if sides == 1:
				self._locate_sphere(sphere, self._nodes[node].front, leafs, areas)
			# Sphere behind node's split plane
			elif sides == 2:
				self._locate_sphere(sphere, self._nodes[node].back, leafs, areas)
			# Sphere crossing node's split plane
			else:
				self._locate_sphere(sphere, self._nodes[node].front, leafs, areas)
				self._locate_sphere(sphere, self._nodes[node].back, leafs, areas)
		# If node is a leaf add it to the list
		else:
			if leafs is not None: leafs.append(-(node+1))
			if self._leafs[-(node+1)].area >= 0 and areas is not None:
				areas.append(self._leafs[-(node+1)].area)
	
	
	# Find in wich leafs and area a child is
	# If world_locate not null then the child is put in the clusters moovables lists
	cdef void _locate_child(self, CoordSyst child):
		cdef float sphere[4]
		cdef int   i, leaf
		# Get the child bounding sphere
		child._get_sphere(sphere)
		sphere_by_matrix(sphere, child._root_matrix())
		sphere_by_matrix(sphere, self._inverted_root_matrix())
		# Remove child from all clusters's lists
		for i from 0 <= i < self._nb_cluster:
			try:
				self._movable_lists[i].remove(child)
			except: pass
		# Locate the child
		leafs_list = []
		self._locate_sphere(sphere, 0, leafs_list, None)
		# Put the child in the clusters moovables lists
		for leaf in leafs_list:
			i = self._leafs[leaf].cluster
			if i >= 0:
				if not child in self._movable_lists[i]:
					self._movable_lists[i].append(child)
	
	
	cdef __getcstate__(self):
		cdef Chunk* chunk
		cdef int    i
		chunk = get_chunk()
		chunk_add_int_endian_safe(chunk, self._nb_plane)
		chunk_add_int_endian_safe(chunk, self._nb_node)
		chunk_add_int_endian_safe(chunk, self._nb_leaf)
		chunk_add_int_endian_safe(chunk, self._nb_cluster)
		chunk_add_int_endian_safe(chunk, self._row_length)
		chunk_add_floats_endian_safe(chunk, self._planes, self._nb_plane*4)
		for i from 0 <= i < self._nb_node:
			chunk_add_int_endian_safe(chunk, self._nodes[i].front)
			chunk_add_int_endian_safe(chunk, self._nodes[i].back)
			chunk_add_int_endian_safe(chunk, self._nodes[i].plane)
		for i from 0 <= i < self._nb_leaf:
			chunk_add_int_endian_safe(chunk, self._leafs[i].cluster)
			chunk_add_int_endian_safe(chunk, self._leafs[i].area)
			chunk_add_int_endian_safe(chunk, self._leafs[i].model_part)
			#chunk_add_int_endian_safe(chunk, self._leafs[i].nb_brush)
			#chunk_add_ints_endian_safe(chunk, self._leafs[i].brushes, self._leafs[i].nb_brush)
			chunk_add_floats_endian_safe(chunk, self._leafs[i].sphere, 4)
			chunk_add_floats_endian_safe(chunk, self._leafs[i].box, 6)
		for i from 0 <= i < self._nb_cluster:
			chunk_add_int_endian_safe(chunk, self._clusters[i])
		chunk_add_chars_endian_safe(chunk, <char*> self._vis_data, self._nb_cluster*self._row_length)
		return _World.__getcstate__(self), drop_chunk_to_string(chunk)
	
	
	cdef void __setcstate__(self, object cstate):
		cdef Chunk*    chunk
		cdef int       i, j
		chunk = string_to_chunk(cstate[1])
		chunk_get_int_endian_safe(chunk, &self._nb_plane)
		chunk_get_int_endian_safe(chunk, &self._nb_node)
		chunk_get_int_endian_safe(chunk, &self._nb_leaf)
		chunk_get_int_endian_safe(chunk, &self._nb_cluster)
		chunk_get_int_endian_safe(chunk, &self._row_length)
		self._planes   = <float*>       malloc(self._nb_plane*4 * sizeof(float))
		self._nodes    = <_BSPNode*>    malloc(self._nb_node    * sizeof(_BSPNode))
		self._leafs    = <_BSPLeaf*>    malloc(self._nb_leaf    * sizeof(_BSPLeaf))
		self._clusters = <int*>         malloc(self._nb_cluster * sizeof(int))
		chunk_get_floats_endian_safe(chunk, self._planes, self._nb_plane*4)
		for i from 0 <= i < self._nb_node:
			chunk_get_int_endian_safe   (chunk, &(self._nodes[i].front))
			chunk_get_int_endian_safe   (chunk, &(self._nodes[i].back))
			chunk_get_int_endian_safe   (chunk, &(self._nodes[i].plane))
		for i from 0 <= i < self._nb_leaf:
			chunk_get_int_endian_safe   (chunk, &(self._leafs[i].cluster))
			chunk_get_int_endian_safe   (chunk, &(self._leafs[i].area))
			chunk_get_int_endian_safe   (chunk, &(self._leafs[i].model_part))
			#chunk_get_int_endian_safe   (chunk, &(self._leafs[i].nb_brush))
			#self._leafs[i].brushes = <int*> malloc(self._leafs[i].nb_brush * sizeof(int))
			#chunk_get_ints_endian_safe(chunk, self._leafs[i].brushes, self._leafs[i].nb_brush)
			chunk_get_floats_endian_safe(chunk,  self._leafs[i].sphere, 4)
			chunk_get_floats_endian_safe(chunk,  self._leafs[i].box, 6)
		self._movable_lists = []
		for i from 0 <= i < self._nb_cluster:
			chunk_get_int_endian_safe(chunk, &(self._clusters[i]))
			movable_list = []
			self._movable_lists.append(movable_list)
		self._movable_lists = tuple(self._movable_lists)
		self._vis_data = <unsigned char*> malloc(self._nb_cluster*self._row_length * sizeof(unsigned char))
		chunk_get_chars_endian_safe(chunk, <char*> self._vis_data, self._nb_cluster*self._row_length)
		self._areamask = <int*> malloc(32 * sizeof(int))
		for i from 0 <= i < 32:
			self._areamask[i] = 1 << i
		self._areamask_modified =  0
		self._old_cluster       = -1
		self._batched_clusters  = []
		self._batched_children  = []
		_World.__setcstate__(self, cstate[0])
		drop_chunk(chunk)
	
	
	# Batch a cluster for rendering
	cdef void _batch_cluster(self, int index):
		cdef float     box[6]
		cdef CoordSyst child
		if self._leafs[self._clusters[index]].model_part >= 0:
			# test cluster's bounding box against frustum
			point_by_matrix_copy(box,   self._leafs[self._clusters[index]].box,   self._root_matrix())
			point_by_matrix_copy(&box[0]+3, &self._leafs[self._clusters[index]].box[0]+3, self._root_matrix())
			if box_in_frustum(renderer.root_frustum, box) > 0:
				self._model._batch_part(self, self._leafs[self._clusters[index]].model_part)
			for child in self._movable_lists[index]:
				if not child in self._batched_children: self._batched_children.append(child)
	
	
	cdef void _batch(self, CoordSyst coordsyst):
		cdef Context   old_context
		cdef CoordSyst child
		cdef float     camera_coord[3]
		cdef int       node, leaf, cam_cluster, cam_area, i, cluster
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
		# Find in witch cluster and area the camera is
		camera_coord[0] = renderer.root_frustum.position[0]
		camera_coord[1] = renderer.root_frustum.position[1]
		camera_coord[2] = renderer.root_frustum.position[2]
		point_by_matrix(camera_coord, renderer.root_object._root_matrix())
		point_by_matrix(camera_coord, self._inverted_root_matrix())
		self._locate_point(camera_coord, &cam_cluster, &cam_area)
		# If we are in the same cluster than last time no need to retest the visibility
		# We need to retest the visibility if the areamask has be modified (ie a door opened or something)
		if cam_cluster == self._old_cluster and not self._areamask_modified:
			for cluster in self._batched_clusters:
				self._batch_cluster(cluster)
		else:
			self._old_cluster       = cam_cluster
			self._areamask_modified = 0
			self._batched_clusters  = []
			self._batched_children  = []
			if cam_cluster < 0:
				print "BSP World Error : camera in invalid leaf !!!"
				return
			# Batch all clusters visible from this one and childrens inside them
			for i from 0 <= i < self._nb_cluster:
				if self._is_visible_from(self._clusters[cam_cluster], self._clusters[i]):
					self._batch_cluster(i)
					self._batched_clusters.append(i)
		self._model._batch_end(self)
		for child in self._batched_children:
			child._batch(self)
		renderer.current_context = old_context
	
	
	# Test a ray against the node plane
	# recursive function
	cdef int _raypick_node(self, RaypickData data, float* raydata, float* start, float length, int node, int category):
		cdef float  num, dem, dist, start_length, end_length
		cdef float  midle[3], vect[3]
		cdef int    i, next_node
		# If node is a leaf
		if node < 0:
			return self._raypick_leaf(data, raydata, -(node+1), category)
		# Test ray against the plane
		dist = ray_distance_plane(start, raydata+3, length, &(self._planes[self._nodes[node].plane]), 0.)
		# Infinit positiv distance : the start point is in front of the plane and the ray don't cross it
		if dist == INFINITY:
			i = self._raypick_node(data, raydata, start, length, self._nodes[node].front, category)
		# Infinit negativ distance : the start point is behind the plane and the ray don't cross it
		elif dist == -INFINITY:
			i = self._raypick_node(data, raydata, start, length, self._nodes[node].back, category)
		# The ray cross the plane
		else:
			# Compute ray fractions in front of and behind the plane
			# We will first check the side where the start of the ray is
			if dist >= 0.:
				next_node = self._nodes[node].front
				start_length = dist
				if length >= 0.: end_length = length - dist
				else:            end_length = -1.
			else:
				next_node = self._nodes[node].back
				start_length = -dist
				if length >= 0.: end_length = length + dist
				else:            end_length = -1.
			# Check first side
			i = self._raypick_node(data, raydata, start, start_length, next_node, category)
			# If the raypick function found something in this leaf it is useless to check the other side
			if i != 0: return i
			# Check the other side
			if next_node == self._nodes[node].front: next_node = self._nodes[node].back
			else:                                    next_node = self._nodes[node].front
			# Compute intersection point
			for i from 0 <= i < 3:
				vect[i] = raydata[i+3]
			# XXX possible optimisation for vector_set_length
			vector_set_length(vect, start_length)
			for i from 0 <= i < 3:
				midle[i] = start[i] + vect[i]
			i = self._raypick_node(data, raydata, &midle[0], end_length, next_node, category)
		return i
	
	
	# Raypick leaf's model part and world children that are located in the leaf
	cdef int _raypick_leaf(self, RaypickData data, float* raydata, int leaf, int category):
		cdef int       i, j, found_something
		cdef CoordSyst something
		found_something = 0
		# If this leaf has no model part there is nothing to test
		if self._leafs[leaf].model_part < 0: return 0
		# First we test the geometry of the leaf itself
		if data.option & RAYPICK_BOOL:
			i = self._model._raypick_part_b(data, raydata, self._leafs[leaf].model_part)
			if i: return 1
		else:
			something = data.result_coordsyst
			self._model._raypick_part(data, raydata, self._leafs[leaf].model_part, self)
			if data.result_coordsyst != something: found_something = 1
		# Test world childrens in this leaf
		# Is it sot possible to have some child in this leaf if it is not a cluster
		if self._leafs[leaf].cluster < 0: return found_something
		something = data.result_coordsyst
		nb_children = len(self._movable_lists[self._leafs[leaf].cluster])
		for i from 0 <= i < nb_children:
			if data.option & RAYPICK_BOOL:
				j = self._movable_lists[self._leafs[leaf].cluster][i]._raypick_b(data, self, category)
				if j: return 1
			else:
				self._movable_lists[self._leafs[leaf].cluster][i]._raypick(data, self, category)
		if data.option & RAYPICK_BOOL: return 0
		if data.result_coordsyst != something: found_something = 1
		return found_something
	
	
	cdef void _raypick(self, RaypickData raypick_data, CoordSyst raypickable, int category):
		cdef float* raydata
		if not (self._category_bitfield & category): return
		raydata = self._raypick_data(raypick_data)
		self._raypick_node(raypick_data, raydata, raydata, raydata[6], 0, category)
	
	
	cdef int _raypick_b(self, RaypickData raypick_data, CoordSyst raypickable, int category):
		cdef float* raydata
		if not (self._category_bitfield & category): return 0
		raydata = self._raypick_data(raypick_data)
		return self._raypick_node(raypick_data, raydata, raydata, raydata[6], 0, category)
	
	
	cdef void _raypick_from_context(self, RaypickData data, Chunk* items, int category):
		cdef float* raydata
		cdef int    leaf
		raydata = self._raypick_data(data)
		leaf    = chunk_get_int(items)
		while leaf != -1:
			self._raypick_leaf(data, raydata, leaf, category)
			leaf = chunk_get_int(items)
	
	
	cdef int _raypick_from_context_b(self, RaypickData data, Chunk* items, int category):
		cdef float* raydata
		cdef int    leaf, i
		raydata = self._raypick_data(data)
		leaf    = chunk_get_int(items)
		while leaf != -1:
			i = self._raypick_leaf(data, raydata, leaf, category)
			if i: break
			leaf = chunk_get_int(items)
		while leaf != -1:
			leaf = chunk_get_int(items)
		return i
	
	
	cdef void _collect_raypickables(self, Chunk* items, float* rsphere, float* sphere, int category):
		cdef float* matrix
		cdef float  s[4]
		cdef int    leaf
		if not (self._category_bitfield & category): return
		leaves = []
		matrix = self._inverted_root_matrix()
		point_by_matrix_copy(s, rsphere, matrix)
		s[3] = length_by_matrix(rsphere[3], matrix)
		self._locate_sphere(s, 0, leaves, None)
		if not len(leaves) == 0:
			chunk_add_ptr(items, <void*> self)
			for leaf in leaves:
				chunk_add_int(items, leaf)
			chunk_add_int(items, -1)
	
	
	def add(self, CoordSyst child not None):
		_World.add(self, child)
		self._locate_child(child)
	
	
	def remove(self, CoordSyst child not None):
		_World.remove(self, child)
		cdef int i
		for i from 0 <= i < self._nb_cluster:
			try:
				self._movable_lists[i].remove(child)
			except: pass
	
	
	def insert(self, int index, CoordSyst child not None):
		_World.insert(self, index, child)
		self._locate_child(child)
	
	
	def to_model(self):
		raise TypeError("BSPWorld does not implement to_model()")
	
	
	def begin_round(self):
		cdef CoordSyst child
		_World.begin_round(self)
		for child in self.children:
			if not child.static: self._locate_child(child)
	
	
	def enable_area_visibility(self, int area1, int area2):
		"""BSPWorld.enable_area_visibility(AREA1, AREA2)

Tell the BSP World that area 1 is visible from area 2 and vis versa.
"""
		if area1 >= 32 or area2 >= 32 or area1 < 0 or area2 < 0:
			return
		self._areamask[area1] = self._areamask[area1] | (1 << area2)
		self._areamask[area2] = self._areamask[area2] | (1 << area1)
		self._areamask_modified = 1
	
	
	def disable_area_visibility(self, int area1, int area2):
		"""BSPWorld.disable_area_visibility(AREA1, AREA2)

Tell the BSP World that area 1 is not visible from area 2 and vis versa.
"""
		if area1 >= 32 or area2 >= 32 or area1 < 0 or area2 < 0:
			return
		self._areamask[area1] = self._areamask[area1] & (0xFFFFFFFF ^ (1 << area2))
		self._areamask[area2] = self._areamask[area2] & (0xFFFFFFFF ^ (1 << area1))
		self._areamask_modified = 1
	
	
	def __init__(self,_SplitedModel model, nodes, leafs, planes, brushes, visdata, _World parent = None, opt = None):
		cdef int       i, j
		_World.__init__(self, parent, model, opt)
		# Register planes
		self._nb_plane = len(planes)
		self._planes = <float*> malloc(self._nb_plane * 4 * sizeof(float))
		for i from 0 <= i < self._nb_plane:
			self._planes[i*4]      = planes[i].a
			self._planes[i*4 + 1]  = planes[i].b
			self._planes[i*4 + 2]  = planes[i].c
			self._planes[i*4 + 3]  = planes[i].d
		# Build cluster list
		# Actually a cluster is just a not invalid leaf
		cluster_list     = []
		self._nb_cluster = visdata.nb_vector
		for i from 0 <= i < self._nb_cluster:
			for leaf in leafs:
				if leaf.cluster == i and not (leaf.box_min_x == 0 and leaf.box_max_x == 0):
					cluster_list.append(leafs.index(leaf))
					break
			else:
				print "BSP World Error : no cluster", i
				cluster_list.append(-1)
		# Register clusters
		self._old_cluster      = -1
		self._batched_clusters = []
		self._batched_children = []
		self._clusters         = <int*> malloc(self._nb_cluster * sizeof(int))
		self._movable_lists    = []
		for i from 0 <= i < self._nb_cluster:
			self._clusters[i] = cluster_list[i]
		# Creat an empty list of movable objects (world's children) for each cluster
		for i from 0 <= i < self._nb_cluster:
			movable_list = []
			self._movable_lists.append(movable_list)
		self._movable_lists = tuple(self._movable_lists)
		# Register leafs
		self._nb_leaf = len(leafs)
		self._leafs   = <_BSPLeaf*> malloc(self._nb_leaf * sizeof(_BSPLeaf))
		for i from 0 <= i < len(leafs):
			self._leafs[i].cluster = leafs[i].cluster
			self._leafs[i].area    = leafs[i].area
			if leafs[i].model_part != -1:
				self._leafs[i].model_part = leafs[i].model_part
				self._leafs[i].sphere[0]  = leafs[i].sphere_x
				self._leafs[i].sphere[1]  = leafs[i].sphere_y
				self._leafs[i].sphere[2]  = leafs[i].sphere_z
				self._leafs[i].sphere[3]  = leafs[i].sphere_r
				self._leafs[i].box[0]     = leafs[i].box_min_x
				self._leafs[i].box[1]     = leafs[i].box_min_y
				self._leafs[i].box[2]     = leafs[i].box_min_z
				self._leafs[i].box[3]     = leafs[i].box_max_x
				self._leafs[i].box[4]     = leafs[i].box_max_y
				self._leafs[i].box[5]     = leafs[i].box_max_z
			else:
				self._leafs[i].model_part = -1
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
			# Register brushes in leaf
			#self._leafs[i].nb_brush = len(leafs[i].brush_indices)
			#if self._leafs[i].nb_brush > 0:
				#self._leafs[i].brushes = <int*> malloc(self._leafs[i].nb_brush * sizeof(int))
				#for j from 0 <= j < self._leafs[i].nb_brush:
					#self._leafs[i].brushes[j] = leafs[i].brush_indices[j]
			#else:
				#self._leafs[i].brushes = NULL
		# Register nodes
		self._nb_node = len(nodes)
		self._nodes   = <_BSPNode*> malloc(self._nb_node * sizeof(_BSPNode))
		for i from 0 <= i < self._nb_node:
			self._nodes[i].plane = nodes[i].plane * 4
			self._nodes[i].front = nodes[i].front
			self._nodes[i].back  = nodes[i].back
		# Register clusters visibility data
		self._row_length = visdata.vector_size
		self._vis_data   = <unsigned char*> malloc(len(visdata.data) * sizeof(unsigned char))
		for i from 0 <= i < len(visdata.data):
			self._vis_data[i] = visdata.data[i]
		# Creat areas visibility data
		self._areamask = <int*> malloc(32 * sizeof(int))
		for i from 0 <= i < 32:
			self._areamask[i] = 1 << i
		self._areamask_modified = 0
	
	
	def __dealloc__(self):
		free(self._planes)
		free(self._clusters)
		free(self._leafs)
		free(self._nodes)
		free(self._vis_data)
