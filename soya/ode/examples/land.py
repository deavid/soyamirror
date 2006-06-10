# -*- indent-tabs-mode: t -*-

# pyODE example 3: Collision detection
# Ported by Sean Lynch <seanl@chaosring.org> to use Soya instead of pyopengl
# This requires pygame 
# cgkit dependency eliminated
# Now uses modified pyode included with Soya. You must set USE_ODE to True in
# your setup.py file and have libode.a and ode.h in your libpath and includes
# respectively.

import soya, soya.widget

print "1"
import sys, os, random


from math import *

from soya import ode



# create_box_soya
def create_box_soya(box, lx, ly, lz):
		"""Create the graphical representation of a box in Soya."""

		lx /= 2.0
		ly /= 2.0
		lz /= 2.0
		soya.Face(box, [soya.Vertex(box,  lx,  ly,  lz, 1.0, 1.0),
								soya.Vertex(box, -lx,  ly,  lz, 0.0, 1.0),
								soya.Vertex(box, -lx, -ly,  lz, 0.0, 0.0),
								soya.Vertex(box,  lx, -ly,  lz, 1.0, 0.0),
								])
		soya.Face(box, [soya.Vertex(box,  lx,  ly, -lz, 0.0, 1.0),
								soya.Vertex(box,  lx, -ly, -lz, 0.0, 0.0),
								soya.Vertex(box, -lx, -ly, -lz, 1.0, 0.0),
								soya.Vertex(box, -lx,  ly, -lz, 1.0, 1.0),
								])
	
		soya.Face(box, [soya.Vertex(box,  lx,  ly,  lz, 1.0, 1.0),
								soya.Vertex(box, lx,  ly,  -lz, 0.0, 1.0),
								soya.Vertex(box, -lx, ly,  -lz, 0.0, 0.0),
								soya.Vertex(box, -lx, ly,  lz, 1.0, 0.0),
								])
		soya.Face(box, [soya.Vertex(box,  lx, -ly,  lz, 0.0, 1.0),
								soya.Vertex(box,  -lx, -ly,  lz, 0.0, 0.0),
								soya.Vertex(box, -lx, -ly, -lz, 1.0, 0.0),
								soya.Vertex(box, lx, -ly, -lz, 1.0, 1.0),
								])

		soya.Face(box, [soya.Vertex(box, lx,  ly,  lz, 1.0, 0.0),
								soya.Vertex(box, lx, -ly, lz, 1.0, 1.0),
								soya.Vertex(box, lx, -ly, -lz, 0.0, 1.0),
								soya.Vertex(box, lx,  ly, -lz, 0.0, 0.0),
								])
		soya.Face(box, [soya.Vertex(box, -lx, ly,  lz, 1.0, 0.0),
								soya.Vertex(box, -lx, ly, -lz, 1.0, 1.0),
								soya.Vertex(box, -lx, -ly, -lz, 0.0, 1.0),
								soya.Vertex(box, -lx, -ly, lz, 0.0, 0.0),
								])
	
	
		return box


geoms = []
# create_box
def create_box(world, space, density, lx, ly, lz):
		"""Create a box body and its corresponding geom."""

		# Create body
		body = ode.Body(world)
		M = ode.Mass()
		M.setBox(density, lx, ly, lz)
		body.mass = M

		# Set parameters for drawing the body
		#body.shape = "box"
		body.boxsize = (lx, ly, lz)

		# Create a box geom for collision detection
		geom = ode.GeomBox(space, lengths=body.boxsize)
		geom.setBody(body)
		geoms.append(geom)

		return body

# drop_object
def drop_object():
		"""Drop an object into the scene."""
		
		body = create_box(world, space, 1000, 1.0,0.2,0.2)
		#body.setPosition( (random.gauss(0,0.1),3.0,random.gauss(0,0.1)) )
		body.set_xyz(random.gauss(0,0.1),3.0,random.gauss(0,0.1))

		# Create the Soya rendition of the box
		create_box_soya(body, 1.0, 0.2, 0.2)
		#body_volume[body] = box

		#m = mat4().rotation(random.uniform(0,2*pi), (0,1,0))

		theta = random.uniform(0, 360.0)
		body.rotate_lateral(theta)
		#body.setRotation((c, 0.0, -s, 0.0, 1.0, 0.0, s, 0.0, c))
		bodies.append(body)
		#counter=0
		#objcount+=1

