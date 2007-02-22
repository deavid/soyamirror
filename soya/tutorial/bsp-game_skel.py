#! /usr/bin/python
# -*- indent-tabs-mode: t -*-
# -*- coding: utf-8 -*-

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
# This is the same than the game_skel-5.py tutorial except that is use a
# BSP Level instead of a terrain.
#

# Choose first person or third person view
THIRD_PERSON = False

# Choose to scale the level or not
SCALE = True

from struct import *
from math import *
import sys, os, os.path
import soya
import soya.widget as widget
import soya.sdlconst as sdlconst

class Action:
	def __init__(self, action):
		self.action = action

ACTION_WAIT          = 0
ACTION_ADVANCE       = 1
ACTION_ADVANCE_LEFT  = 2
ACTION_ADVANCE_RIGHT = 3
ACTION_TURN_LEFT     = 4
ACTION_TURN_RIGHT    = 5
ACTION_GO_BACK       = 6
ACTION_GO_BACK_LEFT  = 7
ACTION_GO_BACK_RIGHT = 8
ACTION_JUMP          = 9


class KeyboardController:
	def __init__(self):
		self.left_key_down = self.right_key_down = self.up_key_down = self.down_key_down = 0
		
	def next(self):
		jump = 0
		for event in soya.process_event():
			if   event[0] == sdlconst.KEYDOWN:
				if   (event[1] == sdlconst.K_q) or (event[1] == sdlconst.K_ESCAPE):
					sys.exit() # Quit the game
				elif event[1] == sdlconst.K_LSHIFT:
					jump = 1
				elif event[1] == sdlconst.K_LEFT:  self.left_key_down  = 1
				elif event[1] == sdlconst.K_RIGHT: self.right_key_down = 1
				elif event[1] == sdlconst.K_UP:    self.up_key_down    = 1
				elif event[1] == sdlconst.K_DOWN:  self.down_key_down  = 1
			elif event[0] == sdlconst.KEYUP:
				if   event[1] == sdlconst.K_LEFT:  self.left_key_down  = 0
				elif event[1] == sdlconst.K_RIGHT: self.right_key_down = 0
				elif event[1] == sdlconst.K_UP:    self.up_key_down    = 0
				elif event[1] == sdlconst.K_DOWN:  self.down_key_down  = 0
		if jump: return Action(ACTION_JUMP)
		return Action({
			(0, 0, 1, 0) : ACTION_ADVANCE,
			(1, 0, 1, 0) : ACTION_ADVANCE_LEFT,
			(0, 1, 1, 0) : ACTION_ADVANCE_RIGHT,
			(1, 0, 0, 0) : ACTION_TURN_LEFT,
			(0, 1, 0, 0) : ACTION_TURN_RIGHT,
			(0, 0, 0, 1) : ACTION_GO_BACK,
			(1, 0, 0, 1) : ACTION_GO_BACK_LEFT,
			(0, 1, 0, 1) : ACTION_GO_BACK_RIGHT,
			}.get((self.left_key_down, self.right_key_down, self.up_key_down, self.down_key_down), ACTION_WAIT))

