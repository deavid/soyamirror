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


# modeling-1: Faces : the pyramid
# requires the basic-* lessons.

# Models are usually designed in Blender and imported in Soya (as in lesson basic-1.py),
# but you can also create them from scratch, using Soya primitives. Learning this is
# the purpose of the modeling-* tutorial series.

# In this lesson, we'll build a pyramid, made of a quad base and 4 triangles.


# Imports and inits Soya (see lesson basic-1.py).

import sys, os, os.path, soya

soya.init()
soya.path.append(os.path.join(os.path.dirname(sys.argv[0]), "data"))

# Creates the scene.

scene = soya.World()

# Creates the World that will contain the pyramid. As previously stated, the
# pyramid is composed of 5 faces; this world is used to group those 5 faces
# (exactly like a Frame can be used in Tkinter to group different widgets).
# The pyramid's parent is the scene.

pyramid = soya.World(scene)

# Creates the first face, the quad base of the pyramid.
# The first argument of the Face constructor is the parent World (the pyramid),
# the second is the list of vertices and the third is the material.
# The number of vertices determines the Face's nature:
#  - 1: a plot
#  - 2: a line
#  - 3: a triangle
#  - 4: a quad
#  - +: a polygon

# The vertices is a list of Vertex object. A Vertex is a subclass of Point that can have
# some modeling attributes like colors or texture coordinates (we'll see them is further
# lessons) The first argument of the constructor is (again) the parent, and the three
# following one are the x, y and z coordinates.

# As 3D object, Point, Vector or Vertex have a parent too, though they are not
# considered as "children". The parent is used for automatic coordinates
# conversion, which will be detailed in a further lesson. Here, the coordinates
# are defined in the pyramid coordinate system.

# The order of the vertices in the list determines which side of the face is
# visible (for triangles, quads and polygons); you can get both side visible
# by setting the "double_sided" attribute to 1.

soya.Face(pyramid, [soya.Vertex(pyramid,  0.5, -0.5,  0.5),
                    soya.Vertex(pyramid, -0.5, -0.5,  0.5),
                    soya.Vertex(pyramid, -0.5, -0.5, -0.5),
                    soya.Vertex(pyramid,  0.5, -0.5, -0.5),
                    ])

# Similarly, creates the 4 triangles.
# Here, we create different vertices ; you can also use the same vertex when 2 vertices
# have the same coordinates and attributes. Both yields the same final result (including
# in performance).

soya.Face(pyramid, [soya.Vertex(pyramid, -0.5, -0.5,  0.5),
                    soya.Vertex(pyramid,  0.5, -0.5,  0.5),
                    soya.Vertex(pyramid,  0.0,  0.5,  0.0),
                    ])

soya.Face(pyramid, [soya.Vertex(pyramid,  0.5, -0.5, -0.5),
                    soya.Vertex(pyramid, -0.5, -0.5, -0.5),
                    soya.Vertex(pyramid,  0.0,  0.5,  0.0),
                    ])

soya.Face(pyramid, [soya.Vertex(pyramid,  0.5, -0.5,  0.5),
                    soya.Vertex(pyramid,  0.5, -0.5, -0.5),
                    soya.Vertex(pyramid,  0.0,  0.5,  0.0),
                    ])

soya.Face(pyramid, [soya.Vertex(pyramid, -0.5, -0.5, -0.5),
                    soya.Vertex(pyramid, -0.5, -0.5,  0.5),
                    soya.Vertex(pyramid,  0.0,  0.5,  0.0),
                    ])

# Saves the pyramid.
# First we set the filename attribute, and then call the save method.
# Soya automatically saves it in directory soya.path[0] + "/worlds",
# and adds a ".data" extention.

pyramid.filename = "pyramid"
pyramid.save()

# Rotates the pyramid (for a better view)

# Notice that we have saved the pyramid BEFORE the rotation, since we don't want
# to save the rotation.

pyramid.rotate_lateral(60.0)

# Creates a light.

light = soya.Light(scene)
light.set_xyz(1.0, 0.7, 1.0)

# Creates a camera.

camera = soya.Camera(scene)
camera.set_xyz(0.0, -0.6, 2.0)
soya.set_root_widget(camera)

soya.Idler(scene).idle()

