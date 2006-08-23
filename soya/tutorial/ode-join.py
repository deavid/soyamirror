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

blade = soya.BoxedMass(0.00005,50,5,1)
pommeau = soya.SphericalMass(50,0.5)
pommeau.translate((25,0,0))
sword.mass = blade+pommeau

joint = soya.BallJoint(sword)



def v (x,y,z):
	return soya.Vector(sword,x,y,z)
sword.add_force(v(10,200,0),v(25,0.001,0.002))
sword.add_force(v(0,60,0),v(0,25,0.5))
sword.add_force(v(0,0,-2303*5),v(-25,0.0001,0.0001))

scene.turn_x = 34
scene.turn_y = 23
scene.turn_z = 12

light = soya.Light(scene)
light.set_xyz(0, 0, 15)

camera = soya.Camera(scene)
camera.set_xyz(1,1,15)


scene.set_xyz(0.5,0.5,-5)

ode_world.gravity = Vector(ode_world,0,-5,0)
soya.set_root_widget(camera)
ml = soya.MainLoop(ode_world)
ml.main_loop()
