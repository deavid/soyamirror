# -*- indent-tabs-mode: t -*-

# Soya 3D
# Copyright (C) 2006 Jean-Baptiste LAMY -- jiba@tuxfamily.org
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


class ALError(StandardError):
	pass


def check_al_error():
	"""check_al_error()

Checks for OpenAL errors, and raise an ALError if so."""
	cdef ALenum error
	error = alGetError()
	if error != AL_NO_ERROR:
		if   error == AL_INVALID_NAME     : s = "AL_INVALID_NAME"
		elif error == AL_INVALID_ENUM     : s = "AL_INVALID_ENUM"
		elif error == AL_INVALID_VALUE    : s = "AL_INVALID_VALUE"
		elif error == AL_INVALID_OPERATION: s = "AL_INVALID_OPERATION"
		elif error == AL_OUT_OF_MEMORY    : s = "AL_OUT_OF_MEMORY"
		print s
		raise ALError(s)

	error = alcGetError(_device)
	if error != ALC_NO_ERROR:
		if   error == ALC_INVALID_DEVICE  : s = "ALC_INVALID_DEVICE"
		elif error == ALC_INVALID_CONTEXT : s = "ALC_INVALID_CONTEXT"
		elif error == ALC_INVALID_ENUM    : s = "ALC_INVALID_ENUM"
		elif error == ALC_INVALID_VALUE   : s = "ALC_INVALID_VALUE"
		elif error == ALC_OUT_OF_MEMORY   : s = "ALC_OUT_OF_MEMORY"
		print s
		raise ALError(s)
	
	

cdef int _SOUND_INITED
_SOUND_INITED = 0

cdef ALCdevice* _device
_device = NULL

cdef ALCcontext* _context
_context = NULL

cdef ALfloat _reference_distance

#def init_sound(ear, device_names = "'( ( devices '( native esd sdl alsa arts null ) ) )", frequency = 44100, doppler_factor = 0.01):
cdef void _init_sound(device_names, int frequency, float reference_distance, float doppler_factor):
	global _SOUND_INITED
	global _device
	global _context
	global _reference_distance
	cdef char* s, s2
	cdef int attrs[6]
	if _SOUND_INITED == 0:
		
		_device = alcOpenDevice(PyString_AS_STRING(device_names))
		
		if _device == NULL:
			raise RuntimeError("Cannot create an OpenAL device!")
		
		attrs[0] = ALC_FREQUENCY
		attrs[1] = frequency
		attrs[2] = ALC_INVALID
		_context = alcCreateContext(_device, attrs)
		
		if _context == NULL:
			raise RuntimeError("Cannot create an OpenAL context!")
		
		alcMakeContextCurrent(_context)
		
		alDopplerFactor(doppler_factor)
		_reference_distance = reference_distance
		
		_SOUND_INITED = 1
		
		s  = alGetString(AL_VERSION   ); print "* Using OpenAL %s" % s
		s  = alGetString(AL_RENDERER  ); print "*   - renderer  : %s" % s
		s  = alGetString(AL_VENDOR    ); print "*   - vendor    : %s" % s
		#s  = alGetString(AL_EXTENSIONS); print "*   - extension : %s" % s
		

def set_sound_volume(float volume):
	"""set_sound_volume(volume)

Sets the global sound volume. VOLUME is a value between 0.0 (no sound) and 1.0 (default)."""
	if _SOUND_INITED == 0: raise RuntimeError("Sound has not been initialized yet, call soya.init(sound = 1) before!")
	alListenerf(AL_GAIN, volume)

def get_sound_volume():
	"""get_sound_volume() -> float

Returns the global sound volume, a value between 0.0 (no sound) and 1.0 (default)."""
	cdef float x
	if _SOUND_INITED == 0: raise RuntimeError("Sound has not been initialized yet, call soya.init(sound = 1) before!")
	alGetListenerf(AL_GAIN, &x)
	return x


