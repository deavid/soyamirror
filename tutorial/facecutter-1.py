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


# facecutter-1: Face cutter : a model beautifier

# The facecutter is a model beautifier : it automatically improves your model by increasing
# the number of faces.
# On smooth_lit faces, the facecutter performs interpolation, so as the faces really look
# smooth (as in this tuto).

# See soya.facecutter.cut.__doc__ for more info.


# Import the Soya module.

import sys, os, os.path, soya, soya.facecutter

soya.init()
soya.path.append(os.path.join(os.path.dirname(sys.argv[0]), "data"))

# Creates a scene.

scene = soya.World()

# Loads the sword model twice
# (we use 'load' instead of 'get' since get would have returned the same object :
# we want 2 DIFFERENT swords, since we are going to modify one of them)

sword1 = soya.World.load("sword")
sword2 = soya.World.load("sword")

# Cuts at least 80 triangles / quads of the second sword.
# Cut triangles / quads are replaced by two triangles, so this mean the sword will have at
# least 80 additionnal faces.

# You can also call the cut fonction by giving the maximum length of the face's edge ;
# every edge longer that the given value will be cut :
# soya.facecutter.cut(sword2, max_length = 1.0)

soya.facecutter.cut(sword2, 80)

# Creates 2 volumes, one for each sword.

volume1 = soya.Volume(scene, sword1.shapify())
volume1.set_xyz(-1.0, -0.5, 0.0)
volume1.rotate_vertical(90.0)
volume1.rotate_lateral (90.0)

volume2 = soya.Volume(scene, sword2.shapify())
volume2.set_xyz(1.0, -0.5, 0.0)
volume2.rotate_vertical(90.0)
volume2.rotate_lateral (90.0)

# Renders the scene in wireframe mode -- it's easier to see the facecutter action
# in wireframe.

soya.toggle_wireframe()

# Creates a light.

light = soya.Light(scene)
light.set_xyz(2.0, 5.0, 0.0)

# Creates a camera.

camera = soya.Camera(scene)
soya.set_root_widget(camera)
camera.set_xyz(0.0, 0.0, 3.0)

# Starts the main loop.

soya.Idler(scene).idle()
