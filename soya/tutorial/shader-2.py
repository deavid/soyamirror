# -*- indent-tabs-mode: t -*-

# Soya 3D tutorial
# Copyright (C) 2001-2010 Jean-Baptiste LAMY
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


# shader-2: fragment shader : displaying a 3D model

# Imports sys, os modules and the Soya module.

import sys, os, os.path, soya

# Initializes Soya (creates and displays the 3D window).

soya.init()

soya.path.append(os.path.join(os.path.dirname(sys.argv[0]), "data"))

# Creates a scene.

scene = soya.World()

# Loads the sword model (from file "tutorial/data/models/sword.data").

sword_model = soya.Model.get("sword")

# Create the model.
		
sword = soya.Body(scene, sword_model)
sword.x =  1.0
sword.y = -1.0
sword.rotate_y( 90.0)
sword.rotate_z(-90.0)

normal_sword = soya.Body(scene, sword_model)
normal_sword.x = -1.0
normal_sword.y = -1.0
normal_sword.rotate_y( 90.0)
normal_sword.rotate_z(-90.0)

# Creates a light and a camera.

light = soya.Light(scene)
light.set_xyz(0.5, 0.0, 2.0)
camera = soya.Camera(scene)
camera.z = 2.0
soya.set_root_widget(camera)

soya.render()



# Basic No-op shader that render textures and colors :
shader_code = """!!ARBfp1.0
TEMP color;
TEX color, fragment.texcoord[0], texture[0], 2D;
MUL result.color, color, fragment.color;

END
"""

# Magic effect shader :

shader_code = """!!ARBfp1.0
TEMP angle;
TEMP angle2;
TEMP color;

MUL angle, program.local[0], 0.1;
MUL angle2, fragment.position.y, 0.03;
ADD angle, angle, angle2;


# Code generated by Cg for computing sinus and cosinus
PARAM c[4] = { { 1, -24.980801, 60.145809, 0.15915491 },
		{ 0.25, 0.5, 0.75, 1 },
		{ -85.453789, 64.939346, -19.73921, 1 },
		{ 1, -1 } };
TEMP R0;
TEMP R1;
TEMP R2;
TEMP sincos;
MOV R0.x, c[0].w;
MUL R0.x, R0, angle;
FRC R1.z, R0.x;
SLT R0, R1.z, c[1];
ADD R2.xyz, R0.yzww, -R0;
MOV R0.yzw, R2.xxyz;
DP3 R1.x, R2, c[1].yyww;
DP4 R1.y, R0, c[1].xxzz;
ADD R1.xy, R1.z, -R1;
MUL R2.xy, R1, R1;
MUL R2.zw, R2.xyxy, R2.xyxy;
MUL R1, R2.zzww, c[0].yzyz;
ADD R1, R1, c[2].xyxy;
MAD R1, R1, R2.zzww, c[2].zwzw;
MAD R1.xy, R1.xzzw, R2, R1.ywzw;
DP4 R1.w, R0, c[3].xxyy;
DP4 R1.z, R0, c[3].xyyx;
MUL sincos, R1.wzzw, R1.yxzw;
#sin = sincos.x,  cos = sincos.y

#MUL sincos.x, sincos.x, 0.5;
#ADD sincos.x, sincos.x, 0.5;
ADD sincos.x, sincos.x, 1.0;
#MUL sincos.x, sincos.x, 0.5;

RSQ sincos.x, sincos.x;
ADD sincos.x, sincos.x, -1.0;

TEX color, fragment.texcoord[0], texture[0], 2D;

TEMP color2;
PARAM d = { 0.7, 0.2, 1.0, 1.0 };

MUL color2, d, sincos.x;
ADD result.color, color, color2;
END
"""


shader = soya.ARBShaderProgram(soya.SHADER_TYPE_FRAGMENT, shader_code)

sword.add_deform(shader())


# Uncomment this line to save a 320x240 screenshot in the results directory.

#soya.render(); soya.screenshot().resize((320, 240)).save(os.path.join(os.path.dirname(sys.argv[0]), "results", os.path.basename(sys.argv[0])[:-3] + ".jpeg"))

# Creates an 'MainLoop' for the scene.

soya.MainLoop(scene).main_loop()


