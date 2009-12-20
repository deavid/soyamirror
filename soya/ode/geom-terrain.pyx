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

# A collider for a Terrain

cdef class _GeomTerrain(_Geom):
	"""Terrain/terrain collider for Soya. This is based on Benoit Chaperot's
	contributed terrain collider for ODE, with some changes to take advantage
	of precomputed normals in Soya's terrain engine.

	How it works: 

	We loop through each "cell," or square of vertices in the heightfield,
	that is underneath the axis-aligned bounding box (AABB) of the geom we're
	testing for collisions with. For rendering, each cell is divided into
	two triangles. We use ray collision to check each edge of one of the 
	triangles, because the other triangle shares edges with adjacent cells
	and we don't want to check edges twice. We make a ray for each direction
	along the edge to get two collision points so we can take the midpoint
	of the two collision points if there is a collision. Right now the normal
	is halfway between the normals computed by Soya for the vertices making
	the edge being tested. This could be weighted, but we don't bother right
	now and it seems to work fine.

	Next, we test the plane of each triangle. We use ODE's own plane collision
	routines to give us a set of collision points on the plane. We then test
	to see if any of the collision points are within the triangle we're testing
	by first seeing if the point is within the cell (a simple range check),
	then testing if it's in the correct isoceles right triangle, which means
	just looking at the sum of the x and z deltas from the upper left vertex
	of the cell. If it's less than the length of one leg, it's in the upper
	triangle. If it's greater, it's in the lower. We keep the normal from any
	plane contact points we keep.

	Ray collision is not currently implemented, but could easily be handled
	using Soya's own raypicking routines. Likewise plane collision, which 
	might be able to use the view frustum culling routines. I don't currently
	plan to implement these because I have ambitions about doing all collision
	detection within Soya rather than using ODE's collision detection.
	"""


	cdef void _get_aabb(self, dReal aabb[6]):
		"""Get the axis-aligned bounding box.
		This is slow and it's fortunate that terrains aren't currently considered
		placeable so it only gets called once. If we want terrains to be
		placeable, we need to cache the information and invalidate it
		if the terrain is moved. This may require going back to subclassing
		_Terrain, or coming up with a hook mechanism for getting notified
		when a coordsyst is updated."""

		cdef _Terrain terrain
		cdef float min_x, max_x, min_y, max_y, min_z, max_z
		cdef int i
		cdef GLfloat m[19], P[3]

		terrain = self._terrain

		# Calculate the true AABB
		# Make sure it's not getting called a lot
		print "Calculating AABB for terrain (slow)"

		# Get the matrix for transforming points to world coordinates
		multiply_matrix(m, terrain._root_matrix(), self._ode_root._inverted_root_matrix())

		# Set up the minima and maxima
		point_by_matrix_copy(P, terrain._vertices[0].coord, m)
		min_x = P[0]
		max_x = P[0]
		min_y = P[1]
		max_y = P[1]
		min_z = P[2]
		max_z = P[2]

		for i from 1 <= i < terrain._nb_vertex_width * terrain._nb_vertex_depth:
				# Transform each vertex to world coordinates
				point_by_matrix_copy(P, terrain._vertices[i].coord, m)
				if P[0] < min_x:
						min_x = P[0]

				if P[0] > max_x:
						max_x = P[0]

				if P[1] < min_y:
						min_y = P[1]
				
				if P[1] > max_y:
						max_y = P[1]

				if P[2] < min_z:
						min_z = P[2]

				if P[2] > max_z:
						max_z = P[2]
		
		self.min_x = aabb[0] = min_x
		self.max_x = aabb[1] = max_x
		self.min_y = aabb[2] = min_y
		self.max_y = aabb[3] = max_y
		self.min_z = aabb[4] = min_z
		self.max_z = aabb[5] = max_z

	cdef int _collide_cell(self, int x, int z, dGeomID o1, 
			 dGeomID o2, int max_contacts, int flags, 
			 dContactGeom *contact, int skip):#,dGetDepthFn *GetDepth):
		"""Test for any collisions within a single cell of the heightfield
		grid."""

		cdef TerrainVertex *vA, *vB, *vC, *vD
		cdef GLfloat A[3], B[3], C[3], D[3], NB[3], NC[3], ND[3]
		cdef GLfloat AB[3], AC[3], BC[3], BD[3], CD[3]
		cdef GLfloat plane[4]
		cdef int num_contacts, numPlaneContacts
		cdef dContactGeom ContactA[3], ContactB[3], *pContact
		cdef dContactGeom planeContact[10]
		cdef GLfloat m[19] # Matrix to convert to world coordinates
		cdef _Terrain terrain

		num_contacts = 0

		terrain = self._terrain

		multiply_matrix(m, terrain._root_matrix(), self._ode_root._inverted_root_matrix())
			
		# Get the four vertices for this cell
		# Pointer arithmetic is evil.
		vA = terrain._vertices + (x + z * terrain._nb_vertex_width)
		vB = vA + 1
		vC = vA + terrain._nb_vertex_width
		vD = vB + terrain._nb_vertex_width

		# Hmmm, already have normals calculated for both
		# vertices *and* triangles. This could be good.

		# Transform each vertex to the world's coordsys
		point_by_matrix_copy(A, vA.coord, m)
		point_by_matrix_copy(B, vB.coord, m)
		point_by_matrix_copy(C, vC.coord, m)
		point_by_matrix_copy(D, vD.coord, m)

		# Transform the normals to the world's coordsys
		point_by_matrix_copy(NB, vB.normal, m)
		point_by_matrix_copy(NC, vC.normal, m)
		point_by_matrix_copy(ND, vD.normal, m)
		
		# Renormalize the normals. This is only needed if we allow the terrain
		# to be scaled by Terrain.scale(fx, fy, fz)
		vector_normalize(NB)
		vector_normalize(NC)
		vector_normalize(ND)


		# Make all the vectors we need
		vector_from_points(AB, A, B)
		vector_normalize(AB)
		vector_from_points(AC, A, C)
		vector_normalize(AC)
		vector_from_points(BC, B, C)
		vector_normalize(BC)
		vector_from_points(BD, B, D)
		vector_normalize(BD)
		vector_from_points(CD, C, D)
		vector_normalize(CD)

		# Ray collision to test edges of one triangle
		# Don't need to test the other because adjacent cells will
		#num_contacts = num_contacts + collide_edge(B, C, BC, NB, 
		#		NC, o1, o2, max_contacts - num_contacts, flags, 
		#		<dContactGeom*>(<char*>contact + (num_contacts * skip)))
		#
		#if num_contacts == max_contacts:
		#		return num_contacts
		#
		#num_contacts = num_contacts + collide_edge(B, D, BD, NB,
		#		ND, o1, o2, max_contacts - num_contacts, flags, 
		#		<dContactGeom*>(<char*>contact + (num_contacts * skip)))
		#
		#if num_contacts == max_contacts:
		#		return num_contacts
		#
		#num_contacts = num_contacts + collide_edge(C, D, CD, NC,
		#		ND, o1, o2, max_contacts - num_contacts, flags, 
		#		<dContactGeom*>(<char*>contact + (num_contacts * skip)))

		#if num_contacts == max_contacts:
		#		return num_contacts

		# Now do planes for each of the two triangle planes
		# XXX If the plane test fails, we could skip the ray tests.
		vector_cross_product(plane, AC, AB)
		#vector_normalize(plane)
		plane[3] = plane[0] * A[0] + plane[1] * A[1] + plane[2] * A[2]
		dGeomPlaneSetParams(_terrain_plane, plane[0], plane[1], plane[2], plane[3])

		numPlaneContacts = dCollide(o2, _terrain_plane, flags, planeContact, sizeof(dContactGeom))

		#print "a", numPlaneContacts

		for i from 0 <= i < numPlaneContacts:
				# Figure out if the point is in the triangle.
				# Only need to test x and z coord because we already know it's
				# in the plane and the plane is not vertical

				# First, check if it's in the cell
				if planeContact[i].pos[0] < A[0] or planeContact[i].pos[0] > D[0]:
						continue

				if planeContact[i].pos[2] < A[2] or planeContact[i].pos[2] > D[2]:
						continue

				# Now, check if it's in the correct triangle in the cell.
				# This is made easier since we only support isoceles right triangles
				if (planeContact[i].pos[0] - A[0] + planeContact[i].pos[2] - A[2]) > (D[0] - A[0]):
						continue
				
				# It's in the triangle, so add it to our list of contacts
				pContact = <dContactGeom*>((<char*>contact) + (num_contacts * skip))
				#print <long>contact, <long>pContact, num_contacts, skip
				pContact.pos[0] = planeContact[i].pos[0]
				pContact.pos[1] = planeContact[i].pos[1]
				pContact.pos[2] = planeContact[i].pos[2]
				pContact.normal[0] = -planeContact[i].normal[0]
				pContact.normal[1] = -planeContact[i].normal[1]
				pContact.normal[2] = -planeContact[i].normal[2]
				pContact.depth = planeContact[i].depth
				pContact.g1 = o1
				pContact.g2 = o2

				##print "a", pContact.pos[0], pContact.pos[1], pContact.pos[2], pContact.normal[0], pContact.normal[1], pContact.normal[2], pContact.depth
				num_contacts = num_contacts + 1

				if num_contacts == max_contacts:
						return num_contacts

		# Try the plane for the other triangle
		vector_cross_product(plane, BD, CD)
		vector_normalize(plane)
		plane[3] = plane[0] * D[0] + plane[1] * D[1] + plane[2] * D[2]
		dGeomPlaneSetParams(_terrain_plane, plane[0], plane[1], plane[2], plane[3])

		numPlaneContacts = dCollide(o2, _terrain_plane, flags, planeContact, sizeof(dContactGeom))

		#print "b", numPlaneContacts

		for i from 0 <= i < numPlaneContacts:
				# Figure out if the point is in the triangle.
				# Only need to test x and z coord because we already know it's
				# in the plane and the plane is not vertical

				# First, check if it's in the cell
				if planeContact[i].pos[0] < A[0] or planeContact[i].pos[0] > D[0]:
						continue

				if planeContact[i].pos[2] < A[2] or planeContact[i].pos[2] > D[2]:
						continue

				# Now, check if it's in the correct triangle in the cell.
				# This is made easier since we only support isoceles right triangles
				if (planeContact[i].pos[0] - A[0] + planeContact[i].pos[2] - A[2]) < (D[0] - A[0]):
						continue
				
				# It's in the triangle, so add it to our list of contacts
				pContact = <dContactGeom*>((<char*>contact) + (num_contacts * skip))
				#print <long>contact, <long>pContact, num_contacts, skip
				pContact.pos[0] = planeContact[i].pos[0]
				pContact.pos[1] = planeContact[i].pos[1]
				pContact.pos[2] = planeContact[i].pos[2]
				pContact.normal[0] = -planeContact[i].normal[0]
				pContact.normal[1] = -planeContact[i].normal[1]
				pContact.normal[2] = -planeContact[i].normal[2]
				pContact.depth = planeContact[i].depth
				pContact.g1 = o1
				pContact.g2 = o2
				
				#print "b", pContact.pos[0], pContact.pos[1], pContact.pos[2], pContact.normal[0], pContact.normal[1], pContact.normal[2], pContact.depth

				num_contacts = num_contacts + 1

				if num_contacts == max_contacts:
						return num_contacts

		return num_contacts


	cdef int _collide(self, dGeomID o1, dGeomID o2, int flags,
										dContactGeom *contact, int skip):#,dGetDepthFn *GetDepth):
			cdef int num_contacts, max_contacts, x, z, i, j, k
			cdef GLfloat min_x, max_x, min_z, max_z
			cdef dReal aabb[6], depth
			cdef dContactGeom *pContact
			cdef dVector3 lengths
			#cdef dReal *R
			cdef TerrainVertex *vA, *vB, *vC, *vD
			cdef GLfloat m[19] # Matrix to convert to terrain's coordinate system
			cdef GLfloat BC, BD, CD
			cdef GLfloat plane[4]
			cdef _Terrain terrain
			cdef GLfloat P[3] # Point for converting AABB corners

			terrain = self._terrain

			# Get the maximum number of contacts from the flags
			max_contacts = (flags & 0xffff) or 1

			# Only 10 contacts allowed for called collision functions
			flags = (flags & 0xffff0000) | 10

			#R = dGeomGetRotation(o2)

			# Get the AAAB of the geom
			dGeomGetAABB(o2, aabb)

			# Convert the AABB to the terrain's coordinate system. XXX this is slower
			# than if we could assume the terrains' axes were aligned with the
			# world's axes, but we can't.

			# Make the matrix
			multiply_matrix(m, self._ode_root._root_matrix(), terrain._inverted_root_matrix())

			P[0] = aabb[0]
			P[1] = aabb[2]
			P[2] = aabb[4]
			
			point_by_matrix(P, m)

			# Only care about x and z axes
			min_x = P[0]
			max_x = P[0]
			min_z = P[2]
			max_z = P[2]

			# Do the other seven corners
			for i, j, k in ((1, 2, 4), (0, 3, 4), (1, 3, 4), (0, 2, 5), (1, 2, 5), (0, 3, 5), (1, 3, 5)):
					P[0] = aabb[i]
					P[1] = aabb[j]
					P[2] = aabb[k]

					point_by_matrix(P, m)
	
					if P[0] < min_x:
							min_x = P[0]
					if P[0] > max_x:
							max_x = P[0]
					if P[2] < min_z:
							min_z = P[2]
					if P[2] > max_z:
							max_z = P[2]

			num_contacts = 0
			# Test all cells that are under the AABB
			for z from <int>floor(max(0, min_z)) <= z < <int>ceil(min(terrain._nb_vertex_depth, max_z)):
					for x from <int>floor(max(0, min_x)) <= x < <int>ceil(min(terrain._nb_vertex_width, max_x)):
							num_contacts = num_contacts + self._collide_cell(x, z, o1, 
									o2, max_contacts - num_contacts, flags, 
									<dContactGeom*>((<char*>contact) + (num_contacts*skip)), 
									skip)

			return num_contacts

	#def __new__(self, _Terrain terrain, SpaceBase space=None, *args, **kw):
		#self._terrain = terrain 
		#self._OdeGeomID = 
		#
		#if space is not None:
		#	dSpaceAdd(space.sid, self._OdeGeomID)

	def __init__(self, _Terrain terrain):
		cdef _World parent
		print "I'm created"
		if terrain is not None:
			parent = terrain._parent
			if parent._space is None:
				SimpleSpace(world=parent)
			space = parent._space
		else:
			space = None
		self._terrain = None
		_Geom.__init__(self,space)
		self.terrain = terrain
	cdef _create(self):
		cdef dSpaceID sid
		if self._space is not None:
			sid = <dSpaceID>self._space._OdeGeomID
		else:
			sid = NULL
		self._OdeGeomID = dCreateGeom(dTerrainClass)
		dSpaceAdd(sid,self._OdeGeomID)

	def __dealloc__(self):
			print "dealloc", self
	property terrain:
		def __set__(self, _Terrain terrain):
			if self._terrain is not terrain:
				if self._terrain is not None:
					self._terrain._geom = None
				self._terrain = terrain
				if terrain  is None:
					#dGeomSetBody(self._OdeGeomID,NULL)
					self._ode_root = None
				else:
					self._ode_root = _find_or_create_most_probable_ode_parent_from(terrain._parent)
					terrain._geom = self
				
			
		def __get__(self):
			return self._terrain

	property body:
		def __get__(self):
			"""Terrain can't have a body, so return environment"""
			return None
	property pushable:
		def __get__(self):
			return False


