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

#cdef struct _BSPPlane:
#	float coords[4]
#	int   signbits

#cdef struct _BSPLeaf:
#	int   cluster
# int   area
#	int   model_part
#	int   nb_brush
#	int*  brushes
#	float sphere[4]
#	float box[6]

#cdef struct _BSPNode:
#	int front
#	int back
#	int plane

#cdef struct _BSPBrush:
#	int  nb_plane
#	int* planes

# Global variables used for raypicking
cdef float _ray_start[3]
cdef float _ray_end[3]
cdef float _ray_length

cdef class _BSPWorld(_World):
#	cdef _BSPNode*      _nodes
#	cdef int            _nb_node
#	cdef _BSPLeaf*      _leafs
#	cdef int            _nb_leaf
#	cdef int*           _clusters
#	cdef object         _movable_lists
#	cdef int            _nb_cluster
#	cdef int            _row_length
#	cdef unsigned char* _vis_data
#	cdef object         _batched_children
	
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
	
	# Return the distance between a point and a plane
	cdef float _distance_to(self, float* coords, int plane):
		return self._planes[plane].coords[0]*coords[0] + \
		       self._planes[plane].coords[1]*coords[1] + \
		       self._planes[plane].coords[2]*coords[2] - \
		       self._planes[plane].coords[3]
	
	# Test a box against a plane
	# Return 1 if the box is in front of the plane, 2 if it is behind, and 0 if it cross it
	cdef char _box_against_plane(self, float* box, int plane):
		cdef float dist1, dist2
		cdef char  sides
		if self._planes[plane].signbits == 0:
			dist1 = self._planes[plane].coords[0]*box[3] + self._planes[plane].coords[1]*box[4] + self._planes[plane].coords[2]*box[5]
			dist2 = self._planes[plane].coords[0]*box[0] + self._planes[plane].coords[1]*box[1] + self._planes[plane].coords[2]*box[2]
		elif self._planes[plane].signbits == 1:
			dist1 = self._planes[plane].coords[0]*box[0] + self._planes[plane].coords[1]*box[4] + self._planes[plane].coords[2]*box[5]
			dist2 = self._planes[plane].coords[0]*box[3] + self._planes[plane].coords[1]*box[1] + self._planes[plane].coords[2]*box[2]
		elif self._planes[plane].signbits == 2:
			dist1 = self._planes[plane].coords[0]*box[3] + self._planes[plane].coords[1]*box[1] + self._planes[plane].coords[2]*box[5]
			dist2 = self._planes[plane].coords[0]*box[0] + self._planes[plane].coords[1]*box[4] + self._planes[plane].coords[2]*box[2]
		elif self._planes[plane].signbits == 3:
			dist1 = self._planes[plane].coords[0]*box[0] + self._planes[plane].coords[1]*box[1] + self._planes[plane].coords[2]*box[5]
			dist2 = self._planes[plane].coords[0]*box[3] + self._planes[plane].coords[1]*box[4] + self._planes[plane].coords[2]*box[2]
		elif self._planes[plane].signbits == 4:
			dist1 = self._planes[plane].coords[0]*box[3] + self._planes[plane].coords[1]*box[4] + self._planes[plane].coords[2]*box[2]
			dist2 = self._planes[plane].coords[0]*box[0] + self._planes[plane].coords[1]*box[1] + self._planes[plane].coords[2]*box[5]
		elif self._planes[plane].signbits == 5:
			dist1 = self._planes[plane].coords[0]*box[0] + self._planes[plane].coords[1]*box[4] + self._planes[plane].coords[2]*box[2]
			dist2 = self._planes[plane].coords[0]*box[3] + self._planes[plane].coords[1]*box[1] + self._planes[plane].coords[2]*box[5]
		elif self._planes[plane].signbits == 6:
			dist1 = self._planes[plane].coords[0]*box[3] + self._planes[plane].coords[1]*box[1] + self._planes[plane].coords[2]*box[2]
			dist2 = self._planes[plane].coords[0]*box[0] + self._planes[plane].coords[1]*box[4] + self._planes[plane].coords[2]*box[5]
		elif self._planes[plane].signbits == 7:
			dist1 = self._planes[plane].coords[0]*box[0] + self._planes[plane].coords[1]*box[1] + self._planes[plane].coords[2]*box[2]
			dist2 = self._planes[plane].coords[0]*box[3] + self._planes[plane].coords[1]*box[4] + self._planes[plane].coords[2]*box[5]
		sides = 0
		if dist1 >= self._planes[plane].coords[3]:
			sides = 1
		if dist2 <  self._planes[plane].coords[3]:
			sides = sides | 2
		return sides
	
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
		cdef int node, cam_cluster, cam_area
		# Start with the root node
		node = 0
		while(node >= 0):
			# Test camera position againt the node
			if self._distance_to(coords, self._nodes[node].plane) >= 0.:
				node = self._nodes[node].front
			else:
				node = self._nodes[node].back
		# Find leaf's cluster and area
		leaf = -(node + 1)
		cluster[0] = self._leafs[leaf].cluster
		area[0]    = self._leafs[leaf].area
	
	# Find in wich cluster(s) the given child is using its bounding box
	# If areas == NULL the child is put in the clusters moovables lists
	cdef void _locate_box(self, child, float* box, int node, int* areas):
		cdef char sides
		# If node is a node, test box with node's split plane
		if node >= 0:
			sides = self._box_against_plane(box, self._nodes[node].plane)
			# Box in front of the plane
			if sides == 1:
				self._locate_box(child, box, self._nodes[node].front, areas)
			# Box behind node's split plane
			elif sides == 2:
				self._locate_box(child, box, self._nodes[node].back, areas)
			# Box crossing node's split plane
			else:
				self._locate_box(child, box, self._nodes[node].front, areas)
				self._locate_box(child, box, self._nodes[node].back, areas)
		# If node is a leaf, add child to corresponding cluster
		else:
			if self._leafs[-(node+1)].cluster >= 0:
				if areas == NULL:
					if not child in self._movable_lists[self._leafs[-(node+1)].cluster]:
						self._movable_lists[self._leafs[-(node+1)].cluster].append(child)
				else:
					if   areas[0] < 0: areas[0] = self._leafs[-(node+1)].area
					elif areas[1] < 0: areas[1] = self._leafs[-(node+1)].area
	
	cdef void _locate_child(self, child, int* areas):
		cdef float box[6]
		cdef int   i
		(<_Body>child)._out(box)
		for i from 0 <= i < 3:
			box[i+3]= box[i]
		# Remove movable from all clusters's lists
		if areas == NULL:
			for i from 0 <= i < self._nb_cluster:
				try:
					self._movable_lists[i].remove(child)
				except: pass
		else:
			areas[0] = -1
			areas[1] = -1
		# Get movable bounding box and sphere
		(<_Body>child)._get_box(box, self._matrix)
		self._locate_box(child, box, 0, areas)
	
	cdef __getcstate__(self):
		cdef Chunk* chunk
		cdef int    i
		
		chunk = get_chunk()
		chunk_add_int_endian_safe(chunk, self._nb_plane)
		chunk_add_int_endian_safe(chunk, self._nb_brush)
		chunk_add_int_endian_safe(chunk, self._nb_node)
		chunk_add_int_endian_safe(chunk, self._nb_leaf)
		chunk_add_int_endian_safe(chunk, self._nb_cluster)
		chunk_add_int_endian_safe(chunk, self._row_length)
		for i from 0 <= i < self._nb_plane:
			chunk_add_floats_endian_safe(chunk, self._planes[i].coords, 4)
			chunk_add_int_endian_safe(chunk, self._planes[i].signbits)
		for i from 0 <= i < self._nb_brush:
			chunk_add_int_endian_safe(chunk, self._brushes[i].nb_plane)
			chunk_add_ints_endian_safe(chunk, self._brushes[i].planes, self._brushes[i].nb_plane)
		for i from 0 <= i < self._nb_node:
			chunk_add_int_endian_safe(chunk, self._nodes[i].front)
			chunk_add_int_endian_safe(chunk, self._nodes[i].back)
			chunk_add_int_endian_safe(chunk, self._nodes[i].plane)
		for i from 0 <= i < self._nb_leaf:
			chunk_add_int_endian_safe(chunk, self._leafs[i].cluster)
			chunk_add_int_endian_safe(chunk, self._leafs[i].area)
			chunk_add_int_endian_safe(chunk, self._leafs[i].model_part)
			chunk_add_int_endian_safe(chunk, self._leafs[i].nb_brush)
			chunk_add_ints_endian_safe(chunk, self._leafs[i].brushes, self._leafs[i].nb_brush)
			chunk_add_floats_endian_safe(chunk, self._leafs[i].sphere, 4)
			chunk_add_floats_endian_safe(chunk, self._leafs[i].box, 6)
		for i from 0 <= i < self._nb_cluster:
			chunk_add_int_endian_safe(chunk, self._clusters[i])
		chunk_add_chars_endian_safe(chunk, <char*> self._vis_data, self._nb_cluster*self._row_length)
		return _World.__getcstate__(self), drop_chunk_to_string(chunk)
	
	cdef void __setcstate__(self, object cstate):
		cdef Chunk* chunk
		cdef int    i
		
		_World.__setcstate__(self, cstate[0])
		chunk = string_to_chunk(cstate[1])
		chunk_get_int_endian_safe(chunk, &self._nb_plane)
		chunk_get_int_endian_safe(chunk, &self._nb_brush)
		chunk_get_int_endian_safe(chunk, &self._nb_node)
		chunk_get_int_endian_safe(chunk, &self._nb_leaf)
		chunk_get_int_endian_safe(chunk, &self._nb_cluster)
		chunk_get_int_endian_safe(chunk, &self._row_length)
		self._planes   = <_BSPPlane*> malloc(self._nb_plane   * sizeof(_BSPPlane))
		self._brushes  = <_BSPBrush*> malloc(self._nb_brush   * sizeof(_BSPBrush))
		self._nodes    = <_BSPNode*>  malloc(self._nb_node    * sizeof(_BSPNode))
		self._leafs    = <_BSPLeaf*>  malloc(self._nb_leaf    * sizeof(_BSPLeaf))
		self._clusters = <int*>       malloc(self._nb_cluster * sizeof(int))
		for i from 0 <= i < self._nb_plane:
			chunk_get_floats_endian_safe(chunk,  self._planes[i].coords, 4)
			chunk_get_int_endian_safe   (chunk, &(self._planes[i].signbits))
		for i from 0 <= i < self._nb_brush:
			chunk_get_int_endian_safe   (chunk, &(self._brushes[i].nb_plane))
			self._brushes[i].planes = <int*> malloc(self._brushes[i].nb_plane * sizeof(int))
			chunk_get_ints_endian_safe(chunk,  self._brushes[i].planes, self._brushes[i].nb_plane)
		for i from 0 <= i < self._nb_node:
			chunk_get_int_endian_safe   (chunk, &(self._nodes[i].front))
			chunk_get_int_endian_safe   (chunk, &(self._nodes[i].back))
			chunk_get_int_endian_safe   (chunk, &(self._nodes[i].plane))
		for i from 0 <= i < self._nb_leaf:
			chunk_get_int_endian_safe   (chunk, &(self._leafs[i].cluster))
			chunk_get_int_endian_safe   (chunk, &(self._leafs[i].area))
			chunk_get_int_endian_safe   (chunk, &(self._leafs[i].model_part))
			chunk_get_int_endian_safe   (chunk, &(self._leafs[i].nb_brush))
			self._leafs[i].brushes = <int*> malloc(self._leafs[i].nb_brush * sizeof(int))
			chunk_get_ints_endian_safe(chunk, self._leafs[i].brushes, self._leafs[i].nb_brush)
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
		self._areamask_modified = 0
		self._old_cluster      = -1
		self._batched_clusters = []
		self._batched_children = []
		drop_chunk(chunk)
	
	cdef void _batch_cluster(self, int index):
		cdef float box[6]
		if self._leafs[self._clusters[index]].model_part >= 0:
			# test cluster's bounding box against frustum
			point_by_matrix_copy(box,   self._leafs[self._clusters[index]].box,   self._parent._root_matrix())
			point_by_matrix_copy(box+3, self._leafs[self._clusters[index]].box+3, self._parent._root_matrix())
			if box_in_frustum(renderer.root_frustum, box) > 0:
				self._model._batch_part(self, self._leafs[self._clusters[index]].model_part)
			for child in self._movable_lists[index]:
				if not child in self._batched_children: self._batched_children.append(child)
	
	cdef void _batch(self, CoordSyst coordsyst):
		cdef Context   old_context
		cdef CoordSyst child
		cdef float     camera_coord[3]
		cdef int       node, leaf, cam_cluster, cam_area, i
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
				print "camera in invalid leaf !!!"
				return
			# Batch all clusters visible from this one and childrens inside them
			for i from 0 <= i < self._nb_cluster:
				if self._is_visible_from(self._clusters[cam_cluster], self._clusters[i]):
					self._batch_cluster(i)
					self._batched_clusters.append(i)
		self._model._batch_end(self)
		for child in self._batched_children:
			#print "rendering one child"
			child._batch(self)
		renderer.current_context = old_context
	
	# Raypicking function, not ready yet, still need a lots of work...
	#cdef int _raypick_leaf(self, RaypickData data, int leaf, int category):
		#global _ray_start
		#global _ray_end
		#global _ray_length
		#cdef int i, j, brush_index, plane_index, brush_hit_plane, hit_plane
		#cdef int start_out, end_out, found_something
		#cdef float start_dist, end_dist, start_fraction, end_fraction, output_fraction, fraction
		#cdef float z, root_z
		#cdef CoordSyst something
		#found_something = 0
		## Raypick against the brushes
		#if self._leafs[leaf].nb_brush > 0:
			#output_fraction = 1.
			## Test every brush in the leaf
			#for i from 0 <= i < self._leafs[leaf].nb_brush:
				#brush_index = self._leafs[leaf].brushes[i]
				#start_fraction = -1.
				#end_fraction   =  1.
				#start_out      = 0
				#end_out        = 0
				## Test every plan of the brush
				#for j from 0 <= j < self._brushes[brush_index].nb_plane:
					## Test ray start and end against the plane
					#plane_index = self._brushes[brush_index].planes[j]
					#start_dist = self._distance_to(_ray_start, plane_index)
					#end_dist   = self._distance_to(_ray_end,   plane_index)
					#if start_dist > 0.: start_out = 1
					#if end_dist   > 0.: end_out   = 1
					## If both start and end are in front of the plane then the ray does not collide with this brush
					#if start_dist >= 0. and end_dist >= 0.:
						#break
					## If both start and end behind the plane then check the next plane
					#if start_dist < 0. and end_dist < 0.:
						#continue
					## If the ray cross the plane we compute the fractions
					#if start_dist > end_dist:
						#fraction = (start_dist - 1./32.) / (start_dist - end_dist)
						#if fraction > start_fraction:
							#start_fraction = fraction
							#brush_hit_plane = plane_index
					#else:
						#fraction = (start_dist + 1./32.) / (start_dist - end_dist)
						#if fraction < end_fraction: end_fraction = fraction
				#else:
					## Check that the ray start point is outside of the brush
					## If it is inside we do not collide but this case should never happend
					#if start_out != 0:
						## If start_fraction < end_fraction then the ray don't collide the brush, this case is not an error
						#if start_fraction < end_fraction and start_fraction > -1.:
							## The ray collide with this brush !
							## Is this brush closer than the one we checked befor ?
							#if start_fraction < output_fraction:
								#output_fraction = start_fraction
								#hit_plane = brush_hit_plane
			## We checked every brush in that leaf, did we collide with anything ?
			#if output_fraction < 1.:
				## Yes, we fill in the raypick data structure
				#found_something = 1
				#z      = _ray_length * output_fraction
				#root_z = self._distance_out(z)
				#if (data.result_coordsyst is None) or (fabs(root_z) < fabs(data.root_result)):
					#data.result      = z
					#data.root_result = root_z
					#data.result_coordsyst = self
					#memcpy(data.normal, self._planes[hit_plane].coords, 3 * sizeof(float))
		## Raypick againt the world's childrens in this leaf, if this leaf is a cluster
		#if self._leafs[leaf].cluster >= 0:
			#something = data.result_coordsyst
			#for child in self._movable_lists[self._leafs[leaf].cluster]:
				#child._raypick(data, self, category)
			#if data.result_coordsyst != something:
				#found_something = 1
		## If found_something = 1 that means the ray collided wth something in this leaf
		#return found_something
	
	#cdef int _raypick_node(self, RaypickData data, float* start, float* end, float start_fraction, float end_fraction, int node, int category):
		#cdef float start_dist, end_dist
		#cdef float midle_fraction, fraction1, fraction2, invert
		#cdef float midle[3]
		#cdef int   side, i
		## Test ray start and end against the plane
		#start_dist = self._distance_to(start, self._nodes[node].plane)
		#end_dist   = self._distance_to(end,   self._nodes[node].plane)
		## If both start and end are in front of the plane
		#if start_dist >= 0. and end_dist >= 0.:
			#if self._nodes[node].front < 0:
				#i = self._raypick_leaf(data, -(self._nodes[node].front+1), category)
			#else:
				#i = self._raypick_node(data, start, end, start_fraction, end_fraction, self._nodes[node].front, category)
		## If both start and end behind the plane
		#if start_dist < 0. and end_dist < 0.:
			#if self._nodes[node].back < 0:
				#i = self._raypick_leaf(data, -(self._nodes[node].back+1), category)
			#else:
				#i = self._raypick_node(data, start, end, start_fraction, end_fraction, self._nodes[node].back, category)
		## Else the ray is crossing the plane
		#else:
			## Compute ray fractions in front of and behind the plane
			## We will first check the side where the start of the ray is
			#if   start_dist < end_dist:
				#side = 1
				#invert    = 1. / (end_dist - start_dist)
				#fraction1 = (start_dist + 1./32.) * invert
				#fraction2 = (start_dist - 1./32.) * invert
				#if   fraction1 < 0.: fraction1 = 0.
				#elif fraction1 > 1.: fraction1 = 1.
				#if   fraction2 < 0.: fraction2 = 0.
				#elif fraction2 > 1.: fraction2 = 1.
			#elif start_dist > end_dist:
				#side = 0
				#invert    = 1. / (end_dist - start_dist)
				#fraction1 = (start_dist + 1./32.) * invert
				#fraction2 = (start_dist - 1./32.) * invert
				#if   fraction1 < 0.: fraction1 = 0.
				#elif fraction1 > 1.: fraction1 = 1.
				#if   fraction2 < 0.: fraction2 = 0.
				#elif fraction2 > 1.: fraction2 = 1.
			#else:
				#side = 0
				#fraction1 = 1.
				#fraction2 = 0.
			## Compute the midle point for the first side
			#midle_fraction = start_fraction + ((end_fraction - start_fraction) * fraction1)
			#for i from 0 <= i < 3:
				#midle[i] = start[i] + (fraction1 * (end[i] - start[i]))
			## Check the first side
			#if self._nodes[node][side] < 0:
				## This side is a leaf
				#i = self._raypick_leaf(data, -(self._nodes[node][side]+1), category)
			#else:
				## This side is a node
				#i = self._raypick_node(data, start, midle, start_fraction, midle_fraction, self._nodes[node][side], category)
			## If the raypick function found something in this leaf it is useless to check the other side
			#if i != 0: return i
			## Compute the midle point for the second side
			#midle_fraction = start_fraction + ((end_fraction - start_fraction) * fraction2)
			#for i from 0 <= i < 3:
				#midle[i] = start[i] + (fraction2 * (end[i] - start[i]))
			## Check the first side
			#if self._nodes[node][not side] < 0: # Hacky hacky...
				## This side is a leaf
				#i = self._raypick_leaf(data, -(self._nodes[node][not side]+1), category)
			#else:
				## This side is a node
				#i = self._raypick_node(data, start, midle, start_fraction, midle_fraction, self._nodes[node][not side], category)
		#return i
	
	cdef void _raypick(self, RaypickData raypick_data, CoordSyst raypickable, int category):
		pass
	
	cdef int _raypick_b(self, RaypickData raypick_data, CoordSyst raypickable, int category):
		pass
	
	cdef void _collect_raypickables(self, Chunk* items, float* rsphere, float* sphere, int category):
		pass
	
	def add(self, CoordSyst child not None):
		_World.add(self, child)
		if isinstance(child, _Body) and child.model:
			print "locate one child"
			self._locate_child(child, NULL)
	
	def remove(self, CoordSyst child not None):
		_World.remove(self, child)
		cdef int i
		for i from 0 <= i < self._nb_cluster:
			try:
				self._movable_lists[i].remove(child)
			except: pass
	
	def insert(self, int index, CoordSyst child not None):
		_World.insert(self, index, child)
		if isinstance(child, _Body) and child.model:
			self._locate_child(child, NULL)
	
	def to_model(self):
		pass
	
	def begin_round(self):
		_World.begin_round(self)
		for child in self.children:
			if isinstance(child, _Body) and child.model and not child.static:
				self._locate_child(child, NULL)
	
	def locate(self, CoordSyst child not None):
		"""BSPWorld.locate(CHILD not None) -> int area1, int area2

Find in wich area(s) the given CoordSyst is. The CoordSyst must be one of the BSP World's children.
A CoordSyst can not be in more than 2 areas at the same time. If it is only in one area, area2 will be negativ.
"""
		cdef int areas[2]
		if isinstance(child, Body):
			self._locate_child(child, areas)
			return areas[0], areas[1]
	
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
		cdef int i, j
		_World.__init__(self, parent, model, opt)
		# Register planes
		self._nb_plane = len(planes)
		self._planes = <_BSPPlane*> malloc(self._nb_plane * sizeof(_BSPPlane))
		for i from 0 <= i < self._nb_plane:
			self._planes[i].coords[0] = planes[i].a
			self._planes[i].coords[1] = planes[i].b
			self._planes[i].coords[2] = planes[i].c
			self._planes[i].coords[3] = planes[i].d
			# Compute signbits (used for fast box against plan test)
			self._planes[i].signbits  = 0
			for j from 0 <= j < 3:
				if self._planes[i].coords[j] < 0.: self._planes[i].signbits = self._planes[i].signbits | (1 << j)
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
			if leafs[i].nb_leaf_face > 0 and leafs[i].cluster >= 0:
				self._leafs[i].model_part = leafs[i].model_part
				if self._leafs[i].model_part == -1:
					print "BSP World Error : leaf / model_part error"
				self._leafs[i].nb_brush   = len(leafs[i].brush_indices)
				self._leafs[i].brushes    = <int*> malloc(self._leafs[i].nb_brush * sizeof(int))
				for j from 0 <= j < self._leafs[i].nb_brush:
					self._leafs[i].brushes[j] = leafs[i].brush_indices[j]
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
				self._leafs[i].brushes    = NULL
				self._leafs[i].nb_brush   = 0
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
		for i from 0 <= i < self._nb_node:
			self._nodes[i].plane = nodes[i].plane
			self._nodes[i].front = nodes[i].front
			self._nodes[i].back  = nodes[i].back
		# Register brushes
		self._nb_brush = len(brushes)
		self._brushes  = <_BSPBrush*> malloc(self._nb_brush * sizeof(_BSPBrush))
		for i from 0 <= i < self._nb_brush:
			self._brushes[i].nb_plane = len(brushes[i].plane_indices)
			self._brushes[i].planes   = <int*> malloc(self._brushes[i].nb_plane * sizeof(int))
			for j from 0 <= j < self._brushes[i].nb_plane:
				self._brushes[i].planes[j] = brushes[i].plane_indices[j]
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
		pass
		"""
		free(self._clusters)
		free(self._leafs)
		free(self._nodes)
		free(self._vis_data)
		_World.__dealloc__(self)
		"""
