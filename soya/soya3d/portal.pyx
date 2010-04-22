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

cdef class _Portal(CoordSyst):
	#cdef _World  _beyond
	#cdef         _beyond_name
	#cdef double* _equation  # Clip plane equations
	#cdef Context _context
	
	#cdef int     _nb_vertices # NB vertex and their coordinates for the portal quad ;
	#cdef float*  _coords      # used to draw this quad (for bounds atmosphere or teleporter).
	
	property beyond:
		def __get__(self):
			return self._beyond
		def __set__(self, _World beyond):
			self._beyond = beyond
			if beyond is None: self._beyond_name = ""
			else:              self._beyond_name = beyond._filename
			
	property beyond_name:
		def __get__(self):
			return self._beyond_name
		def __set__(self, name):
			self._beyond_name = name
			
	property nb_clip_planes:
		def __get__(self):
			if self._option & PORTAL_USE_4_CLIP_PLANES: return 4
			if self._option & PORTAL_USE_5_CLIP_PLANES: return 5
			return 0
		def __set__(self, int x):
			if   x == 4:
				self._option   = self._option |  PORTAL_USE_4_CLIP_PLANES
				self._option   = self._option & ~PORTAL_USE_5_CLIP_PLANES
				self._equation = <double*> realloc(self._equation, 16 * sizeof(double))
			elif x == 5:
				self._option   = self._option & ~PORTAL_USE_4_CLIP_PLANES
				self._option   = self._option |  PORTAL_USE_5_CLIP_PLANES
				self._equation = <double*> realloc(self._equation, 20 * sizeof(double))
			else:
				self._option   = self._option & ~PORTAL_USE_4_CLIP_PLANES
				self._option   = self._option & ~PORTAL_USE_5_CLIP_PLANES
				free(self._equation)
				self._equation = NULL
				
