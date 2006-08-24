# -*- indent-tabs-mode: t -*-

# the hit function take arguments, the first one is the body you collide and the
# second is a list of Contact object containing information about the Point of contact
# 
# In this tutorial you will learn to use the second argument.
# this argument are the list of all Contact betwen self and other this contact
# have many usefull attribut descripting the Contact. This time We are using the
# pos attribut to find the position of the contact and create some particule

print 'arrows: for moving'
print 'espace: for up, left control for down'
print 'clic:   firing laser'
print 'right:  clic for stronger single shot'
print "return: center the camera when you're lost"
print 'escape: quit'

import sys, os
from random import choice, gauss as normalvariate, randint, random, expovariate
from math import sqrt, pi
import soya
import soya.widget
import soya.sphere
import soya.laser
from soya import Vector, Point

if '-f' in sys.argv:
	soya.init("first ODE test",width=1280,height=854,fullscreen=True)
	soya.cursor_set_visible(False)
	soya.set_mouse_pos(1280/2,854/2)
	soya.process_event()
else:
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
materials = (	
	(soya.Material(soya.Image.get("block2.png")), (0.188235,0.141176,0.086275)),
	(soya.Material(soya.Image.get("metal1.png")), (0.329412,0.321569,0.345098)),
	(soya.Material(soya.Image.get( "grass.png")), (0.231373,0.380392,0.149020)),
	(soya.Material(soya.Image.get("ground.png")), (0.768627,0.654902,0.443137)),
	(soya.Material(soya.Image.get(  "snow.png")), (0.886275,0.901961,0.894118)),
	(soya.Material(soya.Image.get(  "lava.png")), (0.894118,0.184314,0.011765)),
	#(soya.Material(soya.Image.get(  "soustoit.png")), (0.5,0.5,0.5)),
)
models = []
for material,color in materials:
	models.append((soya.sphere.Sphere(None,material).shapify(),color))


class Ball(soya.Body):
	#ball_model = soya.Model.get("caterpillar_head")
	ball_model = ball_world = soya.sphere.Sphere(None).shapify()
	tmp_vect = Vector(scene)
	def __init__(self,parent):
		model,color=choice(models)
		soya.Body.__init__(self,parent,model)
		self.dust_color = color
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
			p.set_sizes((0.1, 0.1), (0.15, 0.15))
			p.set_colors(self.dust_color+(0.9,),self.dust_color+(0,))

heads = []
for i in range(100):
	r = (0.4+abs(normalvariate(0.7,1)))
	b = Ball(scene)
	b.mass = soya.SphericalMass(20*4*pi*(r**2),1,"total_mass")
	b.scale(r,r,r)
	soya.GeomSphere(b,1.2*r).bounce = random()
	b.set_xyz(normalvariate(0,150),normalvariate(0,150),normalvariate(0,150))
	b.look_at(scene)
	heads.append(b)


light = soya.Light(scene)
light.set_xyz(30,30,30)



