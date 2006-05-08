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


# modeling-cellshading-1: Modeling : using cell-shading !

# Cell-shading gives a cartoon-like look to your 3D objects by :
#  - adding an outline around this object
#  - shading the object in a non-linear way, according to a 'shader'
#
# The shader is a 1-dimensional gray texture that maps light intensity to the shade level ;
# usually the shader have only a few color levels. See tutorial/data.images/shader.png for
# an example.
#
# In Soya, cell-shading can be activated during world-to-shape compilation.
# In this tuto, we'll draw 2 rotating swords, one normal and one with cell-shading.

# To add cell-shading to an animated character, see also tutorial lesson
# character-animation-shadow-cellshading-1.


# Imports and inits Soya (see lesson basic-1.py).

import sys, os, os.path, soya

soya.init()
soya.path.append(os.path.join(os.path.dirname(sys.argv[0]), "data"))

# Creates the scene.

scene = soya.World()

# Set up an atmosphere, so as the background is white (in order to see the black outline
# of the cell-shading).

scene.atmosphere = soya.Atmosphere()
scene.atmosphere.bg_color = (1.0, 1.0, 1.0, 1.0)


# Loads the sword model

sword = soya.World.get("sword")

# Modify the material, for a better effect

material = sword.children[0].material
material.texture = soya.Image.get("epee_turyle-cs.png")
#material.separate_specular = 1
#material.shininess = 15.0
#material.specular = (1.0, 1.0, 1.0, 1.0)

# Compiles the sword model to a normal shape

sword_shape = sword.shapify()

# Creates the shader. The shader is a normal material with a texture.

shader = soya.Material()
shader.texture = soya.Image.get("shader.png")

# Creates a cell-shading shapifier object. A shapifier is an object that says how a world
# is compiled into a shape. When no shapifier is specified, Soya uses the default shapifier
# (an instance of SimpleShapifier, that does not include cell-shading effect).

cellshading = soya.CellShadingShapifier()

# Sets the shapifier properties. These properties can also be passed to the constructor,
# see docstrings for more info.
# The shader property is (obviously) the shader :-)
# outline_color specifies the color of the outline (default : black)
# outline_width specifies the width of the outline (default 4.0) ; set to 0.0 for no outline
# outline_attenuation specifies how the distance affects the outline_width (default 0.3).

cellshading.shader              = shader
cellshading.outline_color       = (0.0, 0.0, 0.0, 1.0)
cellshading.outline_width       = 7.0
cellshading.outline_attenuation = 1.0

# Assigns the shapifier to the sword.

sword.shapifier = cellshading

# Compiles the sword model to a cell-shaded shape. Notice that is you save the sword now,
# the shapifier would be saved with it too, and thus you can use 'soya.Shape.get("sword")'
# with cell-shading.

sword_cellshaded_shape = sword.shapify()

# Create a rotating volume class, and 2 rotating volumes. The left one is normal, the right
# one is cell-shaded.

class RotatingVolume(soya.Volume):
  def __init__(self, parent = None, shape = None, sens = 1.0):
    soya.Volume.__init__(self, parent, shape)
    self.sens = sens
    
  def advance_time(self, proportion):
    soya.Volume.advance_time(self, proportion)
    self.rotate_lateral(proportion * 2.0 * self.sens)

volume1 = RotatingVolume(scene, sword_shape)
volume1.set_xyz(-1.0, 0.0, 0.0)
volume1.rotate_vertical(90.0)

volume2 = RotatingVolume(scene, sword_cellshaded_shape, -1)
volume2.set_xyz( 1.0, 0.0, 0.0)
volume2.rotate_vertical(90.0)

# Creates a light.

light = soya.Light(scene)
light.set_xyz(0.0, 1.0, 1.0)

# Creates a camera.

camera = soya.Camera(scene)
camera.set_xyz(0.0, 0.8, 2.5)
soya.set_root_widget(camera)

soya.Idler(scene).idle()

