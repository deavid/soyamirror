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

cdef class ModelBuilder(_CObj):
	cdef _Model _to_model(self, _World world)


cdef class SimpleModelBuilder(ModelBuilder):
	cdef int   _shadow
	cdef float _max_face_angle
	
	cdef __getcstate__(self)
	cdef void __setcstate__(self, object cstate)
	cdef _Model _to_model(self, _World world)

	
cdef class TreeModelBuilder(SimpleModelBuilder):
	cdef float _collapsing_distance
	cdef int   _quality
	cdef float _max_child_radius
	
	cdef __getcstate__(self)
	cdef void __setcstate__(self, object cstate)
	cdef _Model _to_model(self, _World world)
	
		
cdef class CellShadingModelBuilder(SimpleModelBuilder):
	cdef _Material _shader
	cdef           _outline_color
	cdef float     _outline_width, _outline_attenuation
	
	cdef __getcstate__(self)
	cdef void __setcstate__(self, object cstate)
	cdef _Model _to_model(self, _World world)
		
	
