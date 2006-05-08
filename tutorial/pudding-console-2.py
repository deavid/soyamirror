#!/usr/bin/env python

""" a complete python console in soya """

import sys, os


import soya
import soya.pudding as pudding
import soya.pudding.python_console

soya.init(width = 800, height = 600)
soya.path.append(os.path.join(os.path.dirname(sys.argv[0]), "data"))

# initialise pudding
pudding.init()

pudding.STYLE.background_color = (.2, .2, .2, .4 )

scene = soya.World()

camera = soya.Camera(scene)

root = pudding.core.RootWidget(width = 640, height = 480)
soya.set_root_widget(root)

panel = pudding.control.Panel(root, left = 10, top = 10, label = "console")
panel.right = 10
panel.bottom = 380
panel.anchors = pudding.ANCHOR_ALL

console = pudding.python_console.PythonConsole(panel, left=10, top=30, lokals = locals())
console.right=10
console.bottom=10
console.anchors = pudding.ANCHOR_ALL
console.input.border_width = 0

root.add_child(camera)

# we need to do this to force the layout to refresh
root.on_resize()


class Idler(soya.Idler):
  def begin_round(self):
    soya.Idler.begin_round(self)

    pudding.process_event()

pudding.idler.Idler(scene).idle()

