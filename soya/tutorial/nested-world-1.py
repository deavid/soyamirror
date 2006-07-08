# -*- indent-tabs-mode: t -*-

# Soya 3D tutorial
# Copyright (C) 2001-2006 Jean-Baptiste LAMY
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


# nested-world-1: Nested worlds : a solar system

# In this lesson, we nest several worlds for modelizing a solar system.


# Imports and inits Soya.

import sys, os, os.path, soya, soya.sphere

soya.init()
soya.path.append(os.path.join(os.path.dirname(sys.argv[0]), "data"))

# Creates the scene.

scene = soya.World()

# Loads the sword model.

sword_model = soya.Model.get("sword")


# Class for CelestialObject.

class CelestialObject(soya.World):
	def advance_time(self, proportion):

		# Calls the super implementation of advance_time.
		
		soya.World.advance_time(self, proportion)
		
		# Rotates the object around Y axis. 
		
		self.rotate_y(proportion * 2.0)


# Code for creating and saving the models

# sun_material = soya.Material(soya.Image.get("lava.png"))
# sun_world = soya.sphere.Sphere(None, sun_material)
# sun_world.filename = "sun"
# sun_world.scale(0.5, 0.5, 0.5)
# sun_world.save()

# earth_material = soya.Material()
# earth_material.diffuse = (0.3, 0.7, 1.0, 1.0)
# earth_world = soya.sphere.Sphere(None, earth_material)
# earth_world.filename = "earth"
# earth_world.scale(0.2, 0.2, 0.2)
# earth_world.save()

# moon_material = soya.Material()
# moon_material.diffuse = (0.8, 0.8, 0.9, 1.0)
# moon_world = soya.sphere.Sphere(None, moon_material)
# moon_world.filename = "moon"
# moon_world.scale(0.1, 0.1, 0.1)
# moon_world.save()



# Creates the sun.

sun = CelestialObject(scene, soya.Model.get("sun"))


# Create the earth, inside the sun's World.

earth = CelestialObject(sun  , soya.Model.get("earth"))
earth.x = 2.0


# Create the moon, inside the earth's World.

moon  = CelestialObject(earth, soya.Model.get("moon" ))
moon.x = 0.5

# Creates a light.

light = soya.Light(scene)
light.set_xyz(0.0, 5.0, 0.0)


# Creates a camera, and makes it looking downward.

camera = soya.Camera(scene)
camera.y = 4.0
camera.look_at(soya.Vector(scene, 0.0, -1.0, 0.0))
soya.set_root_widget(camera)

try:
	soya.MainLoop(scene).main_loop()
except: pass

moon_center = soya.Point(moon, 0.0, 0.0, 0.0)

moon_center.convert_to(sun)

print "In the sun coordinate system, the center of the moon is", moon_center
