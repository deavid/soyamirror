# -*- indent-tabs-mode: t -*-

# Soya 3D tutorial
# Copyright (C) 2006 Jean-Baptiste LAMY
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


# sound-1: real 3D sound

# You may need to stop artsd daemon (typically for KDE user)
#
# The tuto draws a moving cube that play a 3D sound.

import os, os.path, sys

import soya, soya.cube as cube

# Initializes Soya with 3D sound support.
# See soya.init.__doc__ for optional sound-related argument to init.

soya.init(sound = 1)

# Uses set_sound_volume to define the sound volume (1.0 is the default;
# values range from 0.0 to 1.0).

soya.set_sound_volume(1.0)

# Define the data directories ; sounds are searched in sounds/ subdirectory.

soya.path.append(os.path.join(os.path.dirname(sys.argv[0]), "data"))

scene = soya.World()

camera = soya.Camera(scene)
camera.set_xyz(0.0, 0.0, 0.0)
#camera.rotate_lateral(180.0)
soya.set_root_widget(camera)

# Uses this camera as the sound listener.
# The default value of Camera.listen_sound is 1, thus this line is optional.
# However, if you are using several camera, you'll probably want to use only one of them
# as sound listener. This can be done by setting Camera.listen_sound to 0.

camera.listen_sound = 1

# Create a cube.

import math
class NoisyCube(soya.World):
	def __init__(self, parent, shape):
		soya.World.__init__(self, parent, shape)
		self.angle = 3.0
		
	def advance_time(self, proportion):
		soya.check_al_error()
		
		soya.World.advance_time(self, proportion)
		
		soya.check_al_error()
		
		self.angle += 0.04 * proportion
		self.set_xyz(5.0 * math.cos(self.angle), 0.0, 5.0 * math.sin(self.angle))
		#self.set_xyz(0.0, 0.0, 0.0)
		#self.set_xyz(10.0, 0.0, 0.0)
		
		
cube = NoisyCube(scene, cube.Cube().shapify())


# Gets the sound called "test.wav" from the data directory.

sound = soya.Sound.get("test.wav")

# Creates a sound player in the cube.
# Sound players have the following attributes (which can be passed to the constructor, too):
#   - sound      : the sound currently played (read-only)
#   - loop       : if true, the sound restarts from the beginning when it ends; default is false
#   - play_in_3D : if true, the sound is played as a 3D sound; if false, as a 2D sound. Notice that OpenAL cannot play stereo sound in 3D.
#   - gain       : the volume (default 1.0)
#   - auto_remove: if true (default), the SoundPlayer is automatically removed when the sound ends (excepted in cases of looping!)

sound_player = soya.SoundPlayer(cube, sound, loop = 1)



light = soya.Light(scene)
light.set_xyz(1.5, 2.0, 2.2)

soya.Idler(scene).idle()