cdef float _ear_old_pos[3]
cdef void _update_sound_listener_position(CoordSyst ear, float proportion):
	if ear._option & COORDSYS_STATIC: return
	if proportion == 0: return
	
	cdef float pos[6]
	cdef float v[3]
	cdef float dt
	
	ear._out(pos)
	alListenerfv(AL_POSITION, pos)
	alGetListenerfv(AL_POSITION, pos)

	if MAIN_LOOP is None: dt = proportion * 0.030
	else:                 dt = proportion * MAIN_LOOP.round_duration
	alListener3f(AL_VELOCITY,
							 (pos[0] - _ear_old_pos[0]) / dt,
							 (pos[1] - _ear_old_pos[1]) / dt,
							 (pos[2] - _ear_old_pos[2]) / dt,
							 )
	
	memcpy(&_ear_old_pos[0], &pos[0], 3 * sizeof(float))
	
	pos[0] =  0.0
	pos[1] =  0.0
	pos[2] = -1.0
	vector_by_matrix(pos    , ear._root_matrix())
	pos[3] =  0.0
	pos[4] =  1.0
	pos[5] =  0.0
	vector_by_matrix(&pos[0] + 3, ear._root_matrix())
	alListenerfv(AL_ORIENTATION, pos)

	
	
cdef class _Sound(_CObj):
	cdef public        _filename
	cdef               _buffers
	cdef               _file
	cdef        int    _format
	cdef        int    _framerate
	
	def __cinit__(self, *args, **kargs):
		self._buffers = []
		
	def __dealloc__(self):
		cdef ALuint buffer
		if self._buffers:
			for buffer in self._buffers:
				alDeleteBuffers(1, &buffer)
				
	cdef ALuint _getbuffer(self, i): raise NotImplementedError()
	
	property stereo:
		def __get__(self):
			return (self._format == AL_FORMAT_STEREO16) or (self._format == AL_FORMAT_STEREO8)
		
	def __repr__(self):
		return "<%s %s>" % (self.__class__.__name__, self._filename)
	
	
cdef class _PyMediaSound(_Sound):
	def __init__(self, filename):
		print "* Soya * Using PyMedia"
		
		import pymedia
		import pymedia.audio.acodec
		import pymedia.muxer
		self.dm = pymedia.muxer.Demuxer(filename.split(".")[-1].lower())
		
		self._file = open(filename, "rb")
		
		nb = 1
		s = ""
		while 1:
			s = s + self._file.read(8192)
			frames = self.dm.parse(s)
			if frames or (nb > 100): break
			nb = nb + 1
		self._file.seek(0)
		
		self.dec = pymedia.audio.acodec.Decoder(self.dm.streams[0])
		
		self._framerate = self.dm.streams[0]["sample_rate"]
		if self.dm.streams[0]["channels"] == 2:
			if self.dm.streams[0]["bitrate"] / 8 / self._framerate == 2: self._format = AL_FORMAT_STEREO16
			else:                                                        self._format = AL_FORMAT_STEREO8
		else:
			if self.dm.streams[0]["bitrate"] / 8 / self._framerate == 2: self._format = AL_FORMAT_MONO16
			else:                                                        self._format = AL_FORMAT_MONO8
		
	cdef _getnextdata(self):
		s = ""
		i = 0
		for i from 0 <= i < 100:
			s = s + self._file.read(1024 * 64)
			if s == "": return ""
			frames = self.dm.parse(s)
			if frames:
				data = ""
				for frame in frames:
					data = data + str(self.dec.decode(frame[1]).data)
				return data
			
		raise RuntimeError("Cannot read data for sound %s !" % self._filename)
	
	cdef ALuint _getbuffer(self, i):
		if i < len(self._buffers): return self._buffers[i]
		
		if self._file is None: return 0
		
		if i > len(self._buffers): self._getbuffer(i - 1) # Load (recursively) the previous buffers
		
		cdef int length
		data = self._getnextdata()
		length = len(data)
		
		if length == 0: # End of the file
			self._file = None # Now useless
			return 0
		
		cdef ALuint buffer
		alGenBuffers(1, &buffer)
		alBufferData(buffer, self._format, PyString_AS_STRING(data), length, self._framerate)
		self._buffers.append(buffer)
		
		return buffer


