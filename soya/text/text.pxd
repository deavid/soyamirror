# -*- indent-tabs-mode: t -*-

# Soya 3D
# Copyright (C) 2004 Jean-Baptiste LAMY -- jiba@tuxfamily.org
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

# A big part of this file is heavily inspired by OGLFT (www.sf.net/project/oglft)
# We need to rewrite it because OGLFT is written in C++ :-(


cdef class Glyph:
	cdef readonly float _pixels_x1, _pixels_y1, _pixels_x2, _pixels_y2, width, height, y, x
	cdef readonly unichar

	
cdef class _Font:
	cdef FT_Face      _face
	cdef readonly     filename
	cdef int          _width, _height
	cdef              _glyphs
	
	cdef GLubyte*     _pixels
	cdef int          _current_x, _current_y
	cdef readonly int _current_height, _pixels_height
	cdef int          _rendering
	cdef GLuint       _tex_id
	cdef float        _ascender, _descender
	
	cdef Glyph _get_glyph(self, char_)
	cdef _gen_glyph(self, char_, int code)
	cdef void _sizeup_pixel(self, int height)
	cdef void _init(self)
		
	