#   property infinite:
#     def __get__(self):
#       return self._option & PORTAL_INFINITE
#     def __set__(self, int x):
#       if x: self._option = self._option |  PORTAL_INFINITE
#       else: self._option = self._option & ~PORTAL_INFINITE
			
	property bound_atmosphere:
		def __get__(self):
			return self._option & PORTAL_BOUND_ATMOSPHERE
		def __set__(self, int x):
			if x: self._option = self._option |  PORTAL_BOUND_ATMOSPHERE
			else: self._option = self._option & ~PORTAL_BOUND_ATMOSPHERE

	def __init__(self, _World parent = None):
		CoordSyst.__init__(self, parent)
		self._option   = self._option | PORTAL_USE_4_CLIP_PLANES | PORTAL_BOUND_ATMOSPHERE
		self._equation = <double*> malloc(16 * sizeof(double))
		
	def load_beyond(self):
		"""Loads and returns the World beyond the portal.
The default implementation call World.get(self.beyond_name), but you can overrides
it, e.g. if you want to create the world beyond from scratch."""
		if self.beyond_name: return World.get(self.beyond_name)
		return None
	
	def unload_beyond(self):
		"""Called when the portal is no longer visible.
The default implementation does nothing, but you can override it, e.g. to remove
portal.beyond from memory (with 'portal.beyond = None')."""
		pass
	
	
	cdef void _compute_clipping_planes(self):
		cdef float* m
		# we must put these points and vectors in the camera coordsys
		cdef float p1[3], p2[3], v1[3], v2[3]
		p1[0] = p1[1] = -0.5
		p1[2] = 0.0
		p2[0] = p2[1] = 0.5
		p2[2] = 0.0
		v1[0] = v1[2] = 0.0
		v1[1] = 1.0
		v2[1] = v2[2] = 0.0
		v2[0] = 1.0
		
		m = self._root_matrix()
		point_by_matrix (p1, m)
		point_by_matrix (p2, m)
		vector_by_matrix(v1, m)
		vector_by_matrix(v2, m)
		
		m = renderer.current_camera._inverted_root_matrix()
		point_by_matrix (p1, m)
		point_by_matrix (p2, m)
		vector_by_matrix(v1, m)
		vector_by_matrix(v2, m)
		
		# compute planes equations
		self._equation[ 0] = <double> ( p1[1] * v1[2] - p1[2] * v1[1])
		self._equation[ 1] = <double> (-p1[0] * v1[2] + p1[2] * v1[0])
		self._equation[ 2] = <double> ( p1[0] * v1[1] - p1[1] * v1[0])
		self._equation[ 3] = <double> ( 0.0)
		self._equation[ 4] = <double> (-p2[1] * v1[2] + p2[2] * v1[1])
		self._equation[ 5] = <double> ( p2[0] * v1[2] - p2[2] * v1[0])
		self._equation[ 6] = <double> (-p2[0] * v1[1] + p2[1] * v1[0])
		self._equation[ 7] = <double> ( 0.0)
		self._equation[ 8] = <double> (-p1[1] * v2[2] + p1[2] * v2[1])
		self._equation[ 9] = <double> ( p1[0] * v2[2] - p1[2] * v2[0])
		self._equation[10] = <double> (-p1[0] * v2[1] + p1[1] * v2[0])
		self._equation[11] = <double> ( 0.0)
		self._equation[12] = <double> ( p2[1] * v2[2] - p2[2] * v2[1])
		self._equation[13] = <double> (-p2[0] * v2[2] + p2[2] * v2[0])
		self._equation[14] = <double> ( p2[0] * v2[1] - p2[1] * v2[0])
		self._equation[15] = <double> ( 0.0)
		if self._option & PORTAL_USE_5_CLIP_PLANES:
			self._equation[16] = <double> ( v1[1] * v2[2] - v1[2] * v2[1])
			self._equation[17] = <double> (-v1[0] * v2[2] + v1[2] * v2[0])
			self._equation[18] = <double> ( v1[0] * v2[1] - v1[1] * v2[0])
			self._equation[19] = <double> -(self._equation[16] * p1[0] + self._equation[17] * p1[1] + self._equation[18] * p1[2])
			
	cdef void _compute_points(self):
		cdef int      nb, i
		cdef float    v, f
		cdef float*   p1, *p2
		cdef Frustum* frustum
		# it's difficult to draw the portal quad even if a part of the quad is below the camera
		# front plane (we must avoid blinking when the camera is very near the portal)
		
		cdef float p[12] # = { -0.5, -0.5, 0.0, 0.5, -0.5, 0.0, 0.5, 0.5, 0.0, -0.5, 0.5, 0.0 }
		p[ 0] = p[ 1] = -0.5
		p[ 2] =  0.0
		p[ 3] =  0.5
		p[ 4] = -0.5
		p[ 5] =  0.0
		p[ 6] = p[ 7] = 0.5
		p[ 8] =  0.0
		p[ 9] = -0.5
		p[10] =  0.5
		p[11] =  0.0
		
		# put the 4 points of the portal in the camera coordsys. render_matrix must be set !!!
		point_by_matrix(p,     self._render_matrix)
		point_by_matrix(&p[0] + 3, self._render_matrix)
		point_by_matrix(&p[0] + 6, self._render_matrix)
		point_by_matrix(&p[0] + 9, self._render_matrix)
		
		# find any point is behind the camera front plane
		free(self._coords)
		if (p[2] > -renderer.current_camera._front) or (p[5] > -renderer.current_camera._front) or (p[8] > -renderer.current_camera._front) or (p[11] > -renderer.current_camera._front):
			# intersect portal with front plane
			frustum = renderer.current_camera._frustum
			p2 = <float*> malloc(4 * sizeof(float))
			p2[0] = -frustum.planes[0]
			p2[1] = -frustum.planes[1]
			p2[2] = -frustum.planes[2]
			p2[3] =  frustum.planes[3]
			face_intersect_plane(p, 4, p2, &p1, &nb)
			free(p2)
			# intersect portal with side planes
			face_intersect_plane(p1, nb, &frustum.planes[0] +  4, &p2, &nb); free(p1)
			face_intersect_plane(p2, nb, &frustum.planes[0] +  8, &p1, &nb); free(p2)
			face_intersect_plane(p1, nb, &frustum.planes[0] + 12, &p2, &nb); free(p1)
			face_intersect_plane(p2, nb, &frustum.planes[0] + 16, &self._coords, &(self._nb_vertices))
			free(p2)
			# push portal points to the front plane ;
			# actually we must not draw the vertices with the camera front value as Z coordinate,
			# because some OpenGL won't draw the quad
			
			p1 = self._coords
			f = -(renderer.current_camera._front + renderer.current_camera._back) * 0.5
			i = 0
			while i < 3 * self._nb_vertices:
				v = f / p1[i + 2]
				p1[i]     = v * p1[i]
				p1[i + 1] = v * p1[i + 1]
				p1[i + 2] = f
				i = i + 3
		else:
			self._coords      = NULL
			self._nb_vertices = 0
		
		self._coords = <float*> realloc(self._coords, (self._nb_vertices + 4) * 3 * sizeof(float))
		nb = self._nb_vertices * 3
		memcpy(self._coords + nb, &p[0], 12 * sizeof(float))
		
	cdef void _batch(self, CoordSyst coordsyst):
		cdef int      i
		cdef float    p
		cdef float    sphere[4]
		cdef float*   matrix, *ptr
		cdef Frustum* f
		cdef Context  ctx

		if self._option & HIDDEN: return
		self._frustum_id = -1
		
		# visibility test : culling
		ptr    = renderer.root_frustum.position
		matrix = self._inverted_root_matrix()
		p      = ptr[0] * matrix[2] + ptr[1] * matrix[6] + ptr[2] * matrix[10] + matrix[14]
		if p < 0.0: # camera is behind the portal => nothing to render
			if not self._beyond is None: self.unload_beyond()
			return
		
		# visibility test : frustum
		#if self._option & PORTAL_INFINITE:
		if self._option & (PORTAL_USE_4_CLIP_PLANES | PORTAL_USE_5_CLIP_PLANES):
			f = renderer._frustum(self._parent)
			sphere[0] = self._matrix[12]
			sphere[1] = self._matrix[13]
			sphere[2] = self._matrix[14]
			if self._matrix[16] > self._matrix[17]: sphere[3] = sqrt_2 * self._matrix[16]
			else:                                   sphere[3] = sqrt_2 * self._matrix[17]
			if sphere_in_frustum(f, sphere) == 0:
				if not self._beyond is None: self.unload_beyond()
				return
		else:
			f = renderer._frustum(self)
			i = 2
			while i < 24:
				if f.points[i] <= 0.0:
					if not self._beyond is None: self.unload_beyond()
					return
				i = i + 3
			
		# load world self._beyond if necessary
		if self._beyond is None:
			self._beyond = self.load_beyond()
			if self._beyond is None: return
			
		# determine clipping planes
		if self._equation != NULL: self._compute_clipping_planes()
		if self._option & PORTAL_BOUND_ATMOSPHERE:# || self._option & PORTAL_TELEPORTER
			# compute render matrix to go to the portal
			#multiply_matrix(self._render_matrix, renderer.current_camera._render_matrix, self._root_matrix())
			multiply_matrix(self._render_matrix, coordsyst._render_matrix, self._matrix)
			self._compute_points()
			
		renderer.portals.append(self)
		# avoid batching the same world twice
		if self._beyond._option & WORLD_BATCHED: return
		if renderer.current_camera.to_render is None:
			if renderer.current_camera._get_root()._contains(self._beyond): return
		elif renderer.current_camera._to_render ._contains(self._beyond): return
		
		# create a new context
		ctx = renderer.current_context
		self._context = renderer._context()
		self._context.atmosphere = self._beyond._atmosphere
		self._context.portal     = self
		renderer.current_context = self._context
		self._beyond._option = self._beyond._option | WORLD_BATCHED # mark the world self._beyond as batched
		renderer.worlds_made.append(self._beyond)
		multiply_matrix(self._beyond._render_matrix, renderer.current_camera._render_matrix, self._beyond._root_matrix())
		self._beyond._batch(None)
		renderer.current_context = ctx
		
	cdef int _shadow(self, CoordSyst coordsyst, _Light light):
		if (light._option & LIGHT_TOP_LEVEL) and (not self._beyond is None):
			return self._beyond._shadow(coordsyst, light)
		return 0
	
	cdef void _atmosphere_clear_part(self):
		cdef int         i
		cdef float*      ptr
		cdef _Atmosphere atmosphere
		atmosphere = self._beyond._atmosphere
		
		# draw the part of the portal that is in front of the camera
		glLoadIdentity()
		glDisable(GL_TEXTURE_2D)
		glDisable(GL_FOG)
		glDisable(GL_LIGHTING)
		glDepthMask(GL_FALSE)
		glColor4fv(atmosphere._bg_color)
		glDisable(GL_CULL_FACE)
		ptr = self._coords + (self._nb_vertices * 3)
		glBegin(GL_QUADS)
		glVertex3fv(ptr)
		glVertex3fv(ptr + 3)
		glVertex3fv(ptr + 6)
		glVertex3fv(ptr + 9)
		glEnd()
		
		# draw the part of the portal that is behind the front plane of the camera
		if self._nb_vertices > 0:
			glBegin(GL_POLYGON)
			i = 0
			while i < self._nb_vertices * 3:
				glVertex3fv(self._coords + i)
				i = i + 3
			glEnd()
			
		# skyplane
		if isinstance(atmosphere, _SkyAtmosphere):
			# activate and set up clip planes
			if self._equation == NULL:
				self._equation = <double*> malloc(16 * sizeof(double))
				self._compute_clipping_planes()
			glClipPlane(GL_CLIP_PLANE0, self._equation)
			glClipPlane(GL_CLIP_PLANE1, self._equation + 4)
			glClipPlane(GL_CLIP_PLANE2, self._equation + 8)
			glClipPlane(GL_CLIP_PLANE3, self._equation + 12)
			glEnable(GL_CLIP_PLANE0)
			glEnable(GL_CLIP_PLANE1)
			glEnable(GL_CLIP_PLANE2)
			glEnable(GL_CLIP_PLANE3)
			atmosphere._draw_bg() # draw sky
			glDisable(GL_CLIP_PLANE0)
			glDisable(GL_CLIP_PLANE1)
			glDisable(GL_CLIP_PLANE2)
			glDisable(GL_CLIP_PLANE3)
			
		glEnable(GL_CULL_FACE)
		glDepthMask(GL_TRUE)
		glEnable(GL_TEXTURE_2D)
		glEnable(GL_FOG)
		glEnable(GL_LIGHTING)
		

	cdef void _draw_fog(self, _Atmosphere atmosphere):
		cdef float* ptr
		
		# draw the part of the portal that is in front of the camera
		glDisable(GL_TEXTURE_2D)
		glDisable(GL_FOG)
		glDisable(GL_LIGHTING)
		# glDepthMask(GL_FALSE)
		glDisable(GL_CULL_FACE)
		# glEnable(GL_BLEND)
		glLoadIdentity()
		ptr = self._coords + (self._nb_vertices * 3)
		glBegin(GL_QUADS)
		glColor4f(atmosphere._fog_color[0], atmosphere._fog_color[1], atmosphere._fog_color[2], atmosphere._fog_factor_at(ptr    )); glVertex3fv(ptr    )
		glColor4f(atmosphere._fog_color[0], atmosphere._fog_color[1], atmosphere._fog_color[2], atmosphere._fog_factor_at(ptr + 3)); glVertex3fv(ptr + 3)
		glColor4f(atmosphere._fog_color[0], atmosphere._fog_color[1], atmosphere._fog_color[2], atmosphere._fog_factor_at(ptr + 6)); glVertex3fv(ptr + 6)
		glColor4f(atmosphere._fog_color[0], atmosphere._fog_color[1], atmosphere._fog_color[2], atmosphere._fog_factor_at(ptr + 9)); glVertex3fv(ptr + 9)
		glEnd()
		# draw the part of the portal that is behind the front plane of the camera
		# HACK : we supposed to be too near to have fog
		# we suppose that when the protal cut the front plane of the camera, the portal is
		# near to the camera and so the fog has no influence on it
		# => we don't need to draw anything for the part of the portal that is behind
		# the front plane of the camera
		# glDisable(GL_BLEND)
		glEnable(GL_CULL_FACE)
		# glDepthMask(GL_TRUE)
		glEnable(GL_TEXTURE_2D)
		glEnable(GL_FOG)
		glEnable(GL_LIGHTING)

	cdef void _raypick(self, RaypickData raypick_data, CoordSyst raypickable, int category):
		self._beyond._raypick(raypick_data, raypickable, category)
		
	cdef int _raypick_b(self, RaypickData raypick_data, CoordSyst raypickable, int category):
		return self._beyond._raypick_b(raypick_data, raypickable, category)
	
	cdef void _collect_raypickables(self, Chunk* items, float* rsphere, float* sphere, int category):
		if self._option & NON_SOLID: return
		
		cdef CoordSyst child
		cdef float* matrix
		cdef float  s[4]
		# transform sphere to my coordsys
		# XXX avoid using self._inverted_root_matrix() -- use rather the parent's result (=sphere ?) (faster)
		matrix = self._inverted_root_matrix()
		point_by_matrix_copy(s, rsphere, matrix)
		s[3] = length_by_matrix(rsphere[3], matrix)
		
		if vector_length(s) < s[3] + 0.5: # Else, it is too far
			self._beyond._collect_raypickables(items, rsphere, sphere, category)
		
		
	def has_passed_through(self, Position old_pos, Position new_pos):
		"""Portal.has_passed_though(self, old_pos, new_pos) -> bool

Return true if moving from OLD_POS to NEW_POS pass through the portal.
NEW_POS can be either the new position or the speed vector."""
		if self._beyond is None: return 0
		
		cdef float old[3], new[3]
		cdef float f, f1, f2
		old_pos._into(self, old)
		new_pos._into(self, new)
		if isinstance(new_pos, _Vector):
			new[0] = old[0] + new[0]
			new[1] = old[1] + new[1]
			new[2] = old[2] + new[2]
			
		f = old[2] * new[2]
		if  f  > 0.0: return 0 # does not pass through the plane
		if (f == 0.0) and (old[2] == 0.0): return 0 # pass by Z=0.0
		f1 = old[2] / (old[2] + new[2])
		f2 = 1.0 - f1
		return (-0.5 < old[0] * f1 + new[0] * f2 < 0.5) and (-0.5 < old[1] * f1 + new[1] * f2 < 0.5)
	
	# Implemented in Python, due to the use of lambda
	# def pass_through(self, CoordSyst coordsyst):
	
	cdef __getcstate__(self):
		#return self._parent, self._option, self._matrix[0], self._matrix[1], self._matrix[2], self._matrix[3], self._matrix[4], self._matrix[5], self._matrix[6], self._matrix[7], self._matrix[8], self._matrix[9], self._matrix[10], self._matrix[11], self._matrix[12], self._matrix[13], self._matrix[14], self._matrix[15], self._matrix[16], self._matrix[17], self._matrix[18], self._beyond_name
		return CoordSyst.__getcstate__(self), self._beyond_name
	cdef void __setcstate__(self, cstate):
		#self._parent, self._option, self._matrix[0], self._matrix[1], self._matrix[2], self._matrix[3], self._matrix[4], self._matrix[5], self._matrix[6], self._matrix[7], self._matrix[8], self._matrix[9], self._matrix[10], self._matrix[11], self._matrix[12], self._matrix[13], self._matrix[14], self._matrix[15], self._matrix[16], self._matrix[17], self._matrix[18], self._beyond_name = cstate
		CoordSyst.__setcstate__(self, cstate[0])
		self._beyond_name = cstate[1]
		