cdef class _WAVSound(_Sound):
	def __init__(self, filename):
		import wave
		self._file  = wave.open(filename)
		
		if self._file.getnchannels() == 2:
			if self._file.getsampwidth() == 2: self._format = AL_FORMAT_STEREO16
			else:                              self._format = AL_FORMAT_STEREO8
		else:
			if self._file.getsampwidth() == 2: self._format = AL_FORMAT_MONO16
			else:                              self._format = AL_FORMAT_MONO8
		self._framerate = self._file.getframerate()
		
	cdef _getnextdata(self):
		return self._file.readframes(1024 * 64)
	
	cdef ALuint _getbuffer(self, i):
		if i < len(self._buffers): return self._buffers[i]
		
		if self._file is None: return 0
		
		if i > len(self._buffers): self._getbuffer(i - 1) # Load (recursively) the previous buffers
		
		cdef int length
		data = self._getnextdata()
		length = len(data)
		
		if length == 0: # End of the file
			self._file = None # Now useless
			return 0
		
		cdef ALuint buffer
		alGenBuffers(1, &buffer)
		alBufferData(buffer, self._format, PyString_AS_STRING(data), length, self._framerate)
		self._buffers.append(buffer)
		
		return buffer
	
	
	
cdef class _OGGVorbisSound(_Sound):
	def __init__(self, filename):
		import ogg.vorbis
		
		self._file = ogg.vorbis.VorbisFile(filename)
		info = self._file.info()
		
		if info.channels == 2: self._format = AL_FORMAT_STEREO16
		else:                  self._format = AL_FORMAT_MONO16
		self._framerate = info.rate
			
	cdef _getdata(self, int i):
		cdef int length, size
		
		import StringIO
		
		if   self._format == AL_FORMAT_STEREO16: size = 16384 * 2
		elif self._format == AL_FORMAT_MONO16  : size = 16384
		elif self._format == AL_FORMAT_STEREO8 : size = 16384
		elif self._format == AL_FORMAT_MONO8   : size = 16384 / 2
		# Greg Ewing, March 2007 (greg.ewing@canterbury.ac.nz)
		# Else clause added to fix uninitialised variable warning
		else:
			raise ValueError("Unknown size")

		# Catching exception seems to memory leak in pyrex
		#try:    self._file.pcm_seek(i * 8192)
		#except: return "" # End of file
		if i * 8192 > self._file.pcm_total(0): return "" # End of file
		self._file.pcm_seek(i * 8192)
		
		s = StringIO.StringIO()
		length = size
		while length > 0:
			data, bytes, bit = self._file.read(length)
			length = length - bytes
			s.write(data[:bytes])
			if bit: break

		return s.getvalue()
	
	
	cdef ALuint _getbuffer(self, i):
		cdef int j
		while i >= len(self._buffers): self._buffers.append(0)
		
		if self._buffers[i] != 0: return self._buffers[i]
		
		if self._file is None: return 0
		
		cdef int length
		data = self._getdata(i)
		length = len(data)
		
		if length == 0: # End of the file
			for j in self._buffers:
				if j == 0: break
			else:
				self._file = None # Now useless
			return 0
		
		cdef ALuint buffer
		alGenBuffers(1, &buffer)
		alBufferData(buffer, self._format, PyString_AS_STRING(data), length, self._framerate)
		self._buffers[i] = buffer
		
		return buffer
	

