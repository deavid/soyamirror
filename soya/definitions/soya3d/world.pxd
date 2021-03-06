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


	
cdef class _World(_Body):
	cdef readonly         children
	cdef _Atmosphere      _atmosphere
	cdef public           _filename
	cdef ModelBuilder     _model_builder
	cdef dWorldID         _OdeWorldID
	cdef readonly         ode_children
	cdef _Space           _space
	cdef _JointGroup _contact_group
	#_contact_group = _JointGroup()
	
	
	cdef __getcstate__(self)
	cdef void __setcstate__(self, object cstate)
	cdef _World _get_root(self)
	cdef void _invalidate(self)
	cdef void _batch(self, CoordSyst coordsyst)
	cdef int _shadow(self, CoordSyst coordsyst, _Light light)
	cdef void _raypick(self, RaypickData raypick_data, CoordSyst raypickable, int category)
	cdef int _raypick_b(self, RaypickData raypick_data, CoordSyst raypickable, int category)
	cdef int _contains(self, _CObj obj)
	cdef void _get_box(self, float* box, float* matrix)
	cdef void _search_all(self, predicat, result)
	cdef void _collect_raypickables(self, Chunk* items, float* rsphere, float* sphere, int category)
	
	#ode
	cdef void _activate_ode_world(self)
	cdef void _deactivate_ode_world(self)
	
	#cdef void _add_space(self)
