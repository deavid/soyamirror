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

#ctypedef struct TerrainVertex:
#  float texcoord[2]
#  float normal  [3]
#  float coord   [3]
#  Pack* pack

cdef struct _TerrainTri

#cdef struct _TerrainPatch:
#  float     sphere[4]
#  char      level # precision level for rendering
#  _TerrainTri* tri_top
#  _TerrainTri* tri_left
#  _TerrainTri* tri_right
#  _TerrainTri* tri_bottom
#  int       visible
#ctypedef _TerrainPatch TerrainPatch

#cdef struct _TerrainTri:
#  char        level
#  float       normal[3]
#  float       sphere[4]
#  # 3 vertices that determine the triangle. turn right to left (CCW)
#  TerrainVertex* v1 # apex vertex
#  TerrainVertex* v2 # right vertex for the apex
#  TerrainVertex* v3 # left vertex for the apex
#  _TerrainTri*   parent
#  _TerrainTri*   left_child
#  _TerrainTri*   right_child
#  _TerrainTri*   left_neighbor
#  _TerrainTri*   right_neighbor
#  _TerrainTri*   base_neighbor
#  TerrainPatch*  patch
#ctypedef _TerrainTri TerrainTri

cdef void terrain_tri_dealloc(TerrainTri* tri):
	if terrain_tri_has_child(tri):
		terrain_tri_dealloc(tri.left_child)
		terrain_tri_dealloc(tri.right_child)
	free(tri)

cdef int terrain_tri_has_child(TerrainTri* tri):
	return tri.left_child != NULL

cdef int terrain_tri_diamond(TerrainTri* tri):
	return (tri.base_neighbor == NULL) or ((tri.v2 == tri.base_neighbor.v3) and (tri.v3 == tri.base_neighbor.v2))

cdef void terrain_tri_sphere(float r[4], float* p1, float* p2, float* p3):
	cdef float x, y, z, f, d
	# fast function to compute a bounding sphere for 3 points 
	# (faster but rougher than sphere_from_points())
	f = 1.0 / 3.0
	r[0] = (p1[0] + p2[0] + p3[0]) * f
	r[1] = (p1[1] + p2[1] + p3[1]) * f
	r[2] = (p1[2] + p2[2] + p3[2]) * f
	x = p1[0] - r[0]
	y = p1[1] - r[1]
	z = p1[2] - r[2]
	d = x * x + y * y + z * z
	x = p2[0] - r[0]
	y = p2[1] - r[1]
	z = p2[2] - r[2]
	f = x * x + y * y + z * z
	if f > d: d = f
	x = p3[0] - r[0]
	y = p3[1] - r[1]
	z = p3[2] - r[2]
	f = x * x + y * y + z * z
	if f > d: d = f
	r[3] = sqrt(d)


cdef TerrainTri* terrain_get_tri():
	# XXX try to re-use TerrainTri structures
	return <TerrainTri*> malloc(sizeof(TerrainTri))

cdef void terrain_tri_drop(TerrainTri* tri):
	# XXX try to re-use TerrainTri structures
	free(tri)
	
cdef TerrainTri* terrain_create_tri(TerrainVertex* v1, TerrainVertex* v2, TerrainVertex* v3, TerrainPatch* patch):
	cdef TerrainTri* tri
	tri               = terrain_get_tri()
	tri.v1            = v1
	tri.v2            = v2
	tri.v3            = v3
	tri.patch         = patch
	tri.level         = 0
	tri.parent        = NULL
	tri.left_child    = NULL
	tri.right_child   = NULL
	tri.base_neighbor = NULL
	terrain_tri_sphere (tri.sphere, v1.coord, v2.coord, v3.coord)
	face_normal     (tri.normal, v1.coord, v2.coord, v3.coord)
	vector_normalize(tri.normal)
	return tri

cdef TerrainTri* terrain_create_child_tri(TerrainVertex* v1, TerrainVertex* v2, TerrainVertex* v3, TerrainTri* parent):
	cdef TerrainTri* tri
	tri             = terrain_get_tri()
	tri.v1          = v1
	tri.v2          = v2
	tri.v3          = v3
	tri.parent      = parent
	tri.level       = parent.level + 1
	tri.patch       = parent.patch
	tri.left_child  = NULL
	tri.right_child = NULL
	terrain_tri_sphere (tri.sphere, v1.coord, v2.coord, v3.coord)
	face_normal     (tri.normal, v1.coord, v2.coord, v3.coord)
	vector_normalize(tri.normal)
	return tri

cdef void terrain_tri_update_neighbor_after_split (TerrainTri* tri):
	tri.left_child.left_neighbor    = tri.right_child
	if (tri.left_neighbor != NULL) and terrain_tri_has_child(tri.left_neighbor):
		tri.left_child.base_neighbor  = tri.left_neighbor.right_child
	else:
		tri.left_child.base_neighbor  = tri.left_neighbor
		
	tri.right_child.right_neighbor  = tri.left_child
	if (tri.right_neighbor != NULL) and terrain_tri_has_child(tri.right_neighbor):
		tri.right_child.base_neighbor = tri.right_neighbor.left_child
	else:
		tri.right_child.base_neighbor = tri.right_neighbor
	
	if tri.base_neighbor == NULL:
		tri.left_child.right_neighbor = NULL
		tri.right_child.left_neighbor = NULL
	else:
		tri.left_child.right_neighbor = tri.base_neighbor.right_child
		tri.right_child.left_neighbor = tri.base_neighbor.left_child
		
	if tri.left_neighbor != NULL:
		if tri.v1 == tri.left_neighbor.v1:
			tri.left_neighbor.right_neighbor = tri.left_child
		else:
			tri.left_neighbor.base_neighbor = tri.left_child
			if tri.left_neighbor.parent != NULL:
				tri.left_neighbor.parent.right_neighbor = tri.left_child
				
	if tri.right_neighbor != NULL:
		if tri.v1 == tri.right_neighbor.v1:
			tri.right_neighbor.left_neighbor = tri.right_child
		else:
			tri.right_neighbor.base_neighbor = tri.right_child
			if tri.right_neighbor.parent != NULL:
				tri.right_neighbor.parent.left_neighbor = tri.right_child
				
cdef void terrain_tri_force_split(TerrainTri* tri, TerrainVertex* apex):
	tri.left_child  = terrain_create_child_tri(apex, tri.v1, tri.v2, tri)
	tri.right_child = terrain_create_child_tri(apex, tri.v3, tri.v1, tri)
	terrain_tri_update_neighbor_after_split(tri)
	
cdef void terrain_tri_update_neighbor_after_merge (TerrainTri* tri):
	if tri.left_neighbor != NULL:
		if tri.left_neighbor.v1 == tri.v1:
			tri.left_neighbor.right_neighbor = tri
			if terrain_tri_has_child(tri.left_neighbor): tri.left_neighbor.right_child.base_neighbor = tri
		else:
			tri.left_neighbor.base_neighbor = tri
			if tri.left_neighbor.parent != NULL:
				tri.left_neighbor.parent.right_neighbor = tri
	if tri.right_neighbor != NULL:
		if tri.right_neighbor.v1 == tri.v1:
			tri.right_neighbor.left_neighbor = tri
			if terrain_tri_has_child(tri.right_neighbor):
				tri.right_neighbor.left_child.base_neighbor = tri
		else:
			tri.right_neighbor.base_neighbor = tri
			if tri.right_neighbor.parent != NULL:
				tri.right_neighbor.parent.left_neighbor = tri

cdef void terrain_get_height_at_factors(TerrainVertex* v1, TerrainVertex* v2, TerrainVertex* v3, float x, float z, float* k, float* t):
	cdef float  u[2], w[2], q
	cdef float* ptr
	ptr  = v1.coord
	u[0] = v2.coord[0] - ptr[0]
	u[1] = v2.coord[2] - ptr[2]
	w[0] = v3.coord[0] - ptr[0]
	w[1] = v3.coord[2] - ptr[2]
	q    = 1.0 / (w[0] * u[1] - w[1] * u[0])
	t[0] = (  (x - ptr[0]) * u[1] - (z - ptr[2]) * u[0]) * q
	k[0] = (- (x - ptr[0]) * w[1] + (z - ptr[2]) * w[0]) * q


cdef void terrain_drawColor_radeon(float* vect):
	glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, vect)
	
cdef void noop():
	pass

cdef void terrain_disableColor_radeon():
	#glColor4fv(white) # XXX really needed ?
	glDisable(GL_COLOR_MATERIAL)
	glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, white)
	
cdef void terrain_enableColor_radeon():
	glEnable(GL_COLOR_MATERIAL)

#ctypedef void (*terrain_drawColor_FUNC   )(float*)
#ctypedef void (*terrain_disableColor_FUNC)()
#ctypedef void (*terrain_enableColor_FUNC )()

cdef terrain_drawColor_FUNC    terrain_drawColor
cdef terrain_disableColor_FUNC terrain_disableColor
cdef terrain_enableColor_FUNC  terrain_enableColor

terrain_drawColor    = glColor4fv
terrain_disableColor = noop
terrain_enableColor  = noop


# XXX inline this
cdef void SET_COLOR_OPAQUE(_Terrain self, int index):
	if self._colors == NULL: terrain_drawColor(renderer.current_material._diffuse)
	else:                    terrain_drawColor(self._colors + index)

# XXX inline this
cdef void SET_COLOR_ALPHA(_Terrain self, int index):
	cdef float  ccc[4]
	cdef float* color
	if self._colors == NULL: color = renderer.current_material._diffuse
	else:                    color = self._colors + index
	ccc[0] = color[0]
	ccc[1] = color[1]
	ccc[2] = color[2]
	ccc[3] = 0.0
	terrain_drawColor(ccc)


