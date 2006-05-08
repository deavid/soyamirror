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


# modeling-3: Vertex colors : the multicolor pyramid

# Models can be designed in Blender and then imported in Soya (as in lesson basic-1.py),
# but you can also create them from scratch, using Soya primitive. Learning this is
# the purpose of the modeling-* tutorial series.

# In this lesson, we'll build a pyramid, made of a quad base and 4 triangles.


# Imports and inits Soya.

import sys, os, os.path, soya

soya.init()
soya.path.append(os.path.join(os.path.dirname(sys.argv[0]), "data"))

# Creates the scene.

scene = soya.World()

# Creates the World that will contain the pyramid. We don't create the pyramid in the
# scene since we are going to compile the pyramid into a shape.

pyramid_world = soya.World()

# This time, we create the 5 vertices first. We do so to be sure each vertex will have
# the same color on the different faces it belongs to ; though you can still use the way
# we use in lesson modeling-1.py.
# The diffuse attribute of vertex is the color of the vertex ; in Soya, colors are
# (red, green, blue, alpha) tuples where all components are usually in the range 0.0-1.0.
# Set diffuse to None to disable vertex color.

# Here, the apex of the pyramid is in white, the base1 vertex is red, base2 is yellow,
# base3 is green and base4 is blue.

apex  = soya.Vertex(pyramid_world,  0.0,  0.5,  0.0, diffuse = (1.0, 1.0, 1.0, 1.0))
base1 = soya.Vertex(pyramid_world,  0.5, -0.5,  0.5, diffuse = (1.0, 0.0, 0.0, 1.0))
base2 = soya.Vertex(pyramid_world, -0.5, -0.5,  0.5, diffuse = (1.0, 1.0, 0.0, 1.0))
base3 = soya.Vertex(pyramid_world, -0.5, -0.5, -0.5, diffuse = (0.0, 1.0, 0.0, 1.0))
base4 = soya.Vertex(pyramid_world,  0.5, -0.5, -0.5, diffuse = (0.0, 0.0, 1.0, 1.0))

# Now, creates the face, using the vertices we creates above.

soya.Face(pyramid_world, [base1, base2, base3, base4])
soya.Face(pyramid_world, [base2, base1, apex])
soya.Face(pyramid_world, [base4, base3, apex])
soya.Face(pyramid_world, [base1, base4, apex])
soya.Face(pyramid_world, [base3, base2, apex])

# Compile the pyramid into a shape.

pyramid_shape = pyramid_world.shapify()

# Creates a subclass of Volume that permanently rotates.
# See the timemanagement-* lesson series for more info.

class RotatingVolume(soya.Volume):
  def advance_time(self, proportion):
    self.rotate_lateral(2.0 * proportion)

# Create a rotating volume in the scene, using the cube shape.

pyramid = RotatingVolume(scene, pyramid_shape)
pyramid.rotate_vertical(60.0)

# Creates a light.

light = soya.Light(scene)
light.set_xyz(1.0, -1.0, 2.0)

# Creates a camera.

camera = soya.Camera(scene)
camera.set_xyz(0.0, 0.0, 2.0)
soya.set_root_widget(camera)

soya.Idler(scene).idle()

