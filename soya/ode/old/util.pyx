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

# Utilities for custom Soya colliders

cdef int collide_edge(GLfloat *A, GLfloat *B,
											 GLfloat *AB, GLfloat *normalA,
											 GLfloat *normalB,
											 dGeomID o1, dGeomID o2, int max_contacts, 
											 int flags, dContactGeom *contact):
		"""Check for collision with one triangle edge. Uses a normal
		that's halfway between the precomputed normals of the vertices
		that make up the edge."""

		cdef int n, num_contacts, nA, nB
		cdef dContactGeom contactA, contactB
		cdef GeomObject other
		cdef void* tmp_buf

		# First, do one direction
		dGeomRaySetLength(_land_ray, _soya.point_distance_to(A, B))
		dGeomRaySet(_land_ray, A[0], A[1], A[2], AB[0], AB[1], AB[2])
		nA = dCollide(_land_ray, o2, flags, &contactA, sizeof(dContactGeom))

		# Then the other
		dGeomRaySet(_land_ray, B[0], B[1], B[2], -AB[0], -AB[1], -AB[2])
		nB = dCollide(_land_ray, o2, flags, &contactB, sizeof(dContactGeom))

		if nA and nB:
				contact.pos[0] = (contactA.pos[0] + contactB.pos[0]) / 2.0
				contact.pos[1] = (contactA.pos[1] + contactB.pos[1]) / 2.0
				contact.pos[2] = (contactA.pos[2] + contactB.pos[2]) / 2.0

				# D
				contact.normal[0] = (normalA[0] + normalB[0]) / 2.0
				contact.normal[1] = (normalA[1] + normalB[1]) / 2.0
				contact.normal[2] = (normalA[2] + normalB[2]) / 2.0

				# Get the depth of the contact point in the colliding geom
				tmp_buf = dGeomGetData(o2)
				other = <GeomObject>tmp_buf
				contact.depth = other._point_depth(contact.pos[0], contact.pos[1], 
																					 contact.pos[2])
				contact.g1 = o1
				contact.g2 = o2

				return 1

		return 0


