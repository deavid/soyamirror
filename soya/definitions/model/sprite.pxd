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

cdef class _Sprite(CoordSyst):
	cdef float _width, _height
	cdef float _color[4]
	cdef _Material _material
	
	cdef __getcstate__(self)
	cdef void __setcstate__(self, object cstate)
	cdef void _batch(self, CoordSyst coordsyst)
	cdef void _render(self, CoordSyst coordsyst)
	cdef void _compute_alpha(self)
		
		
cdef class _CylinderSprite(_Sprite):
	cdef __getcstate__(self)
	cdef void __setcstate__(self, object cstate)
	cdef void _render(self, CoordSyst coordsyst)


cdef class _Bonus(CoordSyst):
	cdef float _angle
	cdef float _color[4]
	cdef _Material _material, _halo
	
	cdef __getcstate__(self)
	cdef void __setcstate__(self, object cstate)
	cdef void _batch(self, CoordSyst coordsyst)
	cdef void _render(self, CoordSyst coordsyst)

