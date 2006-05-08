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


# land-1: Landscape : bitmap-based landscape

# This lesson shows how to make a landscape (also known as heightmap or terrain), using
# a bitmap to describe the terrain. The bitmap acts like a popographic map ; the brighter
# a pixel is, the higher it is. You can make such bitmaps in software like the Gimp.


# Imports and inits Soya (see lesson basic-1.py).

import sys, os, os.path, soya, soya.sdlconst

soya.init()
soya.path.append(os.path.join(os.path.dirname(sys.argv[0]), "data"))
soya.set_quality(2)

# Creates the scene.

scene = soya.World()

# Creates a new landscape in the scene.

land = soya.Land(scene)

# Gets the image "map1.png" from the tutorial data dir, and create the landscape
# from this image. The image dimension must be power of 2 plus 1 : (2 ** n) + 1.

land.from_image(soya.Image.get("map1.png"))

# By default, the landscape height ranges from 0.0 (black pixels) to 1.0 (white pixels).
# Here, we multiply the height by 8.0 so it ranges from 0.0 to 8.0.

land.multiply_height(8.0)

# Now that we have the landscape, we are going to texture it
# (see lesson modeling-material-2 about texturing). First, we creates two textured
# materials.

#material1 = soya.Material(soya.Image.get("block2.png"))
#material2 = soya.Material(soya.Image.get("metal1.png"))
material1 = soya.Material.get("block2")
material2 = soya.Material.get("metal1")

#material1 = soya.Material()
#material1.diffuse = (0.0, 0.0, 0.0, 1.0)
#material1 = soya.Material.get("block2")
#material2 = soya.Material()

# asigns MATERIAL1 to any point whose height is in the range 0.0-6.0, and material2 to
# any point whose height is in the range 6.0-8.0 (remember, height ranges from 0.0 to 8.0).

land.set_material_layer(material1, 0.0, 6.0)
land.set_material_layer(material2, 6.0, 8.0)

# Assigns material1 to any point whose height is in the range 0.0-8.0 and if the angle
# between the surface normal and the verticalvector is in the range 0.0-20.0.

land.set_material_layer_angle(material1, 0.0, 8.0, 0.0, 20.0)

# Now we set some Land attributes:
#  - texture_factor specifies how much the textures are zoomed (higher values mean
#    smaller texture)

#  - scale_factor specifies how the landscape is scaled in the 2 horizontal dimensions.

#  - the 2 last attributes influence the behaviour of the level of detail (LOD) algorithm
#    (LOD means that parts of the landscape are rendered with more detail / more triangle
#    if they are close to the camera). They are a trading between speed and quality.
#    
#    The higher split_factor is, the better precision you have (it means more triangles
#    to draw the Land even far from Camera).
#    
#    patch_size represents the size of patches. A patch is a square part of the Land that
#    computes its visibility and precision.

# the values below are the default ones.
 
land.texture_factor = 1.0
land.scale_factor   = 1.0
land.patch_size     = 8
land.split_factor   = 2.0
land.texture_factor = 0.25

# Moves the landscape.

land.y = -2.5

# Adds a light.

light = soya.Light(scene)
light.set_xyz(0.0, 15.0, 0.0)

# Adds a keyboard-controlled camera and a rendering loop

class MovableCamera(soya.Camera):
  def __init__(self, parent):
    soya.Camera.__init__(self, parent)
    
    self.speed = soya.Vector(self)
    self.rotation_lateral_speed  = 0.0
    self.rotation_vertical_speed = 0.0
    
  def begin_round(self):
    soya.Camera.begin_round(self)
    
    for event in soya.process_event():
      if event[0] == soya.sdlconst.KEYDOWN:
        if   event[1] == soya.sdlconst.K_UP:     self.speed.z = -1.0
        elif event[1] == soya.sdlconst.K_DOWN:   self.speed.z =  1.0
        elif event[1] == soya.sdlconst.K_LEFT:   self.rotation_lateral_speed =  10.0
        elif event[1] == soya.sdlconst.K_RIGHT:  self.rotation_lateral_speed = -10.0
        elif event[1] == soya.sdlconst.K_q:      soya.IDLER.stop()
        elif event[1] == soya.sdlconst.K_ESCAPE: soya.IDLER.stop()
      if event[0] == soya.sdlconst.KEYUP:
        if   event[1] == soya.sdlconst.K_UP:     self.speed.z = 0.0
        elif event[1] == soya.sdlconst.K_DOWN:   self.speed.z = 0.0
        elif event[1] == soya.sdlconst.K_LEFT:   self.rotation_lateral_speed = 0.0
        elif event[1] == soya.sdlconst.K_RIGHT:  self.rotation_lateral_speed = 0.0
      
  def advance_time(self, proportion):
    self.add_mul_vector(proportion, self.speed)
    self.turn_lateral (self.rotation_lateral_speed  * proportion)
    self.turn_vertical(self.rotation_vertical_speed * proportion)
    

camera = MovableCamera(scene)
camera.set_xyz(16.0, 6.0, 0.0)
camera.look_at(soya.Point(scene, 16.0, 6.0, 10.0))
soya.set_root_widget(camera)


#camera.set_xyz(16.0, 8.0, 0.0)
#camera.look_at(soya.Point(scene, 16.0, 6.0, 10.0))


scene.x = 100.0


scene.atmosphere = soya.Atmosphere()
scene.atmosphere.ambient = (1.0, 1.0, 1.0, 1.0)

#soya.Idler(scene).idle()
i = soya.Idler(scene)
#i.min_frame_duration = 0.0
i.idle()
print i.fps
