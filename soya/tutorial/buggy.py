# -*- indent-tabs-mode: t -*-

#!/usr/bin/env python
# Soya 3D tutorial
# Copyright (C) 2004      Jean-Baptiste 'Jiba'  LAMY
# Copyright (C) 2001-2002 Bertrand 'blam!' LAMY
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

# buggy: ODE

# Need pi and stuff
from math import *

# Imports and inits Soya (see lesson basic-1.py).

import sys, os, os.path, soya, soya.sdlconst as sdl
from soya import ode

soya.init()
soya.path.append(os.path.join(os.path.dirname(sys.argv[0]), "data"))

# Creates the scene.
scene = ode.World()
scene.gravity = (0.0, -9.8, 0.0)

# Create a collision space
print "creating space"
space = ode.HashSpace(scene)

# Creates a new terrain in the scene.
print "creating terrain"
terrain = soya.Terrain(scene)

# Gets the image "map1.png" from the tutorial data dir, and create the terrain
# from this image. The image dimension must be power of 2 plus 1 : (2 ** n) + 1.

print "setting terrain's image"
terrain.from_image(soya.Image.get("map1.png"))

# By default, the terrain height ranges from 0.0 (black pixels) to 1.0 (white pixels).
# Here, we multiply the height by 4.0 so it ranges from 0.0 to 4.0.

print "multiplying height"
terrain.multiply_height(1.0)

# Now that we have the terrain, we are going to texture it
# (see lesson modeling-material-2 about texturing). First, we creates two textured
# materials.

print "making materials"
material1 = soya.Material(soya.Image.get("block2.png"))
material2 = soya.Material(soya.Image.get("metal1.png"))

# asigns MATERIAL1 to any point whose height is in the range 0.0-6.0, and material2 to
# any point whose height is in the range 6.0-8.0 (remember, height ranges from 0.0 to 8.0).

print "setting terrain's materials"
terrain.set_material_layer(material1, 0.0, 3.0)
terrain.set_material_layer(material2, 3.0, 4.0)

# Assigns material1 to any point whose height is in the range 0.0-8.0 and if the angle
# between the surface normal and the verticalvector is in the range 0.0-20.0.

#terrain.set_material_layer_angle(material1, 0.0, 8.0, 0.0, 20.0)

# Now we set some Terrain attributes:
#  - texture_factor specifies how much the textures are zoomed (higher values mean
#    smaller texture)

#  - scale_factor specifies how the terrain is scaled in the 2 horizontal dimensions.

#  - the 2 last attributes influence the behaviour of the level of detail (LOD) algorithm
#    (LOD means that parts of the terrain are rendered with more detail / more triangle
#    if they are close to the camera). They are a trading between speed and quality.
#    
#    The higher split_factor is, the better precision you have (it means more triangles
#    to draw the Terrain even far from Camera).

# the values below are the default ones.
 
terrain.texture_factor = 1.0

# XXX for some reason collisions don't work if this is set to anything other
# than 1.0
terrain.scale_factor   = 1.0

terrain.split_factor   = 2.0

# Moves the terrain.
terrain.y = -2.5
#terrain.scale(8.0, 1.0, 8.0)
# Make sure not to modify the terrain once the simulation starts, because
# the AABB is not recalculated
terrain_geom = ode.GeomTerrain(terrain, space)
terrain_geom.set_xyz(0.0, -2.5, 0.0)
#terrain_geom = ode.Terrain(terrain, space)
#print terrain_geom.getAABB()

# Adds a light.

light = soya.Light(scene)
light.set_xyz(0.0, 30.0, 0.0)