# explosion
def explosion():
		"""Simulate an explosion.

		Every object is pushed away from the origin.
		The force is dependent on the objects distance from the origin.
		"""

		for b in bodies:
				b.enabled = 1
				p = soya.Vector(world, b.x, b.y, b.z)
				d = p.length()
				a = max(0.0, 40000.0*(1.0-0.2*d*d))
				p = soya.Vector(world, p.x/4, p.y, p.z/4)
	p.normalize()
	p *= a
				b.addForce((p.x, p.y, p.z))

# pull
		
# Collision callback
def near_callback(args, geom1, geom2):
		"""Callback function for the collide() method.

		This function checks if the given geoms do collide and
		creates contact joints if they do.
		"""

		# Check if the objects do collide
		contacts = ode.collide(geom1, geom2)

		# Create contact joints
		world,contactgroup = args
		for c in contacts:
				c.setBounce(0.2)
				c.setMu(5000)
				j = ode.ContactJoint(world, contactgroup, c)
				j.attach(geom1.getBody(), geom2.getBody())


######################################################################

class Idler(soya.Idler):
		def __init__(self, *scenes):
				self.counter = 0
				self.state = 0
				self.objcount = 0
				soya.Idler.__init__(self, *scenes)


		def begin_round(self):
				print "."
				self.counter+=1
				# State 0: Drop objects
				if self.state==0:
						if self.counter==40:
								drop_object()
		self.counter = 0
		self.objcount += 1
						if self.objcount==30:
								self.state=1
								self.counter=0
				# State 1: Explosion and pulling back the objects
				elif self.state==1:
						if self.counter==200:
								explosion()
						if self.counter>600:
								self.pull()
						if self.counter==1000:
								self.counter=40

				#space.collide((world,contactgroup), near_callback)
				soya.Idler.begin_round(self)
				#contactgroup.empty()

				# Use pygame's event stuff instead of soya's.
				events = soya.process_event()
#         for e in events:
#             if e.type==QUIT:
#                 self.stop()
#             elif e.type==KEYDOWN:
#                 self.stop()

		def pull(self):
				"""Pull the objects back to the origin.
		
				Every object will be pulled back to the origin.
				Every couple of frames there'll be a thrust upwards so that
				the objects won't stick to the ground all the time.
				"""
		
				for b in bodies:
						b.enabled = 1
						p = soya.Vector(world, b.x, b.y, b.z)
			p.normalize()
			p *= -1000.0
						b.addForce((p.x, p.y, p.z))
						if self.counter%120==0:
								b.addForce((0,10000,0))




def main():
		global world, space, contactgroup, bodies

		# initialize soya. not sure if the order of this relative to pygame matters.
		soya.init()
		soya.path.append(os.path.join(os.path.dirname(sys.argv[0]), "..", "..", "tutorial", "data"))
		
		# create a world object
		world = ode.World()
		world.gravity = (0,-9.81,0)
		world.auto_disable = True
		#print world.__dict__
		#world.erp = 0.8
		#world.cfm = 1e-5
		
		# create a space object
		space = ode.SimpleSpace(world=world)
		
		# create a plane geom which prevent the objects from falling forever
		floor = ode.GeomPlane(space, (0,1,0), 0)
		
		# a list with ode bodies
		bodies = []
		
		# a joint group for the contact joints that are generated whenever
		# two bodies collide
		contactgroup = ode.JointGroup()
		
		# some variables used inside the simulation loop
		dt = 0.010
		#fps = int(1.0/dt)
		world.round_duration = dt
		
		# set up soya
		light = soya.Light(world)
		light.set_xyz(0.5, 4.0, 2.0)
		camera = soya.Camera(world)
		camera.x = 2.0
		camera.y = 3.0
		camera.z = 4.0
		camera.look_at(soya.Point(world, 0.0, 0.0, 0.0))
		#soya.set_root_widget(camera)
		
		# make a landscape
		land = ode.Land(world, space=space)
		land.from_image(soya.Image.get("map1.png"))
		#land.multiply_height(8.0)
		material1 = soya.Material(soya.Image.get("block2.png"))
		material2 = soya.Material(soya.Image.get("metal1.png"))
		land.set_material_layer(material1, 0.0, 0.6)
		land.set_material_layer(material2, 0.6, 0.8)
		land.texture_factor = 1.0
		land.scale_factor   = 1.0
		land.split_factor   = 2.0
		land.x = -4.0
		land.z = -4.0
		#print land.__dict__
		
		soya.set_root_widget(soya.widget.Group())
		soya.root_widget.add(camera)

		# Add an FPS label
		soya.root_widget.add(soya.widget.FPSLabel())

		idler = Idler(world)
		idler.round_duration = dt
		idler.idle()


if __name__ == '__main__':
		main()

