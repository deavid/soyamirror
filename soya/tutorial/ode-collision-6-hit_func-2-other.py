# -*- indent-tabs-mode: t -*-

# the hit function take arguments, the first one is the body you collide and the
# second is a list of Contact object containing information about the Point of contact
# 
# In this more complex scene Head will tell who they hit when collision occured

import sys, os
from random import choice
import soya
from soya import Vector






soya.init("first ODE test",width=1024,height=768)

soya.path.append(os.path.join(os.path.dirname(sys.argv[0]), "data"))

class PoliteHead(soya.Body):
	head_model = soya.Model.get("caterpillar_head")
	sentences = [
		"<%s> Oups sorry *%s*!",
		"<%s> Damned I hit *%s*",
		"<%s> excuse me *%s*. I hope I didn't hurt you",
		"<%s> *%s*! please mind you step !",
		"<%s> ho I did see you *%s* how. are you ?",
		
		]
	def __init__(self,parent,name):
		soya.Body.__init__(self,parent,self.head_model)
		self.name = name
	def hit(self,other,*args,**kargs):
		print choice(self.sentences)%(self.name,other.name)

################################################################################
scene = soya.World()
a_mass = 8
c_m    = 7
d_m    = 2
head_model = soya.Model.get("caterpillar_head")
head_a = PoliteHead(scene,"Pat")
head_a.mass = soya.SphericalMass(a_mass,1,"total_mass")
head_b = PoliteHead(scene,"Lili")
head_b.mass = soya.SphericalMass(3,1,"total_mass")
head_c = PoliteHead(scene,"Sam")
head_c.mass = soya.SphericalMass(c_m,1,"total_mass")
head_d = PoliteHead(scene,"Mike")
head_d.mass = soya.SphericalMass(d_m,1,"total_mass")


head_a.add_force(soya.Vector(head_a,15,34,56)*a_mass)#,soya.Vector(head_a,0.4,0.3,0.2))
head_a.add_force(soya.Vector(scene,-150,1,-505)*a_mass)
head_a.set_xyz(20,-5,0)
head_a.turn_y(30)

head_b.x = 1.0

head_b.add_force(Vector(head_b,0,0,-1368),Vector(head_b,0.0001,0.0002,0.0003))

head_c.set_xyz(-4.5,2.7,-77)
head_c.turn_y(180)

head_d.set_xyz(1,-50,-60)
head_d.turn_x(90)
head_d.add_force(soya.Vector(scene,0,350,-40)*d_m,soya.Vector(head_d,0.001,0.0015,0.002))

light = soya.Light(scene)
light.set_xyz(30, 5, -30)

camera = soya.Camera(scene)
camera.set_xyz(1,50,-40)
camera.turn_x(-90)

scene.gravity = soya.Vector(scene,0.0005,-0.03,2)
for head in (head_a,head_b,head_c,head_d,):
	soya.GeomSphere(head,1.2)
print "scene built"

soya.set_root_widget(camera)
ml = soya.MainLoop(scene)
ml.main_loop()
