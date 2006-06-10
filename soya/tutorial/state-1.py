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


# state-1: CoordSystState object

# In this lesson, you'll learn how to use CoordSystState to interpolate between
# two State (position, orientation and scaling) of a 3D object.


import sys, os, os.path, soya, soya.cube

soya.init()
soya.path.append(os.path.join(os.path.dirname(sys.argv[0]), "data"))

# Creates the scene.

scene = soya.World()


# Create a volume class that interpolates between two States.

class InterpolatingVolume(soya.Volume):
	def __init__(self, parent = None, shape = None):
		soya.Volume.__init__(self, parent, shape)
		
		# Create two State objects, based on the current position of 'self'.
		
		self.state1 = soya.CoordSystState(self)
		self.state2 = soya.CoordSystState(self)
		
		self.factor = 0.0
		
	def advance_time(self, proportion):
		self.factor += 0.01 * proportion
		
		# interpolate(state1, state2, factor) interpolates between state1 and state2.
		
		self.interpolate(self.state1, self.state2, self.factor)
		


volume = InterpolatingVolume(scene, soya.cube.Cube(None).shapify())

# Moves, rotates and scales the States.
# Notice that States have the Soya's usual positioning method (actually State even inherit
# from CoordSyst).

volume.state1.set_xyz(-1.0, -0.5, 0.0)

volume.state2.set_xyz(1.0, 1.0, -1.0)
volume.state2.rotate_y(90.0)
volume.state2.scale(3.0, 1.0, 1.0)


# Adds a light.

light = soya.Light(scene)
light.set_xyz(0.0, 0.2, 1.0)

# Creates a camera.

camera = soya.Camera(scene)
camera.set_xyz(0.0, 0.0, 4.0)
camera.fov = 100.0
soya.set_root_widget(camera)


# Main loop

soya.Idler(scene).idle()


# TODO / exercice : turn this demo into a puzzle game !
