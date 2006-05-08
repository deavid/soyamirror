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

# Soya gaming tutorial, lesson 2
# Adding a keyboard-controlled cube

# A bunch of import
import sys, os, os.path
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
# For more complex actions, you may want to subclass Action.
ACTION_WAIT          = 0
ACTION_ADVANCE       = 1
ACTION_ADVANCE_LEFT  = 2
ACTION_ADVANCE_RIGHT = 3
ACTION_TURN_LEFT     = 4
ACTION_TURN_RIGHT    = 5
ACTION_GO_BACK       = 6
ACTION_GO_BACK_LEFT  = 7
ACTION_GO_BACK_RIGHT = 8


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
    for event in soya.process_event():
      if   event[0] == sdlconst.KEYDOWN:
        if   (event[1] == sdlconst.K_q) or (event[1] == sdlconst.K_ESCAPE):
          sys.exit() # Quit the game
        elif event[1] == sdlconst.K_LEFT:  self.left_key_down  = 1
        elif event[1] == sdlconst.K_RIGHT: self.right_key_down = 1
        elif event[1] == sdlconst.K_UP:    self.up_key_down    = 1
        elif event[1] == sdlconst.K_DOWN:  self.down_key_down  = 1
        
      elif event[0] == sdlconst.KEYUP:
        if   event[1] == sdlconst.K_LEFT:  self.left_key_down  = 0
        elif event[1] == sdlconst.K_RIGHT: self.right_key_down = 0
        elif event[1] == sdlconst.K_UP:    self.up_key_down    = 0
        elif event[1] == sdlconst.K_DOWN:  self.down_key_down  = 0
    
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
  """A character in the game.
I always consider character.x, character.y, character.z (i.e. the point with
coordinates (0.0, 0.0, 0.0) in the character coordinates system :
Point(character, 0.0, 0.0, 0.0)) to be the position of the feet of the character
(and not the center).

Similarly, i consider the X vector of the character (i.e.
Vector(character, 1.0, 0.0, 0.0)) to be the right direction, the Y vector (i.e.
Vector(character, 0.0, 1.0, 0.0)) to be the up direction and the -Z vector (i.e.
Vector(character, 0.0, 0.0, -1.0)) to be the front direction.
(Why -Z and not Z ? just to avoid indirect coordinate systems !!!)"""
  def __init__(self, parent, controller):
    soya.World.__init__(self, parent)
    
    # For now, the character is simply a cube.
    self.set_shape(soya.Shape.get("cube"))
    
    # Disable raypicking on the character itself !!!
    # This is needed for the Tomb-Raider like camera (see below),
    # and for collision detection too (see next lesson).
    self.solid = 0
    
    # The character's controller
    self.controller = controller
    
    # The character's speed : a vector defined in the character coordinates system.
    # E.g. if you want the character to move forward, do character.speed.z = -1.0
    self.speed = soya.Vector(self)
    
    # The character's rotation speed (around the Y axis)
    self.rotation_speed = 0.0
    
  def begin_round(self):
    """This method is called by the Idler each time a round starts. Soya manages
round of 30ms by default, this means that the character will perform each action
during 30ms.

Actually, all round obviously does not last exactely 30ms, but it is true on a
global point of view. E.g., 1000 rounds will last 1000 * 30ms."""
    # Gets the new action from the controller, and begins it
    self.begin_action(self.controller.next())
    
    # Delegate to World, for beginning round of inner children.
    # This should be called after begin_action for a better visual effect,
    # since begin_action may influence World.begin_round (e.g. if begin_action
    # starts an animation, see lesson 4)
    soya.World.begin_round(self)
    
  def begin_action(self, action):
    """This method begins the action ACTION. It DOES NOT perform the action
(see advance_time for that). But it does "decode" the action, and check for any
collision that may occur (not yet, but it will do in lesson 4).
begin_action puts in the speed vector and the rotation_speed floating variable the
character speed and rotation speed (amon the Y axis)."""
    # Reset
    self.rotation_speed = self.speed.x = self.speed.y = self.speed.z = 0.0
    
    # Determine the character rotation
    if   action.action in (ACTION_TURN_LEFT, ACTION_ADVANCE_LEFT, ACTION_GO_BACK_LEFT):
      self.rotation_speed = 5.0
    elif action.action in (ACTION_TURN_RIGHT, ACTION_ADVANCE_RIGHT, ACTION_GO_BACK_RIGHT):
      self.rotation_speed = -5.0
      
    # Determine the character speed
    if   action.action in (ACTION_ADVANCE, ACTION_ADVANCE_LEFT, ACTION_ADVANCE_RIGHT):
      self.speed.z = -0.35
    elif action.action in (ACTION_GO_BACK, ACTION_GO_BACK_LEFT, ACTION_GO_BACK_RIGHT):
      self.speed.z = 0.2
      
    # You can use speed.x for stride/lateral movement,
    # and speed.y for jumping/falling (see lesson 5)
    
  def advance_time(self, proportion):
    """This method is called one or more times between 2 rounds.
PROPORTION is the proportion of the round that has been spent
(e.g. 1.0 for a full round, 0.5 for a half, ...).

ALL character moves MUST occur in the method, in order to take avantage
of the Idler time management system and get the best visual effect."""
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

#soya.render(); soya.screenshot().resize((320, 240)).save(os.path.join(os.path.dirname(sys.argv[0]), "results", os.path.basename(sys.argv[0])[:-3] + ".jpeg"))

# Creates and run an "idler" (=an object that manage time and regulate FPS)
# By default, FPS is locked at 40.
soya.Idler(scene).idle()
