#!/usr/bin/env python

import sys, os

import soya
import soya.pudding as pudding

soya.init()
soya.path.append(os.path.join(os.path.dirname(sys.argv[0]), "data"))

# initialise pudding
pudding.init()

scene = soya.World()

sword_model = soya.Shape.get("sword")
sword = soya.Volume(scene, sword_model)
sword.x = 1
sword.rotate_lateral(90.)

# one line rotation :)
sword.advance_time = lambda p: sword.rotate_lateral(5.*p)

light = soya.Light(scene)
light.set_xyz( .5, 0., 2.)

camera = soya.Camera(scene)
camera.z = 3.

w = pudding.core.RootWidget(width = 1024,height = 768)

button_bar = pudding.container.HorizontalContainer( w, left = 10, width= 164, height=64)
button_bar.set_pos_bottom_right(bottom = 10)
button_bar.anchors = pudding.ANCHOR_BOTTOM

d = button_bar.add_child(pudding.control.Button(label = 'Button1'), pudding.EXPAND_BOTH)
f = button_bar.add_child(pudding.control.Button(label = 'Button2'), pudding.EXPAND_BOTH)
f.right = 130

#logo = pudding.control.Logo(w, 'little-dunk.png')

w.add_child(camera)

soya.set_root_widget(w)

pudding.idler.Idler(scene).idle()

