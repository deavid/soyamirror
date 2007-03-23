/* Soya 3D */
/* Copyright (C) 2001-2004 Jean-Baptiste LAMY -- jiba@tuxfamily.org */

/* This program is free software; you can redistribute it and/or modify */
/* it under the terms of the GNU General Public License as published by */
/* the Free Software Foundation; either version 2 of the License, or */
/* (at your option) any later version. */

/* This program is distributed in the hope that it will be useful, */
/* but WITHOUT ANY WARRANTY; without even the implied warranty of */
/* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the */
/* GNU General Public License for more details. */

/* You should have received a copy of the GNU General Public License */
/* along with this program; if not, write to the Free Software */
/* Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA */


/* This file is required to correctly include Freetype
   It is NOT redundant with any of the Freetype .h file !!! */

#include <ft2build.h>
#include FT_FREETYPE_H // this is not do-able in Pyrex
#include <freetype/freetype.h>
#include <freetype/ftoutln.h>
#include <freetype/ftimage.h>
#include <freetype/ftglyph.h>

