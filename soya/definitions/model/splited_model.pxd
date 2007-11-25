# -*- indent-tabs-mode: t -*-

# Souvarine souvarine@aliasrobotique.org
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

cdef struct _ModelPart:
	int  nb_face_groups
	int* face_groups

cdef class _SplitedModel(_SimpleModel):
	cdef Chunk**     _face_groups
	cdef int         _nb_face_groups
	cdef _ModelPart* _model_parts
	cdef int         _nb_parts
	cdef object      _face2index
	
	cdef      __getcstate__(self)
	cdef void __setcstate__(self, object cstate)
	cdef void _add_face(self, _Face face, vertex2ivertex, ivertex2index, lights, int static_shadow)
	cdef void _batch_part(self, _Body body, int index)
	cdef void _batch_end(self, _Body body)
	cdef void _render(self, _Body body)
	cdef void _raypick_part(self, RaypickData raypick_data, float* raydata, int part, CoordSyst parent)
	cdef int  _raypick_part_b(self, RaypickData raypick_data, float* raydata, int part)
