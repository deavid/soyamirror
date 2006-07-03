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



cdef class _Cal3dBody(CoordSyst):
	cdef _AnimatedModel _model
	cdef             _attached_meshes, _attached_coordsysts
	cdef CalModel*   _model
	cdef float       _delta_time
	cdef float*      _face_planes, *_vertex_coords, *_vertex_normals
	cdef int         _face_plane_ok, _vertex_ok
	
	cdef __getcstate__(self)
	cdef void __setcstate__(self, cstate)
	cdef void _build_submeshes(self)
	cdef void _build_face_planes(self)
	cdef void _attach_all(self)
	cdef void _batch(self, CoordSyst coordsyst)
	cdef int _shadow(self, CoordSyst coordsyst, _Light light)
	cdef void _raypick(self, RaypickData data, CoordSyst parent)
	cdef int _raypick_b(self, RaypickData data, CoordSyst parent)
			
