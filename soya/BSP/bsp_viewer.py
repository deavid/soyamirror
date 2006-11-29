#! /usr/bin/python

# Souvarine souvarine@aliasrobotique.org
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

#
# Quick and dirty Quake 3 BSP viewer. Display a saved soya BSP World.
# Move camera with A, Q and arrow keys
#

from struct import *
from math import *
import sys, os, os.path
import soya
import soya.widget as widget

SPEED = 10.

class moving_camera(soya.Camera):
	def __init__(self, parent):
		soya.Camera.__init__(self, parent)
		self.speed            = soya.Vector(self, 0.0, 0.0, 0.0)
		self.rotation_y_speed = 0.0
	
	def begin_round(self):
		soya.Camera.begin_round(self)
		for event in soya.process_event():
			if event[0] == soya.sdlconst.KEYDOWN:
				if   event[1] == soya.sdlconst.K_UP:     self.speed.z = -SPEED
				elif event[1] == soya.sdlconst.K_DOWN:   self.speed.z =  SPEED
				elif event[1] == soya.sdlconst.K_a:      self.speed.y =  SPEED
				elif event[1] == soya.sdlconst.K_q:      self.speed.y =  -SPEED
				elif event[1] == soya.sdlconst.K_LEFT:   self.rotation_y_speed =  3.0
				elif event[1] == soya.sdlconst.K_RIGHT:  self.rotation_y_speed = -3.0
				elif event[1] == soya.sdlconst.K_ESCAPE: soya.MAIN_LOOP.stop()
			elif event[0] == soya.sdlconst.KEYUP:
				if   event[1] == soya.sdlconst.K_UP:     self.speed.z = 0.0
				elif event[1] == soya.sdlconst.K_DOWN:   self.speed.z = 0.0
				elif event[1] == soya.sdlconst.K_a:      self.speed.y =  0.
				elif event[1] == soya.sdlconst.K_q:      self.speed.y =  0.
				elif event[1] == soya.sdlconst.K_LEFT:   self.rotation_y_speed = 0.0
				elif event[1] == soya.sdlconst.K_RIGHT:  self.rotation_y_speed = 0.0
			elif event[0] == soya.sdlconst.QUIT:
				soya.MAIN_LOOP.stop()
		#self.rotate_y(self.rotation_y_speed)
		
	def advance_time(self, proportion):
		soya.Camera.advance_time(self, proportion)
		self.add_mul_vector(proportion, self.speed)
		self.rotate_y(proportion * self.rotation_y_speed)

soya.init()
soya.path.append(os.path.join(os.path.dirname(sys.argv[0]), "data"))
level = soya.BSPWorld.get("imported_bsp_world")
scene = soya.World()
atmosphere = soya.SkyAtmosphere()
atmosphere.ambient = (0.9, 0.9, 0.9, 1.0)
scene.atmosphere = atmosphere
scene.add(level)

# Creates a camera in the scene
camera = moving_camera(scene)
camera.set_xyz(0.0, 30.0, 3.0)
camera.back = 1500.

# Creates a widget group, containing the camera and a label showing the FPS.
soya.set_root_widget(widget.Group())
soya.root_widget.add(camera)
soya.root_widget.add(widget.FPSLabel())

soya.MainLoop(scene).main_loop()