cdef class _Terrain(CoordSyst):
	#cdef             _materials
	#cdef TerrainVertex* _vertices
	#cdef char*       _vertex_options
	#cdef int*        _vertex_colors
	#cdef float*      _normals # full LOD triangles normals
	#cdef int         _nb_colors
	#cdef float*      _colors # vertices colors
	#cdef int         _nb_vertex_width # size_width and size_depth must be (2^n) + 1
	#cdef int         _nb_vertex_depth # or I don't know what happen (crash?)
	#cdef int         _patch_size
	#cdef int         _max_level
	#cdef float       _texture_factor # a factor that multiply the texture coordinates
	#cdef float       _scale_factor # a factor to decide when the triangle must split (higher value means more accuracy)
	#cdef float       _split_factor
	#cdef int         _nb_patchs
	#cdef int         _nb_patch_width
	#cdef int         _nb_patch_depth
	#cdef TerrainPatch*  _patchs

	property width:
		def __get__(self):
			return self._nb_vertex_width
	property depth:
		def __get__(self):
			return self._nb_vertex_depth
		
	property patch_size:
		def __get__(self):
			return self._patch_size
		def __set__(self, x):
			self._patch_size = x
			if self._option & TERRAIN_INITED: self._option = self._option - TERRAIN_INITED
			
	property has_vertex_options:
		def __get__(self):
			return self._option & TERRAIN_VERTEX_OPTIONS
		
	property split_factor:
		def __get__(self):
			return self._split_factor
		def __set__(self, x):
			self._split_factor = x
		
	property scale_factor:
		def __get__(self):
			return self._scale_factor
		def __set__(self, x):
			self._scale_factor = x
			self._option = self._option & ~TERRAIN_INITED
			self._compute_coords()
			
	property texture_factor:
		def __get__(self):
			return self._texture_factor
		def __set__(self, x):
			self._texture_factor = x
			self._compute_coords()
			
	property raypick_with_LOD:
		def __get__(self):
			return self._option & TERRAIN_REAL_LOD_RAYPICK
		def __set__(self, x):
			if x: self._option = self._option |  TERRAIN_REAL_LOD_RAYPICK
			else: self._option = self._option & ~TERRAIN_REAL_LOD_RAYPICK
			
	cdef TerrainVertex* _get_vertex(self, int x, int z):
		# XXX inline / macroize (how ?) this ?
		return self._vertices + (x + z * self._nb_vertex_width)
	
	cdef void _check_size(self):
		cdef int i, d
		i = 0
		while 1:
			d = (1 << i) + 1
			if self._nb_vertex_width <= d:
				if self._nb_vertex_width < d: print "WARNING Terrain size width must be (2^n) + 1"
				break
			i = i + 1
			
		i = 0
		while 1:
			d = (1 << i) + 1
			if self._nb_vertex_depth <= d:
				if self._nb_vertex_depth < d: print "WARNING Terrain size depth must be (2^n) + 1"
				break
			i = i + 1
			
	#def __new__(self, int width, int depth):
		
	def __init__(self, _World parent = None, int width = 0, int depth = 0, float scale_factor = 1.0):
		cdef TerrainVertex* v
		cdef int         i
		cdef int         nb
		
		CoordSyst.__init__(self, parent)
		if depth == 0: depth = width
		
		self._nb_vertex_width = width
		self._nb_vertex_depth = depth
		self._patch_size      = 8
		self._texture_factor  = 1.0
		self._scale_factor    = scale_factor
		self._split_factor    = 2.0
		self._materials       = [_DEFAULT_MATERIAL]
		if (width != 0) and (depth != 0):
			nb = self._nb_vertex_width * self._nb_vertex_depth
			self._check_size()
			self._vertices = <TerrainVertex*> malloc(nb * sizeof(TerrainVertex))
			for i from 0 <= i < nb:
				v = self._vertices + i
				v.coord[1] = 0
				v.pack = _DEFAULT_MATERIAL._pack(FACE_TRIANGLE)
			self._normals = <float*> malloc((self._nb_vertex_width - 1) * (self._nb_vertex_depth - 1) * 6 * sizeof(float))
		self._compute_coords()
		
		
	cdef void _free_patchs(self):
		cdef TerrainPatch* patch
		cdef int        i
		for i from 0 <= i < self._nb_patchs:
			patch = self._patchs + i
			terrain_tri_dealloc(patch.tri_top)
			terrain_tri_dealloc(patch.tri_left)
			terrain_tri_dealloc(patch.tri_right)
			terrain_tri_dealloc(patch.tri_bottom)
		free(self._patchs)
		self._patchs = NULL
		
		
	def __dealloc__(self):
		self._free_patchs()
		if self._materials: self._materials.__imul__(0)
		free(self._vertices)
		free(self._colors)
		free(self._normals)
		free(self._vertex_options)
		free(self._vertex_colors)
		
	def from_image(self, _Image image):
		cdef GLubyte* ptr
		cdef int nb, i
		self._nb_vertex_width = image.width
		self._nb_vertex_depth = image.height
		self._check_size()
		if self._vertices != NULL: free(self._vertices)
		nb = self._nb_vertex_width * self._nb_vertex_depth
		self._vertices = <TerrainVertex*> malloc(nb * sizeof(TerrainVertex))
		for i from 0 <= i < nb: (self._vertices + i).pack = _DEFAULT_MATERIAL._pack(FACE_TRIANGLE)
		self._normals = <float*> malloc((self._nb_vertex_width - 1) * (self._nb_vertex_depth - 1) * 6 * sizeof(float))
		if   image.nb_color == 3:
			for i from 0 <= i < nb:
				ptr = image._pixels + i * 3
				(self._vertices + i).coord[1] = (ptr[0] + ptr[1] + ptr[2]) / (3.0 * 255.0)
		elif image.nb_color == 4:
			for i from 0 <= i < nb:
				ptr = image._pixels + i * 4
				(self._vertices + i).coord[1] = (ptr[0] + ptr[1] + ptr[2] + ptr[3]) / (4.0 * 255.0)
		elif image.nb_color == 1:
			for i from 0 <= i < nb:
				(self._vertices + i).coord[1] = image._pixels[i] / 255.0
				
		self._option = self._option & ~TERRAIN_INITED
		self._compute_coords()
		
	cdef void _add_material(self, _Material material):
		if material in self._materials: return
		self._materials.append(material)
		self._option = self._option & ~TERRAIN_INITED

	def set_material_from_image(self, _Image image, materials):
		cdef int i, m, w, h, hoffset
		cdef TerrainVertex* vertex
		cdef Pack*       pack[256]
		if (self._nb_vertex_width != image.width) or \
			 (self._nb_vertex_depth != image.height) :
			print "WARNING Material map size must equal terrain size"
			return
		if image.nb_color != 1 :
			print "WARNING Material map must be greyscale or indexed"
			return
		if image.palette : m = len(image.palette)/3
		else : m = 256
		if len(materials) < m :
			print "WARNING Material map has more colors than provided materials"
			return
		for i from 0 <= i < m :
			self._add_material(<_Material> (materials[i]))
			pack[i] =  (<_Material> (materials[i]))._pack(FACE_TRIANGLE)
		for h from 0 <= h < self._nb_vertex_depth :
			hoffset = h * self._nb_vertex_width
			for w from 0 <= w < self._nb_vertex_width :
				vertex = self._get_vertex(w, h)
				i = image._pixels[hoffset+w]
				vertex.pack = pack[i]
		
	def set_material_layer(self, _Material material, float start, float end):
		cdef int            i, j
		cdef TerrainVertex* vertex
		cdef Pack*          pack
		self._add_material(material)
		pack = material._pack(FACE_TRIANGLE)
		for j from 0 <= j < self._nb_vertex_depth:
			for i from 0 <= i < self._nb_vertex_width:
				vertex = self._get_vertex(i, j)
				if (vertex.coord[1] >= start) and (vertex.coord[1] <= end): vertex.pack = pack
		self._option = self._option & ~TERRAIN_INITED
		
	def set_material_layer_angle(self, _Material material, float start, float end, float angle_min, float angle_max):
		cdef int         i, j
		cdef TerrainVertex* vertex
		cdef Pack*       pack
		cdef float       f, v[3]
		v[0] = 0.0; v[1] = 1.0; v[2] = 0.0 # { 0.0, 1.0, 0.0 }
		# ensure the normals are computed
		if not(self._option & TERRAIN_INITED): self._init()
		# angle 0 is horizontal
		self._add_material(material)
		pack = material._pack(FACE_TRIANGLE)
		for j from 0 <= j < self._nb_vertex_depth:
			for i from 0 <= i < self._nb_vertex_width:
				vertex = self._get_vertex(i, j)
				f = fabs(to_degrees(vector_angle(vertex.normal, v)))
				if (vertex.coord[1] >= start) and (vertex.coord[1] <= end) and (angle_min <= f <= angle_max): vertex.pack = pack
		self._option = self._option & ~TERRAIN_INITED
		
		
	def get_normal(self, int x, int z):
		cdef TerrainVertex* vertex
		vertex = self._get_vertex(x, z)
		return vertex.normal[0], vertex.normal[1], vertex.normal[2]
	
	def get_height(self, int x, int z):
		return self._get_height(x, z)
	
	cdef float _get_height(self, int x, int z):
		if (x < 0) or (z < 0) or (x >= self._nb_vertex_width) or (z >= self._nb_vertex_depth): return 0.0
		return self._get_vertex(x, z).coord[1]
	
	def get_material(self, int x, int z):
		if (x < 0) or (z < 0) or (x >= self._nb_vertex_width) or (z >= self._nb_vertex_depth): return None
		return <_Material> (self._get_vertex(x, z).pack.material_id)
	
	cdef void _set_height (self, int x, int z, float height):
		if (x < 0) or (z < 0) or (x >= self._nb_vertex_width) or (z >= self._nb_vertex_depth): return
		self._get_vertex(x, z).coord[1] = height

	def set_height(self, int x, int z, float height):
		if (x < 0) or (z < 0) or (x >= self._nb_vertex_width) or (z >= self._nb_vertex_depth): return
		self._get_vertex(x, z).coord[1] = height
		
	def multiply_height(self, float factor):
		cdef int         i, j
		cdef TerrainVertex* vertex
		for j from 0 <= j < self._nb_vertex_depth:
			for i from 0 <= i < self._nb_vertex_width:
				vertex = self._get_vertex(i, j)
				vertex.coord[1] = vertex.coord[1] * factor
				
	def add_height(self, float height):
		cdef TerrainVertex* vertex
		cdef int         i, j
		for j from 0 <= j < self._nb_vertex_depth:
			for i from 0 <= i < self._nb_vertex_width:
				vertex = self._get_vertex(i, j)
				vertex.coord[1] = vertex.coord[1] + height

	def set_material(self, int x, int z, _Material material):
		cdef Pack* pack
		self._add_material(material)
		pack = material._pack(FACE_TRIANGLE)
		if (0 <= x < self._nb_vertex_width) and (0 <= z < self._nb_vertex_depth):
			self._get_vertex(x, z).pack = pack
			
	def remove_colors(self):
		"""Terrain.remove_colors()

Removes all colors, from all vertices that have colors."""
		free(self._colors)
		free(self._vertex_colors)
		self._nb_colors        = 0
		self._colors           = NULL
		self._vertex_colors    = NULL
		self._option = self._option & (~TERRAIN_COLORED)
		
	def get_vertex_option(self, int x, int z):
		"""Terrain.get_vertex_option(X, Z) => (HIDDEN, NON_SOLID, FORCE_PRESENCE)

Returns the vertex options associated with the vertex of coordinates X, Z, as a 4-int tuple.
See Terrain.set_vertex_option for the available options."""
		cdef int option
		self._check_vertex_options()
		option = self._vertex_options[x + z * self._nb_vertex_width]
		return option & TERRAIN_VERTEX_HIDDEN, option & TERRAIN_VERTEX_NON_SOLID, option & TERRAIN_VERTEX_FORCE_PRESENCE
	
	def set_vertex_option(self, int x, int z, int hidden = 0, int non_solid = 0, int force_presence = 0):
		"""Terrain.set_vertex_option(X, Z, HIDDEN, NON_SOLID, FORCE_PRESENCE)

Sets the vertex options associated with the vertex of coordinates X, Z.
These options are usefull to create hole in the terrain, or non-rectangular terrain.

Options are (all option are boolean, and default is 0 for all):
	- Hidden : hide the vertex (a triangle whose 3 vertices hidden is not drawn)
	- Non-solid : the vertex is non-solid (raypicking is disabled on a triangle whose 3 vertices are non-solid).
	- ForcePresence : the vertex is ALWAYS present (else, the LOD system may remove some vertex temporarily).
"""
		cdef int index
		index = x + z * self._nb_vertex_width
		self._check_vertex_options()
		self._vertex_options[index] = (self._vertex_options[index] & ~(TERRAIN_VERTEX_HIDDEN | TERRAIN_VERTEX_NON_SOLID | TERRAIN_VERTEX_FORCE_PRESENCE)) | (hidden * TERRAIN_VERTEX_HIDDEN) | (non_solid * TERRAIN_VERTEX_NON_SOLID) | (force_presence * TERRAIN_VERTEX_FORCE_PRESENCE)
		
	def set_vertex_color(self, int x, int z, color):
		cdef float  ccolor[4]
		cdef int    n
		n = x + z * self._nb_vertex_width
		ccolor[0] = color[0]
		ccolor[1] = color[1]
		ccolor[2] = color[2]
		ccolor[3] = color[3]
		self._vertex_colors[n] = self._check_color(ccolor)
		if   1.0 - ccolor[3] > EPSILON:          self._vertex_options[n] = self._vertex_options[n] |  TERRAIN_VERTEX_ALPHA
		elif self._option & TERRAIN_VERTEX_OPTIONS: self._vertex_options[n] = self._vertex_options[n] & ~TERRAIN_VERTEX_ALPHA
		if   ccolor[3] < EPSILON:                self._vertex_options[n] = self._vertex_options[n] |  TERRAIN_VERTEX_HIDDEN
		elif self._option & TERRAIN_VERTEX_OPTIONS: self._vertex_options[n] = self._vertex_options[n] & ~TERRAIN_VERTEX_HIDDEN
		
	def reinit(self):
		"""Terrain.reinit()

Re-inits the terrain.
You MUST call this method after the terrain have been modified manually
(e.g. with Terrain.set_height)."""
		if self._option & TERRAIN_INITED: self._option = self._option - TERRAIN_INITED
		
		
	cdef void _init(self):
		if self._patchs != NULL: self._free_patchs()
		self._compute_normals()
		self._create_patchs()
		if self._option & TERRAIN_VERTEX_OPTIONS: self._force_presence()
		self._option = self._option | TERRAIN_INITED
		
	cdef void _compute_normal(self, int x, int y): # compute vertex normal
		cdef float y00, y01, y10, y11, y12, y21, y22, y02, y20, a, b, c
		cdef TerrainVertex* vertex
		vertex = self._get_vertex(x, y)
		y11 = self._get_height(x, y)
		
		y00 = (self._get_height(x - 1, y - 1) - y11)
		y01 = (self._get_height(x - 1, y    ) - y11)
		y10 = (self._get_height(x    , y - 1) - y11)
		y12 = (self._get_height(x    , y + 1) - y11)
		y21 = (self._get_height(x + 1, y    ) - y11)
		y22 = (self._get_height(x + 1, y + 1) - y11)
		y02 = (self._get_height(x - 1, y + 1) - y11)
		y20 = (self._get_height(x + 1, y - 1) - y11)
		
		a = (-y00 - 2.0 * y01 - y02 + y20 + 2.0 * y21 + y22) / self._scale_factor
		b = (-y00 - 2.0 * y10 - y20 + y02 + 2.0 * y12 + y22) / self._scale_factor
		c = 8.0
		vertex.normal[0] = - a
		vertex.normal[1] =   c
		vertex.normal[2] = - b
		vector_normalize(vertex.normal)
		
	cdef void _compute_normals(self):
		cdef int         i, j
		cdef float*      ptr
		cdef TerrainVertex* v1, *v2, *v3, *v4
		# compute points normals
		for j from 0 <= j < self._nb_vertex_depth:
			for i from 0 <= i < self._nb_vertex_width:
				self._compute_normal(i, j)
		# compute triangles normals
		ptr = self._normals
		for j from 0 <= j < self._nb_vertex_depth - 1:
			for i from 0 <= i < self._nb_vertex_width - 1:
				v1 = self._get_vertex(i    , j    )
				v2 = self._get_vertex(i + 1, j    )
				v3 = self._get_vertex(i + 1, j + 1)
				v4 = self._get_vertex(i    , j + 1)
				if ((i & 1) and (j & 1)) or ((not(i & 1)) and (not(j & 1))):
					face_normal(ptr,     v4.coord, v3.coord, v1.coord); vector_normalize(ptr)
					face_normal(ptr + 3, v2.coord, v1.coord, v3.coord); vector_normalize(ptr + 3)
				else:
					face_normal(ptr,     v1.coord, v4.coord, v2.coord); vector_normalize(ptr)
					face_normal(ptr + 3, v3.coord, v2.coord, v4.coord); vector_normalize(ptr + 3)
				ptr = ptr + 6
				
	cdef void _compute_coords(self):
		cdef int         i, j, k
		cdef TerrainVertex* vertex
		k = 0
		for i from 0 <= i < self._nb_vertex_depth:
			for j from 0 <= j < self._nb_vertex_width:
				vertex = self._vertices + k
				vertex.coord[0]    = (<float> j) * self._scale_factor
				vertex.coord[2]    = (<float> i) * self._scale_factor
				vertex.texcoord[0] = (<float> j) * self._texture_factor
				vertex.texcoord[1] = (<float> i) * self._texture_factor
				k = k + 1
				
	cdef void _create_patch(self, TerrainPatch* patch, int x, int z, int patch_size):
		cdef int         i, j, m, nb, x1, z1, x2, z2
		cdef float*      coords
		cdef TerrainVertex* vertex, *center, *v0, *v1, *v2, *v3
		patch.level = 0
		x1 =  x      * patch_size
		x2 = (x + 1) * patch_size
		z1 =  z      * patch_size
		z2 = (z + 1) * patch_size
		
		# compute bounding sphere
		nb     = (patch_size + 1) * (patch_size + 1)
		coords = <float*> malloc(nb * 3 * sizeof(float))
		m      = 0
		for i from x1 <= i <= x2:
			for j from z1 <= j <= z2:
				vertex = self._get_vertex(i, j)
				memcpy(coords + m, vertex.coord, 3 * sizeof(float))
				m = m + 3
		sphere_from_points(patch.sphere, coords, nb)
		free(coords)
		
		# create tris
		v0 = self._get_vertex(x1, z1)
		v1 = v0 + self._patch_size
		v2 = v0 + self._patch_size * self._nb_vertex_width
		v3 = v2 + self._patch_size
		center = v0 + ((v3 - v0) >> 1)
		patch.tri_top    = terrain_create_tri(center, v1, v0, patch)
		patch.tri_left   = terrain_create_tri(center, v0, v2, patch)
		patch.tri_right  = terrain_create_tri(center, v3, v1, patch)
		patch.tri_bottom = terrain_create_tri(center, v2, v3, patch)
		patch.tri_top.left_neighbor     = patch.tri_right
		patch.tri_top.right_neighbor    = patch.tri_left
		patch.tri_top.base_neighbor     = NULL
		patch.tri_left.left_neighbor    = patch.tri_top
		patch.tri_left.right_neighbor   = patch.tri_bottom
		patch.tri_left.base_neighbor    = NULL
		patch.tri_right.left_neighbor   = patch.tri_bottom
		patch.tri_right.right_neighbor  = patch.tri_top
		patch.tri_right.base_neighbor   = NULL
		patch.tri_bottom.left_neighbor  = patch.tri_left
		patch.tri_bottom.right_neighbor = patch.tri_right
		patch.tri_bottom.base_neighbor  = NULL
		
	cdef void _create_patchs(self):
		cdef int        i, j, k
		cdef TerrainPatch* m
		self._max_level = exp_of_2(self._patch_size) * 2 - 1
		# create patchs
		self._nb_patch_width = <int> ((self._nb_vertex_width - 1) / self._patch_size)
		self._nb_patch_depth = <int> ((self._nb_vertex_depth - 1) / self._patch_size)
		self._nb_patchs = self._nb_patch_width * self._nb_patch_depth
		if self._patchs != NULL: terrain_free_patchs(terrain)
		self._patchs = <TerrainPatch*> malloc(self._nb_patchs * sizeof(TerrainPatch))
		k = 0
		for j from 0 <= j < self._nb_patch_depth:
			for i from 0 <= i < self._nb_patch_width:
				self._create_patch(self._patchs + k, i, j, self._patch_size)
				k = k + 1
		# set neighbors
		for j from 0 <= j < self._nb_patch_depth:
			for i from 0 <= i < self._nb_patch_width:
				m = self._patchs + (i + j * self._nb_patch_width)
				if (i > 0                       ): m.tri_left  .base_neighbor = (self._patchs + (i - 1) +  j      * self._nb_patch_width).tri_right
				if (j > 0                       ): m.tri_top   .base_neighbor = (self._patchs +  i      + (j - 1) * self._nb_patch_width).tri_bottom
				if (i < self._nb_patch_width - 1): m.tri_right .base_neighbor = (self._patchs + (i + 1) +  j      * self._nb_patch_width).tri_left
				if (j < self._nb_patch_depth - 1): m.tri_bottom.base_neighbor = (self._patchs +  i      + (j + 1) * self._nb_patch_width).tri_top
				
	cdef int _register_color(self, float color[4]):
		cdef float* c
		cdef int    i, nb
		c = self._colors
		for i from 0 <= i < self._nb_colors:
			if ((fabs(color[0] - c[0]) < EPSILON) and
					(fabs(color[1] - c[1]) < EPSILON) and
					(fabs(color[2] - c[2]) < EPSILON) and
					(fabs(color[3] - c[3]) < EPSILON)): return i
			c = c + 4
		
		i = self._nb_colors * 4
		self._nb_colors = self._nb_colors + 1
		self._colors = <float*> realloc(self._colors, self._nb_colors * 4 * sizeof(float))
		memcpy(self._colors + i, color, 4 * sizeof(float))
		return i
	
	def compute_shadow_color(self, _Light light, shadow_color):
		cdef int    i, nb
		cdef float  color[4]
		cdef float  cshadow_color[4]
		cdef float* ocolor, *old_colors
		cdef int    scolor, wcolor
		nb = self._nb_vertex_width * self._nb_vertex_depth
		if not(self._option & TERRAIN_INITED): self._init()
		
		cshadow_color[0] = shadow_color[0]
		cshadow_color[1] = shadow_color[1]
		cshadow_color[2] = shadow_color[2]
		cshadow_color[3] = shadow_color[3]
		
		# initialize vertex colors if needed
		old_colors = self._colors
		self._colors = NULL
		self._nb_colors = 0
		if not(self._option & TERRAIN_COLORED):
			self._option = self._option | TERRAIN_COLORED
			self._vertex_colors = <int*> malloc(nb * sizeof(int))
			for i from 0 <= i < nb: self._vertex_colors[i] = -1
			self._nb_colors = 2
			self._colors = <float*> malloc(8 * sizeof(float))
			wcolor = 0
			scolor = 4
			memcpy(self._colors + wcolor, white        , 4 * sizeof(float))
			memcpy(self._colors + scolor, cshadow_color, 4 * sizeof(float))
			
		# compute shadows
		for i from 0 <= i < nb:
			if light._shadow_at((self._vertices + i).coord):
				if self._vertex_colors[i] == -1: self._vertex_colors[i] = scolor
				else:
					ocolor = self._colors + self._vertex_colors[i]
					color[0] = ocolor[0] * cshadow_color[0]
					color[1] = ocolor[1] * cshadow_color[1]
					color[2] = ocolor[2] * cshadow_color[2]
					color[3] = ocolor[3] * cshadow_color[3]
					self._vertex_colors[i] = self._register_color(color)
			else:
				if self._vertex_colors[i] == -1: self._vertex_colors[i] = wcolor
				else:                            self._vertex_colors[i] = self._register_color(self._colors + self._vertex_colors[i])
		free(old_colors)


	cdef void _tri_split(self, TerrainTri* tri):
		cdef TerrainVertex* v
		if not terrain_tri_diamond(tri): self._tri_split(tri.base_neighbor)
		
		# hum that is a beautiful code to get the vertex that is the middle of v2-v3
		if tri.v2 < tri.v3: v = tri.v2 + ((tri.v3 - tri.v2) >> 1)
		else:               v = tri.v3 + ((tri.v2 - tri.v3) >> 1)
		tri.left_child  = terrain_create_child_tri(v, tri.v1, tri.v2, tri)
		tri.right_child = terrain_create_child_tri(v, tri.v3, tri.v1, tri)
		if tri.base_neighbor != NULL: terrain_tri_force_split(tri.base_neighbor, v)
		terrain_tri_update_neighbor_after_split(tri)
		
	cdef int _tri_merge_child(self, TerrainTri* tri):
		cdef TerrainTri* base
		# return FALSE if merge can't be done, else TRUE if the merge has been done
		base = tri.base_neighbor
		if ((tri.left_child.level <= tri.left_child.patch.level) or 
			 ((base != NULL) and (base.left_child.level <= base.left_child.patch.level))): return 0

		if terrain_tri_has_child(tri.left_child ) and not self._tri_merge_child(tri.left_child ): return 0
		if terrain_tri_has_child(tri.right_child) and not self._tri_merge_child(tri.right_child): return 0
		if base != NULL:
			if terrain_tri_has_child(base.left_child ) and not self._tri_merge_child(base.left_child ): return 0
			if terrain_tri_has_child(base.right_child) and not self._tri_merge_child(base.right_child): return 0
			
		if (self._option & TERRAIN_VERTEX_OPTIONS) and (self._vertex_options[tri.left_child.v1 - self._vertices] & TERRAIN_VERTEX_FORCE_PRESENCE):
			return 0
		
		terrain_tri_update_neighbor_after_merge(tri)
		if base != NULL:
			terrain_tri_update_neighbor_after_merge(base)
			terrain_tri_drop(base.left_child)
			terrain_tri_drop(base.right_child)
			base.left_child = base.right_child = NULL
			
		terrain_tri_drop(tri.left_child )
		terrain_tri_drop(tri.right_child)
		tri.left_child = tri.right_child = NULL
		return 1
	
	cdef void _tri_set_level(self, TerrainTri* tri, char level):
		if terrain_tri_has_child(tri):
			self._tri_set_level(tri.left_child, level)
			if tri.left_child == NULL: self._tri_set_level(tri,             level) # this means we have merged the children
			else:                      self._tri_set_level(tri.right_child, level)
		else:
			if  (tri.level > level) and (tri.parent != NULL): self._tri_merge_child(tri.parent)
			elif tri.level < level:
				self._tri_split    (tri)
				self._tri_set_level(tri.left_child , level)
				self._tri_set_level(tri.right_child, level)
				
	cdef void _patch_set_level(self, TerrainPatch* patch, char level):
		if patch.level != level:
			patch.level = level
			self._tri_set_level(patch.tri_top   , level)
			self._tri_set_level(patch.tri_left  , level)
			self._tri_set_level(patch.tri_right , level)
			self._tri_set_level(patch.tri_bottom, level)
			
	cdef int _patch_update(self, TerrainPatch* patch, Frustum* frustum, float* frustum_box):
		cdef char   level
		cdef float  d, r
		cdef float* v1, *v2
		# update patch LOD
		v1 = patch.tri_top   .v3.coord
		v2 = patch.tri_bottom.v3.coord
		if (frustum_box[0] > v2[0]) or (frustum_box[2] < v1[0]) or (frustum_box[1] > v2[2]) or (frustum_box[3] < v1[2]) or (not sphere_in_frustum(frustum, patch.sphere)):
			self._patch_set_level(patch, 0)
			return 0
		else:
			d = point_distance_to(patch.sphere, frustum.position)
			r = patch.sphere[3] * self._split_factor
			if d <= r: self._patch_set_level(patch, self._max_level)
			else:
				level = <char> (self._max_level + 1 - <int> (d / r))
				if level < 0: level = 0
				self._patch_set_level(patch, level)
			return 1
		
	cdef void _tri_force_presence(self, TerrainTri* tri, TerrainVertex* v):
		cdef float u[2], w[2]
		cdef float k, m, f, x, z
		if (v == tri.v1) or (v == tri.v2) or (v == tri.v3): return
		if terrain_tri_has_child(tri):
			self._tri_force_presence(tri.left_child,  v)
			self._tri_force_presence(tri.right_child, v)
		else:
			u[0] = tri.v2.coord[0] - tri.v1.coord[0]
			u[1] = tri.v2.coord[2] - tri.v1.coord[2]
			w[0] = tri.v3.coord[0] - tri.v1.coord[0]
			w[1] = tri.v3.coord[2] - tri.v1.coord[2]
			x    = v.coord[0] - tri.v1.coord[0]
			z    = v.coord[2] - tri.v1.coord[2]
			f    = 1.0 / (u[0] * w[1] - u[1] * w[0])
			m    = (u[0] * z - u[1] * x) * f
			k    = (w[1] * x - w[0] * z) * f
			if (m >= 0.0) and (m <= 1.0) and (k >= 0.0) and (k <= 1.0) and (k + m <= 1.0):
				self._tri_split(tri)
				self._tri_force_presence(tri.left_child,  v)
				self._tri_force_presence(tri.right_child, v)
				
	cdef void _force_presence(self):
		cdef TerrainVertex* v
		cdef TerrainPatch*  patch
		cdef int         a, b, i, j
		for j from 0 <= j < self._nb_vertex_depth:
			for i from 0 <= i < self._nb_vertex_width:
				if self._vertex_options[i + j * self._nb_vertex_width] & TERRAIN_VERTEX_FORCE_PRESENCE:
					a = <int> ((<float> i) / self._patch_size)
					b = <int> ((<float> j) / self._patch_size)
					if a >= self._nb_patch_width: a = self._nb_patch_width - 1
					if b >= self._nb_patch_depth: b = self._nb_patch_depth - 1
					patch = self._patchs + a + b * self._nb_patch_width
					v = self._get_vertex(i, j)
					self._tri_force_presence(patch.tri_top,    v)
					self._tri_force_presence(patch.tri_left,   v)
					self._tri_force_presence(patch.tri_right,  v)
					self._tri_force_presence(patch.tri_bottom, v)



	cdef void _tri_batch(self, TerrainTri* tri, Frustum* frustum):
		cdef Pack* p, *p1, *p2, *p3, *p4
		cdef int   o1, o2, o3
		if sphere_in_frustum(frustum, tri.sphere):
			if terrain_tri_has_child(tri): # recurse in children
				self._tri_batch(tri.left_child,  frustum)
				self._tri_batch(tri.right_child, frustum)
			else:
				if self._option & TERRAIN_VERTEX_OPTIONS:
					o1 = self._vertex_options[tri.v1 - self._vertices]
					o2 = self._vertex_options[tri.v2 - self._vertices]
					o3 = self._vertex_options[tri.v3 - self._vertices]
					if ((o1 & TERRAIN_VERTEX_HIDDEN) and
							(o2 & TERRAIN_VERTEX_HIDDEN) and
							(o3 & TERRAIN_VERTEX_HIDDEN)): return
					if (o1 & TERRAIN_VERTEX_ALPHA) or (o2 & TERRAIN_VERTEX_ALPHA) or (o3 & TERRAIN_VERTEX_ALPHA):
						# draw everything in second pass
						p1 = pack_get_secondpass(tri.v1.pack)
						p2 = pack_get_secondpass(tri.v2.pack)
						p3 = pack_get_secondpass(tri.v3.pack)
						if p1 < p2: p = p1
						else:       p = p2
						if p3 < p : p = p3
						pack_batch_face(pack_get_secondpass(p), tri)
						if  p1 != p                               : pack_batch_face(p1, tri)
						if (p2 != p) and (p2 != p1)               : pack_batch_face(p2, tri)
						if (p3 != p) and (p3 != p1) and (p3 != p2): pack_batch_face(p3, tri)
						return
					
				p1 = tri.v1.pack
				p2 = tri.v2.pack
				p3 = tri.v3.pack
				# we must render without alpha the pack that is the most represented 
				# this constraint is needed for special texturing smoothing
				if   p1 == p2:
					pack_batch_face(p1, tri)
					if p3 != p1: pack_batch_face(pack_get_secondpass(p3), tri)
				elif p1 == p3:
					pack_batch_face(p1, tri)
					if p2 != p1: pack_batch_face(pack_get_secondpass(p2), tri)
				elif p2 == p3:
					pack_batch_face(p2, tri)
					if p1 != p2: pack_batch_face(pack_get_secondpass(p1), tri)
				else:
					# take in account the base neighbor if it's a diamond
					if (tri.base_neighbor != NULL) and (tri.v2 == tri.base_neighbor.v3) and (tri.v3 == tri.base_neighbor.v2):
						p4 = tri.base_neighbor.v1.pack
						if   p2 == p4:
							pack_batch_face(                    p2 , tri)
							pack_batch_face(pack_get_secondpass(p1), tri)
							pack_batch_face(pack_get_secondpass(p3), tri)
							return
						elif p3 == p4:
							pack_batch_face(                    p3 , tri)
							pack_batch_face(pack_get_secondpass(p1), tri)
							pack_batch_face(pack_get_secondpass(p2), tri)
							return
					pack_batch_face(                    p1 , tri)
					pack_batch_face(pack_get_secondpass(p2), tri)
					pack_batch_face(pack_get_secondpass(p3), tri)
					
	cdef void _patch_batch(self, TerrainPatch* patch, Frustum* frustum):
		if sphere_in_frustum(frustum, patch.sphere):
			self._tri_batch(patch.tri_top,    frustum)
			self._tri_batch(patch.tri_left,   frustum)
			self._tri_batch(patch.tri_right,  frustum)
			self._tri_batch(patch.tri_bottom, frustum)
			
	cdef void _batch(self, CoordSyst coordsyst):
		if self._option & HIDDEN: return
		
		if not (self._option & TERRAIN_INITED): self._init()
		
		multiply_matrix(self._render_matrix, coordsyst._render_matrix, self._matrix)
		self._frustum_id = -1
		
		cdef Chunk*     chunk
		cdef TerrainPatch* patch
		cdef Frustum*   frustum
		cdef float*     ptr
		cdef float      frustum_box[4]
		cdef int        i
		
		# quadtree visibility computation
		frustum = renderer._frustum(self)
		ptr     = frustum.points
		frustum_box[0] = ptr[0]
		frustum_box[1] = ptr[2]
		frustum_box[2] = ptr[0]
		frustum_box[3] = ptr[2]
		i = 3
		while i < 24:
			if ptr[i] < frustum_box[0]: frustum_box[0] = ptr[i]
			if ptr[i] > frustum_box[2]: frustum_box[2] = ptr[i]
			i = i + 2
			if ptr[i] < frustum_box[1]: frustum_box[1] = ptr[i]
			if ptr[i] > frustum_box[3]: frustum_box[3] = ptr[i]
			i = i + 1
			
		patch = self._patchs
		for i from 0 <= i < self._nb_patchs:
			patch.visible = self._patch_update(patch, frustum, frustum_box)
			patch = patch + 1
			
		patch = self._patchs
		for i from 0 <= i < self._nb_patchs:
			if patch.visible: self._patch_batch(patch, frustum)
			patch = patch + 1
			
		pack_batch_end(self, self)
		
	# XXX We cannot use glColor with COLOR_MATERIAL
	# since some 3D drivers (namely, the free radeon 7500 driver) have a bugged
	# implementation of COLOR_MATERIAL.
	
	cdef void _vertex_render_special(self, TerrainVertex* vertex):
		cdef float  ccc[4]
		cdef float* color
		cdef int    index
		index = vertex - self._vertices
		color = self._colors + index
		
		if (self._option & TERRAIN_VERTEX_OPTIONS) and (self._vertex_options[index] & TERRAIN_VERTEX_ALPHA) and (not (<_Material> (vertex.pack.material_id)) is renderer.current_material):
			ccc[0] = color[0]
			ccc[1] = color[1]
			ccc[2] = color[2]
			ccc[3] = 0.0
			terrain_drawColor (ccc)
		else: terrain_drawColor(color)
		#glArrayElement(index)
		glTexCoord2fv(vertex.texcoord)
		glNormal3fv(vertex.normal)
		glVertex3fv(vertex.coord)
		
		
	cdef void _tri_render_middle(self, TerrainTri* tri):
		cdef float       ccc[4]
		cdef TerrainVertex* v
		cdef float*      color, *color2
		
		if self._colors == NULL:
			color = renderer.current_material._diffuse
			ccc[0] = color[0]
			ccc[1] = color[1]
			ccc[2] = color[2]
		else:
			color  = self._colors + (tri.v2 - self._vertices)
			color2 = self._colors + (tri.v3 - self._vertices)
			ccc[0] = (color[0] + color2[0]) * 0.5
			ccc[1] = (color[1] + color2[1]) * 0.5
			ccc[2] = (color[2] + color2[2]) * 0.5
		ccc[3] = 0.0
		terrain_drawColor(ccc)
		
		if tri.level == self._max_level:
			glTexCoord2f ((tri.v2.texcoord[0] + tri.v3.texcoord[0]) * 0.5,
										(tri.v2.texcoord[1] + tri.v3.texcoord[1]) * 0.5)
			glNormal3f   ((tri.v2.normal  [0] + tri.v3.normal  [0]) * 0.5,
										(tri.v2.normal  [1] + tri.v3.normal  [1]) * 0.5,
										(tri.v2.normal  [2] + tri.v3.normal  [2]) * 0.5)
			glVertex3f   ((tri.v2.coord   [0] + tri.v3.coord   [0]) * 0.5,
										(tri.v2.coord   [1] + tri.v3.coord   [1]) * 0.5,
										(tri.v2.coord   [2] + tri.v3.coord   [2]) * 0.5)
		else:
			if tri.v2 < tri.v3: v = tri.v2 + ((tri.v3 - tri.v2) >> 1)
			else:               v = tri.v3 + ((tri.v2 - tri.v3) >> 1)
			#glArrayElement(v - self._vertices)
			glTexCoord2fv(v.texcoord)
			glNormal3fv(v.normal)
			glVertex3fv(v.coord)
			
	cdef void _tri_render_secondpass(self, TerrainTri* tri):
		cdef float  ccc[4]
		cdef float* color
		cdef int    index

		if ((not(self._option & TERRAIN_VERTEX_OPTIONS) or
				 not((self._vertex_options[tri.v1 - self._vertices] & TERRAIN_VERTEX_ALPHA) or
						 (self._vertex_options[tri.v2 - self._vertices] & TERRAIN_VERTEX_ALPHA) or
						 (self._vertex_options[tri.v3 - self._vertices] & TERRAIN_VERTEX_ALPHA))) and
				(tri.base_neighbor != NULL) and (tri.v2 == tri.base_neighbor.v3) and (tri.v3 == tri.base_neighbor.v2)):
			# diamond base neighbor without alpha => special smooth texturing
			if  (((<_Material> (tri.v2.pack.material_id)) is renderer.current_material) and
					 (tri.v2.pack != tri.v1.pack) and
					 (tri.v2.pack != tri.v3.pack) and
					 (tri.v2.pack != tri.base_neighbor.v1.pack)):
				index = tri.v1 - self._vertices; SET_COLOR_ALPHA (self, index); glTexCoord2fv(tri.v1.texcoord); glNormal3fv(tri.v1.normal); glVertex3fv(tri.v1.coord); #glArrayElement(index)
				index = tri.v2 - self._vertices; SET_COLOR_OPAQUE(self, index); glTexCoord2fv(tri.v2.texcoord); glNormal3fv(tri.v2.normal); glVertex3fv(tri.v2.coord); #glArrayElement(index)
				self._tri_render_middle(tri)
				return
			
			elif (((<_Material> (tri.v3.pack.material_id)) is renderer.current_material) and
					 (tri.v3.pack != tri.v1.pack) and
					 (tri.v3.pack != tri.v2.pack) and
					 (tri.v3.pack != tri.base_neighbor.v1.pack)):
				index = tri.v1 - self._vertices; SET_COLOR_ALPHA (self, index); glTexCoord2fv(tri.v1.texcoord); glNormal3fv(tri.v1.normal); glVertex3fv(tri.v1.coord); #glArrayElement(index)
				self._tri_render_middle(tri)
				index = tri.v3 - self._vertices; SET_COLOR_OPAQUE(self, index); glTexCoord2fv(tri.v3.texcoord); glNormal3fv(tri.v3.normal); glVertex3fv(tri.v3.coord); #glArrayElement(index)
				return
				
		index = tri.v1 - self._vertices
		if (<_Material> (tri.v1.pack.material_id)) is renderer.current_material: SET_COLOR_OPAQUE(self, index)
		else:                                                                    SET_COLOR_ALPHA (self, index)
		glTexCoord2fv(tri.v1.texcoord)
		glNormal3fv(tri.v1.normal)
		glVertex3fv(tri.v1.coord)
		#glArrayElement(index)
		
		index = tri.v2 - self._vertices
		if (<_Material> (tri.v2.pack.material_id)) is renderer.current_material: SET_COLOR_OPAQUE(self, index)
		else:                                                                    SET_COLOR_ALPHA (self, index)
		glTexCoord2fv(tri.v2.texcoord)
		glNormal3fv(tri.v2.normal)
		glVertex3fv(tri.v2.coord)
		#gArrayElement(index)
		
		index = tri.v3 - self._vertices
		if (<_Material> (tri.v3.pack.material_id)) is renderer.current_material: SET_COLOR_OPAQUE(self, index)
		else:                                                                    SET_COLOR_ALPHA (self, index)
		glTexCoord2fv(tri.v3.texcoord)
		glNormal3fv(tri.v3.normal)
		glVertex3fv(tri.v3.coord)
		#glArrayElement(index)


	cdef void _render(self, CoordSyst coordsyst):
		cdef int      cur, index
		cdef Pack*    pack
		cdef TerrainTri* tri
		
		terrain_disableColor()
		# ArrayElement doesn't work well, at least for me
		#glInterleavedArrays(GL_T2F_N3F_V3F, sizeof(TerrainVertex), self._vertices)
		
		# Renderer.data is like :
		#   [pack1*, terrain_tri1*, terrain_tri2*,..., NULL, pack2*, terrain_tri3,..., NULL, NULL]
		
		cur = renderer.data.nb
		pack = <Pack*> chunk_get_ptr(renderer.data)
		
		if   renderer.state == RENDERER_STATE_OPAQUE:
			while pack:
				(<_Material> (pack.material_id))._activate()
				
				glBegin(GL_TRIANGLES)
				tri = <TerrainTri*> chunk_get_ptr(renderer.data)
				while tri:
					#index = tri.v1 - self._vertices
					if self._colors != NULL: terrain_drawColor(self._colors + index)
					#glArrayElement(index)
					glTexCoord2fv(tri.v1.texcoord)
					glNormal3fv(tri.v1.normal)
					glVertex3fv(tri.v1.coord)
					
					#index = tri.v2 - self._vertices
					if self._colors != NULL: terrain_drawColor(self._colors + index)
					#glArrayElement(index)
					glTexCoord2fv(tri.v2.texcoord)
					glNormal3fv(tri.v2.normal)
					glVertex3fv(tri.v2.coord)
					
					#index = tri.v3 - self._vertices
					if self._colors != NULL: terrain_drawColor(self._colors + index)
					#glArrayElement(index)
					glTexCoord2fv(tri.v3.texcoord)
					glNormal3fv(tri.v3.normal)
					glVertex3fv(tri.v3.coord)
					
					tri = <TerrainTri*> chunk_get_ptr(renderer.data)
					
				glEnd()
				pack = <Pack*> chunk_get_ptr(renderer.data)
				
				
		elif renderer.state == RENDERER_STATE_SECONDPASS:
			glEnable(GL_BLEND)
			
			# XXX SORT them BEFORE !!! avoid looping twice !
			
			# draw the special
			while pack:
				if pack.option & PACK_SPECIAL:
					(<_Material> (pack.material_id))._activate()
					glBegin(GL_TRIANGLES)
					tri = <TerrainTri*> chunk_get_ptr(renderer.data)
					while tri:
						self._vertex_render_special(tri.v1)
						self._vertex_render_special(tri.v2)
						self._vertex_render_special(tri.v3)
						tri = <TerrainTri*> chunk_get_ptr(renderer.data)
					glEnd()
				else:
					while chunk_get_ptr(renderer.data): pass
					
				pack = <Pack*> chunk_get_ptr(renderer.data)
				
			# draw the secondpass
			glDepthFunc(GL_LEQUAL)
			glPolygonOffset(-1.0, 0.0)
			renderer.data.nb = cur # Reset the chunk, in order to loop over the same data than above
			pack = <Pack*> chunk_get_ptr(renderer.data)
			while pack:
				if not(pack.option & PACK_SPECIAL):
					(<_Material> (pack.material_id))._activate()
					glEnable(GL_POLYGON_OFFSET_FILL) # Black magic : it doesn't work if GL_POLYGON_OFFSET_FILL is enabled once. we must enable/disable it for all glBegin-glEnd.
					glBegin(GL_TRIANGLES)
					tri = <TerrainTri*> chunk_get_ptr(renderer.data)
					while tri:
						self._tri_render_secondpass(tri)
						tri = <TerrainTri*> chunk_get_ptr(renderer.data)
					glEnd()
					glDisable(GL_POLYGON_OFFSET_FILL) # Black magic
				else:
					while chunk_get_ptr(renderer.data): pass
					
				pack = <Pack*> chunk_get_ptr(renderer.data)
				
			glDisable(GL_BLEND)
			glDepthFunc(GL_LESS)
			glDisable(GL_POLYGON_OFFSET_FILL) # Needed ? It should be already disabled
			
		terrain_drawColor(white)
		terrain_enableColor()
		glDisableClientState(GL_VERTEX_ARRAY)
		glDisableClientState(GL_NORMAL_ARRAY)
		glDisableClientState(GL_TEXTURE_COORD_ARRAY)
		
	cdef void _tri_raypick(self, TerrainTri* tri, float* raydata, RaypickData data):
		cdef float r, root_r
		if terrain_tri_has_child(tri):
			self._tri_raypick(tri.left_child,  raydata, data)
			self._tri_raypick(tri.right_child, raydata, data)
		else:
			if ((self._option & TERRAIN_VERTEX_OPTIONS) and 
					(self._vertex_options[tri.v1 - self._vertices] & TERRAIN_VERTEX_NON_SOLID) and
					(self._vertex_options[tri.v2 - self._vertices] & TERRAIN_VERTEX_NON_SOLID) and
					(self._vertex_options[tri.v3 - self._vertices] & TERRAIN_VERTEX_NON_SOLID)): return
				 
			if triangle_raypick(raydata, tri.v1.coord, tri.v2.coord, tri.v3.coord, tri.normal, data.option, &r):
				root_r = self._distance_out(r)
				if (root_r < data.root_result) or (data.result_coordsyst is None):
					data.result           = r
					data.root_result      = root_r
					data.result_coordsyst = self
					memcpy(data.normal, tri.normal, 3 * sizeof(float))
					
	cdef void _full_raypick(self, TerrainVertex* v1, TerrainVertex* v2, TerrainVertex* v3, float* normal, float* raydata, RaypickData data):
		cdef float* coord1, *coord2, *coord3
		cdef float  a, b, c, root_a
		if ((not(self._option & TERRAIN_VERTEX_OPTIONS)) or 
				(not(self._vertex_options[v1 - self._vertices] & TERRAIN_VERTEX_NON_SOLID)) or
				(not(self._vertex_options[v2 - self._vertices] & TERRAIN_VERTEX_NON_SOLID)) or
				(not(self._vertex_options[v3 - self._vertices] & TERRAIN_VERTEX_NON_SOLID))):
			coord1 = v1.coord
			coord2 = v2.coord
			coord3 = v3.coord
			# compute distance sphere-line
			a = - raydata[5] * (coord1[0] - raydata[0]) + raydata[3] * (coord1[2] - raydata[2])
			if a < 2 * self._scale_factor:
				b = - raydata[5] * (coord2[0] - raydata[0]) + raydata[3] * (coord2[2] - raydata[2])
				c = - raydata[5] * (coord3[0] - raydata[0]) + raydata[3] * (coord3[2] - raydata[2])
				
				if not((a > 0.0) and (b > 0.0) and (c > 0.0)) and not((a < 0.0) and (b < 0.0) and (c < 0.0)):
					if triangle_raypick(raydata, coord1, coord2, coord3, normal, data.option, &a):
						root_a = self._distance_out(a)
						if (root_a < data.root_result) or (data.result_coordsyst is None): # XXX Strange : no 'fabs()' around root_a and data.root_result ???
							data.result           = a
							data.root_result      = root_a
							data.result_coordsyst = self
							memcpy(data.normal, normal, 3 * sizeof(float))

	cdef void _full_raypick_rect(self, int x1, int z1, int x2, int z2, float* raydata, RaypickData data):
		cdef int         i, j
		cdef TerrainVertex* p, *p0
		cdef float*      normal
		p0 = self._get_vertex(x1, z1)
		
		for j from z1 <= j < z2:
			p = p0
			normal = self._normals + 6 * (x1 + j * (self._nb_vertex_width - 1))
			for i from x1 <= i < x2:
				if not((i + j) & 1): # if both j and i are odd or even
					self._full_raypick(p + self._nb_vertex_width, p + self._nb_vertex_width + 1, p, normal, raydata, data)
					normal = normal + 3
					self._full_raypick(p + 1, p, p + self._nb_vertex_width + 1, normal, raydata, data)
					normal = normal + 3
				else:
					self._full_raypick(p, p + self._nb_vertex_width, p + 1, normal, raydata, data)
					normal = normal + 3
					self._full_raypick(p + self._nb_vertex_width + 1, p + 1, p + self._nb_vertex_width, normal, raydata, data)
					normal = normal + 3
				p = p + 1
			p0 = p0 + self._nb_vertex_width

	cdef void _raypick(self, RaypickData raypick_data, CoordSyst raypickable, int category):
		#if self._option & NON_SOLID: return
		if not (self._category_bitfield & category): return
		
		cdef int        i, x, z
		cdef TerrainPatch* patch
		cdef float*     data
		cdef float      f, x1, z1, x2, z2
		data = self._raypick_data(raypick_data)
		if not(self._option & TERRAIN_INITED): self._init()
		
		if self._option & TERRAIN_REAL_LOD_RAYPICK:
			for i from 0 <= i < self._nb_patchs:
				patch = self._patchs + i
				if not sphere_raypick(data, patch.sphere): continue
				# raypick on tris
				self._tri_raypick(patch.tri_top,    data, raypick_data)
				self._tri_raypick(patch.tri_left,   data, raypick_data)
				self._tri_raypick(patch.tri_right,  data, raypick_data)
				self._tri_raypick(patch.tri_bottom, data, raypick_data)
			
		else:
			if (data[3] == 0.0) and (data[5] == 0.0):
				x = <int> (data[0] / self._scale_factor)
				z = <int> (data[2] / self._scale_factor)
				if (0.0 <= x < self._nb_vertex_width) and (0.0 <= z < self._nb_vertex_depth):
					self._full_raypick_rect(x, z, x + 1, z + 1, data, raypick_data)
			else:
				if data[6] < 0.0:
					for i from 0 <= i < self._nb_patchs:
						patch = self._patchs + i
						if not sphere_raypick(data, patch.sphere): continue
						# raypick on tris with full accuracy
						self._full_raypick_rect(<int> (patch.tri_top   .v3.coord[0] / self._scale_factor),
																		<int> (patch.tri_top   .v3.coord[2] / self._scale_factor),
																		<int> (patch.tri_bottom.v3.coord[0] / self._scale_factor),
																		<int> (patch.tri_bottom.v3.coord[2] / self._scale_factor),
																		data, raypick_data)
					
				else:
					if raypick_data.option & RAYPICK_HALF_LINE:
						x1 = data[0]
						z1 = data[2]
					else:
						x1 = data[0] - data[6] * data[3]
						z1 = data[2] - data[6] * data[5]
					x2 = data[0] + data[6] * data[3]
					z2 = data[2] + data[6] * data[5]
					if x1 > x2:
						f  = x1
						x1 = x2
						x2 = f
					if z1 > z2:
						f  = z1
						z1 = z2
						z2 = f
						
					x1 = x1 / self._scale_factor
					z1 = z1 / self._scale_factor
					x2 = x2 / self._scale_factor
					z2 = z2 / self._scale_factor
					if x2 < 0.0: return
					if z2 < 0.0: return
					if x1 >= <float> self._nb_vertex_width: return
					if z1 >= <float> self._nb_vertex_depth: return
					if x1 < 0.0: x1 = 0.0
					if z1 < 0.0: z1 = 0.0
					x2 = x2 + 1.0
					z2 = z2 + 1.0
					if x2 >= <float> self._nb_vertex_width: x2 = <float> self._nb_vertex_width - 1
					if z2 >= <float> self._nb_vertex_depth: z2 = <float> self._nb_vertex_depth - 1
					self._full_raypick_rect(<int> x1, <int> z1, <int> x2, <int> z2, data, raypick_data)

	cdef int _tri_raypick_b(self, TerrainTri* tri, float* raydata, int option):
		cdef float r
		if terrain_tri_has_child(tri):
			if self._tri_raypick_b(tri.left_child,  raydata, option): return 1
			if self._tri_raypick_b(tri.right_child, raydata, option): return 1
		else:
			if self._option & TERRAIN_VERTEX_OPTIONS:
				if ((self._vertex_options[tri.v1 - self._vertices] & TERRAIN_VERTEX_NON_SOLID) and
						(self._vertex_options[tri.v2 - self._vertices] & TERRAIN_VERTEX_NON_SOLID) and
						(self._vertex_options[tri.v3 - self._vertices] & TERRAIN_VERTEX_NON_SOLID)): return 0
			if triangle_raypick(raydata, tri.v1.coord, tri.v2.coord, tri.v3.coord, tri.normal, option, &r):
				return 1
		return 0
	
	cdef int _full_raypick_b(self, TerrainVertex* v1, TerrainVertex* v2, TerrainVertex* v3, float* normal, float* raydata, int option):
		cdef float* coord1, *coord2, *coord3
		cdef float  a, b, c
		if ((not(self._option & TERRAIN_VERTEX_OPTIONS)) or
				(not(self._vertex_options[v1 - self._vertices] & TERRAIN_VERTEX_NON_SOLID)) or
				(not(self._vertex_options[v2 - self._vertices] & TERRAIN_VERTEX_NON_SOLID)) or
				(not(self._vertex_options[v3 - self._vertices] & TERRAIN_VERTEX_NON_SOLID))):
			coord1 = v1.coord
			coord2 = v2.coord
			coord3 = v3.coord
			# compute distance sphere-line
			a = - raydata[5] * (coord1[0] - raydata[0]) + raydata[3] * (coord1[2] - raydata[2])
			if a < 2 * self._scale_factor:
				b = - raydata[5] * (coord2[0] - raydata[0]) + raydata[3] * (coord2[2] - raydata[2])
				c = - raydata[5] * (coord3[0] - raydata[0]) + raydata[3] * (coord3[2] - raydata[2])
				if not((a > 0.0) and (b > 0.0) and (c > 0.0)) and not((a < 0.0) and (b < 0.0) and (c < 0.0)):
					if triangle_raypick(raydata, coord1, coord2, coord3, normal, option, &a): return 1
		return 0
	
	cdef int _full_raypick_rect_b(self, int x1, int z1, int x2, int z2, float* raydata, int option):
		cdef int         i, j
		cdef TerrainVertex* p, *p0
		cdef float*      normal
		p0 = self._get_vertex(x1, z1)
		
		for j from z1 <= j < z2:
			p = p0
			normal = self._normals + 6 * (x1 + j * (self._nb_vertex_width - 1))
			for i from x1 <= i < x2:
				if not((i + j) & 1): # if both j and i are odd or even
					if self._full_raypick_b(p + self._nb_vertex_width, p + self._nb_vertex_width + 1, p, normal, raydata, option): return 1
					normal = normal + 3
					if self._full_raypick_b(p + 1, p, p + self._nb_vertex_width + 1, normal, raydata, option): return 1
					normal = normal + 3
				else:
					if self._full_raypick_b(p, p + self._nb_vertex_width, p + 1, normal, raydata, option): return 1
					normal = normal + 3
					if self._full_raypick_b(p + self._nb_vertex_width + 1, p + 1, p + self._nb_vertex_width, normal, raydata, option): return 1
					normal = normal + 3
				p = p + 1
			p0 = p0 + self._nb_vertex_width
		return 0

	cdef int _raypick_b(self, RaypickData raypick_data, CoordSyst raypickable, int category):
		#if self._option & NON_SOLID: return 0
		if not (self._category_bitfield & category): return 0
		
		cdef int        i, x, z
		cdef TerrainPatch* patch
		cdef float*     data
		cdef float      x1, z1, x2, z2, f
		if not(self._option & TERRAIN_INITED): self._init()
		data = self._raypick_data(raypick_data)
		
		if self._option & TERRAIN_REAL_LOD_RAYPICK:
			for i from 0 <= i < self._nb_patchs:
				patch = self._patchs + i
				if not sphere_raypick(data, patch.sphere): continue
				# raypick on tris
				if self._tri_raypick_b(patch.tri_top,    data, raypick_data.option): return 1
				if self._tri_raypick_b(patch.tri_left,   data, raypick_data.option): return 1
				if self._tri_raypick_b(patch.tri_right,  data, raypick_data.option): return 1
				if self._tri_raypick_b(patch.tri_bottom, data, raypick_data.option): return 1
				
		else:
			if (data[3] == 0.0) and (data[5] == 0.0):
				x = <int> (data[0] / self._scale_factor)
				z = <int> (data[2] / self._scale_factor)
				
				if (0.0 <= x < self._nb_vertex_width) and (0.0 <= z < self._nb_vertex_depth):
					return self._full_raypick_rect_b(x, z, x + 1, z + 1, data, raypick_data.option)
			else:
				if data[6] < 0.0:
					for i from 0 <= i < self._nb_patchs:
						patch = self._patchs + i
						if not sphere_raypick(data, patch.sphere): continue
						# raypick on tris with full accuracy
						if self._full_raypick_rect_b(<int> patch.tri_top   .v3.coord[0] / self._scale_factor,
																				 <int> patch.tri_top   .v3.coord[2] / self._scale_factor,
																				 <int> patch.tri_bottom.v3.coord[0] / self._scale_factor,
																				 <int> patch.tri_bottom.v3.coord[2] / self._scale_factor,
																				 data, raypick_data.option): return 1
				else:
					if raypick_data.option & RAYPICK_HALF_LINE:
						x1 = data[0]
						z1 = data[2]
					else:
						x1 = data[0] - data[6] * data[3]
						z1 = data[2] - data[6] * data[5]
					x2 = data[0] + data[6] * data[3]
					z2 = data[2] + data[6] * data[5]
					if x1 > x2:
						f  = x1
						x1 = x2
						x2 = f
					if z1 > z2:
						f  = z1
						z1 = z2
						z2 = f
					x1 = x1 / self._scale_factor
					z1 = z1 / self._scale_factor
					x2 = x2 / self._scale_factor
					z2 = z2 / self._scale_factor
					if x2 < 0.0: return 0
					if z2 < 0.0: return 0
					if x1 >= <float> self._nb_vertex_width: return 0
					if z1 >= <float> self._nb_vertex_depth: return 0
					if x1 < 0.0: x1 = 0.0
					if z1 < 0.0: z1 = 0.0
					x2 = x2 + 1.0
					z2 = z2 + 1.0
					if x2 >= <float> self._nb_vertex_width: x2 = <float> self._nb_vertex_width - 1
					if z2 >= <float> self._nb_vertex_depth: z2 = <float> self._nb_vertex_depth - 1
					return self._full_raypick_rect_b(<int> x1, <int> z1, <int> x2, <int> z2, data, raypick_data.option)
		return 0
	
	cdef void _collect_raypickables(self, Chunk* items, float* rsphere, float* sphere, int category):
		#if self._option & NON_SOLID: return
		if not (self._category_bitfield & category): return
		
		# XXX not implemented -- no selection
		chunk_add_ptr(items, <void*> self)
		
	def get_true_height_and_normal(self, float x, float z):
		cdef int         i, j
		cdef float       k, t
		cdef float*      norm
		cdef TerrainVertex* v1, *v2
		cdef TerrainPatch*  patch
		cdef TerrainTri*    tri
		
		cdef int         ix, iz
		cdef float       nx, nz
		cdef TerrainVertex* v3
		
		if not(self._option & TERRAIN_INITED): self._init()
		if self._option & TERRAIN_REAL_LOD_RAYPICK:
			# return the true height, the one of the terrain_tri
			for i from 0 <= i < self._nb_patchs:
				patch = self._patchs + i
				v1 = patch.tri_top   .v3
				v2 = patch.tri_bottom.v3
				if (v1.coord[0] <= x <= v2.coord[0]) and (v1.coord[2] <= z <= v2.coord[2]):
					
					# XXX not sure this works... :-(
					
					tri = patch.tri_top
					for j from 0 <= j < 4:
						terrain_get_height_at_factors(tri.v1, tri.v2, tri.v3, x, z, &k, &t)
						if (-EPSILON <= k <= 1.0 + EPSILON) and (-EPSILON <= t <= 1.0 + EPSILON) and (k + t - 1.0 < EPSILON):
							while 1:
								terrain_get_height_at_factors(tri.v1, tri.v2, tri.v3, x, z, &k, &t)
								if terrain_tri_has_child(tri):
									if k >= t: tri = tri.right_child
									else:      tri = tri.left_child
								else:
									norm = tri.normal
									return tri.v1.coord[1] + k * (tri.v2.coord[1] - tri.v1.coord[1]) + t * (tri.v3.coord[1] - tri.v1.coord[1]), Vector(self, norm[0], norm[1], norm[2])
								
						tri = tri + 1 # HACK : patch.tri_top, patch.tri_left, patch.tri_right, patch.tri_bottom are in this order in the TerrainPatch structure.
						
					break
				
		else: # interpolates the height
			nx = x / self._scale_factor
			nz = z / self._scale_factor
			ix = <int> nx
			iz = <int> nz
			if (0 <= ix < self._nb_vertex_width) and (0 <= iz < self._nb_vertex_depth):
				if not((ix + iz) & 1): # if both ix and iz are odd or even
					if nz - iz > nx - ix:
						v1 = self._get_vertex(ix,     iz + 1)
						v2 = self._get_vertex(ix,     iz)
						v3 = self._get_vertex(ix + 1, iz + 1)
						terrain_get_height_at_factors(v1, v2, v3, x, z, &k, &t)
						norm = self._normals + 6 * (ix + iz * (self._nb_vertex_width - 1))
						return v1.coord[1] + k * (v2.coord[1] - v1.coord[1]) + t * (v3.coord[1] - v1.coord[1]), Vector(self, norm[0], norm[1], norm[2])
					else:
						v1 = self._get_vertex(ix + 1, iz)
						v2 = self._get_vertex(ix + 1, iz + 1)
						v3 = self._get_vertex(ix,     iz)
						terrain_get_height_at_factors(v1, v2, v3, x, z, &k, &t)
						norm = self._normals + 6 * (ix + iz * (self._nb_vertex_width - 1)) + 3
						return v1.coord[1] + k * (v2.coord[1] - v1.coord[1]) + t * (v3.coord[1] - v1.coord[1]), Vector(self, norm[0], norm[1], norm[2])
					
				else:
					if nz - iz + nx - ix < 1:
						v1 = self._get_vertex(ix,     iz)
						v2 = self._get_vertex(ix + 1, iz)
						v3 = self._get_vertex(ix,     iz + 1)
						terrain_get_height_at_factors(v1, v2, v3, x, z, &k, &t)
						norm = self._normals + 6 * (ix + iz * (self._nb_vertex_width - 1))
						return v1.coord[1] + k * (v2.coord[1] - v1.coord[1]) + t * (v3.coord[1] - v1.coord[1]), Vector(self, norm[0], norm[1], norm[2])
					else:
						v1 = self._get_vertex(ix + 1, iz + 1)
						v2 = self._get_vertex(ix,     iz + 1)
						v3 = self._get_vertex(ix + 1, iz)
						terrain_get_height_at_factors(v1, v2, v3, x, z, &k, &t)
						norm = self._normals + 6 * (ix + iz * (self._nb_vertex_width - 1)) + 3
						return v1.coord[1] + k * (v2.coord[1] - v1.coord[1]) + t * (v3.coord[1] - v1.coord[1]), Vector(self, norm[0], norm[1], norm[2])
					
		return -1.0, None
	
	
	cdef __getcstate__(self):
		cdef int         i, j, nb
		cdef Chunk*      chunk
		cdef TerrainVertex* v
		cdef             material_id2index
		material_id2index = {}
		for i from 0 <= i < len(self._materials): material_id2index[self._materials[i]] = i
		nb = self._nb_vertex_width * self._nb_vertex_depth
		
		chunk = get_chunk()
		chunk_add_int_endian_safe   (chunk, self._option & ~TERRAIN_INITED)
		chunk_add_floats_endian_safe(chunk, self._matrix, 19)
		chunk_add_int_endian_safe   (chunk, self._nb_vertex_width)
		chunk_add_int_endian_safe   (chunk, self._nb_vertex_depth)
		chunk_add_int_endian_safe   (chunk, self._patch_size)
		chunk_add_float_endian_safe (chunk, self._texture_factor)
		chunk_add_float_endian_safe (chunk, self._scale_factor)
		chunk_add_float_endian_safe (chunk, self._split_factor)
		chunk_add_int_endian_safe   (chunk, self._nb_colors)
		
		if (self._option & TERRAIN_COLORED) and (self._nb_colors > 0):
			chunk_add_floats_endian_safe(chunk, self._colors        , 4 * self._nb_colors)
			chunk_add_ints_endian_safe  (chunk, self._vertex_colors , nb)
			
		if self._option & TERRAIN_VERTEX_OPTIONS: chunk_add_chars_endian_safe(chunk, self._vertex_options, nb)
		
		for i from 0 <= i < nb:
			v = self._vertices + i
			chunk_add_float_endian_safe(chunk, v.coord[1])
			chunk_add_int_endian_safe  (chunk, material_id2index[<_Material> (v.pack.material_id)])
			
		chunk_add_int_endian_safe   (chunk, self._category_bitfield)
		return drop_chunk_to_string(chunk), self._materials
	
	cdef void __setcstate__(self, cstate):
		cdef int         i, j, nb
		cdef int         temp
		cdef Chunk*      chunk
		cdef TerrainVertex* v
		self._materials = cstate[1]
		chunk = string_to_chunk(cstate[0])
		
		chunk_get_int_endian_safe   (chunk, &self._option)
		chunk_get_floats_endian_safe(chunk,  self._matrix, 19)
		chunk_get_int_endian_safe   (chunk, &self._nb_vertex_width)
		chunk_get_int_endian_safe   (chunk, &self._nb_vertex_depth)
		chunk_get_int_endian_safe   (chunk, &self._patch_size)
		chunk_get_float_endian_safe (chunk, &self._texture_factor)
		chunk_get_float_endian_safe (chunk, &self._scale_factor)
		chunk_get_float_endian_safe (chunk, &self._split_factor)
		chunk_get_int_endian_safe   (chunk, &self._nb_colors)
		self._validity = COORDSYS_INVALID
		
		nb = self._nb_vertex_width * self._nb_vertex_depth
		if (self._option & TERRAIN_COLORED) and (self._nb_colors > 0):
			self._colors        = <float*> malloc(4 * self._nb_colors * sizeof(float))
			self._vertex_colors = <int*  > malloc(nb *                  sizeof(int))
			chunk_get_floats_endian_safe(chunk, self._colors        , 4 * self._nb_colors)
			chunk_get_ints_endian_safe  (chunk, self._vertex_colors , nb)
		else: self._colors = self._vertex_colors = NULL
		
		if self._option & TERRAIN_VERTEX_OPTIONS:
			self._vertex_options = <char*> malloc(nb * sizeof(char))
			chunk_get_chars_endian_safe(chunk, self._vertex_options, nb)
		else: self._vertex_options = NULL
			
		if (self._nb_vertex_width != 0) and (self._nb_vertex_depth != 0):
			self._vertices = <TerrainVertex*> malloc(nb * sizeof(TerrainVertex))
			for i from 0 <= i < nb:
				v = self._vertices + i
				chunk_get_float_endian_safe(chunk, v.coord + 1)
				chunk_get_int_endian_safe(chunk, &temp)
				v.pack = (<_Material> (self._materials[temp]))._pack(FACE_TRIANGLE)
			self._normals = <float*> malloc((self._nb_vertex_width - 1) * (self._nb_vertex_depth - 1) * 6 * sizeof(float))
		else: self._vertices = self._normals = NULL

		if len(cstate[0]) > chunk.nb:
			chunk_get_int_endian_safe(chunk, &self._category_bitfield)
		else:
			self._category_bitfield = 1 # For backward compatibility
			
		drop_chunk(chunk)
		self._compute_coords()
		
		
	cdef void _check_vertex_options(self):
		if not(self._option & TERRAIN_VERTEX_OPTIONS):
			self._option = self._option | TERRAIN_VERTEX_OPTIONS
			#free(self._vertex_options)
			self._vertex_options = <char*> calloc(self._nb_vertex_width * self._nb_vertex_depth, sizeof(char))
			
	cdef int _check_color(self, float* color):
		cdef int i, nb, my_white
		if not(self._option & TERRAIN_COLORED):
			nb = self._nb_vertex_width * self._nb_vertex_depth
			self._option = self._option | TERRAIN_COLORED
			self._vertex_colors = <int*> malloc(nb * sizeof(int))
			my_white = self._register_color(white)
			for i from 0 <= i < nb: self._vertex_colors[i] = my_white
		if 1.0 - color[3] > EPSILON: self._check_vertex_options() # need vertex option to stock vertex alpha
		return self._register_color(color)

	
