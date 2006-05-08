#!/usr/bin/env python

import sys, os

import soya
import soya.pudding as pudding

soya.init(width = 1024, height = 768)
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

i = pudding.control.Input(w, 'sometext', top = 10, left = 10, width = 100, height = 50)

w.add_child(camera)

soya.set_root_widget(w)

pudding.idler.Idler(scene).idle()

