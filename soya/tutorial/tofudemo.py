#! /usr/bin/python -O

# Game Skeleton
# Copyright (C) 2003-2005 Jean-Baptiste LAMY
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

# Soya gaming tutorial, lesson 6
# Network gaming with Tofu !

# This tutorial is the same than game_skel-5.py, but with networking support.
# Tofu also save players automatically, so if you play, then disconnect, and then connect
# again, you'll restart at the same position you were when you disconnected.

# To run it:
# 1 - Execute tofudemo_create_level.py, in order to create and save the level
#     (this script is very similar to game_skel-1.py)
# 2 - Run:
#     python ./run_demo.py --single <login>         for single player game
#     python ./run_demo.py --server                 for server
#     python ./run_demo.py --client <host> <login>  for client

# A bunch of import
import sys, os, os.path, math
import soya
import soya.widget as widget
import soya.sdlconst as sdlconst
import tofu, tofu.pickle_sec, soya.tofu4soya

# Tofu provide some base classes that you must extend.
# To use Tofu with Soya, soya.tofu4soya provides these base classes with already Soya-ish
# support.

# The first class is the Level class. soya.tofu4soya. Level already inherits from
# soya.World.


class Level(soya.tofu4soya.Level):
  """A game level."""


# A Player represent a human player.

class Player(soya.tofu4soya.Player):

  # Player.__init__ is called when a NEW player is created (NOT when an existent player
  # logon !).
  # filename and password are the player's login and password. An additional string data
  # can be passed by the client, here we ignore them.
  
  # Player.__init__ must create at least one mobile for the player, then add this mobile
  # in a level and finally add the mobile in the player. Mobiles are a generic concept
  # that includes characters (see below).
  
  def __init__(self, filename, password, client_side_data = ""):
    soya.tofu4soya.Player.__init__(self, filename, password)
    
    level     = tofu.Level.get("level_tofudemo")
    character = Character()
    character.set_xyz(216.160568237, -3.0, 213.817764282)
    level.add_mobile(character)
    self .add_mobile(character)
  

# An Action is an action a mobile can accomplish.
# Here, we identify actions with the following constants:

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


import struct

class Action(soya.tofu4soya.Action):
  """An action that the character can do."""
  def __init__(self, action):
    self.action = action

  # Optimized version, optional (default to serialization)
  
  #def dump  (self): return struct.pack("B", self.action)
  #def undump(data): return Action(struct.unpack("B", data)[0])
  #undump = staticmethod(undump)
  
# A state is the state of a mobile, e.g. values for the set of the attributes of the mobile
# that evolve over the time.
# soya.tofu4soya.CoordSystState provide a state object for CoordSyst, which include
# the position, rotation and scaling attributes. as it extend CoordSyst, CoordSystState
# have all CoordSyst method like set_xyz, add_vector, rotate_*, scale,...

# Here, we also add an animation attribute, since the character's animation evolves
# over time.

class State(soya.tofu4soya.CoordSystState):
  """A state of the character position."""
  
  def __init__(self, mobile = None):
    soya.tofu4soya.CoordSystState.__init__(self, mobile)
    
    self.animation = "attente"
    
  # is_crucial must returns true if the state is crucial.
  # Non-crucial states can be dropped, either for optimization purpose or because of
  # network protocol (currently we use TCP, but in the future we may use UDP to send
  # non-crucial states).
  # Here we have no crucial state.
  
  def is_crucial(self): return 0
  
  # Optimized version, optional (default to serialization)
  
  #def dump  (self): return struct.pack("i10p19f", self.round, self.animation, *self.matrix)
  #def undump(data):
  #  self = State()
  #  data = struct.unpack("i10p19f", data)
  #  self.round     = data[0]
  #  self.animation = data[1]
  #  self.matrix    = data[2:]
  #  return self
  #undump = staticmethod(undump)
  

# The controller is responsible for reading inputs and generating Actions on the client
# side.
# We extend soya.tofu4soya.LocalController; "local" means that the player is controlled
# locally, contrary to the RemoteController.

