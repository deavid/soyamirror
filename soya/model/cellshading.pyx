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


cdef class _CellShadingModel(_SimpleModel):
	#cdef _Material _shader
	#cdef float     _outline_color[4]
	#cdef float     _outline_width, _outline_attenuation
	
	cdef _Model _create_deformed_data(self):
		cdef _CellShadingModel data
		data = _SimpleModel._create_deformed_data(self)
		data._shader              = self._shader
		data._outline_width       = self._outline_width
		data._outline_attenuation = self._outline_attenuation
		memcpy(data._outline_color, self._outline_color, 4 * sizeof(float))
		return data
		
	property shader:
		def __get__(self):
			return self._shader
		
	cdef __getcstate__(self):
		cdef Chunk* chunk
		chunk = get_chunk()
		chunk_add_float_endian_safe (chunk, self._outline_width)
		chunk_add_float_endian_safe (chunk, self._outline_attenuation)
		chunk_add_floats_endian_safe(chunk, self._outline_color, 4)
		return _SimpleModel.__getcstate__(self), drop_chunk_to_string(chunk), self._shader
		
	cdef void __setcstate__(self, cstate):
		_SimpleModel.__setcstate_data__(self, cstate[0])
		
		cdef Chunk* chunk
		chunk = string_to_chunk(cstate[1])
		chunk_get_float_endian_safe (chunk, &self._outline_width)
		chunk_get_float_endian_safe (chunk, &self._outline_attenuation)
		chunk_get_floats_endian_safe(chunk,  self._outline_color, 4)
		drop_chunk(chunk)
		
		self._shader = cstate[2]
		
		# Build the display list data, but don't create the corresponding OpenGL display list
		self._build_display_list()
		
	cdef void _build_cellshading(self, _Material shader, outline_color, float outline_width, float outline_attenuation):
		cdef int i
		
		self._shader              = shader
		self._outline_width       = outline_width
		self._outline_attenuation = outline_attenuation
		for i from 0 <= i < 4: self._outline_color[i] = outline_color[i]
		
	cdef void _batch(self, _Body body):
		if body._option & HIDDEN: return
		
		if quality == QUALITY_LOW:
			_SimpleModel._batch(self, body)
			return
		
		#cdef Frustum* frustum
		#frustum = renderer._frustum(body)
		#if (self._option & MODEL_HAS_SPHERE) and (sphere_in_frustum(frustum, self._sphere) == 0): return
		cdef float sphere[4]
		if self._option & MODEL_HAS_SPHERE:
			sphere_by_matrix_copy(sphere, self._sphere, body._root_matrix())
			if sphere_in_frustum(renderer.root_frustum, sphere) == 0: return
		
		if self._display_lists.nb_opaque_list != 0: renderer._batch(renderer.opaque, body._data, body, NULL)
		if self._display_lists.nb_alpha_list  != 0: renderer._batch(renderer.alpha , body._data, body, NULL)
		
		# For outline
		#if self._outline_width > 0.0: renderer._batch(renderer.secondpass, body._data, body, 0) ???? why 0 and not -1 here ???
		if self._outline_width > 0.0: renderer._batch(renderer.secondpass, body._data, body, NULL)

				
#   cdef void _render(self, CoordSyst coordsyst):
#     cdef int      i, start, end
#     cdef Frustum* frustum
#     cdef Chunk*   chunk
#     cdef float*   shades
		
#     if renderer.state == RENDERER_STATE_SECONDPASS:
#       frustum = renderer._frustum(coordsyst)
#       self._render_outline(frustum)
#     else:
#       model_option_activate(self._option)
			
#       chunk = get_chunk()
#       chunk_register(chunk, self._nb_vnormals * sizeof(float))
#       shades = <float*> chunk.content
#       self._prepare_cellshading(coordsyst, shades)
			
#       self._pack_render_cellshading(shades)
#       drop_chunk(chunk)
#       model_option_inactivate(self._option)
			
			
#   cdef void _pack_render_cellshading(self, float* shades):
#     cdef Pack*      pack
#     cdef ModelFace* face
#     cdef _Material  material

#     # Activate shader texture
#     glActiveTextureARB(GL_TEXTURE1)
#     if self._shader._id == 0: self._shader._init_texture()
#     glEnable       (GL_TEXTURE_2D)
#     glTexEnvi      (GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
#     glBindTexture  (GL_TEXTURE_2D, self._shader._id)
#     glActiveTextureARB(GL_TEXTURE0)
		
