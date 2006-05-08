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


# sound-openal-1: real 3D sound with OpenAL

# You need to install OpenAL (http://openal.org) and PyOpenAL
# (http://home.gna.org/oomadness/en/pyopenal/index.html)
#
# You may need to stop artsd daemon too (typically for KDE user)
#
# The tuto draws a moving cube that play a 3D sound.
# Notice that the two sound modules soya.openal4soya and soya.sdl_mixer4soya have the
# same interface.

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


import soya.openal4soya as sound

# Inits the sound module, and pass to it the location of the listener
# (usually the camera).

sound.init(camera)

# You can set the volume level with set_volume

sound.set_volume(1000000000000000000000000.0)

# Create a cube.

import math
class MovingVolume(soya.Volume):
  def __init__(self, parent, shape):
    soya.Volume.__init__(self, parent, shape)
    self.angle = 3.0
    
  def advance_time(self, proportion):
    self.angle += 0.04 * proportion
    self.set_xyz(100.0 * math.cos(self.angle), 0.0, 100.0 * math.sin(self.angle))

cube = MovingVolume(scene, cube.Cube().shapify())

# The cube continuously play a sound
#
# The parameters for play are:
#  - the sound file name (supported format: Wave, and Ogg Vorbis if PyVorbis is installed)
#  - the sound position
#  - the sound speed (a Vector, optional)
#    the speed is automatically computed if omitted
#    the speed is not used by SDL_mixer, since it doesn't provide Doppler effect.
#  - 1 for looping (0 else)
#  - 1 to load the sound asynchronously (if not already cached)

sound.play("test.wav", cube, None, 1)


light = soya.Light(scene)
light.set_xyz(1.5, 2.0, 2.2)

soya.Idler(scene).idle()
