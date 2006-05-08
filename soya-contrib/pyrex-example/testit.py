# simple test for our pyrex module.

import sys
import os

import soya

# importing our test module here will fail unless we add the path to the 
# _soya.so file into sys.path 

# so here we use the soya modules __file__ attribute to obtain the correct
# path to add

sys.path.append( os.path.dirname(soya.__file__))

# now importing test will be ok 

import test

# the rest of this file does nothing you shouldnt know already 

soya.init()

scene=soya.World()

a=test.AxesMarker(scene)

camera=soya.Camera(scene)
camera.z=5.
camera.y=4
camera.x=3

camera.look_at(a)

soya.set_root_widget(camera)

soya.Idler(scene).idle()
