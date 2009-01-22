# -*- indent-tabs-mode: t -*-

# Soya 3D tutorial
# Copyright (C) 2004      Jean-Baptiste 'Jiba'  LAMY
# Copyright (C) 2001-2002 Bertrand 'blam!' LAMY
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


# terrain-2: Terrain : script-generated terrain

# You create a terrain from a bitmap image, but also by giving the height of each
# vertex individually. In this lesson, learn how!


# This lesson shows how to make a terrain (also known as heightmap or terrain)


# Imports and inits Soya (see lesson basic-1.py).

import sys, os, os.path, random, soya, soya.sdlconst

soya.init()
soya.path.append(os.path.join(os.path.dirname(sys.argv[0]), "data"))

# Creates the scene.

scene = soya.World()

# Creates a new terrain in the scene. terrain_size is the dimension of the terrain ;
# it must be of the form (2 ** n) + 1.

terrain_size = 129
terrain = soya.Terrain(scene, terrain_size, terrain_size)

# Sets a random value for each height.
# Other vertex-setting methods include:
#  - Terrain.set_material     (i, j, material)
#  - Terrain.set_vertex_color (i, j, color) where color is a (red, green, blue, alpha) tuple
#  - Terrain.set_vertex_option(i, j, hidden, invisible, non_solid, force_presence)

for i in range(terrain_size):
	for j in range(terrain_size):
		terrain.set_height(i, j, random.random())

# Multiplies all the heights by 4

terrain.multiply_height(4.0)

# Adds a light.

light = soya.Light(scene)
light.set_xyz(0.0, 15.0, 0.0)

# Add a camera and a loop to render

class MovableCamera(soya.Camera):
	def __init__(self, parent):
		soya.Camera.__init__(self, parent)
		
		self.speed = soya.Vector(self)
		self.rotation_y_speed = 0.0
		self.rotation_x_speed = 0.0
		
	def begin_round(self):
		soya.Camera.begin_round(self)
		
		for event in soya.MAIN_LOOP.events:
			if event[0] == soya.sdlconst.KEYDOWN:
				if   event[1] == soya.sdlconst.K_UP:     self.speed.z = -1.0
				elif event[1] == soya.sdlconst.K_DOWN:   self.speed.z =  1.0
				elif event[1] == soya.sdlconst.K_LEFT:   self.rotation_y_speed =  10.0
				elif event[1] == soya.sdlconst.K_RIGHT:  self.rotation_y_speed = -10.0
				elif event[1] == soya.sdlconst.K_q:      soya.MAIN_LOOP.stop()
				elif event[1] == soya.sdlconst.K_ESCAPE: soya.MAIN_LOOP.stop()
			if event[0] == soya.sdlconst.KEYUP:
				if   event[1] == soya.sdlconst.K_UP:     self.speed.z = 0.0
				elif event[1] == soya.sdlconst.K_DOWN:   self.speed.z = 0.0
				elif event[1] == soya.sdlconst.K_LEFT:   self.rotation_y_speed = 0.0
				elif event[1] == soya.sdlconst.K_RIGHT:  self.rotation_y_speed = 0.0
				
	def advance_time(self, proportion):
		self.add_mul_vector(proportion, self.speed)
		self.turn_y(self.rotation_y_speed * proportion)
		self.turn_x(self.rotation_x_speed * proportion)
		

camera = MovableCamera(scene)
camera.set_xyz(16.0, 6.0, 0.0)
camera.look_at(soya.Point(scene, 16.0, 6.0, 10.0))
#soya.set_root_widget(camera)

import soya.widget
soya.set_root_widget(soya.widget.Group())
soya.root_widget.add(camera)
soya.root_widget.add(soya.widget.FPSLabel())
m = soya.MainLoop(scene)
#m.min_frame_duration = -1.0
m.main_loop()
