# -*- indent-tabs-mode: t -*-

# Soya 3D tutorial
# Copyright (C) 2005 Jean-Baptiste LAMY
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


# sound-sdl_mixer-1: pseudo-3D sound with SDL_mixer

# You need to install PySDL_Mixer (http://gna.org/projects/pysdlmixer/)
#
# You may need to stop artsd daemon too (typically for KDE user)
#
# The tuto draws a moving cube that play a 3D sound.
# Notice that all Soya sound modules have the same interface.

import os, os.path, sys

import soya, soya.cube as cube

soya.init()

# Define the data directories ; sounds are searched in sounds/ subdirectory.

soya.path.append(os.path.join(os.path.dirname(sys.argv[0]), "data"))

scene = soya.World()

camera = soya.Camera(scene)
camera.y = 0.3
camera.z = 2.0

soya.set_root_widget(camera)


import soya.sdl_mixer4soya as sound

# Inits the sound module, and pass to it the location of the listener
# (usually the camera).

sound.init(camera)

# Create a cube.

import math
class MovingBody(soya.Body):
	def __init__(self, parent, model):
		soya.Body.__init__(self, parent, model)
		self.angle = 3.0
		
	def advance_time(self, proportion):
		self.angle += 0.04 * proportion
		self.set_xyz(100.0 * math.cos(self.angle), 0.0, 100.0 * math.sin(self.angle))

cube = MovingBody(scene, cube.Cube().to_model())

# The cube continuously play a sound
#
# The parameters for play are:
#  - the sound file name (supported format: Wave, Ogg Vorbis, MP3,...)
#  - the sound position
#  - the sound speed (a Vector, IGNORED (it is present for compatibility with soya.openal4soya))
#    the speed is automatically computed if omitted
#    the speed is not used by SDL_mixer, since it doesn't provide Doppler effect.
#  - 1 for looping (0 else)
#  - 1 to load the sound asynchronously (if not already cached)

sound.play("test.wav", cube, None, 1)


light = soya.Light(scene)
light.set_xyz(1.5, 2.0, 2.2)

soya.MainLoop(scene).main_loop()
