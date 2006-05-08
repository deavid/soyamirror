# Soya 3D tutorial
# Copyright (C) 2001-2004 Jean-Baptiste LAMY
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


# modeling-shadow-1: Modeling : shadows !

# Shadows must be enabled both on the light that casts the shadow, and on the shape
# that projects it.

# The shadow algorithm assume that non-double sided faces are part of closed volumes, so
# you should take this into account when designing your models.
# Nothing is assumed for double sided faces, though, so in doubt, use double sided faces.

# To add shadow to an animated character, see also tutorial lesson
# character-animation-shadow-cellshading-1.


# Imports and inits Soya (see lesson basic-1.py).

import sys, os, os.path, soya, soya.cube

soya.init()
soya.path.append(os.path.join(os.path.dirname(sys.argv[0]), "data"))

# Creates the scene.

scene = soya.World()

# Loads the sword model.

sword = soya.World.get("sword")

# Creates a simple shape shapifier object. A shapifier is an object that says how a world
# is compiled into a shape. When no shapifier is specified, Soya uses the default shapifier
# (an instance of SimpleShapifier, that does not include shadows).

shapifier = soya.SimpleShapifier()

# Sets the 'shadow' shapifier property to true.

shapifier.shadow = 1

# Assigns the shapifier to the sword.

sword.shapifier = shapifier

# Compiles the sword model to a shadowed shape. Notice that is you save the sword now,
# the shapifier would be saved with it too, and thus you can use 'soya.Shape.get("sword")'.

sword_shape = sword.shapify()

# Create a rotating volume class, and a rotating volume.

class RotatingVolume(soya.Volume):
  def __init__(self, parent = None, shape = None):
    soya.Volume.__init__(self, parent, shape)
    
  def advance_time(self, proportion):
    soya.Volume.advance_time(self, proportion)
    
    self.rotate_lateral(proportion * 2.0)
      
      
volume = RotatingVolume(scene, sword_shape)
volume.set_xyz(1.0, -1.0, 0.0)
volume.rotate_vertical(90.0)

# Creates a wall, to receive the shadow.
# Notice that the wall can be any object (including e.g. a landscape,...) : receiving
# shadows doesn't require any particular property.

wall_model = soya.World()
wall_face = soya.Face(wall_model, [
  soya.Vertex(wall_model, 0.0, -5.0, -5.0),
  soya.Vertex(wall_model, 0.0, -5.0,  5.0),
  soya.Vertex(wall_model, 0.0,  5.0,  5.0),
  soya.Vertex(wall_model, 0.0,  5.0, -5.0),
  ])
wall_face.double_sided = 1
wall = soya.Volume(scene, wall_model.shapify())
wall.set_xyz(-1.0, 0.0, 0.0)

# Creates a light.

light = soya.Light(scene)
light.set_xyz(5.0, 0.0, 0.0)

# Sets the light's shadow color. Semitransparent color (alpha < 1.0) are often used.

light.shadow_color = (0.0, 0.0, 0.0, 0.5)

# Enables shadows for this light

light.cast_shadow = 1

# Creates a camera.

camera = soya.Camera(scene)
camera.set_xyz(0.0, 0.0, 3.5)
soya.set_root_widget(camera)

soya.Idler(scene).idle()
