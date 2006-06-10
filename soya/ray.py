# -*- indent-tabs-mode: t -*-

# Soya 3D
# Copyright (C) 2001-2002 Jean-Baptiste LAMY -- jiba@tuxfamily.org
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

"""soya.ray

Provide a Ray -- a line that draw a fading trace behind it when it moves.
Rays are usually used for sword or reactor.

The line starts at the ray position and ends at "endpoint" (by default,
0.0, 0.0, -1.0 in the ray coordinate system). Move, rotate or scale the
ray if you want a different position or size.

The color of the ray can be changed, as well as the length of the faded trace.

See tutorial lesson 106."""

from soya import PythonCoordSyst, Point, Vector, DEFAULT_MATERIAL
import soya.opengl


class Ray(PythonCoordSyst):
	def __init__(self, parent = None, material = DEFAULT_MATERIAL, length = 10):
		PythonCoordSyst.__init__(self)
		
		self.material = material
		self.length   = length
		self.old_pos  = []
		
		self.endpoint = Point(self, 0.0, 0.0, -1.0)
		
		if parent: parent.add(self)
		
	def __getstate__(self):
		state = PythonCoordSyst.__getstate__(self)
		if state[1] is self.__dict__: state = state[0], state[1].copy()
		del state[1]["old_pos"]
		return state
	
	def __setstate__(self, state):
		PythonCoordSyst.__setstate__(self, state)
		self.old_pos  = []
		
	def zap(self): self.old_pos *= 0
	
	def batch(self): return 2, self.get_root(), self.material
	
	def render(self):
		root = self.get_root()
		
		self.old_pos.insert(0, (root.transform(self), root.transform(self.endpoint)))
		
		
		if len(self.old_pos) > self.length: del self.old_pos[-1]
		
		self.material.activate()
		soya.opengl.glDisable(soya.opengl.GL_LIGHTING)
		soya.opengl.glDisable(soya.opengl.GL_CULL_FACE)
		
		soya.opengl.glBegin(soya.opengl.GL_QUAD_STRIP)
		
		color = list(self.material.diffuse)
		if self.material.texture:
			for start, end in self.old_pos:
				soya.opengl.glColor4f(*color)
				color[3] -= 1.0 / (self.length - 1)
				
				soya.opengl.glTexCoord2f(0.0, color[3])
				soya.opengl.glVertex3f(*end)
				
				soya.opengl.glTexCoord2f(1.0, color[3])
				soya.opengl.glVertex3f(*start)
				
		else:
			for start, end in self.old_pos:
				soya.opengl.glColor4f(*color)
				color[3] -= 1.0 / (self.length - 1)
				
				soya.opengl.glVertex3f(*end)
				soya.opengl.glVertex3f(*start)
				
		soya.opengl.glEnd()
		soya.opengl.glEnable(soya.opengl.GL_LIGHTING)
		soya.opengl.glEnable(soya.opengl.GL_CULL_FACE)
		

class HalfRay(PythonCoordSyst):
	def __init__(self, parent = None, material = DEFAULT_MATERIAL, length = 10):
		PythonCoordSyst.__init__(self)
		
		self.material = material
		self.length   = length
		self.old_pos  = []
		
		self.endpoint = Point(self, 0.0, 0.0, -1.0)
		
		if parent: parent.add(self)
		
	def __getstate__(self):
		state = PythonCoordSyst.__getstate__(self)
		if state[1] is self.__dict__: state = state[0], state[1].copy()
		del state[1]["old_pos"]
		return state
	
	def __setstate__(self, state):
		PythonCoordSyst.__setstate__(self, state)
		self.old_pos  = []
		
	def zap(self): self.old_pos *= 0
	
	def batch(self): return 2, self.get_root(), self.material
	
	def render(self):
		root = self.get_root()
		
		self.old_pos.insert(0, (root.transform(self), root.transform(self.endpoint)))
		
		
		if len(self.old_pos) > self.length: del self.old_pos[-1]
		
		self.material.activate()
		soya.opengl.glDisable(soya.opengl.GL_LIGHTING)
		soya.opengl.glDisable(soya.opengl.GL_CULL_FACE)
		
		soya.opengl.glBegin(soya.opengl.GL_QUAD_STRIP)
		
		color = list(self.material.diffuse)
		if self.material.texture:
			for start, end in self.old_pos:
				soya.opengl.glColor4f(*color)
				color[3] -= 1.0 / (self.length - 1)
				
				soya.opengl.glTexCoord2f(0.0, color[3])
				soya.opengl.glVertex3f(*end)
				
				soya.opengl.glTexCoord2f(1.0, color[3])
				soya.opengl.glVertex3f(*start)
				
		else:
			for start, end in self.old_pos:
				soya.opengl.glColor4f(*color)
				color[3] -= 1.0 / (self.length - 1)
				
				soya.opengl.glVertex3f(*end)
				
				soya.opengl.glColor4f(color[0], color[1], color[2], 0.0)
				
				soya.opengl.glVertex3f(*start)
				
		soya.opengl.glEnd()
		soya.opengl.glEnable(soya.opengl.GL_LIGHTING)
		soya.opengl.glEnable(soya.opengl.GL_CULL_FACE)
		

