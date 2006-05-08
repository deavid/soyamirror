#!/usr/bin/env python

"""
this is basic pudding script demonstrating anchors and containers
"""

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

light = soya.Light(scene)
light.set_xyz( .5, 0., 2.)

camera = soya.Camera(scene)
camera.z = 2.

# we use a special root widget as a small compatability layer

# the width and height can actually be anything you want if using 
# anchors as the widgets will be resized.
# basically, if you set here the width and height at 640,480
# and then layout your components based on that
# when the app is run the components should be positined correctly
# whatever the window size 

w = pudding.core.RootWidget(width = 640,height = 480)

# create a vertical container
c = pudding.container.VerticalContainer(w, left=10, top=10, width=300, height=200)
c.right = 10

# here we' set the anchors. anchors make resizable screen components a doddle
# here we anchor all but the bottom to make a sort of title bar
c.anchors =  pudding.ANCHOR_RIGHT | pudding.ANCHOR_TOP | pudding.ANCHOR_LEFT

# add a button 
# the last argument indicates if the object is free to expand with the container
d = c.add_child(pudding.control.Button(label = 'Button'), 1)
# set the background color for show
d.background_color = (0., 1., 0., 1.)

# add another button but this time specifiy that its not free to grow excpet in the
# horizontal
d = c.add_child(pudding.control.Input(height = 40, initial = 'input'), pudding.EXPAND_HORIZ)
d.background_color = (1., 0., 0., 1.)

# add another container
# this time with one exapanding button and one button that doesnt expand at all
c = pudding.container.HorizontalContainer(w, left=10, top=210, width=300, height=200)
c.bottom = 10

# this time we just anchor one side 
c.anchors = pudding.ANCHOR_BOTTOM

d = c.add_child(pudding.control.Button(label = 'Button'), pudding.EXPAND_BOTH)
d.background_color = (0., 1., 0., 1.)
d = c.add_child(pudding.control.Button(width = 20,height = 20, label = ''))
d.background_color = (1., 0., 0., 1.)

w.add_child(camera)

soya.set_root_widget(w)

pudding.idler.Idler(scene).idle()

