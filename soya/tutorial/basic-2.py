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


# basic-2: Time management : a rotating 3D model

# This lesson is the same as basic-1.py, except that the model rotates.

# You'll learn about time management and rotation.

# Basic Soya's rotation functions are :
#
# rotate_x : rotates around the X axis
# rotate_y : rotates around the Y axis (=in the horizontal plane)
# rotate_z : rotates around the Z axis


# Imports and inits Soya (see lesson basic-1.py).

import sys, os, os.path, soya

soya.init()
soya.path.append(os.path.join(os.path.dirname(sys.argv[0]), "data"))

# Creates the scene.

scene = soya.World()

# Loads the sword model.

sword_model = soya.Model.get("sword")


# Create a class of rotating body. Soya if fully Object Oriented, and almost all
# Soya classes can be extended.
# Here, our class inherits from soya.Body, and so can display a model.

class RotatingBody(soya.Body):
	
	# The MainLoop calls repeatedly the advance_time method, for all object in the scene.
	# To make the body rotate, we just have to override this method.
	# In Soya, the time unit is the "round" ; one round is 30 milliseconds (default value).
	# The proportion argument of advance_time is the proportion of a round that has occured:
	# e.g. 0.3 means that 30% of a round has occured since last call, i.e. 9 milliseconds.
	
	# advance_time should be limited to animation code, and not decision code.  We'll see
	# another method for decision stuff in basic-3.py.
	
	def advance_time(self, proportion):

		# Calls the super implementation of advance_time. This IS NEEDED, as some Soya object
		# already have an advance_time method.
		
		soya.Body.advance_time(self, proportion)
		
		# Rotates the object around Y axis. The angle is proportional to proportion because
		# the more time has been spent, the more we want to rotate, in order to achieve a
		# smooth animation.
		
		# Almost every rotations or moves that occurs in advance_time should be proportional
		# to proportion.
		
		self.rotate_y(proportion * 5.0)

# Creates a rotating body in the scene, using the sword model.

sword = RotatingBody(scene, sword_model)

# Creates a light.

light = soya.Light(scene)
light.set_xyz(0.5, 0.0, 2.0)

# Creates a camera.

camera = soya.Camera(scene)
camera.z = 3.0
soya.set_root_widget(camera)

soya.MainLoop(scene).main_loop()

