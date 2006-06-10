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

from weakref import WeakKeyDictionary


#blended_triangles = WeakKeyDictionary()

#def blend_triangles(_Material m0, _Material m1, float tex0_x0, float tex0_y0, float tex0_x1, float tex0_y1, float tex1_x0, float tex1_y0, float tex1_x1, float tex1_y1):
#  return _blend_triangles(m0, m1, tex0_x0, tex0_y0, tex0_x1, tex0_y1, tex1_x0, tex1_y0, tex1_x1, tex1_y1)

#cdef _Material _blend_triangles(_Material m0, _Material m1, float tex0_x0, float tex0_y0, float tex0_x1, float tex0_y1, float tex1_x0, float tex1_y0, float tex1_x1, float tex1_y1):
	



blended_materials0 = WeakKeyDictionary()
blended_materials1 = WeakKeyDictionary()

def blend_materials(_Material m00, _Material m01, _Material m11, _Material m10, int cut_direction = 0, float tex_x0 = 0.0, float tex_y0 = 0.0, float tex_x1 = 1.0, float tex_y1 = 1.0):
	"""blend_materials(m00, m01, m11, m10, cut_direction = 0, tex_x0 = 0.0, tex_y0 = 0.0, tex_x1 = 1.0, tex_y1) -> Material

Blends the four given materials into a new one. blend_materials generate and returns
a new material with an appropriate texture.

Each of the four material correspond to a corner :

	M00 is the lower left material.
	M01 is the lower right material.
	M11 is the top right material.
	M10 is the top left material.

TEX_X0, TEX_Y0 are the texture coordinate for the lower left corner.
TEX_X1, TEX_Y1 are the texture coordinate for the top right corner.

CUT_DIRECTION indicates how the generated texture quad should be cut (there
is 2 different ways to cut a quad into 2 triangles, and under some condition,
the way of cutting can change the result). CUT_DIRECTION can be 0 or 1.

Notice that if you call several time blend_materials with the same arguments, it will
return the same material (i.e. the result are cached).

WARNING: Don't call blend_materials during rendering (i.e. in render()) ! It can
cause some visual artifact.
However, you can call blend_materials safely in batch().

XXX CAVEATS: if more than two different materials are given, the latest one will be more
visible.
"""
	return _blend_materials(m00, m01, m11, m10, cut_direction, tex_x0, tex_y0, tex_x1, tex_y1)

