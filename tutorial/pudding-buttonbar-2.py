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

class PuddingVolume(pudding.core.Control):
  def __set_left__(self, left):
    pudding.core.Control.__set_left__(self, left)
    self.move_shape()
    
  def __set_top__(self, top):
    pudding.core.Control.__set_top(self, top)
    self.move_shape()
  
  def __init__(self, *args, **kwargs):
    pudding.core.Control.__init__(self, *args, **kwargs)
    self.shape = soya.Volume(scene, sword_model)
    self.shape.rotate_lateral(90) 
    self.shape.scale(.5, .5, .5)
    self.move_shape()

  def on_resize(self):
    self.move_shape()

  def move_shape(self):
    self.shape.move(camera.coord2d_to_3d(self.left, self.top))

w = pudding.core.RootWidget(width = 1024,height = 768)

d = PuddingVolume(w, 200, 100, 100, 100)

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

