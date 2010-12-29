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


# shader-4: shader : loading a shader from a file

# Shaders can be loaded from files, like many other Soya objects.
# Notice that an object with a shader on it cannot be saved or loaded, until
# the shader is defined in a file !
# Soya does NOT serialize shader's code, for obvious security reason !


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

# Loads the shader from shader/magic_sword.txt

shader = soya.ARBShaderProgram.get("magic_sword.txt")

sword.add_deform(shader())


# Uncomment this line to save a 320x240 screenshot in the results directory.

#soya.render(); soya.screenshot().resize((320, 240)).save(os.path.join(os.path.dirname(sys.argv[0]), "results", os.path.basename(sys.argv[0])[:-3] + ".jpeg"))

# Creates an 'MainLoop' for the scene.

soya.MainLoop(scene).main_loop()


