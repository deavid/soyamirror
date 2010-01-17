# -*- indent-tabs-mode: t -*-

import sys, os

import soya
from soya import Vector


soya.init("first ODE test",width=1024,height=768)

soya.path.append(os.path.join(os.path.dirname(sys.argv[0]), "data"))


#create world

ode_world = soya.World()
#scene = ode_world
scene = soya.World(ode_world)
#activate ODE support



sword_model = soya.Model.get("sword")

sword = soya.Body(scene,sword_model)
sword.ode = True
sword.x = 1.0
sword.z = -5

sword2 = soya.Body(scene,sword_model)
sword2.ode = True
sword2.x = 1.0
sword2.z = -3

blade = soya.BoxedMass(0.05,50,5,1)
pommeau = soya.SphericalMass(10,0.5)
pommeau.translate((2,0,0))
sword.mass = blade+pommeau

blade2 = soya.BoxedMass(0.015,50,5,1)
blade2.translate((1,0,0))
sword2.mass = blade2

joint1 = soya.HingeJoint(sword2)
joint2 = soya.HingeJoint(sword,sword2)



def v (x,y,z):
	return soya.Vector(sword,x,y,z)
sword2.add_force(v(-10,50,0),v(2,0.01,0.02))
sword.add_force(v(10,50,0),v(2,0.01,0.02))


light = soya.Light(scene)
light.set_xyz(0, 0, 15)

camera = soya.Camera(scene)
camera.set_xyz(10,1,2)
camera.look_at(sword)
camera.rotate_y(50)
camera.rotate_x(10)


scene.set_xyz(0.5,0.5,-5)

ode_world.gravity = Vector(ode_world,0,-5,0)
soya.set_root_widget(camera)
ml = soya.MainLoop(ode_world)
ml.main_loop()
