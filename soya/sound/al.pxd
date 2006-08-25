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


cdef extern from "include_al.h":
	ctypedef int        		ALenum
	ctypedef char           ALboolean
	ctypedef void						ALvoid
	ctypedef char           ALbyte
	ctypedef short					ALshort
	ctypedef int						ALint
	ctypedef unsigned char  ALubyte
	ctypedef unsigned short	ALushort
	ctypedef unsigned int		ALuint
	ctypedef int						ALsizei
	ctypedef float					ALfloat
	ctypedef double					ALdouble
	ctypedef char 					ALchar
	
	int AL_INVALID
	int AL_NONE
	int AL_FALSE
	int AL_TRUE
	int AL_SOURCE_RELATIVE
	int AL_CONE_INNER_ANGLE
	int AL_CONE_OUTER_ANGLE
	int AL_PITCH
	int AL_POSITION
	int AL_DIRECTION
	int AL_VELOCITY
	int AL_LOOPING
	int AL_BUFFER
	int AL_GAIN
	int AL_MIN_GAIN
	int AL_MAX_GAIN
	int AL_ORIENTATION
	int AL_CHANNEL_MASK
	int AL_SOURCE_STATE
	int AL_INITIAL
	int AL_PLAYING
	int AL_PAUSED
	int AL_STOPPED
	int AL_BUFFERS_QUEUED
	int AL_BUFFERS_PROCESSED
	int AL_SEC_OFFSET
	int AL_SAMPLE_OFFSET
	int AL_BYTE_OFFSET
	int AL_SOURCE_TYPE
	int AL_STATIC
	int AL_STREAMING
	int AL_UNDETERMINED
	int AL_FORMAT_MONO8
	int AL_FORMAT_MONO16
	int AL_FORMAT_STEREO8
	int AL_FORMAT_STEREO16
	int AL_REFERENCE_DISTANCE
	int AL_ROLLOFF_FACTOR
	int AL_CONE_OUTER_GAIN
	int AL_MAX_DISTANCE
	int AL_FREQUENCY
	int AL_BITS
	int AL_CHANNELS
	int AL_SIZE
	int AL_UNUSED
	int AL_PENDING
	int AL_PROCESSED
	int AL_NO_ERROR
	int AL_INVALID_NAME
	int AL_ILLEGAL_ENUM
	int AL_INVALID_ENUM
	int AL_INVALID_VALUE
	int AL_ILLEGAL_COMMAND
	int AL_INVALID_OPERATION
	int AL_OUT_OF_MEMORY
	int AL_VENDOR
	int AL_VERSION
	int AL_RENDERER
	int AL_EXTENSIONS
	int AL_DOPPLER_FACTOR
	int AL_DOPPLER_VELOCITY
	int AL_SPEED_OF_SOUND
	int AL_DISTANCE_MODEL
	int AL_INVERSE_DISTANCE
	int AL_INVERSE_DISTANCE_CLAMPED
	int AL_LINEAR_DISTANCE
	int AL_LINEAR_DISTANCE_CLAMPED
	int AL_EXPONENT_DISTANCE
	int AL_EXPONENT_DISTANCE_CLAMPED
	
	cdef void alEnable(ALenum capability)
	cdef void alDisable(ALenum capability)
	cdef ALboolean alIsEnabled(ALenum capability)
	cdef ALchar* alGetString(ALenum param)
	cdef void alGetBooleanv(ALenum param, ALboolean* data)
	cdef void alGetIntegerv(ALenum param, ALint* data)
	cdef void alGetFloatv(ALenum param, ALfloat* data)
	cdef void alGetDoublev(ALenum param, ALdouble* data)
	cdef ALboolean alGetBoolean(ALenum param)
	cdef ALint alGetInteger(ALenum param)
	cdef ALfloat alGetFloat(ALenum param)
	cdef ALdouble alGetDouble(ALenum param)
	cdef ALenum alGetError()
	cdef ALboolean alIsExtensionPresent(ALchar* extname)
	cdef void* alGetProcAddress(ALchar* fname)
	cdef ALenum alGetEnumValue(ALchar* ename)
	cdef void alListenerf(ALenum param, ALfloat value)
	cdef void alListener3f(ALenum param, ALfloat value1, ALfloat value2, ALfloat value3)
	cdef void alListenerfv(ALenum param, ALfloat* values)
	cdef void alListeneri(ALenum param, ALint value)
	cdef void alListener3i(ALenum param, ALint value1, ALint value2, ALint value3)
	cdef void alListeneriv(ALenum param, ALint* values)
	cdef void alGetListenerf(ALenum param, ALfloat* value)
	cdef void alGetListener3f(ALenum param, ALfloat *value1, ALfloat *value2, ALfloat *value3)
	cdef void alGetListenerfv(ALenum param, ALfloat* values)
	cdef void alGetListeneri(ALenum param, ALint* value)
	cdef void alGetListener3i(ALenum param, ALint *value1, ALint *value2, ALint *value3)
	cdef void alGetListeneriv(ALenum param, ALint* values)
	cdef void alGenSources(ALsizei n, ALuint* sources)
	cdef void alDeleteSources(ALsizei n, ALuint* sources)
	cdef ALboolean alIsSource(ALuint sid)
	cdef void alSourcef(ALuint sid, ALenum param, ALfloat value)
	cdef void alSource3f(ALuint sid, ALenum param, ALfloat value1, ALfloat value2, ALfloat value3)
	cdef void alSourcefv(ALuint sid, ALenum param, ALfloat* values)
	cdef void alSourcei(ALuint sid, ALenum param, ALint value)
	cdef void alSource3i(ALuint sid, ALenum param, ALint value1, ALint value2, ALint value3)
	cdef void alSourceiv(ALuint sid, ALenum param, ALint* values)
	cdef void alGetSourcef(ALuint sid, ALenum param, ALfloat* value)
	cdef void alGetSource3f(ALuint sid, ALenum param, ALfloat* value1, ALfloat* value2, ALfloat* value3)
	cdef void alGetSourcefv(ALuint sid, ALenum param, ALfloat* values)
	cdef void alGetSourcei(ALuint sid,  ALenum param, ALint* value)
	cdef void alGetSource3i(ALuint sid, ALenum param, ALint* value1, ALint* value2, ALint* value3)
	cdef void alGetSourceiv(ALuint sid,  ALenum param, ALint* values)
	cdef void alSourcePlayv(ALsizei ns, ALuint *sids)
	cdef void alSourceStopv(ALsizei ns, ALuint *sids)
	cdef void alSourceRewindv(ALsizei ns, ALuint *sids)
	cdef void alSourcePausev(ALsizei ns, ALuint *sids)
	cdef void alSourcePlay(ALuint sid)
	cdef void alSourceStop(ALuint sid)
	cdef void alSourceRewind(ALuint sid)
	cdef void alSourcePause(ALuint sid)
	cdef void alSourceQueueBuffers(ALuint sid, ALsizei numEntries, ALuint *bids)
	cdef void alSourceUnqueueBuffers(ALuint sid, ALsizei numEntries, ALuint *bids)
	cdef void alGenBuffers(ALsizei n, ALuint* buffers)
	cdef void alDeleteBuffers(ALsizei n, ALuint* buffers)
	cdef ALboolean alIsBuffer(ALuint bid)
	cdef void alBufferData(ALuint bid, ALenum format, ALvoid* data, ALsizei size, ALsizei freq)
	cdef void alBufferf(ALuint bid, ALenum param, ALfloat value)
	cdef void alBuffer3f(ALuint bid, ALenum param, ALfloat value1, ALfloat value2, ALfloat value3)
	cdef void alBufferfv(ALuint bid, ALenum param, ALfloat* values)
	cdef void alBufferi(ALuint bid, ALenum param, ALint value)
	cdef void alBuffer3i(ALuint bid, ALenum param, ALint value1, ALint value2, ALint value3)
	cdef void alBufferiv(ALuint bid, ALenum param, ALint* values)
	cdef void alGetBufferf(ALuint bid, ALenum param, ALfloat* value)
	cdef void alGetBuffer3f(ALuint bid, ALenum param, ALfloat* value1, ALfloat* value2, ALfloat* value3)
	cdef void alGetBufferfv(ALuint bid, ALenum param, ALfloat* values)
	cdef void alGetBufferi(ALuint bid, ALenum param, ALint* value)
	cdef void alGetBuffer3i(ALuint bid, ALenum param, ALint* value1, ALint* value2, ALint* value3)
	cdef void alGetBufferiv(ALuint bid, ALenum param, ALint* values)
	cdef void alDopplerFactor(ALfloat value)
	cdef void alDopplerVelocity(ALfloat value)
	cdef void alSpeedOfSound(ALfloat value)
	cdef void alDistanceModel(ALenum distanceModel)
	
