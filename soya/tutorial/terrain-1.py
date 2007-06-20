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


# terrain-1: Terrain : bitmap-based terrain

# This lesson shows how to make a terrain (also known as heightmap or terrain), using
# a bitmap to describe the terrain. The bitmap acts like a popographic map ; the brighter
# a pixel is, the higher it is. You can make such bitmaps in software like the Gimp.


# Imports and inits Soya (see lesson basic-1.py).

import sys, os, os.path, soya, soya.sdlconst

soya.init()
soya.path.append(os.path.join(os.path.dirname(sys.argv[0]), "data"))
soya.set_quality(2)

# Creates the scene.

scene = soya.World()

# Creates a new terrain in the scene.

terrain = soya.Terrain(scene)

# Gets the image "map1.png" from the tutorial data dir, and create the terrain
# from this image. The image dimension must be power of 2 plus 1 : (2 ** n) + 1.

terrain.from_image(soya.Image.get("map1.png"))

# By default, the terrain height ranges from 0.0 (black pixels) to 1.0 (white pixels).
# Here, we multiply the height by 8.0 so it ranges from 0.0 to 8.0.

terrain.multiply_height(8.0)

# Now that we have the terrain, we are going to texture it
# (see lesson modeling-material-2 about texturing). First, we creates two textured
# materials.

material1 = soya.Material.get("block2")
material2 = soya.Material.get("metal1")

# asigns MATERIAL1 to any point whose height is in the range 0.0-6.0, and material2 to
# any point whose height is in the range 6.0-8.0 (remember, height ranges from 0.0 to 8.0).

terrain.set_material_layer(material1, 0.0, 6.0)
terrain.set_material_layer(material2, 6.0, 8.0)

# Assigns material1 to any point whose height is in the range 0.0-8.0 and if the angle
# between the surface normal and the vertical vector is in the range 0.0-20.0.

terrain.set_material_layer_angle(material1, 0.0, 8.0, 0.0, 20.0)

# Now we set some Terrain attributes:
#  - texture_factor specifies how much the textures are zoomed (higher values mean
#    smaller texture)

#  - scale_factor specifies how the terrain is scaled in the 2 horizontal dimensions.

#  - the 2 last attributes influence the behaviour of the level of detail (LOD) algorithm
#    (LOD means that parts of the terrain are rendered with more detail / more triangle
#    if they are close to the camera). They are a trading between speed and quality.
#    
#    The higher split_factor is, the better precision you have (it means more triangles
#    to draw the Terrain even far from Camera).
#    
#    patch_size represents the size of patches. A patch is a square part of the Terrain that
#    computes its visibility and precision.

# the values below are the default ones.
 
terrain.texture_factor = 1.0
terrain.scale_factor   = 1.0
terrain.patch_size     = 8
terrain.split_factor   = 2.0


terrain.texture_factor = 0.25

# Moves the terrain.

terrain.y = -2.5

# Adds a light.

light = soya.Light(scene)
light.set_xyz(0.0, 15.0, 0.0)

# Adds a keyboard-controlled camera and a rendering loop

class MovableCamera(soya.Camera):
	def __init__(self, parent):
		soya.Camera.__init__(self, parent)
		
		self.speed = soya.Vector(self)
		self.rotation_y_speed = 0.0
		self.rotation_x_speed = 0.0
		
	def begin_round(self):
		soya.Camera.begin_round(self)
		
		for event in soya.process_event():
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
soya.set_root_widget(camera)


#camera.set_xyz(16.0, 8.0, 0.0)
#camera.look_at(soya.Point(scene, 16.0, 6.0, 10.0))


scene.x = 100.0


scene.atmosphere = soya.Atmosphere()
scene.atmosphere.ambient = (1.0, 1.0, 1.0, 1.0)

import soya.widget
soya.set_root_widget(soya.widget.Group())
soya.root_widget.add(camera)
soya.root_widget.add(soya.widget.FPSLabel())
m = soya.MainLoop(scene)
#m.min_frame_duration = 0.0
m.main_loop()
