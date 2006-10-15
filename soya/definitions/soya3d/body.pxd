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



cdef class _Body(CoordSyst):
	cdef _Model _model
	cdef _Model _data
	
	cdef __getcstate__(self)
	cdef void __setcstate__(self, object cstate)
	cdef void _batch(self, CoordSyst coordsyst)
	cdef int _shadow(self, CoordSyst coordsyst, _Light light)
	cdef void _raypick(self, RaypickData raypick_data, CoordSyst raypickable, int category)
	cdef int _raypick_b(self, RaypickData raypick_data, CoordSyst raypickable, int category)
	cdef void _collect_raypickables(self, Chunk* items, float* rsphere, float* sphere, int category)
	cdef int _contains(self, _CObj obj)
	cdef void _get_box(self, float* box, float* matrix)
	
	#ode
	cdef dBodyID _OdeBodyID
	cdef _World _ode_parent
	cdef readonly joints
	cdef readonly __ode_data     #some data about ODE state load when deserealisation
	                        # but not yet used
	
	cdef GLfloat _q[4] # Previous quaternion (into ode_parent coord sys)
	cdef GLfloat _p[4] # Previous position   (into ode_parent coord sys)
	cdef float _t # Cumulative round time
	cdef int _valid # Is the previous quaternion/position valid?
	cdef _PlaceableGeom _geom
	
	
	cdef void _activate_ode_body(_Body self)
	cdef void _activate_ode_body_with(_Body self,_World world)
	cdef void _reactivate_ode_body(_Body self,_World world)
	cdef void _deactivate_ode_body(self)
	cdef _World _find_or_create_most_probable_ode_parent(self)
	cdef void _sync_ode_position(self)
	cdef void _add_joint(self, _Joint joint)
	cdef void _remove_joint(self, _Joint joint)

	
	