# XXX FX
			
#   cdef void _fx_all(self, fx* fx):
#     cdef i, nb
#     nb = self._nb_vertex_width * self._nb_vertex_depth
#     for i from 0 <= i < nb:: fx.apply(fx, i)
		

#   cdef void _fx_in_sphere(self, fx* fx, float sphere[4]):
#     cdef int x1, z1, x2, z2, i, j, k, t
#     # compute box from sphere
#     x1 = <int> ((sphere[0] - sphere[3]) / self._scale_factor)
#     x2 = <int> ((sphere[0] + sphere[3]) / self._scale_factor)
#     z1 = <int> ((sphere[2] - sphere[3]) / self._scale_factor + 1.0)
#     z2 = <int> ((sphere[2] + sphere[3]) / self._scale_factor + 1.0)
#     if (x1 >= self._nb_vertex_width) or (z1 >= self._nb_vertex_depth) or (x2 < 0) or (z2 < 0): return
#     if x1 < 0: x1 = 0
#     if z1 < 0: z1 = 0
#     if x2 > self._nb_vertex_width: x2 = self._nb_vertex_width
#     if z2 > self._nb_vertex_depth: z2 = self._nb_vertex_depth
#     # test each vertex in the box
#     k = x1 + z1 * self._nb_vertex_width
#     for j from z1 <= j < z2:
#       t = k
#       for i from x1 <= i < x2:
#         if point_is_in_sphere(sphere, (self._vertices + t).coord)):
#           fx.apply(fx, t)
#         t = t + 1
#       k = k + self._nb_vertex_width
			
