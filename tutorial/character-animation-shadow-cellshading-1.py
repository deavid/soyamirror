# Soya 3D tutorial
# Copyright (C) 2001-2002 Jean-Baptiste LAMY
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


# character-animation-shadow-cellshading-1: shadowed and cellshaded Cal3D animated character

# In this lesson, we add shadow and cell-shading to Balazar.
#
# See lessons modeling-shadow and modeling-cellshading for more info on shadow or
# cell-shading.


# Imports and inits Soya.

import sys, os, os.path, soya, soya.widget as widget

soya.init()
soya.path.append(os.path.join(os.path.dirname(sys.argv[0]), "data"))

# Creates the scene.

scene = soya.World()

# Set up an atmosphere, so as the background is gray (in order to see the black outline
# of the cell-shading).

scene.atmosphere = soya.Atmosphere()
scene.atmosphere.bg_color = (0.6, 0.6, 0.6, 1.0)

# Loads the sorcerer shape.

sorcerer_shape = soya.Cal3dShape.get("balazar")

# Enables shadows on Balazar !

sorcerer_shape.shadow = 1

# Enables cell-shading on Balazar !
# Arguments (all are optional):
# - shader              (defaults to soya.SHADER_DEFAULT_MATERIAL)
# - outline_color       (defaults to black)
# - outline_width       (defaults to 4.0)
# - outline_attenuation (defaults to 0.3)
#
# See lesson modeling-cellshading-1 for more info on these parameters

sorcerer_shape.set_cellshading()

# Notice that you can also add the following attribute in the Cal3D .cfg file (e.g.
# balazar/balazar.cfg) :
#
#double_sided=1
#shadow=1
#cellshading=1
#cellshading_outline_color=1.0, 1.0, 1.0, 1.0
#cellshading_outline_width=4.0
#cellshading_outline_attenuation=0.0
#
# double_sided draws the Cal3D shape with double sided face (equivalent to
# Face.double_sided). Other attributes have obvious meaning!
#
# And remember : don't put ANY space before or after the "=" !

# Create a sorcerer volume

sorcerer = soya.Cal3dVolume(scene, sorcerer_shape)

# Rotates Balazar the sorcerer

sorcerer.rotate_lateral(-120.0)

# Starts playing the animation called "marche" in cycle ("marche" is the French for walk).

sorcerer.animate_blend_cycle("marche")


# Creates a wall, to receive the shadow.
# Notice that the wall can be any object (including e.g. a landscape,...) : receiving
# shadows doesn't require any particular property.

wall_model = soya.World()
wall_face = soya.Face(wall_model, [
  soya.Vertex(wall_model, -5.0, 0.0, -5.0),
  soya.Vertex(wall_model, -5.0, 0.0,  5.0),
  soya.Vertex(wall_model,  5.0, 0.0,  5.0),
  soya.Vertex(wall_model,  5.0, 0.0, -5.0),
  ])
wall_face.double_sided = 1
wall = soya.Volume(scene, wall_model.shapify())
wall.set_xyz(-1.0, 0.0, 0.0)

# Adds a camera and a light and starts the main loop.

light = soya.Light(scene)
light.set_xyz(2.0, 5.0, -1.0)
light.cast_shadow = 1
light.shadow_color = (0.0, 0.0, 0.0, 0.5)

camera = soya.Camera(scene)
camera.set_xyz(0.0, 1.0, 4.0)

soya.set_root_widget(camera)

soya.Idler(scene).idle()