cdef class _SoundPlayer(CoordSyst):
	cdef _Sound _sound
	cdef ALuint _source, _current_buffer, _pending_buffer
	cdef int    _current_buffer_id
	cdef float  _old_pos[3]
	
	def __cinit__(self, *args, **kargs):
		alGenSources(1, &self._source)
		alSourcef(self._source, AL_REFERENCE_DISTANCE, _reference_distance)
		
	def __dealloc__(self):
		alDeleteSources(1, &self._source)
		
	def __init__(self, _World parent = None, _Sound sound = None, int loop = 0, int play_in_3D = 1, float gain = 1.0, int auto_remove = 1):
		CoordSyst.__init__(self, parent)
		self._sound = sound
		
		alSourcef(self._source, AL_GAIN, gain)
		
		if loop:        self._option = self._option | SOUND_LOOP
		if auto_remove: self._option = self._option | SOUND_AUTO_REMOVE
		
		if play_in_3D:
			self._option = self._option | SOUND_PLAY_IN_3D
			
			self._out(self._old_pos)
			alSourcefv(self._source, AL_POSITION, self._old_pos)
			alSource3f(self._source, AL_VELOCITY, 0.0, 0.0, 0.0)
			
			alSourcei(self._source, AL_SOURCE_RELATIVE, AL_TRUE)
			
		else:
			alSourcei(self._source, AL_SOURCE_RELATIVE, AL_FALSE)
			
			
		if not sound is None:
			if play_in_3D:
				if sound.stereo: raise ValueError("OpenAL cannot play stereo sound as 3D sound!")
				
			self._current_buffer_id = 0
			self._current_buffer = sound._getbuffer(0)
			alSourceQueueBuffers(self._source, 1, &self._current_buffer)
			
			self._pending_buffer = sound._getbuffer(1)
			if self._pending_buffer == 0:
				if loop:
					self._pending_buffer = self._current_buffer
					alSourceQueueBuffers(self._source, 1, &self._pending_buffer)
			else:
				alSourceQueueBuffers(self._source, 1, &self._pending_buffer)
				
			alSourcePlay(self._source)
			
	cdef __getcstate__(self):
		cdef float x
		
		cdef Chunk* chunk
		chunk = get_chunk()
		chunk_add_int_endian_safe   (chunk, self._option)
		chunk_add_floats_endian_safe(chunk, self._matrix, 19)
		chunk_add_floats_endian_safe(chunk, self._old_pos, 3)
		chunk_add_int_endian_safe   (chunk, self._current_buffer_id)
		
		alGetSourcef(self._source, AL_GAIN, &x)
		chunk_add_float_endian_safe (chunk, x)
		
		return drop_chunk_to_string(chunk), self._sound
	
	cdef void __setcstate__(self, cstate):
		self._sound = cstate[1]
		
		cstate = cstate[0]
		
		self._validity = COORDSYS_INVALID
		cdef Chunk* chunk
		cdef float  x
		chunk = string_to_chunk(cstate)
		chunk_get_int_endian_safe   (chunk, &self._option)
		chunk_get_floats_endian_safe(chunk,  self._matrix, 19)
		chunk_get_floats_endian_safe(chunk,  self._old_pos, 3)
		chunk_get_int_endian_safe   (chunk, &self._current_buffer_id)
		
		chunk_get_float_endian_safe (chunk, &x)
		alSourcef(self._source, AL_GAIN, x)
		
		drop_chunk(chunk)
		
		if self._option & SOUND_PLAY_IN_3D:
			alSourcefv(self._source, AL_POSITION, self._old_pos)
			alSourcei(self._source, AL_SOURCE_RELATIVE, AL_TRUE)
			
		else:
			alSourcei(self._source, AL_SOURCE_RELATIVE, AL_FALSE)
			
		if self._sound:
			self._current_buffer = self._sound._getbuffer(self._current_buffer_id)
			alSourceQueueBuffers(self._source, 1, &self._current_buffer)
			
			self._pending_buffer = self._sound._getbuffer(self._current_buffer_id + 1)
			if self._pending_buffer == 0:
				if self._option & SOUND_LOOP:
					self._pending_buffer = self._sound._getbuffer(0)
			alSourceQueueBuffers(self._source, 1, &self._pending_buffer)
			
			alSourcePlay(self._source)
			
	def begin_round(self):
		CoordSyst.begin_round(self)
		
		cdef int    i, nb_queued, nb_processed
		cdef ALuint buffer
		
		if self._pending_buffer == 0:
			if not self._option & SOUND_LOOP:
				alGetSourcei(self._source, AL_SOURCE_STATE, &i)
				if i == AL_STOPPED: self.ended()
				
		alGetSourcei(self._source, AL_BUFFERS_QUEUED   , &nb_queued)
		alGetSourcei(self._source, AL_BUFFERS_PROCESSED, &nb_processed)
		
		if nb_processed >= 1:
			alSourceUnqueueBuffers(self._source, 1, &self._current_buffer)
			
			self._current_buffer    = self._pending_buffer
			
			if self._current_buffer == self._sound._buffers[0]: self._current_buffer_id = 0
			else:                                               self._current_buffer_id = self._current_buffer_id + 1
			
			self._pending_buffer    = self._sound._getbuffer(self._current_buffer_id + 1)
			
			if self._pending_buffer == 0:
				if self._option & SOUND_LOOP: self._pending_buffer = self._sound._getbuffer(0)
				else:                         return
				
			alSourceQueueBuffers(self._source, 1, &self._pending_buffer)
			
			alGetSourcei(self._source, AL_SOURCE_STATE, &i)
			if i == AL_STOPPED: alSourcePlay(self._source)
			
			
	def advance_time(self, float proportion):
		cdef float pos[3]
		cdef float dt
		
		if (self._option & SOUND_PLAY_IN_3D) and (not self._option & COORDSYS_STATIC):
			if MAIN_LOOP is None: dt = proportion * 0.030
			else:             dt = proportion * MAIN_LOOP.round_duration
			
			self._out(pos)
			
			alSourcefv(self._source, AL_POSITION, pos)
			alSource3f(self._source, AL_VELOCITY,
								 (pos[0] - self._old_pos[0]) / dt,
								 (pos[1] - self._old_pos[1]) / dt,
								 (pos[2] - self._old_pos[2]) / dt,
								 )
			
			memcpy(&self._old_pos[0], &pos[0], 3 * sizeof(float))

		else:
			alSourcefv(self._source, AL_POSITION, _ear_old_pos)
			

	property sound:
		def __get__(self):
			return self._sound
		
	property loop:
		def __get__(self):
			return self._option & SOUND_LOOP
		def __set__(self, int x):
			if x: self._option = self._option |  SOUND_LOOP
			else: self._option = self._option & ~SOUND_LOOP
			
	property auto_remove:
		def __get__(self):
			return self._option & SOUND_AUTO_REMOVE
		def __set__(self, int x):
			if x: self._option = self._option |  SOUND_AUTO_REMOVE
			else: self._option = self._option & ~SOUND_AUTO_REMOVE
	
	property play_in_3D:
		def __get__(self):
			return self._option & SOUND_PLAY_IN_3D
		#def __set__(self, int x):
		#	if x: self._option = self._option |  SOUND_PLAY_IN_3D
		#	else: self._option = self._option & ~SOUND_PLAY_IN_3D
	
	property gain:
		def __get__(self):
			cdef float x
			alGetSourcef(self._source, AL_GAIN, &x)
			return x
		def __set__(self, float x):
			alSourcef(self._source, AL_GAIN, x)
			



