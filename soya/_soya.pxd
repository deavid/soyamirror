# -*- indent-tabs-mode: t -*-

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

include "c.pxd"
include "python.pxd"
include "c_opengl.pxd"
include "sdl.pxd"




include "chunk.pxd"
include "list.pxd"
include "definitions/base.pxd"
include "matrix.pxd"
include "definitions/math3d.pxd"
include "definitions/renderer.pxd"
include "definitions/main_loop.pxd"


# definition/ode/
include "definitions/ode/ctype.pxd"
include "definitions/ode/const.pxd"
include "definitions/ode/mass.pxd"
include "definitions/ode/joints.pxd"
include "definitions/ode/geom.pxd"
include "definitions/ode/geom-primitive.pxd"
include "definitions/ode/geom-terrain.pxd"
include "definitions/ode/space.pxd"
include "definitions/ode/contact.pxd"



# soya3d user manipulated stuff
include "definitions/soya3d/atmosphere.pxd"
include "definitions/soya3d/raypick.pxd"
include "definitions/soya3d/coordsyst.pxd"
include "definitions/soya3d/body.pxd"
include "definitions/soya3d/world.pxd"
include "definitions/soya3d/light.pxd"
include "definitions/soya3d/camera.pxd"
include "definitions/soya3d/portal.pxd"
include "definitions/soya3d/traveling_camera.pxd"

#soya stuff (but more insternal)
include "definitions/model/image.pxd"
include "definitions/model/material.pxd"
include "definitions/model/face.pxd"
include "definitions/model/model.pxd"
include "definitions/model/cellshading.pxd"
include "definitions/model/tree.pxd"
include "definitions/model/sprite.pxd"
include "definitions/model/particle.pxd"
include "definitions/model/terrain.pxd"
include "definitions/model/model_builder.pxd"
include "definitions/model/deform.pxd"


# Cal3d stuff
include "cal3d/cal3d.pxd"
include "cal3d/model.pxd"
#include "cal3d/body.pxd"

# Text related stuff
include "text/freetype.pxd"
include "text/text.pxd"

include "definitions/model/splited_model.pxd"
include "definitions/soya3d/bsp_world.pxd"

include "config.pxd"
