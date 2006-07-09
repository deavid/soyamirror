# -*- indent-tabs-mode: t -*-

# Soya 3D tutorial
# Copyright (C) 2001-2004 Jean-Baptiste LAMY
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


# deform-1: Model deforming : 


# Imports sys, os modules and the Soya module.

import sys, os, os.path, math, soya

# Initializes Soya (creates and displays the 3D window).

soya.init()

soya.path.append(os.path.join(os.path.dirname(sys.argv[0]), "data"))

scene = soya.World()

sword_model = soya.Model.get("sword")

sword = soya.Body(scene, sword_model)
sword.x = 1.0
sword.rotate_y(90.0)

class MyDeform(soya.PythonDeform):
	def deform_point(self, x, y, z):
		return x, y, z + 0.3 * math.sin(0.1 * self.time + 5.0 * y)
	
deform = MyDeform()
sword.add_deform(deform)


light = soya.Light(scene)
light.set_xyz(0.5, 0.0, 2.0)

camera = soya.Camera(scene)
camera.z = 2.0
soya.set_root_widget(camera)

soya.MainLoop(scene).main_loop()

