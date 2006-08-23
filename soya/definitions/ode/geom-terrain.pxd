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
ctypedef dReal dGetDepthFn(dGeomID g, dReal x, dReal y, dReal z)

cdef class _GeomTerrain(_Geom):
		cdef _Terrain _terrain
		cdef CoordSyst _ode_root
		cdef float min_x, max_x, min_y, max_y, min_z, max_z

		cdef void _get_aabb(self, dReal aabb[6])
		#cdef int _collide_edge(self, GLfloat *A, GLfloat *B,
		#											 GLfloat *AB, GLfloat *normalA,
		#											 GLfloat *normalB, dGeomID o1, dGeomID o2, 
		#											 int max_contacts, int flags, dContactGeom *contact, 
		#											 dGetDepthFn *GetDepth)
		cdef int _collide_cell(self, int x, int z, dGeomID o1, 
													 dGeomID o2, int max_contacts, int flags, 
													 dContactGeom *contact, int skip)#,
													 #dGetDepthFn *GetDepth)
		cdef int _collide(self, dGeomID o1, dGeomID o2, int flags,
											dContactGeom *contact, int skip)#, 
											#dGetDepthFn *GetDepth)
		

