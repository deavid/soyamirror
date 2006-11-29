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

#cdef struct _ModelPart:
#	int     nb_faces
#	int*    faces

cdef class _SplitedModel(_SimpleModel):
	# _ModelPart* _model_parts
	# int         _nb_face_groups
	# char*       _batched_faces
	# object      _face2index
	
	cdef __getcstate__(self):
		cdef Chunk* chunk
		cdef int i
		
		chunk = get_chunk()
		chunk_add_int_endian_safe(chunk, self._nb_face_groups)
		for i from 0 <= i < self._nb_face_groups:
			chunk_add_int_endian_safe(chunk, self._model_parts[i].nb_faces)
			chunk_add_ints_endian_safe(chunk, self._model_parts[i].faces, self._model_parts[i].nb_faces)
		return _SimpleModel.__getcstate__(self), drop_chunk_to_string(chunk)
	
	cdef void __setcstate__(self, cstate):
		cdef Chunk* chunk
		cdef int i
		
		_SimpleModel.__setcstate_data__(self, cstate[0])
		chunk = string_to_chunk(cstate[1])
		chunk_get_int_endian_safe(chunk, &self._nb_face_groups)
		self._model_parts   = <_ModelPart*> malloc(self._nb_face_groups * sizeof(_ModelPart))
		self._batched_faces = <char*>       malloc(self._nb_faces       * sizeof(char))
		for i from 0 <= i < self._nb_face_groups:
			chunk_get_int_endian_safe(chunk, &(self._model_parts[i].nb_faces))
			self._model_parts[i].faces = <int*> malloc(self._model_parts[i].nb_faces * sizeof(int))
			chunk_get_ints_endian_safe(chunk, self._model_parts[i].faces, self._model_parts[i].nb_faces)
		for i from 0 <= i < self._nb_faces:
			self._batched_faces[i] = 0
		drop_chunk(chunk)
	
	cdef void _batch_part(self, _Body body, int index):
		cdef int      i, face_index
		
		if body._option & HIDDEN: return
		for i from 0 <= i < self._model_parts[index].nb_faces:
			face_index = self._model_parts[index].faces[i]
			# Make sure tha face had not been batched alreay
			# hum... allocating a big array just for this is really beurk beurk BEURK !
			# I shall remove this shit later
			if self._batched_faces[face_index] == 1: continue
			self._batched_faces[face_index] = 1
			self._batch_face(self._faces + face_index)
	
	cdef void _batch_end(self, _Body body):
		pack_batch_end(self, body)
	
	cdef void _render(self, _Body body):
		cdef Pack*      pack
		cdef ModelFace* face
		
		model_option_activate(self._option)
		pack = <Pack*> chunk_get_ptr(renderer.data)
		while pack:
			(<_Material> (pack.material_id))._activate()
			face_option_activate(pack.option)
			face = <ModelFace*> chunk_get_ptr(renderer.data)
			if   pack.option & FACE_TRIANGLE:
				glBegin(GL_TRIANGLES)
				while face:
					self._render_triangle(face)
					self._batched_faces[face - self._faces] = 0
					face = <ModelFace*> chunk_get_ptr(renderer.data)
			elif pack.option & FACE_QUAD:
				glBegin(GL_QUADS)
				while face:
					self._render_quad(face)
					self._batched_faces[face - self._faces] = 0
					face = <ModelFace*> chunk_get_ptr(renderer.data)
			glEnd()
			face_option_inactivate(pack.option)
			pack = <Pack*> chunk_get_ptr(renderer.data)
		model_option_inactivate(self._option)
	
	# Big ugly hack
	cdef void _add_face(self, _Face face, vertex2ivertex, ivertex2index, lights, int static_shadow):
		self._face2index[face] = self._nb_faces
		_SimpleModel._add_face(self, face, vertex2ivertex, ivertex2index, lights, static_shadow)
	
	def __init__(self, _World world, face_groups, float angle, int option, lights):
		cdef int   i, j, nb_faces
		
		self._face2index = {}
		_SimpleModel.__init__(self, world, angle, option, lights)
		self._nb_face_groups = len(face_groups)
		self._batched_faces  = <char*>       malloc(self._nb_faces       * sizeof(char))
		self._model_parts    = <_ModelPart*> malloc(self._nb_face_groups * sizeof(_ModelPart))
		for i from 0 <= i < self._nb_face_groups:
			group    = face_groups[i]
			nb_faces = len(group)
			self._model_parts[i].nb_faces = nb_faces
			self._model_parts[i].faces    = <int*> malloc(nb_faces * sizeof(int))
			for j from 0 <= j < self._model_parts[i].nb_faces:
				self._model_parts[i].faces[j] = self._face2index[group[j]]
		for i from 0 <= i < self._nb_faces:
			self._batched_faces[i] = 0
		self._face2index = None
	