class LaserCamera(soya.Camera):
	def __init__(self, parent):
		soya.Camera.__init__(self, parent)
		
		self.speed = soya.Vector(self)
		self.mouse_sensivity =2
		self.laser_vector = Vector(self,0,0.01,-1)
		self.laser_pos = Point(self,0,-1,0)
		self.laser = soya.laser.Laser(self.parent)
		self.laser.visible = self.laser_on = False
		self.laser_power = 1000
		self.single_blast = False
		
	def begin_round(self):
		soya.Camera.begin_round(self)
		events = soya.process_event()
		
		for evenement in soya.coalesce_motion_event(events) :
			# mouvement de la souris
			if  evenement[0] == soya.sdlconst.MOUSEMOTION  and (evenement[1] != self.get_screen_width()/2 and evenement[2] != self.get_screen_height()/2):
				left = (evenement[1] - self.get_screen_width()/2) * (self.mouse_sensivity-1) + evenement[1]
				top = (evenement[2] - self.get_screen_height()/2) * (self.mouse_sensivity-1) + evenement[2]
				self.look_at(self.coord2d_to_3d( left, top ))
				soya.set_mouse_pos(self.get_screen_width()/2,self.get_screen_height()/2)
		
		for event in events:
			if event[0] == soya.sdlconst.KEYDOWN:
				if   event[1] == soya.sdlconst.K_UP:     self.speed.z = -1.0
				elif event[1] == soya.sdlconst.K_DOWN:   self.speed.z =  1.0
				elif event[1] == soya.sdlconst.K_LEFT:   self.speed.x = -1.0
				elif event[1] == soya.sdlconst.K_RIGHT:  self.speed.x =  1.0
				elif event[1] == soya.sdlconst.K_SPACE:  self.speed.y =  1.0
				elif event[1] == soya.sdlconst.K_LCTRL:  self.speed.y =  -1.0
				elif event[1] == soya.sdlconst.K_q:      soya.MAIN_LOOP.stop()
				elif event[1] == soya.sdlconst.K_ESCAPE: soya.MAIN_LOOP.stop()
				elif event[1] == soya.sdlconst.K_RETURN:
					self.set_xyz(0,0,70),
					self.look_at(Point(self.parent,0,0,0))
			elif event[0] == soya.sdlconst.KEYUP:
				if   event[1] == soya.sdlconst.K_UP:     self.speed.z = 0.0
				elif event[1] == soya.sdlconst.K_DOWN:   self.speed.z = 0.0
				elif event[1] == soya.sdlconst.K_LEFT:   self.speed.x = 0.0
				elif event[1] == soya.sdlconst.K_RIGHT:  self.speed.x = 0.0
				elif event[1] == soya.sdlconst.K_SPACE:  self.speed.y = 0.0
				elif event[1] == soya.sdlconst.K_LCTRL:  self.speed.y = 0.0
			elif event[0] == soya.sdlconst.MOUSEBUTTONDOWN:
				self.laser_on = True
				self.laser.visible = True
				if event[1] == soya.sdlconst.BUTTON_RIGHT:
					self.laser_power=10000
					self.single_blast = True
			elif event[0] == soya.sdlconst.MOUSEBUTTONUP:
				self.laser_on = False
				self.laser.visible = False
				
		if self.laser_on:
			if self.laser_on:
				self.laser.move(self.laser_pos)
				self.laser.look_at(self.laser_vector)
			result = self.parent.raypick(self.laser_pos, self.laser_vector)
			if result:
				impact,normal = result
				#apply force
				target = impact.parent
				target.add_force(self.laser_vector*self.laser_power,impact)
				
				l = self.laser_power/1000.
				#reset the laser power
				self.laser_power = 1000
				#create particle
				# first corresponding to the dust of the planet
				s = soya.Smoke(self.parent)
				s.move(impact)
				s.removable = True
				s.set_colors(target.dust_color+(0.5,),target.dust_color+(0,))
				s.set_sizes((0.3, 0.3), (0.7, 0.7))
				s.life = 1
				#second the lazer beam
				s = soya.Smoke(self.parent)
				s.move(impact)
				s.removable = True
				s.life = 0.4*l
				s.speed = 1
				s.set_colors((0.121569,0.431373,0.792157,0.8),(0.121569,0.431373,0.792157,0.5+l/20.))
				s.set_sizes((0.2, 0.2), (0, 0))

		
				
				
				
	def advance_time(self, proportion):
		self.add_mul_vector(proportion, self.speed)
		if self.laser_on:
			self.laser.move(self.laser_pos)
			self.laser.look_at(self.laser_vector)
		
	def end_round(self):
		if self.single_blast:
			self.laser_on = False
			self.laser.visible = False
			self.single_blast = False





main = soya.widget.Group()
camera = LaserCamera(scene)
camera.set_xyz(0,0,100)
camera.back = 500
fps = soya.widget.FPSLabel(main)
print fps.get_color()
fps.set_color((0.5,0.5,0.5,0.5))
main.add(camera)
main.add(fps)
	
print "scene built"

soya.set_root_widget(main)
ml = soya.MainLoop(scene)
ml.main_loop()
