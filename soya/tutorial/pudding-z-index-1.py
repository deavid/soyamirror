#!/usr/bin/env python

import sys, os, PIL.Image

import soya
import soya.pudding as pudding

soya.init()
pudding.init()

scene = soya.World()
scene.atmosphere = soya.Atmosphere()
scene.atmosphere.bg_color = (1.0, 1.0, 1.0, 1.0)
camera = soya.Camera(scene)

root = pudding.core.RootWidget(width=640, height=480)

box1 = pudding.control.Box(root,
                           left=150, top=150, width=340, height=180,
                           background_color=(1.0, 0.0, 0.0, 1.0),
                           z_index=0)

box2 = pudding.control.Box(root,
                           left=100, top=100, width=200, height=280,
                           background_color=(0.0, 1.0, 0.0, 1.0),
                           z_index=-1)

box3 = pudding.control.Box(root,
                           left=340, top=100, width=200, height=280,
                           background_color=(0.0, 0.0, 1.0, 1.0),
                           z_index=1)

root.add_child(camera)
soya.set_root_widget(root)
pudding.idler.Idler(scene).idle()
