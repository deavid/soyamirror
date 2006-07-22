# -*- indent-tabs-mode: t -*-

# Soya 3D
# Copyright (C) 2003-2004 Jean-Baptiste LAMY -- jiba@tuxfamily.org
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

cdef class _Vertex(_Point):
	cdef float   _tex_x, _tex_y
	cdef         _diffuse, _emissive
	cdef _Face   _face
	cdef _Vector _normal
	
	cdef __getcstate__(self)
	cdef void __setcstate__(self, object cstate)
	cdef void _render(self, CoordSyst coord_syst)
	cdef float _angle_at(self)


cdef class _Face(CoordSyst):
	cdef object     _vertices
	cdef _Material  _material
	cdef _Vector    _normal
	
	cdef __getcstate__(self)
	cdef void __setcstate__(self, object cstate)
	cdef void _compute_normal(self)
	cdef void _batch(self, CoordSyst coord_syst)
	cdef void _render(self, CoordSyst coord_syst)
	cdef void _get_box(self, float* box, float* matrix)
	cdef void _raypick(self, RaypickData data, CoordSyst parent, int category)
	cdef int _raypick_b(self, RaypickData data, CoordSyst parent, int category)
	cdef void _collect_raypickables(self, Chunk* items, float* rsphere, float* sphere, int category)

