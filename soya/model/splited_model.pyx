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
#	int     nb_face_groups
#	int*    face_groups


cdef class _SplitedModel(_SimpleModel):
#	cdef Chunk**     _face_groups
#	cdef int         _nb_face_groups
#	cdef _ModelPart* _model_parts
#	cdef int         _nb_parts
#	cdef object      _face2index
	
	
	cdef __getcstate__(self):
		cdef Chunk*     chunk
		cdef Chunk*     face_group
		cdef ModelFace* face
		cdef int        i, j, face_index
		chunk = get_chunk()
		# Save face groups
		chunk_add_int_endian_safe(chunk, self._nb_face_groups)
		for i from 0 <= i < self._nb_face_groups:
			face_group = self._face_groups[i]
			face_group.nb = 0
			face = <ModelFace*> chunk_get_ptr(face_group)
			while face:
				face_index = <int> (face - self._faces)
				chunk_add_int_endian_safe(chunk, face_index)
				face = <ModelFace*> chunk_get_ptr(face_group)
			chunk_add_int_endian_safe(chunk, -1)
		# Save model parts
		chunk_add_int_endian_safe(chunk, self._nb_parts)
		for i from 0 <= i < self._nb_parts:
			chunk_add_int_endian_safe(chunk, self._model_parts[i].nb_face_groups)
			for j from 0 <= j < self._model_parts[i].nb_face_groups:
				chunk_add_int_endian_safe(chunk, self._model_parts[i].face_groups[j])
		return _SimpleModel.__getcstate__(self), drop_chunk_to_string(chunk)
	
	
	cdef void __setcstate__(self, cstate):
		cdef Chunk* chunk
		cdef int i, j, face_index
		_SimpleModel.__setcstate_data__(self, cstate[0])
		chunk = string_to_chunk(cstate[1])
		# Restor face groups
		chunk_get_int_endian_safe(chunk, &self._nb_face_groups)
		self._face_groups = <Chunk**> malloc(self._nb_face_groups * sizeof(Chunk*))
		for i from 0 <= i < self._nb_face_groups:
			self._face_groups[i] = get_chunk()
			chunk_get_int_endian_safe(chunk, &face_index)
			while face_index >= 0:
				chunk_add_ptr(self._face_groups[i], <void*> (self._faces + face_index))
				chunk_get_int_endian_safe(chunk, &face_index)
			chunk_add_ptr(self._face_groups[i], NULL)
		# Restor model parts
		chunk_get_int_endian_safe(chunk, &self._nb_parts)
		self._model_parts = <_ModelPart*> malloc(self._nb_parts * sizeof(_ModelPart))
		for i from 0 <= i < self._nb_parts:
			chunk_get_int_endian_safe(chunk, &(self._model_parts[i].nb_face_groups))
			self._model_parts[i].face_groups = <int*> malloc(self._model_parts[i].nb_face_groups * sizeof(int))
			for j from 0 <= j < self._model_parts[i].nb_face_groups:
				chunk_get_int_endian_safe(chunk, &(self._model_parts[i].face_groups[j]))
		drop_chunk(chunk)
	
	
	cdef void _batch_part(self, _Body body, int index):
		cdef int   i, face_index
		cdef ModelFace* first_face
		cdef Pack* pack
		if body._option & HIDDEN: return
		for i from 0 <= i < self._model_parts[index].nb_face_groups:
			self._face_groups[self._model_parts[index].face_groups[i]].nb = 0
			first_face = <ModelFace*> chunk_get_ptr(self._face_groups[self._model_parts[index].face_groups[i]])
			pack = first_face.pack
			pack_batch_face(pack, self._face_groups[self._model_parts[index].face_groups[i]], 1)
	
	
	cdef void _batch_end(self, _Body body):
		pack_batch_end(self, body)
	
	
	cdef void _render(self, _Body body):
		cdef Pack*        pack
		cdef Chunk*       face_group
		cdef int          i
		cdef ModelFace*   face
		cdef CListHandle* handle
		model_option_activate(self._option)
		handle = renderer.current_data
		pack   = <Pack*> handle.data
		handle = handle.next
		while pack:
			(<_Material> (pack.material_id))._activate()
			face_option_activate(pack.option)
			face_group = <Chunk*> handle.data
			handle     = handle.next
			while face_group:
				face_group.nb = 0
				face = <ModelFace*> chunk_get_ptr(face_group)
				if pack.option & FACE_TRIANGLE:
					glBegin(GL_TRIANGLES)
					while face:
						self._render_triangle(face)
						face = <ModelFace*> chunk_get_ptr(face_group)
				elif pack.option & FACE_QUAD:
					glBegin(GL_QUADS)
					while face:
						self._render_quad(face)
						face = <ModelFace*> chunk_get_ptr(face_group)
				glEnd()
				face_group = <Chunk*> handle.data
				handle     = handle.next
			face_option_inactivate(pack.option)
			pack   = <Pack*> handle.data
			handle = handle.next
		model_option_inactivate(self._option)
	
	
	cdef void _add_face(self, _Face face, vertex2ivertex, ivertex2index, lights, int static_shadow):
		self._face2index[face] = self._nb_faces
		_SimpleModel._add_face(self, face, vertex2ivertex, ivertex2index, lights, static_shadow)
	
	
	cdef void _raypick(self, RaypickData data, CoordSyst parent):
		raise TypeError("Splited model doesn't support raypicking. Only part raypicking is possible.")
	
	
	cdef int _raypick_b(self, RaypickData data, CoordSyst parent):
		raise TypeError("Splited of model doesn't support raypicking. Only part raypicking is possible.")
	
	
	cdef void _raypick_part(self, RaypickData raypick_data, float* raydata, int part, CoordSyst parent):
		cdef int         i, j, nb_faces
		cdef ModelFace** faces
		for i from 0 <= i < self._model_parts[part].nb_face_groups:
			nb_faces = (self._face_groups[self._model_parts[part].face_groups[i]].nb / sizeof(ModelFace*)) - 1
			faces    = <ModelFace**> self._face_groups[self._model_parts[part].face_groups[i]].content
			for j from 0 <= j < nb_faces:
				self._face_raypick(faces[j], raydata, raypick_data, parent)
	
	
	cdef int _raypick_part_b(self, RaypickData raypick_data, float* raydata, int part):
		cdef int         i, j, nb_faces
		cdef ModelFace** faces
		for i from 0 <= i < self._model_parts[part].nb_face_groups:
			nb_faces = (self._face_groups[self._model_parts[part].face_groups[i]].nb / sizeof(ModelFace*)) - 1
			faces    = <ModelFace**> self._face_groups[self._model_parts[part].face_groups[i]].content
			for j from 0 <= j < nb_faces:
				if self._face_raypick_b(faces[j], raydata, raypick_data): return 1
		return 0
	
	
	def __init__(self, _World world, facegroups, parts, float angle, int option, lights):
		cdef int i, j, index
		# Creat model
		self._face2index = {}
		_SimpleModel.__init__(self, world, angle, option, lights)
		# Creat face groups
		self._nb_face_groups = len(facegroups)
		self._face_groups    = <Chunk**> malloc(self._nb_face_groups * sizeof(Chunk*))
		for i from 0 <= i < self._nb_face_groups:
			self._face_groups[i] = get_chunk()
			for face in facegroups[i]:
				index = self._face2index[face]
				chunk_add_ptr(self._face_groups[i], <void*> (self._faces + index))
			chunk_add_ptr(self._face_groups[i], NULL)
		# Creat model parts
		self._nb_parts    = len(parts)
		self._model_parts = <_ModelPart*> malloc(self._nb_parts * sizeof(_ModelPart))
		for i from 0 <= i < self._nb_parts:
			self._model_parts[i].nb_face_groups = len(parts[i])
			self._model_parts[i].face_groups    = <int*> malloc(self._model_parts[i].nb_face_groups * sizeof(int))
			for j from 0 <= j < self._model_parts[i].nb_face_groups:
				self._model_parts[i].face_groups[j] = parts[i][j]
		self._face2index = None
	
	
	def __dealloc__(self):
		cdef int i
		for i from 0 <= i < self._nb_face_groups:
			chunk_dealloc(self._face_groups[i])
		free(self._face_groups)
		for i from 0 <= i < self._nb_parts:
			free(self._model_parts[i].face_groups)
		free(self._model_parts)
