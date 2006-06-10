# -*- indent-tabs-mode: t -*-

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


# modeling-material-2: Texture (skin) : textured cube and pyramid

# In addition to colors and shininess, materials can have a texture.
# Textures are used to put a bitmap image on the surface of a 3D object.
# It is sometimes called "skin" by graphists ; in Blender it corresponds
# to the UV texture map.

# Soya image loading is done through the PIL (Python Imaging Library), so you need the PIL.
# When the material is saved, the raw image data are included in the material file and so
# the final user may not need the PIL.


# Imports and inits Soya.

import sys, os, os.path, soya, soya.cube

soya.init()
soya.path.append(os.path.join(os.path.dirname(sys.argv[0]), "data"))

# Creates the scene.

scene = soya.World()

# Creates the material

material = soya.Material()

# Sets the material's texture. The texture must be a soya.Image object, or None for no
# texture (the default). Texture images dimensions MUST BE POWER OF 2
# (e.g. 64x64, 128x256,...).
# Here we use soya.Image.get(filename) to load the image tutorials/data/images/block2.png.

# You can also use soya.open_image(filename) for loading an image from any file,
# or soya.image_from_pil(PIL.Image.Image) to turn a PIL image into a Soya image.

material.texture = soya.Image.get("block2.png")

# Creates the World that will contain the pyramid. We don't create the pyramid in the
# scene since we are going to compile the pyramid into a shape.

pyramid_world = soya.World()

# Creates the 5 faces of the pyramid (see lesson modeling-1).
# The third argument of the face constructor is the material ; it defaults to
# soya.DEFAULT_MATERIAL (a white material).

# For each vertex, we specify the texture coordinates (sometimes called u,v) as the
# 5th and 6th arguments of the constructor. They correspond to the tex_x and tex_y
# attributes of the vertex.

soya.Face(pyramid_world, [soya.Vertex(pyramid_world,  0.5, -0.5,  0.5, 0.0, 0.0),
													soya.Vertex(pyramid_world, -0.5, -0.5,  0.5, 0.0, 1.0),
													soya.Vertex(pyramid_world, -0.5, -0.5, -0.5, 1.0, 1.0),
													soya.Vertex(pyramid_world,  0.5, -0.5, -0.5, 1.0, 0.0),
													], material)

soya.Face(pyramid_world, [soya.Vertex(pyramid_world, -0.5, -0.5,  0.5, 0.0, 1.0),
													soya.Vertex(pyramid_world,  0.5, -0.5,  0.5, 0.0, 0.0),
													soya.Vertex(pyramid_world,  0.0,  0.5,  0.0, 1.0, 0.0),
													], material)

soya.Face(pyramid_world, [soya.Vertex(pyramid_world,  0.5, -0.5, -0.5, 1.0, 0.0),
													soya.Vertex(pyramid_world, -0.5, -0.5, -0.5, 1.0, 1.0),
													soya.Vertex(pyramid_world,  0.0,  0.5,  0.0, 0.0, 1.0),
													], material)

soya.Face(pyramid_world, [soya.Vertex(pyramid_world,  0.5, -0.5,  0.5, 0.0, 0.0),
													soya.Vertex(pyramid_world,  0.5, -0.5, -0.5, 1.0, 0.0),
													soya.Vertex(pyramid_world,  0.0,  0.5,  0.0, 0.0, 1.0),
													], material)

soya.Face(pyramid_world, [soya.Vertex(pyramid_world, -0.5, -0.5, -0.5, 1.0, 1.0),
													soya.Vertex(pyramid_world, -0.5, -0.5,  0.5, 0.0, 1.0),
													soya.Vertex(pyramid_world,  0.0,  0.5,  0.0, 1.0, 0.0),
													], material)

# Creates a cube.
# soya.cube generates texture coordinates automatically.

cube_world = soya.cube.Cube(None, material)

# Creates a subclass of Volume that permanently rotates.
# See the timemanagement-* lesson series for more info.

class RotatingVolume(soya.Volume):
	def advance_time(self, proportion):
		self.rotate_y(2.0 * proportion)

# Create a rotating volume in the scene, using the cube shape.

cube = RotatingVolume(scene, cube_world.shapify())
cube.x = -1.0
cube.rotate_x(30.0)

# Create a rotating volume in the scene, using the pyramid shape.

pyramid = RotatingVolume(scene, pyramid_world.shapify())
pyramid.x = 1.0
pyramid.rotate_x(30.0)

# Creates a light.

light = soya.Light(scene)
light.set_xyz(0.5, 1.0, 2.0)

# Creates a camera.

camera = soya.Camera(scene)
camera.set_xyz(0.0, 0.0, 3.0)
camera.set_xyz(-1.0, 0.0, 1.4)
soya.set_root_widget(camera)

soya.Idler(scene).idle()

