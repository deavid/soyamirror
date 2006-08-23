# -*- indent-tabs-mode: t -*-

# the hit function take arguments, the first one is the body you collide and the
# second is a list of Contact object containing information about the Point of contact
# 
# In this tutorial you will learn to use the second argument.
# this argument are the list of all Contact betwen self and other this contact
# have many usefull attribut descripting the Contact. This time We are using the
# pos attribut to find the position of the contact and create some particule

import sys, os
from random import choice, gauss as normalvariate, randint, random, expovariate
from math import sqrt
import soya
import soya.widget
from soya import Vector

soya.init("first ODE test",width=1024,height=768)

soya.path.append(os.path.join(os.path.dirname(sys.argv[0]), "data"))
scene = soya.World()

class Nova(soya.Smoke):
	def __init__(self,parent,nb_particles=12):
		soya.Smoke.__init__(self,parent,nb_particles=nb_particles)
		#self.set_colors((1.0, 1.0, 1.0, 1.0), (1.0, 0.0, 0.0,0.5),(1.0,1.0,0.,0.5),(0.5,0.5,0.5,0.5),(0.,0.,0.,0.5))
		#self.set_sizes ((0.19, 0.19), (0.35, 0.35))
		#self.auto_generate_particle=1
	def added_into(self,parent):
		#print 'former:',self.parent
		if self.parent is not None:
			self.parent.parent.remove(self.parent)
		soya.Smoke.added_into(self,parent)
		
	def generate(self, index):
		sx = (random()- 0.5)
		sy = (random()-0.5)
		sz = (normalvariate(0,0.1))
		l  = self.speed * (0.2 * (1.0 + random())) / sqrt(sx * sx + sy * sy + sz * sz) * 0.4 * self.matrix[16]
		lb  = self.life
		lf = self.life_function
		a = self.acceleration
		sx=sx*l
		sy=sy*l
		sz=sz*l
		#print sz
		self.set_particle(index, (1 + lf())*lb, sx, sy, sz, sx*a, sy*a, sz*a)
		


class BouncingHead(soya.Body):
	head_model = soya.Model.get("caterpillar_head")
	tmp_vect = Vector(scene)
	def __init__(self,parent):
		soya.Body.__init__(self,parent,self.head_model)
	def begin_round(self):
		soya.Body.begin_round(self)
		self.tmp_vect.set_xyz(-self.x,-self.y,-self.z)
		self.add_force(self.tmp_vect)
	def hit(self,other,contacts):
		s = self.linear_velocity.length()
		s = (s**2/200.)
		es= 0.1+(s**2)
		l = 1+(150*s)
		a = -0.0001/(1+l)
		#print s
		for contact in contacts:
			w=soya.World(scene)
			w.look_at(contact.normal)
			w.move(contact.pos)
			p = Nova(w)
			p.particle_coordsyst = w
			#p = soya.Fountain(scene)
			p.removable = True
			p.speed = es
			p.life  = l
			p.acceleration = a
			p.set_sizes((0.2, 0.2), (0.3, 0.3))
			p.set_colors((0.9,0.9,0.35,0.9),(0.95,0.95,0.40,0))

heads = []
for i in range(100):
	b = BouncingHead(scene)
	b.mass = soya.SphericalMass((3+random()*15)**3,1,"total_mass")
	soya.GeomSphere(b,1.2).bounce = random()
	b.set_xyz(normalvariate(0,150),normalvariate(0,150),normalvariate(0,150))
	b.look_at(scene)
	heads.append(b)


light = soya.Light(scene)
light.set_xyz(30,30,30)

main = soya.widget.Group()
camera = soya.Camera(scene)
camera.set_xyz(0,0,70)
camera.back = 300
fps = soya.widget.FPSLabel(main)
print fps.get_color()
fps.set_color((0.5,0.5,0.5,0.5))
main.add(camera)
main.add(fps)
	
print "scene built"

soya.set_root_widget(main)
ml = soya.MainLoop(scene)
ml.main_loop()
