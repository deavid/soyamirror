# -*- indent-tabs-mode: t -*-

# Soya 3D
# Copyright (C) 2005 Jean-Baptiste LAMY -- jiba@tuxfamily.org
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

import math

import soya, soya.opengl as opengl

class MovingMaterial(soya.PythonMainLoopingMaterial):
	def __init__(self, texture = None, dtex_x = 0.0, dtex_y = 0.0, tex_x0 = 0.0, tex_y0 = 0.0):
		soya.PythonMainLoopingMaterial.__init__(self, texture)
		
		self.dtex_x = dtex_x
		self.dtex_y = dtex_y
		self._tex_x = tex_x0
		self._tex_y = tex_y0
		
	def advance_time(self, proportion):
		self._tex_x += proportion * self.dtex_x
		self._tex_y += proportion * self.dtex_y
	
	def activated(self):
		opengl.glMatrixMode(opengl.GL_TEXTURE)
		opengl.glLoadIdentity() # Needed, because activated() may be called several time without inactivated being called
		opengl.glTranslatef(self._tex_x, self._tex_y, 0.0)
		opengl.glMatrixMode(opengl.GL_MODELVIEW)
		
	def inactivated(self):
		opengl.glMatrixMode(opengl.GL_TEXTURE)
		opengl.glLoadIdentity()
		opengl.glMatrixMode(opengl.GL_MODELVIEW)
		
		
class RotatingMaterial(soya.PythonMainLoopingMaterial):
	def __init__(self, texture = None, amplitude = 0.2, speed = 0.1):
		soya.PythonMainLoopingMaterial.__init__(self, texture)
		
		self.amplitude = amplitude
		self.speed     = speed
		self._angle    = 0.0
		
	def advance_time(self, proportion):
		self._angle += proportion * self.speed
		
	def activated(self):
		opengl.glMatrixMode(opengl.GL_TEXTURE)
		opengl.glLoadIdentity() # Needed, because activated() may be called several time without inactivated being called
		opengl.glTranslatef(self.amplitude * math.cos(self._angle), self.amplitude * math.sin(self._angle), 0.0)
		opengl.glMatrixMode(opengl.GL_MODELVIEW)
		
	def inactivated(self):
		opengl.glMatrixMode(opengl.GL_TEXTURE)
		opengl.glLoadIdentity()
		opengl.glMatrixMode(opengl.GL_MODELVIEW)
		
		
class ZoomingMaterial(soya.PythonMainLoopingMaterial):
	def __init__(self, texture = None, speed = 0.1, amplitude = 0.1):
		soya.PythonMainLoopingMaterial.__init__(self, texture)
		
		self.angle     = 0.0
		self.speed     = speed
		self.amplitude = amplitude
		
	def advance_time(self, proportion):
		self.angle += proportion * self.speed
		
	def activated(self):
		f1 = self.amplitude * (math.cos(self.angle) + 1.0)
		f2 = 1.0 - 2.0 * f1
		
		opengl.glMatrixMode(opengl.GL_TEXTURE)
		opengl.glLoadIdentity() # Needed, because activated() may be called several time without inactivated being called
		opengl.glTranslatef(f1, f1, 0.0)
		opengl.glScalef(f2, f2, 1.0)
		opengl.glMatrixMode(opengl.GL_MODELVIEW)
		
	def inactivated(self):
		opengl.glMatrixMode(opengl.GL_TEXTURE)
		opengl.glLoadIdentity()
		opengl.glMatrixMode(opengl.GL_MODELVIEW)
		
