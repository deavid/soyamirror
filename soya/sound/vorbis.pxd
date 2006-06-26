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


cdef extern from "vorbis/vorbisfile.h":
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
	
	
cdef extern from "AL/al.h":
	cdef void alEnable(ALenum capability)
	cdef void alDisable(ALenum capability)
	cdef ALboolean alIsEnabled(ALenum capability)
	cdef ALchar* alGetString(ALenum param)
	cdef void alGetBooleanv(ALenum param, ALboolean* data)
	cdef void alGetIntegerv(ALenum param, ALint* data)
	cdef void alGetFloatv(ALenum param, ALfloat* data)
