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


# modeling-solid-model-1: Solid Model : the cutted cube

# Solid models are similar to simple models, but when they are cut by the camera front,
# plane the section is drawn, so as they appear as "solid / plain" and not "empty".

# Solid models are slower than simple model, thus you should use them only
# when the model is often cut by the camera. They are usefull for light effect, e.g.
# light cones,...


# Imports and inits Soya (see lesson basic-1.py).

import sys, os, os.path, soya, soya.cube

soya.init()
soya.path.append(os.path.join(os.path.dirname(sys.argv[0]), "data"))

# Creates the scene.

scene = soya.World()

# Creates a normal cube world

empty_cube_world = soya.cube.Cube()

# Creates a cube world that will yield a solid model
# (solid models can only be used on models, NOT with faces)

solid_cube_world = soya.cube.Cube()
solid_cube_world.model_builder = soya.SolidModelBuilder()


# Creates a body using the normal cube

empty_cube = soya.Body(scene, empty_cube_world.to_model())
empty_cube.x = -1.0
empty_cube.rotate_y(45.0)
empty_cube.rotate_x(45.0)

# Creates a body using the solid model cube

solid_cube = soya.Body(scene, solid_cube_world.to_model())
solid_cube.x =  1.0
solid_cube.rotate_y(45.0)
solid_cube.rotate_x(45.0)


# Creates a light.

light = soya.Light(scene)
light.set_xyz(1.0, 0.7, 1.0)

# Creates a camera.

camera = soya.Camera(scene)
camera.set_xyz(0.0, 0.0, 3.0)

# Increases the camera's front plane, in order to cut the two cubes.

camera.front = 2.5

soya.set_root_widget(camera)

soya.MainLoop(scene).main_loop()

