#!/usr/bin/env python

import sys, os

import soya
import soya.pudding as pudding

soya.init(width = 640, height = 480)
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

w = pudding.core.RootWidget(width = 640,height = 480)

mypic = soya.Material( soya.Image.get('grass.png'))

grass = pudding.control.Image(w, mypic, left=0, top = 0, width = 320, height=480)
grass.anchors = pudding.ANCHOR_ALL

logo = pudding.control.Logo(w, 'little-dunk.png')

w.add_child(camera)

soya.set_root_widget(w)

pudding.idler.Idler(scene).idle()

