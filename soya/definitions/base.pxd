# -*- indent-tabs-mode: t -*-

# Soya 3D
# Copyright (C) 2003-2004 Jean-Baptiste LAMY -- jiba@tuxfamily.org
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

cdef class _CObj
cdef class _Image(_CObj)
cdef class _Material(_CObj)
cdef class _Model(_CObj)
cdef class _SimpleModel(_Model)
cdef class _CellShadingModel(_SimpleModel)
cdef class _TreeModel(_SimpleModel)
cdef class _ModelData(_Model)
cdef class _AnimatedModelData(_ModelData)
cdef class Position(_CObj)
cdef class _Point(Position)
cdef class _Vector(_Point)
cdef class _Vertex(_Point)
cdef class CoordSyst(Position)
cdef class _Camera(CoordSyst)
cdef class _Light(CoordSyst)
cdef class _Body(CoordSyst)
cdef class _World(_Body)
cdef class _Face(CoordSyst)
#cdef class _Cal3dBody(CoordSyst)
cdef class _AnimatedModel(_Model)
cdef class _Sprite(CoordSyst)
cdef class _Portal(CoordSyst)
cdef class _Terrain(CoordSyst)
cdef class _Atmosphere(_CObj)
cdef class Renderer
cdef class Context
cdef class RaypickData
cdef class RaypickContext
cdef class MainLoop
cdef class Glyph
cdef class _Font
cdef class ModelBuilder(_CObj)
cdef class Traveling(_CObj)
cdef class _TravelingCamera(_Camera)
cdef class _Deform(_ModelData)

cdef enum:
	QUALITY_LOW    = 0
	QUALITY_MEDIUM = 1
	QUALITY_HIGH   = 2

cdef enum:
	INITED      = 1 << 0
	USE_MIPMAP  = 1 << 1
	FULLSCREEN  = 1 << 2
	WIREFRAME   = 1 << 3
	FX_INITED   = 1 << 4
	SHADOWS     = 1 << 5
	HAS_STENCIL = 1 << 6
	
cdef enum:
	MATERIAL_SEPARATE_SPECULAR   = 1 << 1
	MATERIAL_ADDITIVE_BLENDING   = 1 << 2
	MATERIAL_ALPHA               = 1 << 3
	MATERIAL_MASK                = 1 << 4
	MATERIAL_CLAMP               = 1 << 5
	MATERIAL_ENVIRONMENT_MAPPING = 1 << 6
	MATERIAL_MIPMAP              = 1 << 7
	MATERIAL_BORDER              = 1 << 8
	MATERIAL_EMULATE_BORDER      = 1 << 9
	
cdef enum:
	VERTEX_ALPHA         = 1 << 1
	VERTEX_MADE          = 1 << 3  # temporaly used in FX
	VERTEX_INVISIBLE     = 1 << 4
	VERTEX_FX_TRANSITION = 1 << 5
	
cdef enum:
	FACE_TRIANGLE                   = 1 << 0
	FACE_QUAD                       = 1 << 1
	FACE_NON_SOLID                  = 1 << 2
	FACE_HIDDEN                     = 1 << 3
	FACE_ALPHA                      = 1 << 4
	FACE_DOUBLE_SIDED               = 1 << 5
	FACE_SMOOTH_LIT                 = 1 << 6
	FACE_FRONT                      = 1 << 7 # Temporarily used by
	FACE_BACK                       = 1 << 8 # cell-shading
	FACE_NO_VERTEX_NORMAL_INFLUENCE = 1 << 9
	FACE_NON_LIT                    = 1 << 10
	FACE_STATIC_LIT                 = 1 << 11
	FACE_LIGHT_FRONT                = 1 << 12 # Temporarily used by
	FACE_LIGHT_BACK                 = 1 << 13 # shadows
	
cdef enum:
	PACK_SECONDPASS = 1 << 2
	PACK_SPECIAL    = 1 << 3
	
cdef enum:
	HIDDEN                = 1 << 0
	LEFTHANDED            = 1 << 3
	NON_SOLID             = 1 << 4
	WORLD_BATCHED         = 1 << 6
	BONUS_BATCHED         = 1 << 6
	WORLD_PORTAL_LINKED   = 1 << 7
	LIGHT_TOP_LEVEL       = 1 << 7
	LIGHT_DIRECTIONAL     = 1 << 8
	LIGHT_NO_SHADOW       = 1 << 9
	LIGHT_SHADOW_COLOR    = 1 << 10
	LIGHT_STATIC          = 1 << 11
	LIGHT_INVALID         = 1 << 6
	CAMERA_PARTIAL        = 1 << 5
	CAMERA_ORTHO          = 1 << 6
	CAMERA_NO_LISTENER    = 1 << 7
	SOUND_PLAY_IN_3D      = 1 << 6
	SOUND_AUTO_REMOVE     = 1 << 7
	SOUND_LOOP            = 1 << 8
	FACE2_LIT             = 1 << 12 # FACE2_* constants are for soya.Face 
	FACE2_SMOOTH_LIT      = 1 << 13 # FACE_* are for the ModelFace structure used by models
	FACE2_STATIC_LIT      = 1 << 14 # They have equivalent meanings, but are not used for
	FACE2_DOUBLE_SIDED    = 1 << 15 # the same objects.
	COORDSYST_STATE_VALID = 1 << 16
	
