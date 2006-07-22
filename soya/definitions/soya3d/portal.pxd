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
	cdef _World  _beyond
	cdef         _beyond_name
	cdef double* _equation  # Clip plane equations
	cdef Context _context
	
	cdef int     _nb_vertices # NB vertex and their coordinates for the portal quad ;
	cdef float*  _coords      # used to draw this quad (for bounds atmosphere or teleporter).
	
	cdef void _compute_clipping_planes(self)
	cdef void _compute_points(self)
	cdef void _batch(self, CoordSyst coordsyst)
	cdef int _shadow(self, CoordSyst coordsyst, _Light light)
	cdef void _atmosphere_clear_part(self)
	cdef void _draw_fog(self, _Atmosphere atmosphere)
	cdef void _raypick(self, RaypickData raypick_data, CoordSyst raypickable, int category)
	cdef int _raypick_b(self, RaypickData raypick_data, CoordSyst raypickable, int category)
	cdef void _collect_raypickables(self, Chunk* items, float* rsphere, float* sphere, int category)
	cdef __getcstate__(self)
	cdef void __setcstate__(self, object cstate)


