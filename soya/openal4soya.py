# -*- indent-tabs-mode: t -*-

# Soya
# Copyright (C) 2003 Jean-Baptiste LAMY -- jiba@tuxfamily.org
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

"""soya.openal4soya

A module for interfacing OpenAL and PyOpenAL with the Soya 3D engine.

The DOPPLER_EFFECT_FACTOR constant can be used to
increase / decrease the Doppler effect."""


import pyopenal, os, os.path, sys
import soya
from pyopenal import *

_BUFFERS  = {}
_LISTENER = None
_CAMERA   = None
_INITED   = 0

def find_file_in_path(filename):
	for p in soya.path:
		file = os.path.join(p, "sounds", filename)
		if os.path.exists(file): return file
	raise ValueError("Cannot find file named %s in soya.path!" % filename)

def set_body(body = 1.0):
	"""Set the global body level to BODY (a float value between 0.0 and 1.0).
(though, it seems that setting body to 0.2 or to 1.0 is quite the same)."""
	_LISTENER.gain = body
	
def init(camera, freq = 44100):
	"""init(camera, freq = 44100)

Inits OpenAL for Soya. CAMERA will be used to compute the position of the listener ;
it is not required that it is a Camera, though it is usually one."""
	
	
	global _LISTENER, _CAMERA, _INITED
	if not _INITED:
		soya.BEFORE_RENDER.append(render)
		pyopenal.init()
		if not _LISTENER:
			try:
				_LISTENER          = Listener(freq)
				_LISTENER.position = (0.0, 0.0,  0.0)
				_LISTENER.at       = (0.0, 0.0, -1.0)
				_LISTENER.up       = (0.0, 1.0,  0.0)
				_INITED = 1
			except:
				print "Can't create listener for audio device, sound will be disabled"
		
	_CAMERA = camera

_SOURCES_POS_SPEED = []
_PENDING = []

DISTANCE_ATTENUATION  = 7.0
DOPPLER_EFFECT_FACTOR = 1.0
DOPPLER_EFFECT_FACTOR = 0.0001

def preload_sound(filename, async = 0):
	"""Pre-load sound FILENAME, in order to be able to play it immediately later.
If ASYNC, the sound is pre-loaded in an other thread.

The sound is NOT played!"""
	if not _BUFFERS.has_key(filename):
		if async:
			import thread
			thread.start_new_thread(_play_async, (None, filename, None, None, 1.0))
			
		else:
			if   filename.endswith(".wav"): buffer = _BUFFERS[filename] = WaveBuffer     (find_file_in_path(filename))
			elif filename.endswith(".ogg"): buffer = _BUFFERS[filename] = OggVorbisBuffer(find_file_in_path(filename))
			else: raise ValueError("Unsupported file format %s!" % filename)
			

def play(filename, position = None, speed = None, looping = 0, async = 0, gain = 1.0):
	"""play(filename, position = None, speed = None, looping = 0, async = 0)

Plays sound FILENAME, at the given POSITION and SPEED (for Doppler effect).
Sound file's data are cached for more efficiency.

If POSITION and SPEED are omitted, the sound is played without 3D features.
If SPEED is omitted, it is automatically computed.
If LOOPING is true, the sound is played in loop.
If ASYNC is true, the sound is loading asynchronously (in a new thread), and
thus it does not start immediately. ASYNC has not effect if the sound is
already loaded (=cached). Usefull for OggVorbis file (take a while to
uncompress).

FILENAME can be Wave or Ogg Vorbis file (need PyOgg and PyVorbis) ; the file
is searched in {soya.path}/sounds/."""

	# Exit when sound not initialized
	if not _INITED:
		return
	
	buffer = _BUFFERS.get(filename)
	if not buffer:
		if async:
			import thread
			source         = _AsyncSource()
			source.looping = looping
			thread.start_new_thread(_play_async, (source, filename, position, speed, gain))
			return source
		
		else:
			if   filename.endswith(".wav"): buffer = _BUFFERS[filename] = WaveBuffer     (find_file_in_path(filename))
			elif filename.endswith(".ogg"): buffer = _BUFFERS[filename] = OggVorbisBuffer(find_file_in_path(filename))
			
	source          = Source()
	source.buffer   = buffer
	source.looping  = looping
	source.gain     = gain * 20.0 # This is to keep a similar body level with soya.sdl_mixer4soya
	
	_SOURCES_POS_SPEED.append((source, position, speed))
	
	if position:
		source.position = _CAMERA.transform(position)
		
		if speed:
			source.velocity = _CAMERA.transform(speed)
			
	source.play()
	
	return source

def _play_async(source, filename, position, speed, gain):
	# Exit when sound not initialized
	if not _INITED:
		return
	if sys.platform!="win32":
		os.nice(5)
	if   filename.endswith(".wav"): format, data, freq = wave_data      (find_file_in_path(filename))
	elif filename.endswith(".ogg"): format, data, freq = ogg_vorbis_data(find_file_in_path(filename))
	if source: _PENDING.append((source, filename, format, data, freq, position, speed, gain))

class _AsyncSource(Source):
	def __init__(self):
		Source.__init__(self)
		self.canceled = 0
		
	def stop(self):
		Source.stop(self)
		self.canceled = 1


import time

_LAST_TIME = time.time()
def render():
	"""render()

Update the sources's positions and speed.

This function is called before each Soya rendering."""
	global _LAST_TIME
	now = time.time()
	dt = (now - _LAST_TIME) / DOPPLER_EFFECT_FACTOR
	_LAST_TIME = now
	
	i = 0
	while i < len(_SOURCES_POS_SPEED):
		source, position, speed = _SOURCES_POS_SPEED[i]
		
		if source.get_state() == AL_STOPPED: del _SOURCES_POS_SPEED[i]
		
		else:
			i += 1
			if position:
				oldpos = source.position
				pos    = _CAMERA.transform(position)
				pos    = (
					pos[0] * DISTANCE_ATTENUATION,
					pos[1] * DISTANCE_ATTENUATION,
					pos[2] * DISTANCE_ATTENUATION,
					)
				source.position = pos
				if speed:
					source.velocity = _CAMERA.transform(speed)
				elif dt:
					source.velocity = (
						(pos[0] - oldpos[0]) / dt,
						(pos[1] - oldpos[1]) / dt,
						(pos[2] - oldpos[2]) / dt,
						)
					
	if _PENDING: # An async loading is finished ! We can now play it !
		source, filename, format, data, freq, position, speed, gain = _PENDING.pop()
		
		buffer = _BUFFERS[filename] = Buffer()
		buffer.set_data(format, data, freq)
		
		source.buffer = buffer
		_SOURCES_POS_SPEED.append((source, position, speed))
		
		if position:
			source.position = _CAMERA.transform(position)
			
			if speed:
				source.velocity = _CAMERA.transform(speed)
				
		if not source.canceled: source.play()
		
		