class Car(ode.Body):
		speed = 3.0

		def __init__(self, scene):

				# Set initial turn angle to 0
				# XXX should do Ackerman steering and probably differential
				# drive on the rear wheels
				self.turn_angle = 0.0

				print "making SimpleSpace"
				self.space = ode.SimpleSpace(None, space)
				print "setting car's model"
				car_model = soya.Model.load("buggy_chassis")
				print "Initializing body"
				ode.Body.__init__(self, scene, model=car_model)

				print "Creating chassis geom"
				#self.chassis_geom = ode.GeomModel(self, self.space)
				
				print "setting car's mass"
				car_mass = ode.Mass()
				car_mass.setBox(1.0, 5.0, 2.0, 4.0)
				car_mass.adjust(7.0)
				
				self.mass = car_mass

				print "making wheel mass object"
				# Create the wheels
				wheel_model = soya.Model.load("wheel4")
				wheel_mass = ode.Mass()
				wheel_mass.setSphere(1.0, 1.0)
				wheel_mass.adjust(1.0)
				
				self.wheels = []
				# Make sure the wheel geoms don't get garbage collected
				# XXX this shouldn't be necessary
				self.wheel_geoms = []
				print "making wheels"
				for i in range(4):
						wheel = ode.Body(scene, model=wheel_model)
						wheel.mass = wheel_mass
						wheel_geom = ode.GeomSphere(wheel, self.space, 1.0)
						#wheel_geom = ode.GeomModel(wheel, space)
						self.wheel_geoms.append(wheel_geom)
						self.wheels.append(wheel)
				
				print "setting wheels' positions"
				self.wheels[0].set_xyz(2.5, 0.0, -2.0)
				self.wheels[1].set_xyz(2.5, 0.0, 2.0)
				self.wheels[2].set_xyz(-2.5, 0.0, -2.0)
				self.wheels[3].set_xyz(-2.5, 0.0, 2.0)

				self.wheel_joints = []
				for i in range(4):
						joint = ode.Hinge2Joint(scene)
						joint.attach(self, self.wheels[i])
						joint.anchor = (self.wheels[i].x, self.wheels[i].y, self.wheels[i].z)
						joint.axis1 = (0.0, 1.0, 0.0)
						joint.axis2 = (0.0, 0.0, 1.0)
						joint.suspension_erp = 0.25
						joint.suspension_cfm = 0.004
				
						joint.velocity2 = 0.0
						joint.fmax2 = 120.0
				
						# Only set stops on the back wheels. The controller for the
						# front wheels will handle them.
						if i > 2:
								joint.lo_stop = 0.0
								joint.hi_stop = 0.0

						joint.fmax = 120.0

						self.wheel_joints.append(joint)

		def begin_round(self):
				ode.Body.begin_round(self)

				for event in soya.process_event():
					if event[0] == sdl.KEYDOWN:
						if   event[1] == sdl.K_UP:
								for joint in self.wheel_joints:
										joint.velocity2 = self.speed
						elif event[1] == sdl.K_DOWN:
								for joint in self.wheel_joints:
										joint.velocity2 = -self.speed
						elif event[1] == sdl.K_LEFT:   
								self.turn_angle = -0.25 * pi
						elif event[1] == sdl.K_RIGHT:  
								self.turn_angle = 0.25 * pi
						elif event[1] == sdl.K_q:      
								soya.MAIN_LOOP.stop()
						elif event[1] == sdl.K_r:
								self.wheels[0].set_xyz(2.5, 0.0, -2.0)
								self.wheels[1].set_xyz(2.5, 0.0, 2.0)
								self.wheels[2].set_xyz(-2.5, 0.0, -2.0)
								self.wheels[3].set_xyz(-2.5, 0.0, 2.0)
						elif event[1] == sdl.K_w:
								soya.toggle_wireframe()
				
						elif event[1] == sdl.K_ESCAPE: soya.MAIN_LOOP.stop()
		
					if event[0] == sdl.KEYUP:
							if   event[1] == sdl.K_UP:
									for joint in self.wheel_joints:
											joint.velocity2 = 0.0
							elif event[1] == sdl.K_DOWN:
									for joint in self.wheel_joints:
											joint.velocity2 = 0.0
							elif event[1] in (sdl.K_LEFT, sdl.K_RIGHT):
									self.turn_angle = 0.0
					
				for i in (0, 1):
						# Steer the wheels to the desired position
						# we should do ackerman steering here
						joint = self.wheel_joints[i]
						
						v = (self.turn_angle - joint.angle1) * 10.0
						joint.velocity = v
		

print "making car"
car = Car(scene)
print "setting car's position"
car.set_xyz(32.0, 30.0, 20.0)
print "done"

camera = soya.TravelingCamera(scene)

traveling = soya.ThirdPersonTraveling(car)
#traveling = soya.ThirdPersonTraveling(soya.Point(car, 0.0, 1.0, 0.0))
traveling.distance = 15.0
#traveling.smooth_move     = 1
traveling.smooth_rotation = 0
#traveling.direction = soya.Vector(camera, 1.0, 2.0, 0.0)
#traveling.incline_as = None

camera.add_traveling(traveling)
camera.speed = 0.3
camera.set_xyz(16.0, 15.0, 0.0)
camera.look_at(car)

#camera = MovableCamera(scene)
#camera.set_xyz(16.0, 6.0, 0.0)
#camera.look_at(soya.Point(scene, 16.0, 6.0, 10.0))
soya.set_root_widget(camera)

contactgroup = ode.JointGroup()

def near_callback(g1, g2):
		"""Called for each potentially intersecting geom. Not called (right now)
		for spaces because they're handled automatically."""

		#print g1, g2

		contacts = ode.collide(g1, g2, 20)

		for contact in contacts:
				#print contact
				# Set surface parameters here
				#contact.setMu(5.0)
				joint = ode.ContactJoint(scene, contactgroup, contact)
				joint.attach(g1.body, g2.body)

		
class BuggyMainLoop(soya.MainLoop):
		"""Idle with collision testing"""

		def begin_round(self):
		
				# Eliminate all contact joints
				contactgroup.empty()

				# First, do collisions
				space.collide(near_callback)

				# Do everything else
				soya.MainLoop.begin_round(self)


print "idling"
BuggyMainLoop(scene).main_loop()

