# -*- indent-tabs-mode: t -*-

# In this tutorial we'll learn how made soya detect collision with ODE
# 
# Our example is to simple head going on eatch other
#
# To enable ODE's collision detection, you only have create a Geom for bodys 
# you want to collide. here we use : "GeomSphere(body,radius)"

import sys, os
import soya

soya.init("collision-1-base",width=1024,height=768)
soya.path.append(os.path.join(os.path.dirname(sys.argv[0]), "data"))

# create world
scene = soya.World()
# getting the head model
head_model = soya.Model.get("caterpillar_head")
# creating two head
heads = (
	soya.Body(scene,head_model),
	soya.Body(scene,head_model))
## Adding a mass ##
for head in heads:
	head.mass = soya.SphericalMass()
### Creating a Geometry object __for each__ Body###
soya.GeomSphere(heads[0],1.2)
soya.GeomSphere(heads[1],1.2)
######
#placing the body face to face
heads[0].x = -25
heads[1].x = 25
heads[0].look_at(heads[1])
heads[1].look_at(heads[0])
#pushing them forward
for head in heads:
	head.add_force(soya.Vector(head,0,0,-500))

#placing light over the duel
light = soya.Light(scene)
light.set_xyz(0, 15,0)
# adding camera
camera = soya.Camera(scene)
camera.set_xyz(0,0,50)
#running soya
soya.set_root_widget(camera)
ml = soya.MainLoop(scene)
ml.main_loop()
