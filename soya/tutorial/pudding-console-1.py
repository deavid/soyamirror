#!/usr/bin/env python

import sys, os

import soya
import soya.pudding as pudding
import soya.pudding.sysfont

soya.init()
soya.path.append(os.path.join(os.path.dirname(sys.argv[0]), "data"))

# initialise pudding
pudding.init()

# with a little code borred from pygame we can get a decent list of the system fonts
print "Available fonts are :", pudding.sysfont.get_fonts()

myfont = soya.Font(pudding.sysfont.SysFont('serif, freeserif'), 15, 15 )
print "Choosen font :", myfont

scene = soya.World()

sword_model = soya.Shape.get("sword")
sword = soya.Volume(scene, sword_model)
sword.x = 1
sword.rotate_lateral(90.)

# one line rotation :)
sword.advance_time = lambda p: sword.rotate_lateral(5.*p)

camera = soya.Camera(scene)
camera.z = 2

# we use a special root widget as a small compatability layer
root = pudding.core.RootWidget(width = 640, height = 480)
soya.set_root_widget(root)

panel = pudding.control.Panel(root, left = 10, top = 10, label = "console")
panel.right = 10
panel.bottom = 100
panel.anchors = pudding.ANCHOR_ALL

msg = """pudding version : %s
---------------------------------
most of layout of this page is done using anchors.
type text and press enter to "send"
see how you can only type when the mouse is over the console window?

we also use the wrap flag to wrap really long lines.. you know that reminds me of a time when my great great grandmother was showing my uncle how to suck eggs...

also checkout pudding.sysfont as it can query available system fonts.

now go make a soya pudding :)

""" % pudding.__revision__

console = pudding.control.Console(panel, left=10, top=30, initial = msg)
console.right=10
console.bottom=10
console.anchors = pudding.ANCHOR_ALL
console.output.font = myfont

root.add_child(camera)

# we need to do this to force the layout to refresh
root.on_resize()

pudding.idler.Idler(scene).idle()

