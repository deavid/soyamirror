#!/usr/bin/env python

import sys, os

import soya
import soya.pudding as pudding

import pudding.ext.meter

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

soya.set_root_widget(pudding.core.RootWidget())

meter = pudding.ext.meter.Meter(soya.root_widget, min=0, max=100,
                                left=10, top=10, width=100, height=20)
meter.border_color = (1, 1, 1, 1)

# meterplus = pudding.ext.meter.MeterPlus(soya.root_widget, "health:", 
#                                         top = 10, width = 200,
#                                         height = 20)
# meterplus.set_pos_bottom_right(right = 10)
# meterplus.anchors = pudding.ANCHOR_TOP_RIGHT
# meterplus.meter.border_color = (1, 1, 1, 1)
# meterplus.label.color = meterplus.meter.border_color

soya.root_widget.add_child(camera)

pudding.idler.Idler(scene).idle()

