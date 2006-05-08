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


# modeling-2: Shape : displaying two pyramids

# The pyramid model we create in the previous lesson was still in a scratchy form :
# all faces and vertices were python object, and were rendered individually, which
# implies a performance lost.

# In this lesson we'll see how to "compile" our pyramid model into a Shape,
# and how to use it in the same way we use the sword model in the basic-1.py lesson.


# Imports and inits Soya.

import sys, os, os.path, soya

soya.init()
soya.path.append(os.path.join(os.path.dirname(sys.argv[0]), "data"))

# Creates the scene.

scene = soya.World()

# Loads the pyramid model that we have created and saved in the modeling-basic-1.py
# lesson.
# We ask Soya for s Shape called "pyramid", though it does not exist ! Remember, we have
# created a World pyramid, not a Shape. In this case, Shape.get automatically loads the
# pyramid World, compiles it into a Shape, and saves the Shape in the "./shapes" directory
# in soya.path[0].
# Soya Shape compilation behaves like Python compilation of .py files in .pyc : whenever
# the World file is changed, Shape.get will recompile it automatically.
# You can also use the World.shapify() to compile a World into a Shape without saving it.

pyramid_model = soya.Shape.get("pyramid")

# Creates a Volume in the scene, that displays the pyramid.

pyramid1 = soya.Volume(scene, pyramid_model)

# Moves and rotates the pyramid (for a better view)

pyramid1.x = -0.7
pyramid1.rotate_lateral(60.0)

# Creates a second pyramid. Contrary to World, Shape model can be displayed several
# time at different position.
# Soya separates the model part (the Shape) from the position part (the Volume).

pyramid2 = soya.Volume(scene, pyramid_model)
pyramid2.x = 0.8
pyramid2.rotate_lateral(45.0)

# Creates a light.

light = soya.Light(scene)
light.set_xyz(1.0, 0.7, 1.0)

# Creates a camera.

camera = soya.Camera(scene)
camera.set_xyz(0.0, -0.6, 2.0)
soya.set_root_widget(camera)

soya.Idler(scene).idle()

