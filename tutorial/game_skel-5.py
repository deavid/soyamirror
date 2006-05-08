#! /usr/bin/python -O

# Game Skeleton
# Copyright (C) 2003-2004 Jean-Baptiste LAMY
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

# Soya gaming tutorial, lesson 5
# Adding jumping

# New stuff is in the Controller and Character class


# A bunch of import
import sys, os, os.path, math
import soya
import soya.widget as widget
import soya.sdlconst as sdlconst

# Inits Soya
soya.init()

# Define data path (=where to find models, textures, ...)
HERE = os.path.dirname(sys.argv[0])
soya.path.append(os.path.join(HERE, "data"))


class Level(soya.World):
  """A game level.
Level is a subclass of soya.World."""


class Action:
  """An action that the character can do."""
  def __init__(self, action):
    self.action = action

# The available actions
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
  """A controller is an object that gives orders to a character.
Here, we define a keyboard based controller, but there may be mouse-based or IA-based
controllers.
Notice that the unique method is called "next", which allows to use Python generator
as controller."""
  def __init__(self):
    self.left_key_down = self.right_key_down = self.up_key_down = self.down_key_down = 0
    
  def next(self):
    """Returns the next action"""
    jump = 0
    
    for event in soya.process_event():
      if   event[0] == sdlconst.KEYDOWN:
        if   (event[1] == sdlconst.K_q) or (event[1] == sdlconst.K_ESCAPE):
          sys.exit() # Quit the game
          
        elif event[1] == sdlconst.K_LSHIFT:
          # Shift key is for jumping
          # Contrary to other action, jump is only performed once, at the beginning of
          # the jump.
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
    
    # People saying that Python doesn't have switch/select case are wrong...
    # Remember this if you are coding a fighting game !
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


class Character(soya.World):
  """A character in the game."""
  def __init__(self, parent, controller):
    soya.World.__init__(self, parent)

    # Loads a Cal3D shape (=model)
    balazar = soya.Cal3dShape.get("balazar")
    
    # Creates a Cal3D volume displaying the "balazar" shape
    # (NB Balazar is the name of a wizard).
    self.perso = soya.Cal3dVolume(self, balazar)
    
    # Starts playing the idling animation in loop
    self.perso.animate_blend_cycle("attente")
    
    # The current animation
    self.current_animation = "attente"
    
    # Disable raypicking on the character itself !!!
    self.solid = 0
    
    self.controller     = controller
    self.speed          = soya.Vector(self)
    self.rotation_speed = 0.0
    
    # We need radius * sqrt(2)/2 < max speed (here, 0.35)
    self.radius         = 0.5
    self.radius_y       = 1.0
    self.center         = soya.Point(self, 0.0, self.radius_y, 0.0)
    
    self.left   = soya.Vector(self, -1.0,  0.0,  0.0)
    self.right  = soya.Vector(self,  1.0,  0.0,  0.0)
    self.down   = soya.Vector(self,  0.0, -1.0,  0.0)
    self.up     = soya.Vector(self,  0.0,  1.0,  0.0)
    self.front  = soya.Vector(self,  0.0,  0.0, -1.0)
    self.back   = soya.Vector(self,  0.0,  0.0,  1.0)

    # True is the character is jumping, i.e. speed.y > 0.0
    self.jumping = 0
    
  def play_animation(self, animation):
    if self.current_animation != animation:
      # Stops previous animation
      self.perso.animate_clear_cycle(self.current_animation, 0.2)
      
      # Starts the new one
      self.perso.animate_blend_cycle(animation, 1.0, 0.2)
      
      self.current_animation = animation
      
  def begin_round(self):
    self.begin_action(self.controller.next())
    soya.World.begin_round(self)
    
  def begin_action(self, action):
    # Reset
    self.speed.x = self.speed.z = self.rotation_speed = 0.0
    
    # If the haracter is jumping, we don't want to reset speed.y to 0.0 !!!
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
    
    # Gets the ground, and check if the character is falling
    r = context.raypick(new_center, self.down, 0.1 + self.radius_y, 1, 1)

    if r and not self.jumping:
      # Puts the character on the ground
      # If the character is jumping, we do not put him on the ground !
      ground, ground_normal = r
      ground.convert_to(self)
      self.speed.y = ground.y
      
      # Jumping is only possible if we are on ground
      if action.action == ACTION_JUMP:
        self.jumping = 1
        self.speed.y = 0.5
        
    else:
      # No ground => start falling
      # Test the fall with the pit behind the second house
      self.speed.y = max(self.speed.y - 0.02, -0.25)
      animation = "chute"
      
      # If the vertical speed is negative, the jump is over
      if self.speed.y < 0.0: self.jumping = 0
      
    new_center = self.center + self.speed
    
    # The movement (defined by the speed vector) may be impossible if the character
    # would encounter a wall.
    
    for vec in (self.left, self.right, self.front, self.back, self.up):
      r = context.raypick(new_center, vec, self.radius, 1, 1)
      if r:
        # The ray encounters a wall => the character cannot perform the planned movement.
        # We compute a correction vector, and add it to the speed vector, as well as to
        # new_center (for the following raypicks ; remember that
        # new_center = self.center + self.speed, so if speed has changed, we must update
        # it).
        
        collision, wall_normal = r
        hypo = vec.length() * self.radius - (new_center >> collision).length()
        correction = wall_normal * hypo
        
        # Theorical formula, but more complex and identical result
        #angle = (180.0 - vec.angle_to(wall_normal)) / 180.0 * math.pi
        #correction = wall_normal * hypo * math.cos(angle)
        
        self.speed.add_vector(correction)
        new_center.add_vector(correction)
        
    self.play_animation(animation)
      
  def advance_time(self, proportion):
    soya.World.advance_time(self, proportion)
    
    self.add_mul_vector(proportion, self.speed)
    self.rotate_lateral(proportion * self.rotation_speed)

    
# Create the scene (a world with no parent)
scene = soya.World()

# Loads the level, and put it in the scene
level = soya.World.get("level_demo")
scene.add(level)

# Creates a character in the level, with a keyboard controller
character = Character(level, KeyboardController())
character.set_xyz(216.160568237, -7.93332195282, 213.817764282)

# Creates a Tomb Raider-like camera in the scene
camera = soya.TravelingCamera(scene)
traveling = soya.ThirdPersonTraveling(character)
traveling.distance = 5.0
camera.add_traveling(traveling)
camera.zap()
camera.back = 70.0

# Creates a widget group, containing the camera and a label showing the FPS.
soya.set_root_widget(widget.Group())
soya.root_widget.add(camera)
soya.root_widget.add(widget.FPSLabel())

# Creates and run an "idler" (=an object that manage time and regulate FPS)
# By default, FPS is locked at 40.
soya.Idler(scene).idle()
