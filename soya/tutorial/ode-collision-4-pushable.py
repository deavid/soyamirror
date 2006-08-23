# -*- indent-tabs-mode: t -*-

# The lighter body will now take it's revenge from the big one
# It will be set as no-pushable (with heads[0].pushable = False)
# Detection continue to be detected but not affect the no-pushable object which 
# continue they way normaly



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
### Setting the lighter head as no-pushable ###
heads[0].pushable = False
	
## Adding a mass ##
heads[0].mass = soya.SphericalMass()
heads[1].mass = soya.SphericalMass(8)

# Creating a Geometry object for each Body #
soya.GeomSphere(heads[0],1.2)
soya.GeomSphere(heads[1],1.2)
#
#placing the body face to face
heads[0].x = -25
heads[1].x =  25
heads[0].look_at(heads[1])
heads[1].look_at(heads[0])
heads[0].set_xyz(-25,-0.5,-0.7)
heads[1].set_xyz(25,0.4,0.8)
#pushing them forward
heads[0].add_force(soya.Vector(heads[0],0,0,-1000))
heads[1].add_force(soya.Vector(heads[1],0,0,-8000)) # the bigger body need a bigger push

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