class ThirdPersonCharacter(soya.World):
	def __init__(self, parent, controller):
		soya.World.__init__(self, parent)
		balazar = soya.AnimatedModel.get("balazar")
		self.perso = soya.Body(self, balazar)
		self.perso.animate_blend_cycle("attente")
		self.current_animation = "attente"
		self.solid          = 0
		self.controller     = controller
		self.speed          = soya.Vector(self)
		self.rotation_speed = 0.0
		self.radius         = 0.5
		self.radius_y       = 1.0
		self.center         = soya.Point(self, 0.0, self.radius_y, 0.0)
		self.left           = soya.Vector(self, -1.0,  0.0,  0.0)
		self.right          = soya.Vector(self,  1.0,  0.0,  0.0)
		self.down           = soya.Vector(self,  0.0, -1.0,  0.0)
		self.up             = soya.Vector(self,  0.0,  1.0,  0.0)
		self.front          = soya.Vector(self,  0.0,  0.0, -1.0)
		self.back           = soya.Vector(self,  0.0,  0.0,  1.0)
		self.jumping        = 0
		self.camera = soya.TravelingCamera(parent)
		traveling = soya.ThirdPersonTraveling(self)
		traveling.distance = 5.
		self.camera.add_traveling(traveling)
		self.camera.zap()
		
	def play_animation(self, animation):
		if self.current_animation != animation:
			self.perso.animate_clear_cycle(self.current_animation, 0.2)
			self.perso.animate_blend_cycle(animation, 1.0, 0.2)
			self.current_animation = animation
			
	def begin_round(self):
		self.begin_action(self.controller.next())
		soya.World.begin_round(self)
		
	def begin_action(self, action):
		# Reset
		self.speed.x = self.speed.z = self.rotation_speed = 0.0
		
		# If the character is jumping, we don't want to reset speed.y to 0.0 !!!
		if (not self.jumping) and self.speed.y > 0.0: self.speed.y = 0.0
		
		animation = "attente"
		
		# Determine the character rotation
		if   action.action in (ACTION_TURN_LEFT, ACTION_ADVANCE_LEFT, ACTION_GO_BACK_LEFT):
			self.rotation_speed = 4.0
			animation = "tourneG"
		elif action.action in (ACTION_TURN_RIGHT, ACTION_ADVANCE_RIGHT, ACTION_GO_BACK_RIGHT):
			self.rotation_speed = -4.0
			animation = "tourneD"
			
		# Determine the character speed
		if   action.action in (ACTION_ADVANCE, ACTION_ADVANCE_LEFT, ACTION_ADVANCE_RIGHT):
			self.speed.z = -0.25
			animation = "marche"
		elif action.action in (ACTION_GO_BACK, ACTION_GO_BACK_LEFT, ACTION_GO_BACK_RIGHT):
			self.speed.z = 0.06
			animation = "recule"
		
		new_center = self.center + self.speed
		context = scene.RaypickContext(new_center, max(self.radius, 0.1 + self.radius_y))
		r = context.raypick(new_center, self.down, 0.1 + self.radius_y, 1, 1)
		if r and not self.jumping:
			ground, ground_normal = r
			ground.convert_to(self)
			self.speed.y = ground.y
			if action.action == ACTION_JUMP:
				self.jumping = 1
				self.speed.y = 0.5
		else:
			self.speed.y = max(self.speed.y - 0.02, -0.25)
			animation = "chute"
			if self.speed.y < 0.0:
				self.jumping = 0
		new_center = self.center + self.speed
		for vec in (self.left, self.right, self.front, self.back, self.up):
			r = context.raypick(new_center, vec, self.radius, 1, 1)
			if r:
				collision, wall_normal = r
				
				# Necessary because of scaling...
				wall_normal %= scene
				wall_normal.normalize()
				
				hypo = vec.length() * self.radius - (new_center >> collision).length()
				correction = (wall_normal * hypo)
				self.speed.add_vector(correction)
				new_center.add_vector(correction)
		self.play_animation(animation)
		
	def advance_time(self, proportion):
		soya.World.advance_time(self, proportion)
		self.add_mul_vector(proportion, self.speed)
		self.rotate_y(proportion * self.rotation_speed)