#   cdef void _fx_in_cylinderY(self, fx* fx, float cylinder[3]):
#     cdef float* f
#     cdef float  x, z
#     cdef int    x1, z1, x2, z2, i, j, k, t
#     # make box from cylinder
#     x1 = <int> ((cylinder[0] - cylinder[2]) / self._scale_factor)
#     x2 = <int> ((cylinder[0] + cylinder[2]) / self._scale_factor)
#     z1 = <int> ((cylinder[1] - cylinder[2]) / self._scale_factor + 1.0)
#     z2 = <int> ((cylinder[1] + cylinder[2]) / self._scale_factor + 1.0)
#     if (x1 >= self._nb_vertex_width) or (z1 >= self._nb_vertex_depth) or (x2 < 0) or (z2 < 0): return
#     if x1 < 0: x1 = 0
#     if z1 < 0: z1 = 0
#     if x2 > self._nb_vertex_width: x2 = self._nb_vertex_width
#     if z2 > self._nb_vertex_depth: z2 = self._nb_vertex_depth
#     # test each vertex in the box
#     k = x1 + z1 * self._nb_vertex_width
#     for j from z1 <= j < z2:
#       t = k
#       for i from x1 <= i < x2:
#         f = (self._vertices + t).coord
#         x = f[0] - cylinder[0]
#         z = f[2] - cylinder[1]
#         if x * x + z * z <= cylinder[2] * cylinder[2]:
#           fx.apply(fx, t)
#         t = t + 1
#       k = k + self._nb_vertex_width


