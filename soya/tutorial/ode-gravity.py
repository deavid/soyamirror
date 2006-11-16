# -*- indent-tabs-mode: t -*-

import sys, os

import soya



soya.init("first ODE test",width=1024,height=768)

soya.path.append(os.path.join(os.path.dirname(sys.argv[0]), "data"))


# create a world
scene = soya.World()
# load a model
head_model = soya.Model.get("caterpillar_head")
# instanciate two Body
heads = [ soya.Body(scene,head_model) for i in xrange(2)]
# adding two mass
for head in heads:
    head.mass = soya.SphericalMass()
# Setting the gravity of the scene
scene.gravity = soya.Vector(scene,0,-9.8,0)
#Set whether the body is influenced by the world's gravity
#or not. If body.gravity_mode is True it is, otherwise it isn't.
#(default to True)
heads[0].gravity_mode = False
heads[1].gravity_mode = True
#place the head
heads[0].x=-3
heads[0].x= 3

#light and camera stuff
light = soya.Light(scene)
light.set_xyz(30, 5, -30)

camera = soya.Camera(scene)
camera.z = 25

soya.set_root_widget(camera)
ml = soya.MainLoop(scene)
ml.main_loop()
