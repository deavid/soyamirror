#!/usr/bin/env python

"""
a test showing how simple components can be used to build more complex
controls 
"""

import sys, os

import soya
import soya.pudding as pudding

soya.init(width = 320, height = 200)
soya.path.append(os.path.join(os.path.dirname(sys.argv[0]), "data"))

# initialise pudding
pudding.init()

scene = soya.World()

sword_model = soya.Shape.get("sword")
sword = soya.Volume(scene, sword_model)
sword.y = -1
sword.x = -1.5
sword.rotate_vertical(90.)

# one line animation :)
sword.advance_time = lambda p: sword.rotate_lateral(5.*p)

light = soya.Light(scene)
light.set_xyz( .5, 0., 2.)

camera = soya.Camera(scene)
camera.z = 3.

# here we construct a simple menu item widget that highlights
# when it gets focus and calls a function when its clicked

class MenuOption(pudding.control.Label):
  def __init__(self, label, function ):
    pudding.control.Label.__init__(self, label = label)

    self.function = function

    self.color1 = (1., 1., 1., 1.)
    self.color2 = (1., 0., 0., 1.)

  def on_focus(self):
    self.color = self.color2

  def on_loose_focus(self):
    self.color = self.color1

  def on_mouse_up(self, button, x, y):
    print "click on %s" % self.label

    self.function()

    # we must return True here to stop even propgation
    return True

# some pretend menu functions 

def go_game():
  print "starting game..."

def go_menu():
  print "starting menu..."

def go_quit():
  print "quitting..."

  sys.exit()

w = pudding.core.RootWidget(width = 640,height = 480)

# make a vertical container to put our menu items in 
vc = pudding.container.VerticalContainer(w, width = 10, height = 50)
print vc.child

# make use of the right and bottom properties so we dont need
# to think about width and height 
vc.right = 10
vc.bottom = 10

# anchor the whole container so it stays the same size whatever 
# the window size
vc.anchors = pudding.ANCHOR_ALL

# add some padding so our menu items are not too close together
vc.padding = 15

# what we have now is a big invisible column covering the whole screen
# we will add the menu items, telling the container that they are a 
# fixed size and should not be expanded. This will result in all 
# the items being neatly underneath each other. Behind the scenes
# the Label control by default will adjust its width and height 
# based on its content. So to center the text we simply need to 
# pass the CENTER_HORIZ flag to the container

op1 = vc.add_child( MenuOption('Game', go_game ), pudding.CENTER_HORIZ)
op2 = vc.add_child( MenuOption('Menu', go_menu ), pudding.CENTER_HORIZ)
op3 = vc.add_child( MenuOption('Quit', go_quit ), pudding.CENTER_HORIZ)

# you can get and set options after creation too
print vc.get_child_options(op3)

w.add_child(camera)

soya.set_root_widget(w)

pudding.idler.Idler(scene).idle()