# _Sound without streaming; quite useless

# cdef class _Sound(_CObj):
# 	cdef public        _filename
# 	cdef        ALuint _buffer
	
# 	def __new__(self, *args, **kargs):
# 		alGenBuffers(1, &self._buffer)
		
# 	def __dealloc__(self):
# 		alDeleteBuffers(1, &self._buffer)
		
# 	property stereo:
# 		def __get__(self):
# 			cdef int x
# 			alGetBufferi(self._buffer, AL_CHANNELS, &x)
# 			return x - 1
			
# 	def _load_wav(self, filename):
# 		cdef ALenum format
		
# 		import wave
# 		wav  = wave.open(filename)
		
# 		if wav.getnchannels() == 2:
# 			if wav.getsampwidth() == 2: format = AL_FORMAT_STEREO16
# 			else:                       format = AL_FORMAT_STEREO8
# 		else:
# 			if wav.getsampwidth() == 2: format = AL_FORMAT_MONO16
# 			else:                       format = AL_FORMAT_MONO8
			
# 		data = wav.readframes(wav.getnframes())
		
# 		alBufferData(self._buffer, format, PyString_AS_STRING(data), len(data), wav.getframerate())
		
# 	def _load_ogg(self, filename):
# 		cdef ALenum format
		
# 		import ogg.vorbis, StringIO
		
# 		vorb = ogg.vorbis.VorbisFile(filename)
# 		info = vorb.info()
		
# 		bytes = 1
# 		data  = StringIO.StringIO()
# 		while bytes:
# 			buff, bytes, bit = vorb.read(4096)
# 			data.write(buff[:bytes])
# 		data = data.getvalue()
		
# 		# Assume Ogg Vorbis file are 16 bit sounds !!!
# 		# XXX I'm not sure of that !!!
		
# 		if info.channels == 2: format = AL_FORMAT_STEREO16
# 		else:                  format = AL_FORMAT_MONO16
		
# 		alBufferData(self._buffer, format, PyString_AS_STRING(data), len(data), info.rate)
		
	
