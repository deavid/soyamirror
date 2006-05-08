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


# modeling-material-1: Material colors : a metallic blue cube

# In this lesson, we introduce the Material object and build a material blue cube.
# A material defines the properties of a surface, including shininess, color and
# texture (skin). Each face can have a different material, as well as other objects.


# Imports and inits Soya (see lesson basic-1.py).

import sys, os, os.path, soya, soya.cube

soya.init()
soya.path.append(os.path.join(os.path.dirname(sys.argv[0]), "data"))

# Creates the scene.

scene = soya.World()

# Creates the material

material = soya.Material()

# Sets the material's shininess to 0.5. The shininess ranges from 0.0 to 128.0;
# 0.0 is the most metallic / shiny, and 128.0 is the most plastic.

material.shininess = 0.5

# Sets the material's diffuse color. The diffuse color is the basic color.
# In Soya 3D, colors are tuples of 4 floats: (red, green, blue, alpha), where
# each component normally ranges from 0.0 to 1.0 (though you can use values
# out of this range, e.g. negative values to get a dark light), and alpha
# is used for transparency (1.0 is opaque and 0.0 fully transparent).

# We use here a blue diffuse color.

material.diffuse   = (0.0, 0.2, 0.7, 1.0)

# Sets the material's specular color. The specular color is the one used for
# the specular / shiny effects.

# We use here a light blue, to get metallic reflexions.

material.specular  = (0.2, 0.7, 1.0, 1.0)

# Activates the separate specular. This results in a brighter specular effect.

material.separate_specular = 1

# Other interesting attributes of materials are:
# - wireframed        : draw in wireframe
# - additive_blending : usefull for alpha-blending and special effect

# The soya.cube module creates cubes by adding 6 faces inside a world ; it works
# exactely as we do in the modeling-1.py lesson.
# As usually, the first argument is the parent and the second is the material.
# Here, we specify None as parent because we don't want to display this cube ;
# we are going to compile it for speed purpose.

# Similarly you can set a Material to a face, either in the constructor or with
# face.material = material.

# Notice that None is not a valid material ; use soya.DEFAULT_MATERIAL instead.

cube_world = soya.cube.Cube(None, material)

# Creates a subclass of Volume that permanently rotates.
# See the timemanagement-* lesson series for more info.

class RotatingVolume(soya.Volume):
  def advance_time(self, proportion):
    self.rotate_lateral(2.0 * proportion)

# Create a rotating volume in the scene, using the cube shape.

cube = RotatingVolume(scene, cube_world.shapify())
cube.rotate_vertical(30.0)

# Creates a light.

light = soya.Light(scene)
light.set_xyz(0.5, 1.0, 2.0)

# Creates a camera.

camera = soya.Camera(scene)
camera.set_xyz(0.0, 0.0, 2.0)
soya.set_root_widget(camera)

soya.Idler(scene).idle()

