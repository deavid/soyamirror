# -*- indent-tabs-mode: t -*-

# Soya 3D
# Copyright (C) 2003 Jean-Baptiste LAMY -- jiba@tuxfamily.org
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

cdef class Position(_CObj):
	cdef CoordSyst _parent
	cdef void _into(self, CoordSyst coordsyst, float* result)
	cdef void _out(self, float* result)


cdef class _Point(Position):
	cdef float _matrix[3]
	cdef void _into(self, CoordSyst coordsyst, float* result)
	cdef void _out(self, float* result)
	cdef __getcstate__(self)
	cdef void __setcstate__(self, object cstate)


cdef class _Vector(_Point):
	cdef void _into(self, CoordSyst coordsyst, float* result)
	cdef void _out(self, float* result)

cdef class _Plane(Position):
	cdef float _matrix[4]
	cdef void _into(self, CoordSyst coordsyst, float* result)
	cdef void _out(self, float* result)
	cdef void _init_from_equation(self, float a, float b, float c, float d)
	cdef void _init_from_point_and_normal(self, _Point point, _Vector normal)
	cdef void _init_from_3_points(self, _Point p1, _Point p2, _Point p3)
