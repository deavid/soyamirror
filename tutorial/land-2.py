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


# land-2: Landscape : script-generated landscape

# You create a landscape from a bitmap image, but also by giving the height of each
# vertex individually. In this lesson, learn how!


# This lesson shows how to make a landscape (also known as heightmap or terrain)


# Imports and inits Soya (see lesson basic-1.py).

import sys, os, os.path, random, soya, soya.sdlconst

soya.init()
soya.path.append(os.path.join(os.path.dirname(sys.argv[0]), "data"))

# Creates the scene.

scene = soya.World()

# Creates a new landscape in the scene. land_size is the dimension of the landscape ;
# it must be of the form (2 ** n) + 1.

land_size = 33
land = soya.Land(scene, land_size, land_size)

# Sets a random value for each height.
# Other vertex-setting methods include:
#  - Land.set_material     (i, j, material)
#  - Land.set_vertex_color (i, j, color) where color is a (red, green, blue, alpha) tuple
#  - Land.set_vertex_option(i, j, hidden, invisible, non_solid, force_presence)

for i in range(land_size):
  for j in range(land_size):
    land.set_height(i, j, random.random())

# Multiplies all the heights by 4

land.multiply_height(4.0)

# Adds a light.

light = soya.Light(scene)
light.set_xyz(0.0, 15.0, 0.0)

# Add a camera and a loop to render

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

soya.Idler(scene).idle()
