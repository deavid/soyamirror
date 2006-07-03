# -*- indent-tabs-mode: t -*-

# Soya
# Copyright (C) 2005 Jean-Baptiste LAMY -- jiba@tuxfamily.org
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

"""soya.pygame_sound4soya

A module for interfacing PyGame sound module with the Soya 3D engine.

Note: it seems that PyGame works much better under windows than OpenAL or SDL_mixer.
"""


import pygame, pygame.mixer, os, os.path, time, sys
import soya

DISTANCE_ATTENUATION = 10.0

_BUFFERS  = {}
_LISTENER = None
_CAMERA   = None
_FRONT    = soya.Vector()
_DIR      = soya.Vector()
_INITED   = 0
_SOURCES  = []

def set_body(body):
	"""Set the global body level to BODY (a float value between 0.0 and 1.0)."""
	pysdl_mixer.channel_body(-1, int(body * 255.0))
	
def find_file_in_path(filename):
	for p in soya.path:
		file = os.path.join(p, "sounds", filename)
		if os.path.exists(file): return file
	raise ValueError("Cannot find file named %s in soya.path!" % filename)

def init(camera, freq = 44100, size = -16, stereo = 2, buffersize = 1024):
	"""init(camera, freq = 44100, size = -16, stereo = 2, buffersize = 1024)

Inits OpenAL for Soya. CAMERA will be used to compute the position of the listener ;
it is not required that it is a Camera, though it is usually one."""
	
	global _LISTENER, _CAMERA, _INITED, _CHANNELS
	_CAMERA = camera
	_FRONT.__init__(_CAMERA, 0.0, 0.0, -1.0)
	_DIR  .__init__(_CAMERA, 0.0, 0.0,  0.0)
	if not _INITED:
		soya.BEFORE_RENDER.append(render)
		pygame.mixer.init(freq, size, stereo, buffersize)
		_INITED = 1
		
def preload_sound(filename, async = 0):
	"""Pre-load sound FILENAME, in order to be able to play it immediately later.
If ASYNC, the sound is pre-loaded in an other thread.

The sound is NOT played!"""
	# Not yet implemented; not really required as PyGame / SDL load sounds quickly.
	pass

class Source(object):
	def __init__(self, sound, position, speed, looping, gain):
		self.sound    = sound
		self.position = position
		self.speed    = speed
		self.looping  = looping
		self.gain     = gain
		self.channel = None
		_SOURCES.append(self)
		self.update(0)
		if sound: self.channel = sound.play(-self.looping)
		
		self._first   = 1
		
	def stop(self):
		if self.channel: self.channel.stop()
		
	def update(self, may_remove = 1):
		if may_remove and ((not self.channel) or (not self.channel.get_busy())): # Play ended
			_SOURCES.remove(self)
			return
		
		if self.position and self.channel:
			x, y, z = _CAMERA.transform(self.position)
			#d = self.position.distance_to(_CAMERA) / DISTANCE_ATTENUATION
			#self.channel.set_body(1.0 - d)
			d = self.position.distance_to(_CAMERA)
			self.channel.set_body(DISTANCE_ATTENUATION / d)
			
			
class AsyncSource(Source):
	# Not yet implemented; not really required as PyGame / SDL load sounds quickly.
	pass

def play(filename, position = None, speed = None, looping = 0, async = 0, gain = 1.0):
	"""play(filename, position = None, speed = None, looping = 0, async = 0, gain = 1.0)

Plays sound FILENAME, at the given POSITION and SPEED (for Doppler effect).
Sound file's data are cached for more efficiency.

If POSITION and SPEED are omitted, the sound is played without 3D features.
If SPEED is ignored (it is present for compatibility with soya.openal4soya).
If LOOPING is true, the sound is played in loop.
If ASYNC is true, the sound is loading asynchronously (in a new thread), and
thus it does not start immediately. ASYNC has not effect if the sound is
already loaded (=cached). Usefull for OggVorbis file (take a while to
uncompress).

FILENAME can be Wave, Ogg Vorbis, MP3 or any other format supported by PyGame / SDL_mixer;
the file is searched in {soya.path}/sounds/."""

	# Exit when sound not initialized
	if not _INITED: return
	
	buffer = _BUFFERS.get(filename)
	if not buffer:
		buffer = _BUFFERS[filename] = pygame.mixer.Sound(find_file_in_path(filename))
		
	return Source(buffer, position, speed, looping, gain)
	

def render():
	"""render()

Update the sources's positions and speed.

This function is called before each Soya rendering."""
	for source in _SOURCES[:]: source.update()
		
