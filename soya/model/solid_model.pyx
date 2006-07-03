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

cdef class _SolidModel(_SimpleModel):
	cdef void _render(self, CoordSyst coord_syst):
		cdef float         pos[3]
		cdef int           v2[3]
		cdef ModelFace*    face
		cdef DisplayList*  display_list
		cdef int           i, j, start, end
		
		point_by_matrix_copy(pos, self._sphere, coord_syst._render_matrix)
		#print "pos", pos[0], pos[1], pos[2]
		#print self._sphere[0], self._sphere[1], self._sphere[2], self._sphere[3]
		if pos[2] + self._sphere[3] < -renderer.current_camera._front:
			#print "en dehors"


			_SimpleModel._render(self, coord_syst)
			
		else:
			#print "dedans"

			
			if not(self._option & MODEL_INITED): self._init_display_list()
			
			glLoadIdentity()
			
			if renderer.state == RENDERER_STATE_OPAQUE:
				start = 0
				end   = self._display_lists.nb_opaque_list
			else:
				start = self._display_lists.nb_opaque_list
				end   = start + self._display_lists.nb_alpha_list
				
			display_list = self._display_lists.display_lists
			
			for i from start <= i < end:
				display_list = self._display_lists.display_lists + i
				(<_Material> (display_list.material_id))._activate()
				face_option_activate(display_list.option)
				
				for j from 0 <= j < self._nb_faces:
					face = self._faces + j
					if ((face.option & DISPLAY_LIST_OPTIONS) == display_list.option) and (face.pack.material_id == display_list.material_id):
						if face.option & FACE_QUAD:
							self._render_triangle_solid(face, coord_syst, face.v)
							v2[0] = face.v[0]
							v2[1] = face.v[2]
							v2[2] = face.v[3]
							self._render_triangle_solid(face, coord_syst, v2)
						else:
							self._render_triangle_solid(face, coord_syst, face.v)
							
				face_option_inactivate(display_list.option)
			model_option_inactivate(self._option)
			
	cdef void _render_triangle_solid(self, ModelFace* face, CoordSyst coord_syst, int vertex_indices[3]):
		cdef int    i, i3, j, j3, cur_inter3, nb_inter
		cdef float  f, f1, n[3], p[9], inter[4 * (3 + 2 + 4 + 4)]
		cur_inter3 = 0
		nb_inter   = 0
		
		if not(face.option & FACE_SMOOTH_LIT): glNormal3fv(self._values + face.normal) # face normal
		
		glBegin(GL_TRIANGLES)
		for i from 0 <= i < 3:
			point_by_matrix_copy(p + 3 * i, self._coords   + self._vertex_coords[vertex_indices[i]], coord_syst._render_matrix)
			
			if self._option & MODEL_DIFFUSES : glColor4fv   (self._colors   + self._vertex_diffuses [vertex_indices[i]])
			if self._option & MODEL_EMISSIVES: glMaterialfv (GL_FRONT_AND_BACK, GL_EMISSION, self._colors + self._vertex_emissives[vertex_indices[i]]) # XXX use glColorMaterial when emissive color but no diffuse ?
			if self._option & MODEL_TEXCOORDS: glTexCoord2fv(self._values   + self._vertex_texcoords[vertex_indices[i]])
			if face.option & FACE_SMOOTH_LIT :
				vector_by_matrix_copy(n, self._vnormals + self._vertex_coords[vertex_indices[i]], coord_syst._render_matrix)
				glNormal3fv(n)
			glVertex3fv(p + 3 * i)
		glEnd()
		
		for i from 0 <= i < 3:
			i3 = 3 * i
			if i == 2: j = 0    ; j3 = 0
			else:      j = i + 1; j3 = 3 * j
			
			if p[i3 + 2] > -renderer.current_camera._front:
				inter[cur_inter3    ] = p[i3    ]
				inter[cur_inter3 + 1] = p[i3 + 1]
				inter[cur_inter3 + 2] = -renderer.current_camera._front - 0.0001
				
				if self._option & MODEL_DIFFUSES : memcpy(inter + (cur_inter3 +  3), self._colors + self._vertex_diffuses [vertex_indices[i]], 4 * sizeof(float))
				if self._option & MODEL_EMISSIVES: memcpy(inter + (cur_inter3 +  7), self._colors + self._vertex_emissives[vertex_indices[i]], 4 * sizeof(float))
				if self._option & MODEL_TEXCOORDS: memcpy(inter + (cur_inter3 + 11), self._values + self._vertex_texcoords[vertex_indices[i]], 2 * sizeof(float))
				
				cur_inter3 = cur_inter3 + 13
				nb_inter   = nb_inter   + 1
				
				
			if ((p[i3 + 2] + renderer.current_camera._front) * (p[j3 + 2] + renderer.current_camera._front) < 0.0) and (nb_inter < 4): # Change side of the camera front plane
				n[0] = p[i3    ] - p[j3    ]
				n[1] = p[i3 + 1] - p[j3 + 1]
				n[2] = p[i3 + 2] - p[j3 + 2]
				
				f  = -(p[i3 + 2] + renderer.current_camera._front) / n[2]
				f1 = 1.0 - f
				inter[cur_inter3    ] = p[i3    ] + f * n[0]
				inter[cur_inter3 + 1] = p[i3 + 1] + f * n[1]
				inter[cur_inter3 + 2] = -renderer.current_camera._front - 0.0001
				
				if self._option & MODEL_DIFFUSES :
					inter[cur_inter3 + 3] = f * self._colors[self._vertex_diffuses[vertex_indices[i]]    ] + f1 * self._colors[self._vertex_diffuses[vertex_indices[j]]    ]
					inter[cur_inter3 + 4] = f * self._colors[self._vertex_diffuses[vertex_indices[i]] + 1] + f1 * self._colors[self._vertex_diffuses[vertex_indices[j]] + 1]
					inter[cur_inter3 + 5] = f * self._colors[self._vertex_diffuses[vertex_indices[i]] + 2] + f1 * self._colors[self._vertex_diffuses[vertex_indices[j]] + 2]
					inter[cur_inter3 + 6] = f * self._colors[self._vertex_diffuses[vertex_indices[i]] + 3] + f1 * self._colors[self._vertex_diffuses[vertex_indices[j]] + 3]
					
				if self._option & MODEL_EMISSIVES:
					inter[cur_inter3 + 3] = f * self._colors[self._vertex_emissives[vertex_indices[i]]    ] + f1 * self._colors[self._vertex_emissives[vertex_indices[j]]    ]
					inter[cur_inter3 + 4] = f * self._colors[self._vertex_emissives[vertex_indices[i]] + 1] + f1 * self._colors[self._vertex_emissives[vertex_indices[j]] + 1]
					inter[cur_inter3 + 5] = f * self._colors[self._vertex_emissives[vertex_indices[i]] + 2] + f1 * self._colors[self._vertex_emissives[vertex_indices[j]] + 2]
					inter[cur_inter3 + 6] = f * self._colors[self._vertex_emissives[vertex_indices[i]] + 3] + f1 * self._colors[self._vertex_emissives[vertex_indices[j]] + 3]
					
				if self._option & MODEL_TEXCOORDS:
					inter[cur_inter3 + 11] = f * self._values[self._vertex_texcoords[vertex_indices[i]]    ] + f1 * self._values[self._vertex_texcoords[vertex_indices[j]]    ]
					inter[cur_inter3 + 12] = f * self._values[self._vertex_texcoords[vertex_indices[i]] + 1] + f1 * self._values[self._vertex_texcoords[vertex_indices[j]] + 1]
					
				cur_inter3 = cur_inter3 + 13
				nb_inter   = nb_inter   + 1
				
		if cur_inter3 != 0:
			if not face.option & FACE_DOUBLE_SIDED: glDisable(GL_CULL_FACE)
			
			glBegin(GL_POLYGON)
			glNormal3f(0.0, 0.0, 1.0)
			for i from 0 <= i < nb_inter:
				cur_inter3 = i * 13
				if self._option & MODEL_DIFFUSES : glColor4fv   (inter + (cur_inter3 +  3))
				if self._option & MODEL_EMISSIVES: glMaterialfv (GL_FRONT_AND_BACK, GL_EMISSION, inter + (cur_inter3 +  7))
				if self._option & MODEL_TEXCOORDS: glTexCoord2fv(inter + (cur_inter3 + 11))
				glVertex3fv(inter + cur_inter3)
			glEnd()
			
			if not face.option & FACE_DOUBLE_SIDED: glEnable(GL_CULL_FACE)
				
		
