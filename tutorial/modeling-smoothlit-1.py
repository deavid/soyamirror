# Soya 3D tutorial
# Copyright (C) 2004 Jean-Baptiste LAMY
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


# modeling-smoothlit-1: Smooth lit : the sphere and the faceted ball

# Smooth-lit is one of the most important modeling attribute, but also one of the
# most difficult to understand. I hope this tutorial helps ;-)

# Smooth-lit is used for model that must look smooth, like sphere or characters.
# (if you have some 3D technical backgrounds, smooth-lit corresponds to per-vertex normal
# vector, instead of per-face normal vector).

# In Blender, smooth-lit corresponds to the "set smooth" and "set solid" buttons in
# the "link and materials" panel.


# Imports and inits Soya (see lesson basic-1.py).

import sys, os, os.path, soya, soya.sphere

soya.init()
soya.path.append(os.path.join(os.path.dirname(sys.argv[0]), "data"))

# Creates the scene.

scene = soya.World()

# The soya.sphere module contains a Sphere function that creates and returns a World
# with several faces inside, organized in a sphere (see soya.sphere.Sphere.__doc__
# for more info).
# By default, soya.sphere creates smooth-lit faces.

sphere_world = soya.sphere.Sphere()

# Creates another sphere.

faceted_ball_world = soya.sphere.Sphere()

# By default, faces are not smooth-lit, but soya.sphere adds the smooth-lit
# so we must remove it on the faceted ball.
# For each face in the faceted ball's children, we set its smooth_lit attributes to 0.

for face in faceted_ball_world.children:
  face.smooth_lit = 0

# Compiles sphere_world and faceted_ball_world into Shape.
# Creates a sphere Volume in the scene, using the compilation of sphere_word as Shape.
# Notice the use of World.shapify() to compile a World.

sphere = soya.Volume(scene, sphere_world.shapify())

# Moves the sphere on the left.

sphere.x = -1.2

# Does the same with the faceted ball.

faceted_ball = soya.Volume(scene, faceted_ball_world.shapify())
faceted_ball.x = 1.2

# Creates a light.

light = soya.Light(scene)
light.set_xyz(0.0, 0.7, 2.0)

# Creates a camera.

camera = soya.Camera(scene)
camera.set_xyz(0.0, 0.0, 3.5)
soya.set_root_widget(camera)

soya.Idler(scene).idle()

