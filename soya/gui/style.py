# -*- indent-tabs-mode: t -*-
# -*- coding: utf-8 -*-

# Soya 3D
# Copyright (C) 2007 Jean-Baptiste LAMY -- jiba@tuxfamily.org
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

import os, os.path
import soya, soya.sdlconst as sdlconst, soya.opengl as opengl

class Style(object):
	def __init__(self):
		self.table_row_pad = 5
		self.table_col_pad = 5
		#self.font = soya.Font(os.path.join(soya.DATADIR, "FreeSans.ttf"), 25, 30)
		#self.font = soya.Font(os.path.join(soya.DATADIR, "FreeSans.ttf"), 30, 30)
		self.font = soya.Font(os.path.join(soya.DATADIR, "FreeSans.ttf"), 20, 20)
		self.font.filename = "DEFAULT_FONT"
		self.char_height = self.font.height
		
		self.materials = [
			soya.Material(),
			soya.Material(),
			soya.Material(),
			soya.Material(),
			soya.Material(),
			]
# 		self.materials[0].diffuse = (0.3, 0.3, 0.3, 0.8) # Base
# 		self.materials[1].diffuse = (0.0, 0.6, 0.0, 1.0) # Selected
# 		self.materials[2].diffuse = (0.0, 0.6, 0.0, 1.0) # Window title
# 		self.materials[3].diffuse = (0.0, 0.8, 0.0, 1.0) # Selected window title
# 		self.line_colors = [
# 			(1.0, 1.0, 1.0, 0.8), # Base
# 			(1.0, 1.0, 1.0, 1.0), # Selected
# 			(1.0, 1.0, 1.0, 1.0), # Window title
# 			(1.0, 1.0, 1.0, 1.0), # Selected window title
# 			]
# 		self.line_width     = 2
		
		self.materials[0].diffuse = (0.8, 0.0, 0.0, 1.0) # Base
		self.materials[1].diffuse = (1.0, 0.2, 0.2, 1.0) # Selected
		self.materials[2].diffuse = (0.8, 0.0, 0.0, 1.0) # Window title
		self.materials[3].diffuse = (1.0, 0.0, 0.0, 1.0) # Selected window title
		self.materials[4].diffuse = (1.0, 1.0, 1.0, 0.9) # Window background
		self.corner_colors = [
			(0.0, 0.0, 0.0, 1.0), # Base
			(0.0, 0.0, 0.0, 1.0), # Selected
			(0.0, 0.0, 0.0, 1.0), # Window title
			(0.0, 0.0, 0.0, 1.0), # Selected window title
			(0.5, 0.5, 0.5, 0.5), # Window background
			]
		self.line_colors = [
			(0.0, 0.0, 0.0, 1.0), # Base
			(0.0, 0.0, 0.0, 1.0), # Selected
			(0.0, 0.0, 0.0, 1.0), # Window title
			(0.0, 0.0, 0.0, 1.0), # Selected window title
			(0.0, 0.0, 0.0, 1.0), # Window background
			]
		self.text_colors = [
			(0.0, 0.0, 0.0, 1.0), # Base
			(0.0, 0.2, 0.0, 1.0), # Selected
			(1.0, 1.0, 1.0, 1.0), # Window title
			]
		self.line_width = 1
		
		
		self.materials[0].diffuse = (1.0, 0.9, 0.4, 1.0) # Base
		self.materials[1].diffuse = (1.0, 1.0, 0.7, 1.0) # Selected
		self.materials[2].diffuse = (1.0, 0.9, 0.4, 1.0) # Window title
		self.materials[3].diffuse = (1.0, 1.0, 0.5, 1.0) # Selected window title
		
		self.materials[2].diffuse = (1.0, 0.7, 0.2, 1.0) # Window title
		self.materials[3].diffuse = (1.0, 0.9, 0.4, 1.0) # Selected window title
		self.materials[4].diffuse = (1.0, 1.0, 1.0, 0.9) # Window background
		b  = (0.9, 0.6, 0.0, 1.0)
		b2 = (0.9, 0.5, 0.0, 1.0)
		self.corner_colors = [
			b, # Base
			b, # Selected
			b2, # Window title
			b2, # Selected window title
			(1.0, 0.9, 0.4, 0.9), # Window background
			]
		self.line_colors = [
			b, # Base
			b, # Selected
			b2, # Window title
			b2, # Selected window title
			b, # Window background
			]
		self.text_colors = [
			(0.0, 0.0, 0.0, 1.0), # Base
			#(0.0, 0.2, 0.0, 1.0), # Selected
			(0.4, 0.4, 0.0, 1.0), # Selected
			(0.7, 0.4, 0.0, 1.0), # Window title
			]
		self.line_width = 1
    
	def rectangle(self, x1, y1, x2, y2, material_index = 0):
		self.materials[material_index].activate()
		if self.materials[material_index].is_alpha(): opengl.glEnable(opengl.GL_BLEND)
