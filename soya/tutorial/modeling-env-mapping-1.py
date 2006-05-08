# Soya 3D tutorial
# Copyright (C) 2004 Thomas Paviot
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


# modeling-env-mapping-1: Environment Mapping

# Environment Mapping can be used to simulate reflection, using a particular texture
# called a "sphere map".
# You can create such texture from a panorama using e.g. the Polar coordinate
# effect of Gimp.


# Imports and inits Soya (see lesson basic-1.py).

import sys, os, os.path, soya, soya.sphere,soya.cube

soya.init()
soya.path.append(os.path.join(os.path.dirname(sys.argv[0]), "data"))

# Creates the scene.

scene = soya.World()

material = soya.Material()
material.environment_mapping = 1 # Specifies environment mapping is active
material.texture = soya.Image.get("sphere_map.jpg")# The textured sphere map

ball_world=soya.sphere.Sphere()
faceted_ball_world = soya.sphere.Sphere()
cube_world=soya.cube.Cube()

# Sets the material to each face
for face in faceted_ball_world.children:
  face.smooth_lit=0
  face.material=material
for face in ball_world.children:
  face.smooth_lit=1
  face.material=material
for face in cube_world.children:
  face.smooth_lit=0
  face.material=material
  
class RotatingVolume(soya.Volume):
  def advance_time(self, proportion):
    self.rotate_lateral(2.0 * proportion)
    

ball         = RotatingVolume(scene, ball_world        .shapify())
cube         = RotatingVolume(scene, cube_world        .shapify())
faceted_ball = RotatingVolume(scene, faceted_ball_world.shapify())
ball.x         = -1
ball.y         =  1
cube.x         =  1.2
cube.y         =  0.5
faceted_ball.y = -1


# Creates a light.

light = soya.Light(scene)
light.set_xyz(0.0, 0.7, 2.0)

# Creates a camera.

camera = soya.Camera(scene)
camera.set_xyz(0.0, 0.0, 3.5)
soya.set_root_widget(camera)

soya.Idler(scene).idle()