cdef dGeomID _terrain_plane # Reusable plane geom
cdef dGeomID _terrain_ray   # Reusable ray geom

_terrain_plane = dCreatePlane(NULL, 0.0, 1.0, 0.0, 0.0)
_terrain_ray = dCreateRay(NULL, 1.0)

cdef void _TerrainGetAABB(dGeomID geom, dReal aabb[6]):
		cdef _GeomTerrain geom_terrain
		cdef void* tmp_ptr
		tmp_ptr = dGeomGetData(geom)
		geom_terrain = <_GeomTerrain>tmp_ptr
		geom_terrain._get_aabb(aabb)

cdef int _TerrainCollide(dGeomID o1, dGeomID o2, int flags,
										 dContactGeom *contact, int skip):
		cdef _GeomTerrain geom_terrain
		cdef void* tmp_ptr
		tmp_ptr = dGeomGetData(o1)
		geom_terrain = <_GeomTerrain>tmp_ptr
		return geom_terrain._collide(o1, o2, flags, contact, skip)


cdef dColliderFn * _TerrainGetColliderFn(int gclass):

		if gclass in (dSphereClass, dBoxClass, dCapsuleClass, dCylinderClass):
				return _TerrainCollide
		raise RuntimeError("TerrainGeom can't collide with non primitive Geom")


#U#cdef int _TerrainAABBTest(dGeomID o1, dGeomID o2, dReal aabb2[6]):
#U#		pass



		
cdef int dTerrainClass


cdef void geomterrain_init():
	global dTerrainClass 
	cdef dGeomClass dTerrainGeomClass

	dTerrainGeomClass.bytes = 0
	dTerrainGeomClass.collider = _TerrainGetColliderFn
	dTerrainGeomClass.aabb = _TerrainGetAABB
	dTerrainGeomClass.aabb_test = NULL # Need to write this function
	dTerrainGeomClass.dtor = NULL	
	dTerrainClass = dCreateGeomClass(&dTerrainGeomClass)


