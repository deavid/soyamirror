# -*- indent-tabs-mode: t -*-

# Soya 3D
# Copyright (C) 2001-2004 Jean-Baptiste LAMY -- jiba@tuxfamily.org
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

cdef class MainLoop:
	cdef                 _next_round_tasks
	cdef                 _round_tasks
	cdef                 _return_value
	cdef                 _scenes
	cdef                 _events
	cdef                 _raw_events
	cdef                 _queued_events
	cdef public   double round_duration, min_frame_duration
	cdef readonly double fps
	cdef public   int    running
	cdef public   int    will_render
	cdef double          _time, _time_since_last_round
	cdef          double _last_fps_computation_time
	cdef          int    _nb_frame
