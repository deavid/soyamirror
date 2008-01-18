# -*- indent-tabs-mode: t -*-
# -*- coding: utf-8 -*-

# Soya 3D
# Copyright (C) 2007 Jean-Baptiste LAMY -- jiba@tuxfamily.org
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

import sys, os, os.path, random
import soya, soya.gui
import soya.widget

soya.path.append(os.path.join(os.path.dirname(sys.argv[0]), "data"))

soya.init(width = 640, height = 480)


red = soya.Material()
red.diffuse = (1.0, 0.0, 0.0, 1.0)

root  = soya.gui.RootLayer(None)
import soya.cube
scene = soya.World()
light = soya.Light(scene)
light.set_xyz(0.5, 0.0, 2.0)
camera = soya.Camera(scene)
camera.z = 2.0
camera.partial = 1
cube = soya.cube.Cube(scene, red)
cube.advance_time = lambda proportion: cube.rotate_lateral(proportion)
soya.gui.CameraViewport(root, camera)

window = soya.gui.Window(root, u"Soya GUI demo: window over camera", closable = 0)
table = soya.gui.VTable(window)
soya.gui.CancelButton(table, u"Quit", on_clicked = sys.exit)

print root.widgets

soya.set_root_widget(root)
soya.MainLoop(scene).main_loop()

