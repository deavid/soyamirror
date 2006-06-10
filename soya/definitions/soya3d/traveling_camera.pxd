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

cdef class _TravelingCamera(_Camera):
	cdef           _travelings
	cdef Traveling _traveling
	cdef float     _speed_value, _proportion
	cdef _Vector   _speed
	
	cdef void _traveling_changed(self)
		
		
cdef class Traveling(_CObj):
	cdef CoordSyst _incline_as
	cdef int       _smooth_move, _smooth_rotation
	

cdef class _FixTraveling(Traveling):
	cdef Position _target, _direction
	

cdef class _ThirdPersonTraveling(Traveling):
	cdef Position _target
	cdef _Point   __target, _best, _result, __direction
	cdef _Vector  _direction, __normal
	cdef float _distance, _offset_y, _offset_y2, _lateral_angle, _top_view
	cdef float _speed
	cdef RaypickContext _context
	
	cdef float _check(self, RaypickContext root, Position target, _Vector direction, _Point result)
