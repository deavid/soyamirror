# -*- indent-tabs-mode: t -*-

#!/usr/bin/env python

import sys, os

import soya
import soya.pudding as pudding

soya.init(width = 1024, height = 768)
soya.path.append(os.path.join(os.path.dirname(sys.argv[0]), "data"))

# initialise pudding
pudding.init()

scene = soya.World()

sword_model = soya.Model.get("sword")
sword = soya.Body(scene, sword_model)
sword.x = 1
sword.rotate_y(90.)

# one line rotation :)
sword.advance_time = lambda p: sword.rotate_y(5.*p)

light = soya.Light(scene)
light.set_xyz( .5, 0., 2.)

camera = soya.Camera(scene)
camera.z = 3.

class PuddingBody(pudding.core.Control):
	def __set_left__(self, left):
		pudding.core.Control.__set_left__(self, left)
		self.move_model()
		
	def __set_top__(self, top):
		pudding.core.Control.__set_top(self, top)
		self.move_model()
	
	def __init__(self, *args, **kwargs):
		pudding.core.Control.__init__(self, *args, **kwargs)
		self.model = soya.Body(scene, sword_model)
		self.model.rotate_y(90) 
		self.model.scale(.5, .5, .5)
		self.move_model()

	def on_resize(self):
		self.move_model()

	def move_model(self):
		self.model.move(camera.coord2d_to_3d(self.left, self.top))

w = pudding.core.RootWidget(width = 1024,height = 768)

d = PuddingBody(w, 200, 100, 100, 100)

button_bar = pudding.container.HorizontalContainer( w, left = 10, width= 164, height=64)
button_bar.set_pos_bottom_right(bottom = 10)
button_bar.anchors = pudding.ANCHOR_BOTTOM

d = button_bar.add_child(pudding.control.Button(label = 'Button1'), pudding.EXPAND_BOTH)
f = button_bar.add_child(pudding.control.Button(label = 'Button2'), pudding.EXPAND_BOTH)
f.right = 130

#logo = pudding.control.Logo(w, 'little-dunk.png')

w.add_child(camera)

soya.set_root_widget(w)

pudding.main_loop.MainLoop(scene).main_loop()

