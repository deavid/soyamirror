#!/usr/bin/env python

import os, sys

import soya.pudding as pudding
import soya.pudding.ext.svgelements as svgelements

import soya

soya.init()
soya.path.append(os.path.join(os.path.dirname(sys.argv[0]), "data"))

e_man = svgelements.ElementManager('test.png', 'test.svg')
e_man.find_elements()
print e_man.elements

scene = soya.World()
camera = soya.Camera(scene)

soya.set_root_widget(pudding.core.RootWidget())
soya.root_widget.add_child(camera)

elimg = svgelements.ElementImage(soya.root_widget,
                                 left=0, top=0, width=0, height=0,
                                 manager=e_man, image='console')
elimg.on_resize()

svgelements.ElementImage(soya.root_widget,
                         left=0, top=elimg.height, width=0, height=0,
                         manager=e_man, image='info')

pudding.idler.Idler(scene).idle()

  
