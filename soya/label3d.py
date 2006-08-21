# -*- indent-tabs-mode: t -*-

#! /usr/bin/python -O

# Game Skeleton
# Copyright (C) 2003-2004 Jean-Baptiste LAMY
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

# Soya gaming tutorial, lesson 5
# Adding jumping

# New stuff is in the Controller and Character class


# A bunch of import
import soya
import soya.widget as widget
import soya.opengl as opengl

class Label3D(soya.PythonCoordSyst):
	"""Label3D -- a 2D label displayed at a 3D position

Label3Ds can be added in Worlds.

Attributes :
 - text
 - font
 - size : scales the label. With size = 1.0, a 3D unit corresponds to 1 pixel of the font,
	 which is probably not what you expect, and thus the default value is 0.01. You can increase
	 size to get a bigger label ; if the text is pixelised you should use a bigger font.
 - lit (default 1) : if false, disable lighting effects
 - center_x : -1 : texte is ragged left
							 0 : texte is centered horizontally
							 1 : texte is ragged right
 - center_y : -1 : texte is ragged top
							 0 : texte is centered vertically
							 1 : texte is ragged bottom
 - auto_flip : if true (=default), automatically flip the text if the camera looks at the back
							 of the text.
"""
	def __init__(self, parent = None, text = "", font = None, size = 0.01):
		soya.PythonCoordSyst.__init__(self, parent)
		
		self._text         = text
		self._font         = font or widget.default_font
		self._size         = size
		self._lit          = 1
		self._color        = soya.WHITE
		self._center_x     = 0
		self._center_y     = 0
		self.auto_flip     = 1
		
		self._display_list = soya.DisplayList()
		self._changed      = -2
		
	def __setstate__(self, state):
		soya.PythonCoordSyst.__setstate__(self, state)
		
		self._changed  = -2
		
	def get_font     (self): return self._font
	def set_font     (self, x): self._font  = x; self._changed = -2
	def get_color    (self): return self._color
	def set_color    (self, x): self._color = x; self._changed = -2
	def get_text     (self): return self._text
	def set_text     (self, x): self._text  = x; self._changed = -2
	def get_lit      (self): return self._lit
	def set_lit      (self, x): self._lit = x; self._changed = -2
	def get_size     (self): return self._size
	def set_size     (self, x): self._size = x; self._changed = -2
	def get_center_x (self): return self._center_x
	def set_center_x (self, x): self._center_x = x; self._changed = -2
	def get_center_y (self): return self._center_y
	def set_center_y (self, y): self._center_y = y; self._changed = -2
	def get_auto_flip(self): return self._auto_flip
	def set_auto_flip(self, y): self._auto_flip = y; self._changed = -2
	font      = property(get_font , set_font )
	color     = property(get_color, set_color)
	text      = property(get_text , set_text )
	lit       = property(get_lit  , set_lit  )
	size      = property(get_size , set_size )
	center_x  = property(get_center_x, set_center_x)
	center_y  = property(get_center_y, set_center_y)
	auto_flip = property(get_auto_flip, set_auto_flip)
	
	def batch(self): return 2, self, None
	
	def render(self):
		soya.DEFAULT_MATERIAL.activate()
		
		if self._changed != self._font._pixels_height:
			self._font.create_glyphs(self._text)
			
			opengl.glNewList(self._display_list.id, opengl.GL_COMPILE_AND_EXECUTE)
			self.build_display_list()
			opengl.glEndList()
			self._changed = self._font._pixels_height
		else:
			opengl.glCallList(self._display_list.id)
			
	def build_display_list(self):
		if not self.lit: opengl.glDisable(opengl.GL_LIGHTING)
		
		opengl.glColor4f(*self._color)
		opengl.glScalef(self._size, -self._size, 1.0)
		
		w, h = self._font.get_print_size(self._text)
		if   self.center_x == 0: opengl.glTranslatef(-w / 2.0, 0.0, 0.0)
		elif self.center_x == 1: opengl.glTranslatef(-w      , 0.0, 0.0)
		if   self.center_y == 0: opengl.glTranslatef(0.0, -h / 2.0, 0.0)
		elif self.center_y == 1: opengl.glTranslatef(0.0, -h      , 0.0)

		if self._auto_flip:
			opengl.glEnable(opengl.GL_CULL_FACE)
			self._font.draw(self._text, 0.0, 0.0, 0.0, 1)
			
			opengl.glTranslatef(w, 0.0, 0.0)
			opengl.glScalef(-1.0, 1.0, 1.0)
			self._font.draw(self._text, 0.0, 0.0, 0.0, 1)
			opengl.glDisable(opengl.GL_CULL_FACE)
		else:
			self._font.draw(self._text, 0.0, 0.0, 0.0)
			
		opengl.glEnable(opengl.GL_BLEND) # Font.draw calls glDisable(GL_BLEND)
		
		if not self.lit: opengl.glEnable(opengl.GL_LIGHTING)

	# Hack to make it partly saveable
	#def __getstate__(self):
	#  state = soya.PythonCoordSyst.__getstate__(self)
	#  state[1]["_font"] = None
	#  return state
	

if __name__ == "__main__":
	import sys, os, os.path
	
	# Inits Soya
	soya.init()

	# Define data path (=where to find models, textures, ...)
	HERE = os.path.dirname(sys.argv[0])
	soya.path.append(os.path.join(HERE, "data"))


	# Create the scene (a world with no parent)
	scene = soya.World()


	label = Label3D(scene, "Test bla bla bla bla")
	label.x = 0.0
	label.lit = 0

	camera = soya.Camera(scene)
	camera.z = 4.0
	camera.back = 1000.0

	# Creates a widget group, containing the camera and a label showing the FPS.
	soya.set_root_widget(widget.Group())
	soya.root_widget.add(camera)
	soya.root_widget.add(widget.FPSLabel())

	# Creates and run an "main_loop" (=an object that manage time and regulate FPS)
	# By default, FPS is locked at 40.
	soya.MainLoop(scene).main_loop()
