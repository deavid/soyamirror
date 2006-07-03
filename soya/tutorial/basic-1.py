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


# basic-1: Setting up : displaying a 3D model

# This is the first lesson of the Soya tutorial.
# This lesson just sets up everything and display a 3D model. In order to do that,
# we need :
#  - a model,
#  - a light,
#  - a camera,
#  - a scene, to group the three other 3D objects.


# Imports sys, os modules and the Soya module.

import sys, os, os.path, soya

# Initializes Soya (creates and displays the 3D window).

soya.init()

# Add the path "tutorial/data" to the list of soya data path. When soya loads some data,
# like a model or a texture, it always searches the data in soya.path.
# soya.path behaves like Python's sys.path.
# Soya's data directory should be organized as following :
#   ./images    : the image file
#   ./materials : the materials (including textures, optimized forms of images)
#   ./worlds    : the model
#   ./models    : the optimized model

# Notice the use of sys.argv to get the directory where this script lives.

soya.path.append(os.path.join(os.path.dirname(sys.argv[0]), "data"))

# Creates a scene. The scene is a World, which contains all the 3D elements we are
# about to render. A World is a 3D object that can contain other 3D objects (including
# other worlds) ; think to World as a group of 3D objects.

scene = soya.World()

# Loads the sword model (from file "tutorial/data/models/sword.data").

# A model is an optimized model ; the sword model we use here was designed in Blender.

# Model.get is a static method that returns the object of the corresponding filename,
# and loads it if needed, i.e. if you call get a second time, it will return the same
# object instead of loading it again.
# Any dependancy of the model (e.g. materials) are loaded too.

sword_model = soya.Model.get("sword")

# Create the model.
# A Body displays a model. The first argument of the Body constructor is the
# parent of the new body ; here we put the body in the scene. The parent must be
# a World or a World derivative (or None).
# (this is a convention, similarly to Tkinter, where the first argument of a
# widget's constructor is the master).
# The second argument of the Body constructor is the model : our sword model.

sword = soya.Body(scene, sword_model)

# The default position is 0.0, 0.0, 0.0
# To view it better, we moves the sword to the right.

sword.x = 1.0

# Rotates the sword on the Y axis, of 60.0 degrees.
# (in Soya, all angles are in degrees).

sword.rotate_y(90.0)


# Creates a light in the scene (same convention: the first argument of the
# constructor is the parent) and moves it to (1.5, 2.0, 0.2).

light = soya.Light(scene)
light.set_xyz(0.5, 0.0, 2.0)

# Creates a camera in the scene and moves it to z = 5.0. The camera looks in the
# -Z direction, so, in this case, towards the cube.
#
# When relevant, Soya always considers the X direction to be on the right,
# the Y direction to be on the top and the -Z to be the front.
# (Using -Z for front seems odd, but using Z for front makes all coordinate systems
# indirect, which is a mathematical nightmare !)

camera = soya.Camera(scene)
camera.z = 2.0

# Say to Soya that the camera is what we want to be rendered.

soya.set_root_widget(camera)

# Uncomment this line to save a 320x240 screenshot in the results directory.

#soya.render(); soya.screenshot().resize((320, 240)).save(os.path.join(os.path.dirname(sys.argv[0]), "results", os.path.basename(sys.argv[0])[:-3] + ".jpeg"))

# Creates an 'MainLoop' for the scene, and launch it.
# The MainLoop is the object that manages the Soya's mainloop. It take care of :
#  - looping
#  - regulating the frame rate to 40 FPS
#  - smoothing the animation
#  - computing FPS
#  - rendering the screen

soya.MainLoop(scene).main_loop()