cdef _Material _blend_materials(_Material m00, _Material m01, _Material m11, _Material m10, int cut_direction, float tex_x0, float tex_y0, float tex_x1, float tex_y1):
	cdef _Material m
	cdef int       delta
	
	if ((m00 is m01) and (m11 is m10)) or ((m00 is m10) and (m11 is m01)):
		# In this case, cut_direction doesn't change the result
		cut_direction = 0
		
	delta = (<int> tex_x0)
	tex_x0 = tex_x0 - delta
	tex_x1 = tex_x1 - delta
	
	delta = (<int> tex_y0)
	tex_y0 = tex_y0 - delta
	tex_y1 = tex_y1 - delta
	
	if cut_direction == 0: dico1 = blended_materials0
	else:                  dico1 = blended_materials1
	
	dico2 = dico1.get(m00)
	if dico2 is None:
		dico2 = dico1            [m00] = WeakKeyDictionary()
		dico3 = dico2            [m01] = WeakKeyDictionary()
		dico4 = dico3            [m11] = WeakKeyDictionary()
		dico5 = dico4            [m10] = {}
		
	else:
		dico3 = dico2.get(m01)
		if dico3 is None:
			dico3 = dico2          [m01] = WeakKeyDictionary()
			dico4 = dico3          [m11] = WeakKeyDictionary()
			dico5 = dico4          [m10] = {}
		else:
			dico4 = dico3.get(m11)
			if dico4 is None:
				dico4 = dico3        [m11] = WeakKeyDictionary()
				dico5 = dico4        [m10] = {}
			else:
				dico5 = dico4.get(m10)
				if dico5 is None:
					dico5 = dico4      [m10] = {}
				else:
					m = dico5.get((tex_x0, tex_y0, tex_x1, tex_y1))
					if not m is None: return m
					
	cdef int size
	cdef float delta_tex, max_delta_tex
	
	m = dico5[(tex_x0, tex_y0, tex_x1, tex_y1)] = Material()
	if not m00._texture is None:
		size = power_of_2(m00._texture.width)
		if (quality != QUALITY_HIGH) and (size > 1): size = size / 2
	else: size = 32
	
	delta_tex     = 2 * fabs(tex_x0 - tex_x1)
	max_delta_tex = 2 * fabs(tex_y0 - tex_y1)
	if delta_tex > max_delta_tex: max_delta_tex = delta_tex
	
	if max_delta_tex < 1.0:
		# Reduce texture size, since only a part of it is used.
		size = power_of_2(<int> ((<float> size) * max_delta_tex))
		if size < 4: size = 4
		
	m.clamp = 1
	if 0 and CAN_USE_TEX_BORDER:
		size = size + 2 # for the border
	else:
		# Emulate texture border, by adding the border inside the texture
		m._option = m._option | MATERIAL_EMULATE_BORDER
		delta_tex = 2.0 * 1.0 / (<float> size)
		max_delta_tex = delta_tex * abs(tex_x0 - tex_x1)
		
		
		if tex_x0 < tex_x1:
			tex_x0 = tex_x0 - max_delta_tex
			tex_x1 = tex_x1 + max_delta_tex
		else:
			tex_x0 = tex_x0 + max_delta_tex
			tex_x1 = tex_x1 - max_delta_tex
		max_delta_tex = delta_tex * abs(tex_y0 - tex_y1)
		if tex_y0 < tex_y1:
			tex_y0 = tex_y0 - max_delta_tex
			tex_y1 = tex_y1 + max_delta_tex
		else:
			tex_y0 = tex_y0 + max_delta_tex
			tex_y1 = tex_y1 - max_delta_tex
			
	m.texture = Image(None, size, size, 3)
	m.filename = "blended_material_=" + m00.filename + "__" + m01.filename + "__" + m11.filename + "__" + m10.filename
	
	glPushAttrib(GL_VIEWPORT_BIT | GL_ENABLE_BIT | GL_COLOR_BUFFER_BIT)
	glMatrixMode(GL_PROJECTION); glPushMatrix(); glLoadIdentity()
	glMatrixMode(GL_MODELVIEW ); glPushMatrix(); glLoadIdentity()
	glViewport(0, 0, size, size)
	glDisable(GL_LIGHTING)
	glDisable(GL_CULL_FACE)
	glDisable(GL_DEPTH_TEST)
	
	m._init_texture()
	_DEFAULT_MATERIAL._activate()
	m00._activate()
	glBegin(GL_QUADS)
	glTexCoord2f(tex_x0, tex_y0); glVertex2f(-1.0, -1.0)
	glTexCoord2f(tex_x1, tex_y0); glVertex2f( 1.0, -1.0)
	glTexCoord2f(tex_x1, tex_y1); glVertex2f( 1.0,  1.0)
	glTexCoord2f(tex_x0, tex_y1); glVertex2f(-1.0,  1.0)
	glEnd()

	if m01 is m00: m01 = None
	if m11 is m00: m11 = None
	if m10 is m00: m10 = None
	
	glEnable(GL_BLEND)
	
	if m01:
		m01._activate()
		glBegin(GL_TRIANGLE_FAN)
		
		if cut_direction == 0:
			glColor4f(m01._diffuse[0], m01._diffuse[1], m01._diffuse[2], 0.0)
			glTexCoord2f(tex_x0, tex_y0); glVertex2f(-1.0, -1.0)
			
		glColor4fv(m01._diffuse)
		glTexCoord2f(tex_x1, tex_y0); glVertex2f( 1.0, -1.0)
		
		if m11 is m01: glColor4fv(m01._diffuse); m11 = None
		else:          glColor4f (m01._diffuse[0], m01._diffuse[1], m01._diffuse[2], 0.0)
		glTexCoord2f(tex_x1, tex_y1); glVertex2f( 1.0,  1.0)

		if m10 is m01: glColor4fv(m01._diffuse); m10 = None
		else:          glColor4f (m01._diffuse[0], m01._diffuse[1], m01._diffuse[2], 0.0)
		glTexCoord2f(tex_x0, tex_y1); glVertex2f(-1.0,  1.0)
		
		if cut_direction == 1:
			glColor4f(m01._diffuse[0], m01._diffuse[1], m01._diffuse[2], 0.0)
			glTexCoord2f(tex_x0, tex_y0); glVertex2f(-1.0, -1.0)
			
		glEnd()
	
	if m11:
		m11._activate()
		glBegin(GL_TRIANGLE_FAN)

		glColor4f (m11._diffuse[0], m11._diffuse[1], m11._diffuse[2], 0.0)
		if cut_direction == 0:
			glTexCoord2f(tex_x0, tex_y0); glVertex2f(-1.0, -1.0)
		glTexCoord2f(tex_x1, tex_y0); glVertex2f( 1.0, -1.0)
		
		glColor4fv(m11._diffuse)
		glTexCoord2f(tex_x1, tex_y1); glVertex2f( 1.0,  1.0)
		
		if m10 is m11: glColor4fv(m11._diffuse); m10 = None
		else:          glColor4f (m11._diffuse[0], m11._diffuse[1], m11._diffuse[2], 0.0)
		glTexCoord2f(tex_x0, tex_y1); glVertex2f(-1.0,  1.0)
		
		if cut_direction == 1:
			glColor4f (m11._diffuse[0], m11._diffuse[1], m11._diffuse[2], 0.0)
			glTexCoord2f(tex_x0, tex_y0); glVertex2f(-1.0, -1.0)
			
		glEnd()
		
	if m10:
		m10._activate()
		glBegin(GL_TRIANGLE_FAN)
		
		glColor4f (m10._diffuse[0], m10._diffuse[1], m10._diffuse[2], 0.0)
		if cut_direction == 0:
			glTexCoord2f(tex_x0, tex_y0); glVertex2f(-1.0, -1.0)
		glTexCoord2f(tex_x1, tex_y0); glVertex2f( 1.0, -1.0)
		glTexCoord2f(tex_x1, tex_y1); glVertex2f( 1.0,  1.0)
		
		glColor4fv(m10._diffuse)
		glTexCoord2f(tex_x0, tex_y1); glVertex2f(-1.0,  1.0)
		
		if cut_direction == 1:
			glColor4f (m10._diffuse[0], m10._diffuse[1], m10._diffuse[2], 0.0)
			glTexCoord2f(tex_x0, tex_y0); glVertex2f(-1.0, -1.0)
			
		glEnd()
		
	glReadBuffer(GL_BACK)
	
	glReadPixels(0, 0, size, size, GL_RGB, GL_UNSIGNED_BYTE, m._texture._pixels)
	m.texture = m._texture # Needed to update the material, and generate mipmaps
	
	glPopAttrib()
	glMatrixMode(GL_PROJECTION); glPopMatrix()
	glMatrixMode(GL_MODELVIEW ); glPopMatrix()
	
	return m






