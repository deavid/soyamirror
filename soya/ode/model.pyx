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

# A collider for a Model

cdef class _TriMesh(GeomObject):
		"""Parent class for all TriMesh-derived geoms.
		TriMesh-TriMesh collison does not currently return meaningful normals
		or depth, so don't try to use it for collision response!"""

		cdef dTriMeshDataID _data
		cdef double _last_transformation[16]
		cdef int _colliding # Flag indicating if we're currently colliding with
												# another TriMesh

		def __new__(self, parent, space, *args, **kw):
				self._data = dGeomTriMeshDataCreate()
				#self._last_transformation = <double*>malloc(16 * sizeof(double))
				self._colliding = 0

		def __dealloc__(self):
				dGeomTriMeshDataDestroy(self._data)
				#free(self._last_transformation)

		cdef void _set_last_transformation(self):
				#cdef dReal *R, *P
				cdef double *t
				cdef int i, j

				t = self._last_transformation
				# Only set the last transformation if we're not currently colliding
				# with another TriMesh
				if self._colliding == 0:
						print 'setting last transformation'
						#R = dGeomGetRotation(self.gid)
						#P = dGeomGetPosition(self.gid)
		
						for i from 0 <= i < 16:
								t[i] = <double>self._matrix[i]
						## Try transposing
						#for j from 0 <= j < 3:
						#    for i from 0 <= i < 3:
						#        t[i*4+j] = <double>self._matrix[j*4+i]
	 # 
	 #         t[3] = 0.0
	 #         t[7] = 0.0
	 #         t[11] = 0.0
	 #         t[12] = <double>self._matrix[13]
	 #         t[13] = <double>self._matrix[14]
	 #         t[14] = <double>self._matrix[15]
	 #         t[15] = 1.0
				
				else:
						# Reset the colliding flag. This assumes that _invalidate
						# is only called once per round, which is probably not
						# valid. XXX
						self._colliding = 0

				# I think this needs to be called regardless of whether there's an
				# update
				dGeomTriMeshDataSet(self._data, TRIMESH_LAST_TRANSFORMATION, <void*>t)

cdef class _GeomModel(_TriMesh):
		"""Model collider for Soya.

		Models can collide with primitives (box, sphere, capped cylinder, ray),
		but not with other models or with terrains.

		The axis-aligned bounding box (AABB) is calculated from the bounding
		sphere of the model.

		Models *must* be made of only triangles!
		"""

		cdef readonly _soya._SimpleModel model
		cdef float *_normals
		cdef int *_indices

		def __new__(self, _soya._World parent, SpaceBase space, _soya._SimpleModel model=None, *args, **kw):
				cdef _soya.ModelFace face
				cdef float *normals
				cdef int *indices
				cdef int i, nb_tris
				cdef dSpaceID sid

				if model is None:
						model = parent._model

				self.model = model

				nb_tris = model._nb_faces
				# Count the number of quads and add one triangle for each quad
				for i from 0 <= i < model._nb_faces:
						if model._faces[i].option & _soya.FACE_QUAD:
								nb_tris = nb_tris + 1
						

				self._normals = <float*>malloc(nb_tris * sizeof(dReal) * 3)
				self._indices = <int*>malloc(nb_tris * sizeof(int) * 3)

				if space is None:
						sid = NULL
				else:
						sid = space.sid

				normals = self._normals
				indices = self._indices

				# Extract the normals from the model while making sure all the
				# faces are triangles

				for i from 0 <= i < model._nb_faces:
						face = model._faces[i]

						memcpy(normals, model._values + face.normal, 3 * sizeof(dReal))
						normals = normals + 3

						indices[0] = model._vertex_coords[face.v[0]] / 3
						indices[1] = model._vertex_coords[face.v[1]] / 3
						indices[2] = model._vertex_coords[face.v[2]] / 3
						indices = indices + 3

						if face.option & _soya.FACE_QUAD:
								# Do a second triangle using the fourth vertex
								memcpy(normals, model._values + face.normal, 3 * sizeof(dReal))
								normals = normals + 3

								indices[0] = model._vertex_coords[face.v[1]] / 3
								indices[1] = model._vertex_coords[face.v[2]] / 3
								indices[2] = model._vertex_coords[face.v[3]] / 3
								indices = indices + 3

				#print <long>model._coords, model._nb_coords, <long>self._indices, model._nb_faces * 3, <long>normals

				dGeomTriMeshDataBuildSingle1(self._data, model._coords, 3 * sizeof(dReal), model._nb_coords, self._indices, nb_tris * 3, 3 * sizeof(int), <void*>self._normals)

				self.gid = dCreateTriMesh(sid, self._data, NULL, NULL, NULL)

		def __dealloc__(self):
				free(self._normals)
				free(self._indices)

		def placeable(self):
				return True


cdef class _GeomTerrain(_TriMesh):
		"""Terrain collider for Soya.
		"""

		cdef readonly _soya._Terrain terrain
		cdef float *_normals
		cdef int *_indices

		def __new__(self, _soya._Terrain terrain, SpaceBase space, *args, **kw):
				cdef float *normals
				cdef int *indices
				cdef int i, nvertices, ntris, v1, v2, v3, v4
				cdef dSpaceID sid

				if space is None:
						sid = NULL
				else:
						sid = space.sid

				self.terrain = terrain

				nvertices = terrain._nb_vertex_width * terrain._nb_vertex_depth
				ntris = ((terrain._nb_vertex_width - 1) * (terrain._nb_vertex_depth - 1)) * 2

				#self._vertices = <float*>malloc(nvertices * sizeof(float) * 3)
				#self._normals = <float*>malloc(ntris * sizeof(float) * 3)
				self._indices = <int*>malloc(ntris * sizeof(int) * 3)

				indices = self._indices
				for j from 0 <= j < terrain._nb_vertex_depth - 1:
						for i from 0 <= i < terrain._nb_vertex_width - 1:
								v1 = i + j * terrain._nb_vertex_width       
								v2 = i + 1 + j * terrain._nb_vertex_width
								v3 = i + 1 + (j + 1) * terrain._nb_vertex_width
								v4 = i + (j + 1) * terrain._nb_vertex_width

								# Terrain uses diamonds
								if ((i & 1) and (j & 1)) or ((not (i * 1)) and (not (j & 1))):
										# Down and to the right
										indices[0] = v4
										indices[1] = v3
										indices[2] = v1
										indices[3] = v2
										indices[4] = v1
										indices[5] = v3
								else:
										# Down and to the left
										indices[0] = v1
										indices[1] = v4
										indices[2] = v2
										indices[3] = v3
										indices[4] = v2
										indices[5] = v4

								indices = indices + 6
				
				dGeomTriMeshDataBuildSingle1(self._data, terrain._vertices[0].coord, sizeof(terrain._vertices[0]), nvertices, self._indices, ntris * 3, 3 * sizeof(int), NULL) #<void*>terrain._normals)

				self.gid = dCreateTriMesh(sid, self._data, NULL, NULL, NULL)

		def __dealloc__(self):
				free(self._indices)

		def __init__(self, _soya._Terrain terrain, SpaceBase space=None):
				GeomObject.__init__(self, terrain._parent, space)

		def placeable(self):
				return True




