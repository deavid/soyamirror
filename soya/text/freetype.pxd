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

# This is only a PARTIAL definition file -- i've defined only the stuff i need

# cdef extern from "freetype/freetype.h":
#   pass
# cdef extern from "freetype/ftoutln.h":
#   pass
# cdef extern from "freetype/ftimage.h":
#   pass
# cdef extern from "freetype/ftglyph.h":
#   pass

#cdef extern from "ft2build.h":
#  pass
#cdef extern from "FT_FREETYPE_H":
#  pass

cdef extern from "include_freetype.h":
#cdef extern from *:
	cdef int FT_LOAD_DEFAULT
	cdef int FT_FACE_FLAG_SCALABLE
	cdef int ft_glyph_bbox_unscaled
	cdef int FT_RENDER_MODE_NORMAL
	cdef int FT_GLYPH_FORMAT_BITMAP
	
	cdef struct FT_LibraryRec_:
		int _dummy
	ctypedef FT_LibraryRec_* FT_Library
	
	ctypedef struct FT_Vector:
		signed long x, y
		
	ctypedef struct FT_BBox:
		long xMin, yMin, xMax, yMax
		
	ctypedef struct FT_Outline:
		int _dummy
		
	cdef struct FT_GlyphRec_:
		FT_Vector advance
	ctypedef FT_GlyphRec_  FT_GlyphRec
	ctypedef FT_GlyphRec_* FT_Glyph
	
	cdef struct FT_OutlineGlyphRec_:
		FT_GlyphRec root
		FT_Outline  outline
	ctypedef FT_OutlineGlyphRec_* FT_OutlineGlyph
		
	cdef struct FT_Bitmap_:
		int             rows
		int             width
		int             pitch
		unsigned char*  buffer
		short           num_grays
		char            pixel_mode
		char            palette_mode
	ctypedef FT_Bitmap_ FT_Bitmap
	
	cdef struct FT_GlyphSlotRec_:
		FT_Vector       advance
		int             format
		FT_Bitmap       bitmap
		int             bitmap_left
		int             bitmap_top
		
	ctypedef FT_GlyphSlotRec_* FT_GlyphSlot

	ctypedef struct FT_Size_Metrics:
		unsigned short  x_ppem      # horizontal pixels per EM
		unsigned short  y_ppem      # vertical pixels per EM
		long            x_scale     # two scales used to convert font units
		long            y_scale     # to 26.6 frac. pixel coordinates..
		long            ascender    # ascender in 26.6 frac. pixels
		long            descender   # descender in 26.6 frac. pixels
		long            height      # text height in 26.6 frac. pixels
		long            max_advance # max horizontal advance, in 26.6 pixels
		
	cdef struct FT_SizeRec_:
		FT_Size_Metrics metrics
	ctypedef FT_SizeRec_* FT_Size
	
	cdef struct FT_CharMapRec_:
		int encoding
	ctypedef FT_CharMapRec_* FT_CharMap
		
	cdef struct FT_FaceRec_:
		unsigned short units_per_EM
		FT_GlyphSlot   glyph
		long           num_glyphs
		short          height
		short          ascender
		short          descender
		FT_Size        size
		int            num_charmaps
		FT_CharMap     charmap
		FT_CharMap*    charmaps
		long           face_flags
	ctypedef FT_FaceRec_* FT_Face
	
	ctypedef int (*FT_Outline_MoveToFunc ) (FT_Vector*, void*)
	ctypedef int (*FT_Outline_LineToFunc ) (FT_Vector*, void*)
	ctypedef int (*FT_Outline_ConicToFunc) (FT_Vector*, FT_Vector*, void*)
	ctypedef int (*FT_Outline_CubicToFunc) (FT_Vector*, FT_Vector*, FT_Vector*, void*)
	
	ctypedef struct FT_Outline_Funcs:
		FT_Outline_MoveToFunc  move_to
		FT_Outline_LineToFunc  line_to
		FT_Outline_ConicToFunc conic_to
		FT_Outline_CubicToFunc cubic_to
		int  shift
		long delta
		
	cdef int          FT_Init_FreeType    (FT_Library*)
	cdef int          FT_New_Face         (FT_Library, char*, long, FT_Face*)
	cdef int          FT_Done_Face        (FT_Face)
	cdef unsigned int FT_Get_Char_Index   (FT_Face, long)
	cdef int          FT_Load_Glyph       (FT_Face, unsigned int, int)
	cdef int          FT_Outline_Decompose(FT_Outline*, FT_Outline_Funcs*, void*)
	cdef int          FT_Get_Glyph        (FT_GlyphSlot, FT_Glyph*)
	cdef void         FT_Glyph_Get_CBox   (FT_Glyph, unsigned int, FT_BBox*)
	cdef void         FT_Done_Glyph       (FT_Glyph)
	cdef void         FT_Select_Charmap   (FT_Face, int)
	cdef int          FT_Set_Char_Size    (FT_Face, signed long, signed long, unsigned int, unsigned int)
	cdef int          FT_Render_Glyph     (FT_GlyphSlot, int)
	cdef int          FT_Set_Pixel_Sizes  (FT_Face, int, int)

	
