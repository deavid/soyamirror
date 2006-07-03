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

"""soya.sdl_mixer4soya

A module for interfacing SDL_mixer and pysdl_mixer with the Soya 3D engine.
"""


import pysdl_mixer, os, os.path, time, sys
import soya

DISTANCE_ATTENUATION = 1.0

_BUFFERS  = {}
_LISTENER = None
_CAMERA   = None
_FRONT    = soya.Vector()
_DIR      = soya.Vector()
_INITED   = 0
_SOURCES  = []
_PENDING  = []
_CHANNELS = []

def set_body(body):
	"""Set the global body level to BODY (a float value between 0.0 and 1.0)."""
	pysdl_mixer.channel_body(-1, int(body * 255.0))
	
def find_file_in_path(filename):
	for p in soya.path:
		file = os.path.join(p, "sounds", filename)
		if os.path.exists(file): return file
	raise ValueError("Cannot find file named %s in soya.path!" % filename)

def init(camera, nb_channels = 16, freq = 44100, size = -16, stereo = 2, buffersize = 1024):
	"""init(camera, nb_channels = 16, freq = 44100, size = -16, stereo = 2, buffersize = 1024)

Inits OpenAL for Soya. CAMERA will be used to compute the position of the listener ;
it is not required that it is a Camera, though it is usually one."""
	
	global _LISTENER, _CAMERA, _INITED, _CHANNELS
	_CAMERA = camera
	_FRONT.__init__(_CAMERA, 0.0, 0.0, -1.0)
	_DIR  .__init__(_CAMERA, 0.0, 0.0,  0.0)
	if not _INITED:
		soya.BEFORE_RENDER.append(render)
		pysdl_mixer.init(freq, size, stereo, buffersize)
		pysdl_mixer.allocate_channels(nb_channels)
		_CHANNELS = range(nb_channels)
		_INITED = 1
		
def preload_sound(filename, async = 0):
	"""Pre-load sound FILENAME, in order to be able to play it immediately later.
If ASYNC, the sound is pre-loaded in an other thread.

The sound is NOT played!"""
	if not _BUFFERS.has_key(filename):
		if async:
			_BUFFERS[filename] = []
			import thread
			thread.start_new_thread(_load_async, (filename,))
			
		else:
			buffer = _BUFFERS[filename] = pysdl_mixer.Sample(find_file_in_path(filename))
			
			
class Source(object):
	def __init__(self, channel, sound, position, speed, looping, gain):
		self.channel  = channel
		self.sound    = sound
		self.position = position
		self.speed    = speed
		self.looping  = looping
		self.gain     = gain
		_SOURCES.append(self)
		self.update(0)
		if sound: sound.play(self.channel, -self.looping)
		
		self._first   = 1
		
	def stop(self):
		pysdl_mixer.halt_channel(self.channel)
		
	def update(self, may_remove = 1):
		if may_remove and not pysdl_mixer.channel_is_playing(self.channel): # Play ended
			_CHANNELS.append(self.channel)
			_SOURCES.remove(self)
			return
		
		if self.position:
			x, y, z = _CAMERA.transform(self.position)
			_DIR.set_xyz(x, 0.0, z)
			angle = _FRONT.angle_to(_DIR)
			if x < 0.0: angle = 360 - angle
			pysdl_mixer.channel_set_position(self.channel, int(angle), int(DISTANCE_ATTENUATION * self.position.distance_to(_CAMERA)))
			
class AsyncSource(Source):
	def __init__(self, channel, filename, position, speed, looping, gain):
		Source.__init__(self, channel, None, position, speed, looping, gain)
		self.canceled = 0
		
	def stop(self):
		if not self.sound: self.canceled = 1
		else: Source.stop(self)

	def update(self, may_remove = 1):
		if self.sound: Source.update(self, may_remove)
		
	def _loaded(self, sound):
		if self.canceled:
			_CHANNELS.append(self.channel)
			_SOURCES.remove(self)
		else:
			sound.play(self.channel)
			self.sound = sound


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

FILENAME can be Wave, Ogg Vorbis, MP3 or any other format supported by SDL_mixer file ;
the file is searched in {soya.path}/sounds/."""

	# Exit when sound not initialized
	if not _INITED: return
	
	if not _CHANNELS:
		print "* Soya PySDL_Mixer * Not enough channels for playing %s!" % filename
		return
	
	buffer = _BUFFERS.get(filename)
	if not buffer:
		if async:
			import thread
			source = AsyncSource(_CHANNELS.pop(), None, position, speed, looping, gain)
			_BUFFERS[filename] = [source._loaded]
			thread.start_new_thread(_load_async, (filename,))
			return source
		
		else:
			buffer = _BUFFERS[filename] = pysdl_mixer.Sample(find_file_in_path(filename))
			
	elif isinstance(buffer, list): # a list of waiter
		source = AsyncSource(_CHANNELS.pop(), None, position, speed, looping, gain)
		buffer.append(source._loaded)
		if not async: # Wait until loaded
			while isinstance(_BUFFERS[filename], list): time.sleep(0.01)
		return source
	
	return Source(_CHANNELS.pop(), buffer, position, speed, looping, gain)
	
def _load_async(filename):
	if sys.platform!="win32":
			os.nice(5)
	buffer = pysdl_mixer.Sample(find_file_in_path(filename))
	_PENDING.append((filename, buffer))


def render():
	"""render()

Update the sources's positions and speed.

This function is called before each Soya rendering."""
	for source in _SOURCES[:]: source.update()

	global _PENDING
	if _PENDING: # An async loading is finished ! We can now play it !
		for filename, buffer in _PENDING:
			for waiter in _BUFFERS[filename]: waiter(buffer)
			_BUFFERS[filename] = buffer
		_PENDING = []
		
