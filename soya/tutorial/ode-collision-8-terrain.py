# -*- indent-tabs-mode: t -*-

# the hit function take arguments, the first one is the body you collide and the
# second is a list of Contact object containing information about the Point of contact
# 
# In this more complex scene Head will tell who they hit when collision occured

import sys, os
from random import choice, gauss as normalvariate, randint, random, expovariate
import soya
import soya.widget
from soya import Vector






soya.init("first ODE test",width=1024,height=768)
soya.path.append(os.path.join(os.path.dirname(sys.argv[0]), "data"))
scene = soya.World()

# Gets the image "map1.png" from the tutorial data dir, and create the terrain
# from this image. The image dimension must be power of 2 plus 1 : (2 ** n) + 1.
terrain = soya.Terrain(scene)
print "setting terrain's image"
terrain.from_image(soya.Image.get("map3.png"))

# By default, the terrain height ranges from 0.0 (black pixels) to 1.0 (white pixels).
# Here, we multiply the height by 4.0 so it ranges from 0.0 to 4.0.

print "multiplying height"
terrain_height =  100.
terrain.multiply_height(terrain_height)

# Now that we have the terrain, we are going to texture it
# (see lesson modeling-material-2 about texturing). First, we creates two textured
# materials.

print "making materials"
block  = soya.Material(soya.Image.get("block2.png"))
metal  = soya.Material(soya.Image.get("metal1.png"))
grass  = soya.Material(soya.Image.get("grass.png"))
ground = soya.Material(soya.Image.get("ground.png"))
print "setting terrain's materials"
terrain.set_material_layer(ground, 0.0, 5*terrain_height/12.)
#terrain.set_material_layer(grass, 7*terrain_height/12., 5*terrain_height/6.)
terrain.set_material_layer_angle(ground, 0.0, terrain_height, 45, 90)
terrain.set_material_layer_angle(grass, 5*terrain_height/12, terrain_height, 0.0, 45)

terrain.texture_factor = 1.0

# XXX for some reason collisions don't work if this is set to anything other
# than 1.0
terrain.scale_factor   = 1.0
terrain.split_factor   = 2.0
terrain.geom = True
print 'terrain.geom :',terrain.geom
#g = soya._GeomTerrain(terrain)




class Head(soya.Body):
	model = soya.Model.get("caterpillar_head")
	def __init__(self,parent):
		soya.Body.__init__(self,parent, self.model)
		self.mass = soya.SphericalMass(5,1,"total_mass")
		self.geom = soya.GeomSphere(self,1.2)
		
	#def hit(self,other, contacts):
		#for contact in contacts:
		#	contact.bounce*=10
		#print len(contacts)


head_a = Head(scene)
head_a.set_xyz(77, terrain_height, 20)
#head_a.add_force(soya.Vector(scene,-100,-120,-140))
head_b = Head(scene)
head_b.set_xyz(75, terrain_height-10, 22)
#head_b.add_force(soya.Vector(scene,-120,-110,-140))
head_c = Head(scene)
#head_c.add_force(soya.Vector(scene,-131,-134,-130))
head_c.set_xyz(79, terrain_height+10, 18)

head_c.bounce=1
head_b.bounce=1
head_a.bounce=1

scene.gravity = soya.Vector(scene,0,-19,0)


light = soya.Light(scene)
light.set_xyz(100,70,100)

main = soya.widget.Group()
camera = soya.Camera(scene)
camera.set_xyz(125, 110,100)
#camera.turn_y(-45)#135)
#camera.turn_x(-30)
#camera.turn_z(15)
camera.look_at(soya.Point(scene,0,50,35))

camera.back = 300
fps = soya.widget.FPSLabel(main)
print fps.get_color()
fps.set_color((0.5,0.5,0.5,0.5))
main.add(camera)
main.add(fps)
	
print "scene built"
print scene.space.geoms

soya.set_root_widget(main)
class MainLoop(soya.MainLoop):
	def __init__(self,world):
		soya.MainLoop.__init__(self,world)
		self.prob = -0.03
	def begin_round(self):
		soya.MainLoop.begin_round(self)

		# wait for any keystoke to quit
		#for e in soya.process_event():
		#	if e[0]==sdlconst.KEYDOWN and e[1]!=0:
		if random() < self.prob:
			print "let's add another one \o/"
			head = Head(scene)
			head.set_xyz(98+4*random(), 5*terrain_height/6, 5+4*random())
			head.add_force(Vector(scene,-600-random()*2000,0,150+random()*500))
			self.prob -=0.03
		else:
			#print self.prob
			self.prob += 0.0003

MainLoop(scene).main_loop()