class KeyboardController(soya.tofu4soya.LocalController):
  def __init__(self, mobile):
    soya.tofu4soya.LocalController.__init__(self, mobile)
    
    self.left_key_down = self.right_key_down = self.up_key_down = self.down_key_down = 0
    self.current_action = ACTION_WAIT
    
  def begin_round(self):
    """Returns the next action"""
    
    jump = 0
    
    for event in soya.process_event():
      if   event[0] == sdlconst.KEYDOWN:
        if   (event[1] == sdlconst.K_q) or (event[1] == sdlconst.K_ESCAPE):
          tofu.GAME_INTERFACE.end_game() # Quit the game
          
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
    
    if jump: action = ACTION_JUMP
    else:
      # People saying that Python doesn't have switch/select case are wrong...
      # Remember this if you are coding a fighting game !
      action = {
        (0, 0, 1, 0) : ACTION_ADVANCE,
        (1, 0, 1, 0) : ACTION_ADVANCE_LEFT,
        (0, 1, 1, 0) : ACTION_ADVANCE_RIGHT,
        (1, 0, 0, 0) : ACTION_TURN_LEFT,
        (0, 1, 0, 0) : ACTION_TURN_RIGHT,
        (0, 0, 0, 1) : ACTION_GO_BACK,
        (1, 0, 0, 1) : ACTION_GO_BACK_LEFT,
        (0, 1, 0, 1) : ACTION_GO_BACK_RIGHT,
        }.get((self.left_key_down, self.right_key_down, self.up_key_down, self.down_key_down), ACTION_WAIT)

    if action != self.current_action:
      self.current_action = action
      self.mobile.doer.do_action(Action(action))
      
# A mobile is anything that can move and evolve in a level. This include player characters
# but also computer-controlled objects (also named bots).

# Here we have a single class of Mobile: character.

# soya.tofu4soya.Mobile already inherits from World.
  
class Character(soya.tofu4soya.Mobile):
  """A character in the game."""
  def __init__(self):
    soya.tofu4soya.Mobile.__init__(self)
    
    # Loads a Cal3D shape (=model)
    balazar = soya.Cal3dShape.get("balazar")
    
    # Creates a Cal3D volume displaying the "balazar" shape
    # (NB Balazar is the name of a wizard).
    self.perso = soya.Cal3dVolume(self, balazar)
    
    # Starts playing the idling animation in loop
    self.perso.animate_blend_cycle("attente")
    
    # The current animation
    self.current_animation = ""
    
    self.current_action    = ACTION_WAIT
    
    # Disable raypicking on the character itself !!!
    self.solid = 0
    
    self.speed          = soya.Vector(self)
    self.rotation_speed = 0.0
    
    # We need radius * sqrt(2)/2 > max speed (here, 0.35)
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
    
  # loaded is called when the mobile is loaded from a file.
  # Here, we reset the current animation, because currently Soya doesn't save Cal3DVolume
  # current's animation yet.
  
  def loaded(self):
    soya.tofu4soya.Mobile.loaded(self)
    self.current_animation = ""

  # do_action is called when the mobile executes the given action. It is usually called
  # on the server side.
  # It must return the new State of the Mobile, after the action is executed.
  
  def do_action(self, action):
    
    # Create a new State for self. By default, the state is at the same position,
    # orientation and scaling that self.
    
    state = State(self)
    
    # If an action is given, we interpret it by moving the state according to the action.
    # We also set the state's animation.
    
    if action:
      self.current_action = action.action
      
      
    if   self.current_action in (ACTION_TURN_LEFT, ACTION_ADVANCE_LEFT, ACTION_GO_BACK_LEFT):
      state.rotate_lateral( 4.0)
      state.animation = "tourneG"
    elif self.current_action in (ACTION_TURN_RIGHT, ACTION_ADVANCE_RIGHT, ACTION_GO_BACK_RIGHT):
      state.rotate_lateral(-4.0)
      state.animation = "tourneD"

    if   self.current_action in (ACTION_ADVANCE, ACTION_ADVANCE_LEFT, ACTION_ADVANCE_RIGHT):
      state.shift(0.0, 0.0, -0.25)
      state.animation = "marche"
    elif self.current_action in (ACTION_GO_BACK, ACTION_GO_BACK_LEFT, ACTION_GO_BACK_RIGHT):
      state.shift(0.0, 0.0, 0.06)
      state.animation = "recule"
      
    # Now, we perform collision detection.
    # state_center is roughly the center of the character at the new state's position.
    # Then we create a raypicking context.
    # Detection collision is similar to the previous game_skel, except that "state"
    # replaces "new_center"
    
    state_center = soya.Point(state, 0.0, self.radius_y, 0.0)
    context = scene.RaypickContext(state_center, max(self.radius, 0.1 + self.radius_y))
    
    # Gets the ground, and check if the character is falling
    
    r = context.raypick(state_center, self.down, 0.1 + self.radius_y, 1, 1)
    
    if r and not self.jumping:
      
      # Puts the character on the ground
      # If the character is jumping, we do not put him on the ground !
      
      ground, ground_normal = r
      ground.convert_to(self)
      self.speed.y = ground.y
      
      # Jumping is only possible if we are on ground
      
      if action and (action.action == ACTION_JUMP):
        self.jumping = 1
        self.speed.y = 0.5
        
    else:
      
      # No ground => start falling
      
      self.speed.y = max(self.speed.y - 0.02, -0.25)
      state.animation = "chute"
      
      if self.speed.y < 0.0: self.jumping = 0

    # Add the current vertical speed to the state.
    
    state.y += self.speed.y
    
    # Check for walls.
    
    for vec in (self.left, self.right, self.front, self.back, self.up):
      r = context.raypick(state_center, vec, self.radius, 1, 1)
      if r:
        # The ray encounters a wall => the character cannot perform the planned movement.
        # We compute a correction vector, and add it to the state.
        
        collision, wall_normal = r
        hypo = vec.length() * self.radius - (state_center >> collision).length()
        correction = wall_normal * hypo
        
        # Theorical formula, but more complex and identical result
        #angle = (180.0 - vec.angle_to(wall_normal)) / 180.0 * math.pi
        #correction = wall_normal * hypo * math.cos(angle)
        
        state.add_vector(correction)

    # Returns the resulting state.
    
    self.doer.action_done(state)
  
  # set_state is called when the mobile's state change, due to the execution of an
  # action. It is called BOTH server-side and client-side.
  
  def set_state(self, state):
    # The super implementation take care of the position, rotation and scaling stuff.
    
    soya.tofu4soya.Mobile.set_state(self, state)
    
    # Play the new animation.
    if self.current_animation != state.animation:
      # Stops previous animation
      if self.current_animation: self.perso.animate_clear_cycle(self.current_animation, 0.2)
      
      # Starts the new one
      self.perso.animate_blend_cycle(state.animation, 1.0, 0.2)
      
      self.current_animation = state.animation
      
  # control_owned is called on the client-side when the player gets the control of the
  # mobile (i.e. the mobile is not a bot).
  
  def control_owned(self):
    soya.tofu4soya.Mobile.control_owned(self)
    
    # Use our KeyboardController instead of Tofu's default LocalController.
    
    self.controller = KeyboardController(self)
    
    # Create a camera traveling, in order to make the camera look toward this character.
    
    traveling = soya.ThirdPersonTraveling(self)
    traveling.distance = 5.0
    tofu.GAME_INTERFACE.camera.add_traveling(traveling)
    tofu.GAME_INTERFACE.camera.zap()
    