#cdef extern from "AL/alut.h":
#ALUTAPI void ALUTAPIENTRY alutInit( int *argc, char *argv[] );
#ALUTAPI void ALUTAPIENTRY alutExit( void );


	
cdef extern from "include_alc.h":
	ctypedef char           ALCboolean
	ctypedef char           ALCchar
	ctypedef char           ALCbyte
	ctypedef unsigned char  ALCubyte
	ctypedef short          ALCshort
	ctypedef unsigned short ALCushort
	ctypedef int            ALCint
	ctypedef unsigned int   ALCuint
	ctypedef int            ALCsizei
	ctypedef int            ALCenum
	ctypedef float          ALCfloat
	ctypedef double         ALCdouble
	ctypedef void           ALCvoid
	
	int ALC_INVALID
	int ALC_FALSE
	int ALC_TRUE
	int ALC_FREQUENCY
	int ALC_REFRESH
	int ALC_SYNC
	int ALC_MONO_SOURCES
	int ALC_STEREO_SOURCES
	int ALC_NO_ERROR
	int ALC_INVALID_DEVICE
	int ALC_INVALID_CONTEXT
	int ALC_INVALID_ENUM
	int ALC_INVALID_VALUE
	int ALC_OUT_OF_MEMORY
	int ALC_DEFAULT_DEVICE_SPECIFIER
	int ALC_DEVICE_SPECIFIER
	int ALC_EXTENSIONS
	int ALC_MAJOR_VERSION
	int ALC_MINOR_VERSION
	int ALC_ATTRIBUTES_SIZE
	int ALC_ALL_ATTRIBUTES
	int ALC_CAPTURE_DEVICE_SPECIFIER
	int ALC_CAPTURE_DEFAULT_DEVICE_SPECIFIER
	int ALC_CAPTURE_SAMPLES
	
	ctypedef struct ALCcontext:
		pass
	
	ctypedef struct ALCdevice:
		pass
	
	cdef ALCcontext* alcCreateContext(ALCdevice *device,  ALCint* attrlist)
	cdef ALCboolean alcMakeContextCurrent(ALCcontext *context)
	cdef void alcProcessContext(ALCcontext *context)
	cdef void alcSuspendContext(ALCcontext *context)
	cdef void alcDestroyContext(ALCcontext *context)
	cdef ALCcontext* alcGetCurrentContext()
	cdef ALCdevice* alcGetContextsDevice(ALCcontext *context)
	cdef ALCdevice* alcOpenDevice(ALCchar *devicename)
	cdef ALCboolean alcCloseDevice(ALCdevice *device)
	cdef ALCenum alcGetError(ALCdevice *device)
	cdef ALCboolean alcIsExtensionPresent(ALCdevice *device, ALCchar *extname)
	cdef void* alcGetProcAddress(ALCdevice *device, ALCchar *funcname)
	cdef ALCenum alcGetEnumValue(ALCdevice *device, ALCchar *enumname)
	cdef ALCchar* alcGetString(ALCdevice *device, ALCenum param)
	cdef void alcGetIntegerv(ALCdevice *device, ALCenum param, ALCsizei size, ALCint *data)
	cdef ALCdevice* alcCaptureOpenDevice(ALCchar *devicename, ALCuint frequency, ALCenum format, ALCsizei buffersize)
	cdef ALCboolean alcCaptureCloseDevice(ALCdevice *device)
	cdef void alcCaptureStart(ALCdevice *device)
	cdef void alcCaptureStop(ALCdevice *device)
	cdef void alcCaptureSamples(ALCdevice *device, ALCvoid *buffer, ALCsizei samples)


