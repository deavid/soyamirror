# Soya 3D
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

# Import base C lib
include "c.pxd"
include "python.pxd"
#include "c_opengl.pxd"
#include "sdl.pxd"

# Still in C :-(
#include "chunk.pxd"

# Pyrex base module
include "base.pyx"

# Still in C :-(
#include "matrix.pxd"

# Pyrex modules
include "init.pyx"
include "math3d.pyx"
include "renderer.pyx"
include "idler.pyx"

include "soya3d/atmosphere.pyx"
include "soya3d/raypick.pyx"
include "soya3d/coordsyst.pyx"
include "soya3d/volume.pyx"
include "soya3d/world.pyx"
include "soya3d/light.pyx"
include "soya3d/camera.pyx"
include "soya3d/portal.pyx"
include "soya3d/traveling_camera.pyx"

include "model/image.pyx"
include "model/material.pyx"
#include "model/blend_materials.pyx"
include "model/face.pyx"
include "model/shape.pyx"
include "model/solid_shape.pyx"
include "model/cellshading.pyx"
include "model/tree.pyx"
include "model/sprite.pyx"
include "model/particle.pyx"
include "model/land.pyx"
include "model/watercube.pyx"
include "model/shapifier.pyx"

# Cal3D stuff
#include "cal3d/cal3d.pxd"
include "cal3d/shape.pyx"
include "cal3d/volume.pyx"

# Text stuff
#include "text/freetype.pxd"
include "text/text.pyx"

#include "shader/shader.pyx"