#     pack = <Pack*> chunk_get_ptr(renderer.data)
#     while pack:
#       material = <_Material> (pack.material_id)
#       material._activate()
			
#       face_option_activate(pack.option)
			
#       face = <ModelFace*> chunk_get_ptr(renderer.data)
#       if   pack.option & FACE_TRIANGLE:
#         glBegin(GL_TRIANGLES)
#         while face:
#           self._render_triangle_cellshading(face, shades)
#           face = <ModelFace*> chunk_get_ptr(renderer.data)
					
#       elif pack.option & FACE_QUAD:
#         glBegin(GL_QUADS)
#         while face:
#           self._render_quad_cellshading(face, shades)
#           face = <ModelFace*> chunk_get_ptr(renderer.data)
					
#       glEnd()
			
#       face_option_inactivate(pack.option)
#       pack = <Pack*> chunk_get_ptr(renderer.data)
		
#     # Unactivate shader texture
#     glActiveTextureARB(GL_TEXTURE1)
#     glDisable         (GL_TEXTURE_2D)
#     glActiveTextureARB(GL_TEXTURE0)
		
		
	cdef void _render(self, _Body body):
		if quality == QUALITY_LOW:
			_SimpleModel._render(self, body)
			return
		
		cdef int          i, start, end
		cdef int*         face_id
		cdef Frustum*     frustum
		cdef Chunk*       chunk
		cdef float*       shades
		cdef _Material    material
		cdef DisplayList* display_list
		
		if renderer.state == RENDERER_STATE_SECONDPASS:
			frustum = renderer._frustum(body)
			self._render_outline(frustum)
		else:
			if body._option & LEFTHANDED: glFrontFace(GL_CW)
			model_option_activate(self._option)
			
			chunk = get_chunk()
			chunk_register(chunk, self._nb_vnormals * sizeof(float))
			shades = <float*> chunk.content
			self._prepare_cellshading(body, shades)
			
			if renderer.state == RENDERER_STATE_OPAQUE:
				start = 0
				end   = self._display_lists.nb_opaque_list
			else: # Alpha
				start = self._display_lists.nb_opaque_list
				end   = start + self._display_lists.nb_alpha_list
				
			# Activate shader texture
			glActiveTextureARB(GL_TEXTURE1)
			
			if self._shader._id == 0:	self._shader._init_texture()
			
			glEnable          (GL_TEXTURE_2D)
			glTexEnvi         (GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
			glBindTexture     (GL_TEXTURE_2D, self._shader._id)
			glActiveTextureARB(GL_TEXTURE0)
			
			for i from start <= i < end:
				display_list = self._display_lists.display_lists + i
				
				material = <_Material> (display_list.material_id)
				material._activate()
				
				face_option_activate(display_list.option)
				
				face_id = display_list.faces_id
				if   display_list.option & FACE_TRIANGLE:
					glBegin(GL_TRIANGLES)
					while face_id[0] != -1:
						self._render_triangle_cellshading(self._faces + face_id[0], shades)
						face_id = face_id + 1
						
				elif display_list.option & FACE_QUAD:
					glBegin(GL_QUADS)
					while face_id[0] != -1:
						self._render_quad_cellshading(self._faces + face_id[0], shades)
						face_id = face_id + 1
						
				glEnd()
				
				face_option_inactivate(display_list.option)
			
			# Unactivate shader texture
			glActiveTextureARB(GL_TEXTURE1)
			glDisable         (GL_TEXTURE_2D)
			glActiveTextureARB(GL_TEXTURE0)
				
				
			drop_chunk(chunk)
			model_option_inactivate(self._option)
			if body._option & LEFTHANDED: glFrontFace(GL_CCW)
			
			
	cdef void _render_outline(self, Frustum* frustum):
		cdef int        i, j, k, ns, nb
		cdef float      d
		cdef float*     plane
		cdef ModelFace* face, neighbor_face
		
		# Compute outline width, which depends on distance to camera
		d = sphere_distance_point(self._sphere, frustum.position) * self._outline_attenuation
		if d < 1.0: d = self._outline_width
		else:
			d = self._outline_width / d
			if d < 2.0: d = 2.0
			
		_DEFAULT_MATERIAL._activate()
		glLineWidth(d)
		glColor4fv (self._outline_color)
		glDisable  (GL_LIGHTING)
		glDepthFunc(GL_LEQUAL)
		
		# mark faces as either front or back
		for i from 0 <= i < self._nb_faces:
			face = self._faces + i
			plane = self._values + face.normal
			if plane[0] * frustum.position[0] + plane[1] * frustum.position[1] + plane[2] * frustum.position[2] + plane[3] > 0.0:
				face.option = (face.option & ~FACE_BACK ) | FACE_FRONT
			else:
				face.option = (face.option & ~FACE_FRONT) | FACE_BACK
				
				
#     # find and draw edges   
#     glBegin(GL_LINES)
#     for i from 0 <= i < self._nb_faces:
#       face = self._faces + i
#       if face.option & FACE_FRONT:
#         # test if neighbors are back
#         for j from 0 <= j < 4:
#           k = self._neighbors[4 * i + j]
#           if k != -1:
#             neighbor_face = self._faces[k]
#             if neighbor_face.option & FACE_BACK:
#               # draw edge between vertices k and k + 1
#               #print "an edge", (face.option & FACE_QUAD), 
#               #print "  ", i, j, k
#               #print "  ", face.v[j]
#               #print "  ", self._vertex_coords[face.v[j]]
#               glVertex3fv(self._coords + self._vertex_coords[face.v[j]])
#               #print "  ..."
							
#               if ((face.option & FACE_QUAD) and (j < 3)) or (j < 2):
#                 glVertex3fv(self._coords + self._vertex_coords[face.v[j + 1]])
#               else:
#                 glVertex3fv(self._coords + self._vertex_coords[face.v[    0]])
								
#     glEnd()


#     cdef Chunk* chunk
#     chunk = get_chunk()
#     chunk_register(chunk, self._nb_coords * sizeof(int))
#     cdef int* vertex2next
#     vertex2next = <int*> (chunk.content)
#     for i from 0 <= i < self._nb_coords: vertex2next[i] = -1

#     # find edges   
#     #print "draw edges", self._nb_coords
#     for i from 0 <= i < self._nb_faces:
#       face = self._faces + i
#       if face.option & FACE_FRONT:
#         # test if neighbors are back
#         for j from 0 <= j < 4:
#           k = self._neighbors[4 * i + j]
#           if k != -1:
#             neighbor_face = self._faces[k]
#             if neighbor_face.option & FACE_BACK:
#               # draw edge between vertices k and k + 1
#               if ((face.option & FACE_QUAD) and (j < 3)) or (j < 2):
#                 vertex2next[self._vertex_coords[face.v[j]] / 3] = self._vertex_coords[face.v[j + 1]] / 3
#               else:
#                 vertex2next[self._vertex_coords[face.v[j]] / 3] = self._vertex_coords[face.v[0]] / 3
								
#     # draw edges
#     for i from 0 <= i < self._nb_coords:
#       if vertex2next[i] >= 0:
#         j = i
#         glBegin(GL_LINE_STRIP)
#         while vertex2next[j] >= 0:
#           glVertex3fv(self._coords + j * 3)
#           k = vertex2next[j] # Next vertex
#           vertex2next[j] = -2
#           j = k
					
#         glVertex3fv(self._coords + j * 3)
#         glEnd()
				




		cdef Chunk* chunk
		chunk = get_chunk()
		chunk_register(chunk, self._nb_coords * sizeof(int))
		cdef int* vertex_used
		vertex_used = <int*> (chunk.content)
		for i from 0 <= i < self._nb_coords: vertex_used[i] = -1
		
		
		# find and draw edges   
		glBegin(GL_LINES)
		for i from 0 <= i < self._nb_faces:
			face = self._faces + i
			if face.option & FACE_ALPHA: continue
			
			if face.option & FACE_QUAD: nb = 4
			else:                       nb = 3
			
			if face.option & FACE_SMOOTH_LIT:
				if face.option & FACE_DOUBLE_SIDED:
					for j from 0 <= j < nb:
						k = self._neighbors[4 * i + j]
						if k == -1: # No neighbor, but double-sided face => the face is its own neighbor
							vertex_used[self._vertex_coords[face.v[j]] / 3] = 1

							# draw edge between vertices j and j + 1
							glVertex3fv(self._coords + self._vertex_coords[face.v[j]])
							if j < nb - 1: glVertex3fv(self._coords + self._vertex_coords[face.v[j + 1]])
							else:          glVertex3fv(self._coords + self._vertex_coords[face.v[    0]])
								
						else:
							ns = self._neighbors_side[4 * i + j]
							neighbor_face = self._faces[k]
							if (
								(ns == -1) and (((face.option & FACE_FRONT) and (neighbor_face.option & FACE_BACK )) or ((face.option & FACE_BACK) and (neighbor_face.option & FACE_FRONT)))
									) or (
								(ns ==  1) and (((face.option & FACE_FRONT) and (neighbor_face.option & FACE_FRONT)) or ((face.option & FACE_BACK) and (neighbor_face.option & FACE_BACK)))
								):
								vertex_used[self._vertex_coords[face.v[j]] / 3] = 1
								
								# draw edge between vertices j and j + 1
								glVertex3fv(self._coords + self._vertex_coords[face.v[j]])
								if j < nb - 1: glVertex3fv(self._coords + self._vertex_coords[face.v[j + 1]])
								else:          glVertex3fv(self._coords + self._vertex_coords[face.v[    0]])
								
				else:
					if face.option & FACE_FRONT:
						# test if neighbors are back
						for j from 0 <= j < nb:
							k = self._neighbors[4 * i + j]
							if (k == -1) or (self._faces[k].option & FACE_BACK):
								vertex_used[self._vertex_coords[face.v[j]] / 3] = 1
								
								# draw edge between vertices j and j + 1
								glVertex3fv(self._coords + self._vertex_coords[face.v[j]])
								if j < nb - 1: glVertex3fv(self._coords + self._vertex_coords[face.v[j + 1]])
								else:          glVertex3fv(self._coords + self._vertex_coords[face.v[    0]])
								
			else: # Not smoothlit
				if (face.option & FACE_FRONT) or (face.option & FACE_DOUBLE_SIDED):
					for j from 0 <= j < nb:
						# draw edge between vertices j and j + 1
						glVertex3fv(self._coords + self._vertex_coords[face.v[j]])
						if j < nb - 1: glVertex3fv(self._coords + self._vertex_coords[face.v[j + 1]])
						else:          glVertex3fv(self._coords + self._vertex_coords[face.v[    0]])
						
		glEnd()
		
		glPointSize(d / 2)
				
		glBegin(GL_POINTS)
		for i from 0 <= i < self._nb_coords:
			if vertex_used[i] == 1: glVertex3fv(self._coords + i * 3)
		glEnd()
		
		
		drop_chunk(chunk)
		
		glLineWidth(1.0) # Reset to default
		glPointSize(1.0) # Reset to default
		glEnable   (GL_LIGHTING)
		glDepthFunc(GL_LESS)
		glColor4fv (white)


	cdef float _vertex_compute_cellshading(self, float* coord, float* normal, lights, float shade):
		cdef _Light light
		cdef float  ptr[3]
		cdef float  tmp
		cdef int    i
		
		for light in lights:
			if light._w == 0.0: # directional light
				tmp = -vector_dot_product(normal, light._data)
			else: # positional light
				ptr[0] = light._data[0] - coord[0]
				ptr[1] = light._data[1] - coord[1]
				ptr[2] = light._data[2] - coord[2]
				vector_normalize(ptr)
				tmp = vector_dot_product(normal, ptr)
				
			shade = shade + tmp
			
		return shade

	cdef void _prepare_cellshading_shades(self, float* shades, lights):
		cdef _Light light
		cdef float* ptr1, *ptr2
		cdef float  v[3]
		cdef float  tmp
		cdef int    i, j, k
		
		for light in lights:
			ptr1 = self._vnormals
			if light._w == 0.0: # directional light
				for j from 0 <= j < self._nb_vnormals:
					tmp = -vector_dot_product(ptr1, light._data)
					shades[j] = shades[j] + tmp
					ptr1 = ptr1 + 3
					
			else: # positional light
				ptr2 = self._coords
				for j from 0 <= j < self._nb_vnormals:
					v[0] = light._data[0] - ptr2[0]
					v[1] = light._data[1] - ptr2[1]
					v[2] = light._data[2] - ptr2[2]
					vector_normalize(v)
					tmp = vector_dot_product(ptr1, v)
					shades[j] = shades[j] + tmp
					ptr1 = ptr1 + 3
					ptr2 = ptr2 + 3
					
	cdef void _prepare_cellshading(self, CoordSyst coordsyst, float* shades):
		cdef int    n
		cdef _Light light
		for light in renderer.top_lights:             light._cast_into(coordsyst)
		for light in renderer.current_context.lights: light._cast_into(coordsyst)
		
		if self._nb_vnormals > 0: # Else the shades are computed at the vertex rendering time, since the shades are not shared (all (coord,normal) couples are different)
			for n from 0 <= n < self._nb_vnormals: shades[n] = 0.5
			self._prepare_cellshading_shades(shades, renderer.top_lights)
			self._prepare_cellshading_shades(shades, renderer.current_context.lights)
			
			# clip shade texcoord values
			for n from 0 <= n < self._nb_vnormals:
				# do not clip with interval [0, 1] because smooth magnification of texture
				# causes visual bugs
				if   shades[n] > 0.95: shades[n] = 0.95
				elif shades[n] < 0.05: shades[n] = 0.05


	cdef void _render_triangle_cellshading(self, ModelFace* face, float* shades):
		if face.option & FACE_SMOOTH_LIT:
			self._render_vertex_cellshading_smoothlit(face.v[0], face.option, shades)
			self._render_vertex_cellshading_smoothlit(face.v[1], face.option, shades)
			self._render_vertex_cellshading_smoothlit(face.v[2], face.option, shades)
		else:
			glNormal3fv(self._values + face.normal)
			self._render_vertex_cellshading(face.v[0], face.option, self._values + face.normal)
			self._render_vertex_cellshading(face.v[1], face.option, self._values + face.normal)
			self._render_vertex_cellshading(face.v[2], face.option, self._values + face.normal)

	cdef void _render_quad_cellshading(self, ModelFace* face, float* shades):
		if face.option & FACE_SMOOTH_LIT:
			self._render_vertex_cellshading_smoothlit(face.v[0], face.option, shades)
			self._render_vertex_cellshading_smoothlit(face.v[1], face.option, shades)
			self._render_vertex_cellshading_smoothlit(face.v[2], face.option, shades)
			self._render_vertex_cellshading_smoothlit(face.v[3], face.option, shades)
		else:
			glNormal3fv(self._values + face.normal)
			self._render_vertex_cellshading(face.v[0], face.option, self._values + face.normal)
			self._render_vertex_cellshading(face.v[1], face.option, self._values + face.normal)
			self._render_vertex_cellshading(face.v[2], face.option, self._values + face.normal)
			self._render_vertex_cellshading(face.v[3], face.option, self._values + face.normal)


	# XXX face_option arg is useless
	cdef void _render_vertex_cellshading_smoothlit (self, int index, int face_option, float* shades):
		cdef int    n
		cdef float* coord
		cdef float  shade
		n     = self._vertex_coords[index]
		coord = self._coords + n
		
		if face_option & FACE_NON_LIT:
			shade = 0.5 # Medium shade
		else:
			shade = shades[n / 3]
		
		if self._option & MODEL_DIFFUSES : glColor4fv   (self._colors   + self._vertex_diffuses [index])
		if self._option & MODEL_EMISSIVES: glMaterialfv (GL_FRONT_AND_BACK, GL_EMISSION, self._colors + self._vertex_emissives[index]) # XXX use glColorMaterial when emissive color but no diffuse ?
		if self._option & MODEL_TEXCOORDS:
			glMultiTexCoord2fvARB(GL_TEXTURE0, self._values + self._vertex_texcoords[index])
			glMultiTexCoord2fARB (GL_TEXTURE1, shade, shade)
		else: glTexCoord2f(shade, shade)
		
		glNormal3fv(self._vnormals + n)
		glVertex3fv(coord)
		
	# XXX face_option arg is useless
	cdef void _render_vertex_cellshading(self, int index, int face_option, float* fnormal):
		cdef float* coord
		cdef float  shade
		coord = self._coords + self._vertex_coords[index]
		
		if face_option & FACE_NON_LIT:
			shade = 0.5 # Medium value
		else:
			shade = self._vertex_compute_cellshading(coord, fnormal, renderer.top_lights, 0.5)
			shade = self._vertex_compute_cellshading(coord, fnormal, renderer.current_context.lights, shade)
			if   shade < 0.05: shade = 0.05
			elif shade > 0.95: shade = 0.95
			
		if self._option & MODEL_DIFFUSES : glColor4fv  (self._colors   + self._vertex_diffuses [index])
		if self._option & MODEL_EMISSIVES: glMaterialfv(GL_FRONT_AND_BACK, GL_EMISSION, self._colors + self._vertex_emissives[index]) # XXX use glColorMaterial when emissive color but no diffuse ?
		if self._option & MODEL_TEXCOORDS:
			glMultiTexCoord2fvARB(GL_TEXTURE0, self._values + self._vertex_texcoords[index])
			glMultiTexCoord2fARB (GL_TEXTURE1, shade, shade)
		else: glTexCoord2f(shade, shade)
		
		glVertex3fv(coord)
		
	

