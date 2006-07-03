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

# Import base C lib

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
include "main_loop.pyx"

include "soya3d/atmosphere.pyx"
include "soya3d/raypick.pyx"
include "soya3d/coordsyst.pyx"
include "soya3d/body.pyx"
include "soya3d/world.pyx"
include "soya3d/light.pyx"
include "soya3d/camera.pyx"
include "soya3d/portal.pyx"
include "soya3d/traveling_camera.pyx"

include "model/image.pyx"
include "model/material.pyx"
#include "model/blend_materials.pyx"
include "model/face.pyx"
include "model/model.pyx"
include "model/solid_model.pyx"
include "model/cellshading.pyx"
include "model/tree.pyx"
include "model/sprite.pyx"
include "model/particle.pyx"
include "model/terrain.pyx"
include "model/model_builder.pyx"

# Cal3D stuff
include "cal3d/model.pyx"
#include "cal3d/body.pyx"

# Text stuff
include "text/text.pyx"

# Optional modules
include "config.pyx"

#include "shader/shader.pyx"