# 		opengl.glBegin   (opengl.GL_QUADS)
# 		opengl.glTexCoord2f(0.0, 0.0); opengl.glVertex2i(x1, y1)
# 		opengl.glTexCoord2f(0.0, 1.0); opengl.glVertex2i(x1, y2)
# 		opengl.glColor4f(*self.corner_colors[material_index])
# 		opengl.glTexCoord2f(1.0, 1.0); opengl.glVertex2i(x2, y2)
# 		opengl.glColor4f(*self.materials[material_index].diffuse)
# 		opengl.glTexCoord2f(1.0, 0.0); opengl.glVertex2i(x2, y1)
# 		opengl.glEnd()
		if self.corner_colors[material_index]:
			if  (x2 - x1) // 2 < y2 - y1:
				opengl.glBegin   (opengl.GL_QUADS)
				opengl.glVertex2i(x1, y1)
				opengl.glVertex2i(x1, y2)
				opengl.glVertex2i(x2, y2 - (x2 - x1) // 2)
				opengl.glVertex2i(x2, y1)
				opengl.glEnd()
				opengl.glBegin   (opengl.GL_TRIANGLES)
				opengl.glVertex2i(x2, y2 - (x2 - x1) // 2)
				opengl.glVertex2i(x1, y2)
				opengl.glColor4f(*self.corner_colors[material_index])
				opengl.glVertex2i(x2, y2)
				opengl.glEnd()
			else:
				opengl.glBegin   (opengl.GL_QUADS)
				opengl.glVertex2i(x1, y1)
				opengl.glVertex2i(x1, y2)
				opengl.glVertex2i(x2 - 2 * (y2 - y1), y2)
				opengl.glVertex2i(x2, y1)
				opengl.glEnd()
				opengl.glBegin   (opengl.GL_TRIANGLES)
				opengl.glVertex2i(x2, y1)
				opengl.glVertex2i(x2 - 2 * (y2 - y1), y2)
				opengl.glColor4f(*self.corner_colors[material_index])
				opengl.glVertex2i(x2, y2)
				opengl.glEnd()
		else:
			opengl.glBegin   (opengl.GL_QUADS)
			opengl.glTexCoord2f(0.0, 0.0); opengl.glVertex2i(x1, y1)
			opengl.glTexCoord2f(0.0, 1.0); opengl.glVertex2i(x1, y2)
			opengl.glTexCoord2f(1.0, 1.0); opengl.glVertex2i(x2, y2)
			opengl.glTexCoord2f(1.0, 0.0); opengl.glVertex2i(x2, y1)
			opengl.glEnd()
		soya.DEFAULT_MATERIAL.activate()
		if self.line_width and self.line_colors[material_index][3]:
			opengl.glColor4f(*self.line_colors[material_index])
			opengl.glLineWidth(self.line_width)
			opengl.glBegin   (opengl.GL_LINE_LOOP)
			opengl.glVertex2i(x1, y1)
			opengl.glVertex2i(x1, y2)
			opengl.glVertex2i(x2, y2)
			opengl.glVertex2i(x2, y1)
			opengl.glEnd()
			opengl.glLineWidth(1.0)
		
	def triangle(self, side, x1, y1, x2, y2, material_index = 0):
		self.materials[material_index].activate()
		if self.materials[material_index].is_alpha(): opengl.glEnable(opengl.GL_BLEND)
		opengl.glBegin   (opengl.GL_TRIANGLES)
		if   side == 0:
			opengl.glTexCoord2f(0.0, 0.5); opengl.glVertex2i(x1, (y1 + y2) // 2)
			opengl.glTexCoord2f(1.0, 1.0); opengl.glVertex2i(x2, y2)
			opengl.glTexCoord2f(1.0, 0.0); opengl.glVertex2i(x2, y1)
		elif side == 1:
			opengl.glTexCoord2f(1.0, 0.5); opengl.glVertex2i(x2, (y1 + y2) // 2)
			opengl.glTexCoord2f(0.0, 0.0); opengl.glVertex2i(x1, y1)
			opengl.glTexCoord2f(0.0, 1.0); opengl.glVertex2i(x1, y2)
		elif side == 2:
			opengl.glTexCoord2f(0.5, 0.0); opengl.glVertex2i((x1 + x2) // 2, y1)
			opengl.glTexCoord2f(0.0, 1.0); opengl.glVertex2i(x1, y2)
			opengl.glTexCoord2f(1.0, 1.0); opengl.glVertex2i(x2, y2)
		elif side == 3:
			opengl.glTexCoord2f(0.5, 1.0); opengl.glVertex2i((x1 + x2) // 2, y2)
			opengl.glTexCoord2f(1.0, 0.0); opengl.glVertex2i(x2, y1)
			opengl.glTexCoord2f(0.0, 0.0); opengl.glVertex2i(x1, y1)
		opengl.glEnd()
		soya.DEFAULT_MATERIAL.activate()
		if self.line_width and self.line_colors[material_index][3]:
			opengl.glColor4f(*self.line_colors[material_index])
			opengl.glLineWidth(self.line_width)
			opengl.glBegin   (opengl.GL_LINE_LOOP)
			if   side == 0:
				opengl.glVertex2i(x1, (y1 + y2) // 2)
				opengl.glVertex2i(x2, y1)
				opengl.glVertex2i(x2, y2)
			elif side == 1:
				opengl.glVertex2i(x2, (y1 + y2) // 2)
				opengl.glVertex2i(x1, y1)
				opengl.glVertex2i(x1, y2)
			elif side == 2:
				opengl.glVertex2i((x1 + x2) // 2, y1)
				opengl.glVertex2i(x1, y2)
				opengl.glVertex2i(x2, y2)
			elif side == 3:
				opengl.glVertex2i((x1 + x2) // 2, y2)
				opengl.glVertex2i(x1, y1)
				opengl.glVertex2i(x2, y1)
			opengl.glEnd()
			opengl.glLineWidth(1.0)
		
		