cdef enum:
	PORTAL_USE_4_CLIP_PLANES = 1 << 5 # the part of world beyond that is out of the portal rectangle is not rendered
	PORTAL_USE_5_CLIP_PLANES = 1 << 6 # id and the part of world beyond that is in front of the portal is not rendered
	PORTAL_BOUND_ATMOSPHERE  = 1 << 8 # if world and world beyond doesn't have the same atmosphere and you want to see beyond atmosphere through the portal
	PORTAL_TELEPORTER        = 1 << 9 # the elements that are behind the portal are not rendered (protect Z-buffer)
	
cdef enum:
	RAYPICK_CULL_FACE = 1 << 0
	RAYPICK_HALF_LINE = 1 << 1
cdef enum: # returned by math raypick functions
	RAYPICK_DIRECT   = 1
	RAYPICK_INDIRECT = 2


cdef enum:
	COORDSYS_INVALID             = 0
	COORDSYS_ROOT_VALID          = 1 << 0
	COORDSYS_INVERTED_ROOT_VALID = 1 << 1
	COORDSYS_STATIC              = 1 << 19
	COORDSYS_NON_AUTO_STATIC     = 1 << 20

cdef enum:
	RENDERER_STATE_OPAQUE     = 0
	RENDERER_STATE_SECONDPASS = 1
	RENDERER_STATE_ALPHA      = 2
	RENDERER_STATE_SPECIAL    = 3

cdef enum:
	PACK_OPTIONS         = FACE_TRIANGLE | FACE_QUAD | FACE_ALPHA | FACE_DOUBLE_SIDED | FACE_NON_LIT
	DISPLAY_LIST_OPTIONS = FACE_TRIANGLE | FACE_QUAD | FACE_ALPHA | FACE_DOUBLE_SIDED | FACE_NON_LIT
	
cdef enum:
	MODEL_DIFFUSES         = 1 << 5
	MODEL_EMISSIVES        = 1 << 6
	MODEL_TEXCOORDS        = 1 << 8
	MODEL_VERTEX_OPTIONS   = 1 << 10
	MODEL_CELLSHADING      = 1 << 11
	MODEL_NEVER_LIT        = 1 << 12
	MODEL_PLANE_EQUATION   = 1 << 14
	MODEL_NEIGHBORS        = 1 << 15
	MODEL_INITED           = 1 << 16
	MODEL_TREE             = 1 << 17
	MODEL_DISPLAY_LISTS    = 1 << 18
	MODEL_FACE_LIST        = 1 << 19
	MODEL_HAS_SPHERE       = 1 << 20
	MODEL_SHADOW           = 1 << 21
	MODEL_STATIC_SHADOW    = 1 << 22
	MODEL_STATIC_LIT       = 1 << 23
	MODEL_SIMPLE_NEIGHBORS = 1 << 24 # Neighbors take face angle into account, but simple neighbors don't
	MODEL_SHARED_DATA      = 1 << 25
	
cdef enum:
	TEXT_ALIGN_LEFT   = 0
	TEXT_ALIGN_CENTER = 1
	
cdef enum:
	FONT_RASTER  = 1
	FONT_TEXTURE = 2

cdef enum:
	ATMOSPHERE_FOG           = 1 << 3
	ATMOSPHERE_SKY_BOX_ALPHA = 1 << 7
	ATMOSPHERE_HAS_CHILD     = 1 << 8
	
cdef enum:
	SPRITE_ALPHA          = 1 <<  7
	SPRITE_COLORED        = 1 <<  9
	SPRITE_NEVER_LIT      = 1 << 11
	SPRITE_RECEIVE_SHADOW = 1 << 12

cdef enum:
	PARTICLES_MULTI_COLOR   = 1 << 14
	PARTICLES_MULTI_SIZE    = 1 << 15
	PARTICLES_CYLINDER      = 1 << 16
	PARTICLES_AUTO_GENERATE = 1 << 17
	PARTICLES_REMOVABLE     = 1 << 18

cdef enum:
	TERRAIN_INITED           = 1 << 2
	TERRAIN_REAL_LOD_RAYPICK = 1 << 3
	TERRAIN_VERTEX_OPTIONS   = 1 << 7
	TERRAIN_COLORED          = 1 << 8

cdef enum:
	TERRAIN_VERTEX_HIDDEN         = 1 << 0
	TERRAIN_VERTEX_ALPHA          = VERTEX_ALPHA # 1 << 1
	TERRAIN_VERTEX_NON_SOLID      = 1 << 2
	TERRAIN_VERTEX_FORCE_PRESENCE = 1 << 3

cdef enum:
	CAL3D_ALPHA        = 1 <<  5
	CAL3D_CELL_SHADING = 1 <<  6
	CAL3D_SHADOW       = 1 <<  7
	CAL3D_NEIGHBORS    = 1 <<  8
	CAL3D_INITED       = 1 <<  9
	CAL3D_DOUBLE_SIDED = 1 << 10


ctypedef struct Frustum:
## Frustum
## points :
## 15-------12
## |\       /|
## | \     / |
## |  3---0  |
## |  |   |  |
## |  6---9  |
## | /     \ |
## |/       \|
## 18-------21
## 
## plane[ 0] : front plane
## plane[ 4] : top plane
## plane[ 8] : bottom plane
## plane[12] : right plane
## plane[16] : left plane
## plane[20] : back plane
## plane normals are oriented toward the exterior of the frustum
	float position[3]  # camera position (x,y,z)
	float points  [24] # points : (x,y,z) * 8
	float planes  [24] # planes equation : (a,b,c,d) * 6

cdef struct _Pack: # See material.pyx for doc and comments
	int    option
	int    material_id
	_Pack* alpha
	_Pack* secondpass
	Chunk* batched_faces

ctypedef _Pack Pack

cdef class _CObj:
	cdef __getcstate__(self)
	cdef void __setcstate__(self, cstate)

