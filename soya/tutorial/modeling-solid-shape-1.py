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


# modeling-solid-shape-1: Solid Shape : the cutted cube

# Solid shapes are similar to simple shapes, but when they are cut by the camera front,
# plane the section is drawn, so as they appear as "solid / plain" and not "empty".

# Solid shapes are slower than simple shape, thus you should use them only
# when the shape is often cut by the camera. They are usefull for light effect, e.g.
# light cones,...


# Imports and inits Soya (see lesson basic-1.py).

import sys, os, os.path, soya, soya.cube

soya.init()
soya.path.append(os.path.join(os.path.dirname(sys.argv[0]), "data"))

# Creates the scene.

scene = soya.World()

# Creates a normal cube world

empty_cube_world = soya.cube.Cube()

# Creates a cube world that will yield a solid shape
# (solid shapes can only be used on shapes, NOT with faces)

solid_cube_world = soya.cube.Cube()
solid_cube_world.shapifier = soya.SolidShapifier()


# Creates a volume using the normal cube

empty_cube = soya.Volume(scene, empty_cube_world.shapify())
empty_cube.x = -1.0
empty_cube.rotate_y(45.0)
empty_cube.rotate_x(45.0)

# Creates a volume using the solid shape cube

solid_cube = soya.Volume(scene, solid_cube_world.shapify())
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

soya.Idler(scene).idle()