class FirstPersonCharacter(soya.World):
	def __init__(self, parent, controller):
		soya.World.__init__(self, parent)
		self.solid          = 0
		self.controller     = controller
		self.speed          = soya.Vector(self)
		self.rotation_speed = 0.0
		self.radius         = 0.5
		self.radius_y       = 1.0
		self.center         = soya.Point(self, 0.0, self.radius_y, 0.0)
		self.left           = soya.Vector(self, -1.0,  0.0,  0.0)
		self.right          = soya.Vector(self,  1.0,  0.0,  0.0)
		self.down           = soya.Vector(self,  0.0, -1.0,  0.0)
		self.up             = soya.Vector(self,  0.0,  1.0,  0.0)
		self.front          = soya.Vector(self,  0.0,  0.0, -1.0)
		self.back           = soya.Vector(self,  0.0,  0.0,  1.0)
		self.jumping        = 0
		self.camera         = soya.Camera(self)
		self.camera.set_xyz(0.0, self.radius_y*2., 0.0)
	
	def begin_round(self):
		self.begin_action(self.controller.next())
		soya.World.begin_round(self)
	
	def begin_action(self, action):
		# Reset
		self.speed.x = self.speed.z = self.rotation_speed = 0.0
		
		# If the character is jumping, we don't want to reset speed.y to 0.0 !!!
		if (not self.jumping) and self.speed.y > 0.0: self.speed.y = 0.0
		
		# Determine the character rotation
		if   action.action in (ACTION_TURN_LEFT, ACTION_ADVANCE_LEFT, ACTION_GO_BACK_LEFT):
			self.rotation_speed = 4.0
		elif action.action in (ACTION_TURN_RIGHT, ACTION_ADVANCE_RIGHT, ACTION_GO_BACK_RIGHT):
			self.rotation_speed = -4.0
			
		# Determine the character speed
		if   action.action in (ACTION_ADVANCE, ACTION_ADVANCE_LEFT, ACTION_ADVANCE_RIGHT):
			self.speed.z = -0.25
		elif action.action in (ACTION_GO_BACK, ACTION_GO_BACK_LEFT, ACTION_GO_BACK_RIGHT):
			self.speed.z = 0.06
		
		new_center = self.center + self.speed
		context = scene.RaypickContext(new_center, max(self.radius, 0.1 + self.radius_y))
		r = context.raypick(new_center, self.down, 0.1 + self.radius_y, 1, 1)
		if r and not self.jumping:
			ground, ground_normal = r
			ground.convert_to(self)
			self.speed.y = ground.y
			if action.action == ACTION_JUMP:
				self.jumping = 1
				self.speed.y = 0.5
		else:
			self.speed.y = max(self.speed.y - 0.02, -0.25)
			if self.speed.y < 0.0:
				self.jumping = 0
		new_center = self.center + self.speed
		for vec in (self.left, self.right, self.front, self.back, self.up):
			r = context.raypick(new_center, vec, self.radius, 1, 1)
			if r:
				collision, wall_normal = r
				
				# Necessary because of scaling...
				wall_normal %= scene
				wall_normal.normalize()
				
				hypo = vec.length() * self.radius - (new_center >> collision).length()
				correction = (wall_normal * hypo)
				self.speed.add_vector(correction)
				new_center.add_vector(correction)
		
	def advance_time(self, proportion):
		soya.World.advance_time(self, proportion)
		self.add_mul_vector(proportion, self.speed)
		self.rotate_y(proportion * self.rotation_speed)



soya.init()
soya.path.append(os.path.join(os.path.dirname(sys.argv[0]), "../tutorial/data"))
level = soya.BSPWorld.get("bsp_demo")
# We need to scale the level because it's really too big compared to Balazar.
if SCALE:
	level.scale(0.05, 0.05, 0.05)

# Try to comment this line and go to the small square room to see what it does
level.enable_area_visibility(0, 1)


scene = soya.World()
atmosphere = soya.SkyAtmosphere()
atmosphere.ambient = (0.9, 0.9, 0.9, 1.0)
scene.atmosphere = atmosphere
scene.add(level)

if THIRD_PERSON:
	print "Third person mode !"
	character = ThirdPersonCharacter(scene, KeyboardController())
else:
	print "First person mode !"
	character = FirstPersonCharacter(scene, KeyboardController())

print "Use arrow keys to move and shift to jump."

if SCALE:
	character.set_xyz(-128.0/20., 40.0/20., 8.0/20.)
else:
	character.set_xyz(-128.0, 40.0, 8.0)

if SCALE:
	character.camera.back = 80.0
else:
	character.camera.back = 1500.0


#scene.add(character.camera)

# Creates a widget group, containing the camera and a label showing the FPS.
soya.set_root_widget(widget.Group())
soya.root_widget.add(character.camera)
soya.root_widget.add(widget.FPSLabel())

soya.MainLoop(scene).main_loop()
