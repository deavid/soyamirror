# -*- indent-tabs-mode: t -*-

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


# basic-3: Time management : a randomly moving sphere

# In this lesson, we'll create a spherish head that moves around randomly.
# You'll learn about time management (second part), vectors and coordinate-system
# conversion.


# Import the Soya module.

import sys, os, os.path, random, soya

soya.init()
soya.path.append(os.path.join(os.path.dirname(sys.argv[0]), "data"))

# Creates a scene.

scene = soya.World()


# Creates the randomly moving sphere's class. We call it head, because we'll use
# a head-like model.
# This class inherits from soya.Body, so it can have a model (the head).
		
class Head(soya.Body):
	
	# Redefine the constructor.
	
	def __init__(self, parent):
		
		# Calls the soya.Body constructor (remember, calling the super implementation is
		# always a good idea), and use the model called 'caterpillar_head'.
		
		soya.Body.__init__(self, parent, soya.Model.get("caterpillar_head"))
		
		# Adds a speed attribute to our new object.
		# The speed is a Vector object. A Vector is a mathematical object, used for
		# computation ; contrary to other object (Light, Camera, Body, World,...) it does not
		# modify the rendering in any way.
		
		# A vector is defined by a coordinate system and 3 coordinates (X, Y, Z) ; here the
		# speed is defined in 'self', i.e. the Head, and with coordinates 0.0, 0.0, -0.2.
		# Remember that in Soya, the -Z direction is the front. So the speed
		# This means that the speed vector is parallel to the direction the head is looking
		# at, and has a length of 0.2.
		
		self.speed = soya.Vector(self, 0.0, 0.0, -0.2)
		
		# The current rotation speed (around Y axis)
		
		self.rotation_speed = 0.0
		
	# Like advance_time, begin_round is called by the main_loop.
	# But contrary to advance_time, begin_round is called regularly, at the beginning of each
	# round ; thus it receive no 'proportion' argument.
	# Decision process should occurs in begin_round.
		
	def begin_round(self):
		
		# Calls the super implementation.
		
		soya.Body.begin_round(self)
		
		# Computes the new rotation speed: a random angle between -25.0 and 25.0 degrees.
		
		self.rotation_speed = random.uniform(-25.0, 25.0)
		
		# The speed vector doesn't need to be recomputed, since it is expressed in the Head
		# CoordSyst.
		
	# In advance_time, we make the head advance.
	
	def advance_time(self, proportion):
		soya.Body.advance_time(self, proportion)
		
		# Performs the rotation, taking into account the proportion argument.
		
		self.rotate_y(proportion * self.rotation_speed)
		
		# Moves the head according to the speed vector.
		# add_mul_vector is identical to: self.add_vector(proportion * self.speed), but faster.
		
		# The speed vector and the Head are not in the same coordinate system, but Soya automatically
		# performs the needed conversion.
		
		self.add_mul_vector(proportion, self.speed)


# Creates a Head in the scene.

head = Head(scene)

# Creates a light.

light = soya.Light(scene)
light.set_xyz(2.0, 5.0, 0.0)

# Creates a camera.

camera = soya.Camera(scene)
soya.set_root_widget(camera)
camera.set_xyz(0.0, 15.0, 15.0)

# Makes the camera looking at the head's initial position.
# The look_at method is another rotation method ; it makes any 3D object looking toward
# the given position (a 3D object or a Point), or in the given direction (if the argument
# is a Vector).

camera.look_at(head)

#import time; main_loop = soya.MainLoop(scene)
#for i in range(3):
#	for j in range(5):
#		time.sleep(0.1); main_loop.update()
#	soya.render(); soya.screenshot().resize((320, 240)).save(os.path.join(os.path.dirname(sys.argv[0]), "results", os.path.basename(sys.argv[0])[:-3] + "_%s.jpeg" % i))

soya.MainLoop(scene).main_loop()
