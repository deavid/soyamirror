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


# basic-savingfile-cerealizer-1: Save a file with cerealizer : save the rotating body

# This lesson saves the rotating model of lesson basic-2 into a file, using Cerealizer.
# Of course, you need to install Cerealizer (a secure Pickle-like module), from:
#
#            http://home.gna.org/oomadness/en/cerealizer/index.html


# Imports Soya and Cerealizer.

import sys, os, os.path, soya
import cerealizer


# Create a class of rotating body. See tuto basic-2 for more information on this.
# Notice that you can add attribute to your class, and they will be automatically saved.

class RotatingBody(soya.Body):
	def advance_time(self, proportion):
		soya.Body.advance_time(self, proportion)
		
		self.rotate_y(proportion * 5.0)

# Register the RotatingBody class as safe for Cerealizer.

cerealizer.register(RotatingBody)

# The cerealizer.register accept any Python classes. Wether a class inherits from a Soya class
# (such as, here, Body) or not, doesn't change anything.
# However, if your class inherits from World, Image, Model, Material, you have to do something
# special if you want to use YourClass.get() or YourClass.save(). This involves actually any
# SavedInAPath object, i.e. any object Soya saves in a specific subpath of soya.path.
#
# E.g. for a World, you should do:
#
#import soya.cerealizer4soya
#class YourWorld(soya.World):
#  pass
#cerealizer.register(YourWorld, soya.cerealizer4soya.SavedInAPathHandler(YourWorld))
#
# And then you can use YourWorld.get("filename") and so on.
#
# If you want the file to be saved in a different subdirectory of soya.path, e.g.
# data/your_worlds/ instead of data/worlds/, do:
#
#class YourWorld(soya.World):
#  DIRNAME = "your_worlds"



# The rest of the file is executed ONLY if this file is run as a script.
# This allows to import this file as a module, for defining the RotatingBody class.

if sys.argv[0].endswith("basic-savingfile-cerealizer-1.py"):
	# Inits Soya and sets the data directory.
	
	soya.init()
	soya.path.append(os.path.join(os.path.dirname(sys.argv[0]), "data"))
	
	# Sets the file format soya uses for saving file.
	#
	# The default configuration is to use cPickle for saving files, and to support loading
	# files saved either by cPickle or Cerealizer (if available).
	#
	# The complete syntax is set_file_format(saving_format, loading_format), where loading_format
	# is optional and can be either a single format, or a list of format.
	# There are currently 2 supported formats: cPickle and Cerealizer.
	# See set_file_format's __doc__ for more information.
	
	soya.set_file_format(cerealizer)

	# Creates the scene.

	scene = soya.World()

	# Loads the sword model.

	sword_model = soya.Model.get("sword")


	# Creates a rotating body in the scene, using the sword model.

	sword = RotatingBody(scene, sword_model)

	# Creates a light.

	light = soya.Light(scene)
	light.set_xyz(0.5, 0.0, 2.0)

	# Set the scene filename. It is just the name of the file, soya adds automatically
	# a directory path as well as a ".data" extention.

	scene.filename = "a_scene_with_a_rotating_body"

	# Saves the scene. The file is created in the <soya.path[0]>/worlds/ directory, here:
	#
	#          tutorial/data/worlds/a_scene_with_a_rotating_body.data
	#
	# The file is ALWAYS saved in the FIRST path listed in soya.path (which is, as sys.path,
	# a list of path).
	#
	# Soya separates the "set filename" and the "save" step, because it allows you to set the
	# filename once, and then to save the object several times without having to remind its
	# filename.
	#
	# Notice that, while saving the scene, Soya will save a reference to the "sword" Model we
	# have used above. However, the data of this Model are NOT dupplicated.

	scene.save()

	# Creates a camera.
	#
	# For technical reasons, camera are not saveable yet. This is not really a problem since the
	# camera is not really scene-dependent by rather configuration-dependent.
	# We thus add the camera AFTER saving the scene.

	camera = soya.Camera(scene)
	camera.z = 3.0
	soya.set_root_widget(camera)

	soya.MainLoop(scene).main_loop()

	# That's all -- after running this tutorial, you should have a
	# tutorial/data/worlds/a_scene_with_a_rotating_body.data file. The easiest way to verify
	# that this file is REALLY a Cerealizer file, is to open the file and check if it begins
	# by the magic string "cereal1".
