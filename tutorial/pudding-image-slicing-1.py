#!/usr/bin/env python

import sys, os, PIL.Image

import soya
import soya.pudding as pudding
import soya.pudding.ext.slicingimage

soya.init()
soya.path.append(os.path.join(os.path.dirname(sys.argv[0]), "data"))

pudding.init()

scene = soya.World()
scene.atmosphere = soya.Atmosphere()
scene.atmosphere.bg_color = (1.0, 1.0, 1.0, 1.0)
camera = soya.Camera(scene)

w = pudding.core.RootWidget(width = 640,height = 480)

# note that the image dimensions are 312 x 132!
pil_logo = PIL.Image.open(os.path.join(os.path.dirname(__file__),
                                       'data/images/oomad.png'))
logo = pudding.ext.slicingimage.SlicingImage(w, pil_logo, left=100, top=100)

w.add_child(camera)
soya.set_root_widget(w)
pudding.idler.Idler(scene).idle()