# GameInterface is the interface of the game.

class GameInterface(soya.tofu4soya.GameInterface):
  def __init__(self):
    soya.tofu4soya.GameInterface.__init__(self)
    
    soya.init()
    
    self.player_character = None
    
    # Creates a traveling camera in the scene, with a default look-toward-nothing
    # traveling.
    
    self.camera = soya.TravelingCamera(scene)
    self.camera.back = 70.0
    self.camera.add_traveling(soya.FixTraveling(soya.Point(), soya.Vector(None, 0.0, 0.0, -1.0)))
    
    soya.set_root_widget(soya.widget.Group())
    soya.root_widget.add(self.camera)
    
  # ready is called when the client has contacted the server and anything is ready.
  # In particular, we can now call self.notifier.login_player to logon the server.
  # Additional arguments to self.notifier.login_player will be pickled and sent to the
  # server, and then made available to the player (see client_side_data above).
  
  def ready(self, notifier):
    soya.tofu4soya.GameInterface.ready(self, notifier)
    
    login, password = sys.argv[-1], "test"
    self.notifier.login_player(login, password)
    
    
# Define data path (=where to find models, textures, ...)

HERE = os.path.dirname(sys.argv[0])
soya.path.append(os.path.join(HERE, "data"))
tofu.path.append(os.path.join(HERE, "data"))

# Create the scene (a world with no parent)

scene = soya.World()

# Inits Tofu with our classes.

soya.tofu4soya.init(GameInterface, Player, Level, Action, State, Character)

# Use cPickle for serializing local file (faster), and Cerealizer for network.

tofu.enable_pickle    (1, 0)
tofu.enable_cerealizer(0, 1)

# Make our classes safe for Cerealizer

import cerealizer, soya.cerealizer4soya
cerealizer.register_class(Action)
cerealizer.register_class(State)
cerealizer.register_class(KeyboardController)
cerealizer.register_class(Character)
cerealizer.register_class(Level)



# To use Jelly (buggy :-( )
# soya.tofu4soya.allow_jelly()
# tofu.allow_jelly()
# tofu.allow_jelly(
#   Action,
#   Character,
#   KeyboardController,
#   Level,
#   State,
#   )


# For security reason, there is a maximum to the size of the transmitted serialized
# object, which default to 99999. You may need to increase this value, e.g. up to
# 1MB (this is not needed for the demo, thus the following code is commented).

#import tofu.client
#tofu.client.MAX_LENGTH = 1000000


# This function makes all Soya pickleable classes safe for pickle_sec.


if __name__ == "__main__":
  print """Don't run me, run run_tofudemo.py instead !!!"""
