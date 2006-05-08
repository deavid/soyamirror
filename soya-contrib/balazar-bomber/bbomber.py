
import sys, os, os.path, math
import soya
import soya.widget as widget
import soya.sdlconst as sdlconst
import tofu, tofu.pickle_sec, tofu4soyapudding


import pudding.core
import pudding.control
import pudding.idler
import pudding.ext.fpslabel
import pudding.sysfont


import guicreation


class SoftBox(tofu4soyapudding.Mobile):
   
    def __init__(self):
        tofu4soyapudding.Mobile.__init__(self)
        box_model = soya.Shape.get("soft_cube")
        soft_cube = soya.Volume(self, box_model)
        bot = 1
        self.state = BoxState(self)
        
    def do_action(self, action):
        self.state = BoxState(self)
        return None
    
    def set_state(self, state):
        tofu4soyapudding.Mobile.set_state(self, state)
        

class BoxState(tofu4soyapudding.CoordSystState):
    def __init__(self, mobile):
        tofu4soyapudding.CoordSystState.__init__(self, mobile)
    
    def is_crucial(self): return 0
    
class Level(tofu4soyapudding.Level):
  """A game level."""



class Player(tofu4soyapudding.Player):

  # Player.__init__ is called when a NEW player is created (NOT when an existent player
  # logon !).
  # filename and password are the player's login and password. An additional string data
  # can be passed by the client, here we ignore them.
  
  # Player.__init__ must create at least one mobile for the player, then add this mobile
  # in a level and finally add the mobile in the player. Mobiles are a generic concept
  # that includes characters (see below).
  
  def __init__(self, filename, password, client_side_data = ""):
    tofu4soyapudding.Player.__init__(self, filename, password)
    
    avatar = Character()
    self .add_mobile(avatar)
    


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

class Action(tofu4soyapudding.Action):
  """An action that the character can do."""
  def __init__(self, action):
    self.action = action

# A state is the state of a mobile, e.g. values for the set of the attributes of the mobile
# that evolve over the time.
# tofu4soyapudding.CoordSystState provide a state object for CoordSyst, which include
# the position, rotation and scaling attributes. as it extend CoordSyst, CoordSystState
# have all CoordSyst method like set_xyz, add_vector, rotate_*, scale,...

# Here, we also add an animation attribute, since the character's animation evolves
# over time.

class State(tofu4soyapudding.CoordSystState):
  """A state of the character position."""
  
  def __init__(self, mobile):
    tofu4soyapudding.CoordSystState.__init__(self, mobile)
    
    self.animation = "attente"
    
  # is_crucial must returns true if the state is crucial.
  # Non-crucial states can be dropped, either for optimization purpose or because of
  # network protocol (currently we use TCP, but in the future we may use UDP to send
  # non-crucial states).
  # Here we have no crucial state.
  
  def is_crucial(self): return 0

# The controller is responsible for reading inputs and generating Actions on the client
# side.
# We extend tofu4soyapudding.LocalController; "local" means that the player is controlled
# locally, contrary to the RemoteController.

class KeyboardController(tofu4soyapudding.LocalController):
  def __init__(self, mobile):
    tofu4soyapudding.LocalController.__init__(self, mobile)
    
    self.left_key_down = self.right_key_down = self.up_key_down = self.down_key_down = 0
    
  def next(self):
    """Returns the next action"""
    
    jump = 0
    
    for event in pudding.process_event():
      if   event[0] == sdlconst.KEYDOWN:
        if   (event[1] == sdlconst.K_q) or (event[1] == sdlconst.K_ESCAPE):
          tofu.GAME_INTERFACE.end_game() # Quit the game
        
        elif event[1] == sdlconst.K_m:
            print "trying to change single to multiplayer mode"
            tofu.GAME_INTERFACE.end_game('client')
              
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


# A mobile is anything that can move and evolve in a level. This include player characters
# but also computer-controlled objects (also named bots).

# Here we have a single class of Mobile: character.

# tofu4soyapudding.Mobile already inherits from World.


class Character(tofu4soyapudding.Mobile):
  """A character in the game."""
  def __init__(self):
    tofu4soyapudding.Mobile.__init__(self)
    level = soya.World.get("level1_bbomber")
    #self.guicreator = guicreation.GuiMaker(tofu.GAME_INTERFACE, self)
    
    # Loads a Cal3D shape (=model)
    balazar = soya.Cal3dShape.get("balazar")
    
    # Creates a Cal3D volume displaying the "balazar" shape
    # (NB Balazar is the name of a wizard).
    self.perso = soya.Cal3dVolume(self, balazar)
    
    # Starts playing the idling animation in loop
    self.perso.animate_blend_cycle("attente")
    
    # The current animation
    self.current_animation = ""
    
    # Disable raypicking on the character itself !!!
    self.solid = 0
    
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
    #self.scale(0.25, 0.25, 0.25)
    self.set_xyz(127.0, 2.0,127.0)
    level.add_mobile(self)
    guicreation.introgui(tofu.GAME_INTERFACE, self)
    
  # loaded is called when the mobile is loaded from a file.
  # Here, we reset the current animation, because currently Soya doesn't save Cal3DVolume
  # current's animation yet.
  
  def loaded(self):
    tofu4soyapudding.Mobile.loaded(self)
    self.current_animation = ""

  # Plays the given animation.
  
  def play_animation(self, animation):
    if self.current_animation != animation:
      # Stops previous animation
      if self.current_animation: self.perso.animate_clear_cycle(self.current_animation, 0.2)
      
      # Starts the new one
      self.perso.animate_blend_cycle(animation, 1.0, 0.2)
      
      self.current_animation = animation
      
  # do_action is called when the mobile executes the given action. It is usually called
  # on the server side.
  # It must return the new State of the Mobile, after the action is executed.
  def dummy_node(self):
    print "just printing something dumb"
    #print msg
    
  def change_level(self, newlevelname):
    self.level.remove_mobile(self)
    new_level =  soya.World.get(newlevelname)
    new_level.add_mobile(self)
    
  def do_action(self, action):
    
    # Create a new State for self. By default, the state is at the same position,
    # orientation and scaling that self.
    
    state = State(self)
    
    # If an action is given, we interpret it by moving the state according to the action.
    # We also set the state's animation.
    
    if action:
      if   action.action in (ACTION_TURN_LEFT, ACTION_ADVANCE_LEFT, ACTION_GO_BACK_LEFT):
        state.rotate_lateral( 4.0)
        state.animation = "tourneG"
      elif action.action in (ACTION_TURN_RIGHT, ACTION_ADVANCE_RIGHT, ACTION_GO_BACK_RIGHT):
        state.rotate_lateral(-4.0)
        state.animation = "tourneD"

      if   action.action in (ACTION_ADVANCE, ACTION_ADVANCE_LEFT, ACTION_ADVANCE_RIGHT):
        state.shift(0.0, 0.0, -0.25)
        state.animation = "marche"
      elif action.action in (ACTION_GO_BACK, ACTION_GO_BACK_LEFT, ACTION_GO_BACK_RIGHT):
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
    
    r = context.raypick(state_center, self.down, 0.1 + self.radius_y, 0, 0)
    
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
      r = context.raypick(state_center, vec, self.radius, 0, 0)
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
    
    return state
  
  # set_state is called when the mobile's state change, due to the execution of an
  # action. It is called BOTH server-side and client-side.
  
  def set_state(self, state):
    
    # The super implementation take care of the position, rotation and scaling stuff.
    
    tofu4soyapudding.Mobile.set_state(self, state)
    
    # Play the new animation.
    
    self.play_animation(state.animation)
    
  # control_owned is called on the client-side when the player gets the control of the
  # mobile (i.e. the mobile is not a bot).
  
  def control_owned(self):
    tofu4soyapudding.Mobile.control_owned(self)
    
    # Use our KeyboardController instead of Tofu's default LocalController.
    
    self.controller = KeyboardController(self)
    
    # Create a camera traveling, in order to make the camera look toward this character.
    
    traveling = soya.ThirdPersonTraveling(self)
    traveling.distance = 18.0
    traveling.top_view = 0.9
    
    tofu.GAME_INTERFACE.camera.add_traveling(traveling)
    tofu.GAME_INTERFACE.camera.zap()
    

# GameInterface is the interface of the game.

class GameInterface(tofu4soyapudding.GameInterface):
  def __init__(self):
    tofu4soyapudding.GameInterface.__init__(self)
    
    soya.init()
    pudding.init()
    
    self.player_character = None
    
    # Creates a traveling camera in the scene, with a default look-toward-nothing
    # traveling.
    
    self.camera = soya.TravelingCamera(scene)
    self.camera.back = 70.0
    self.camera.add_traveling(soya.FixTraveling(soya.Point(), soya.Vector(None, 0.0, 0.0, 10.0)))
    self.root = pudding.core.RootWidget(width = 640, height = 480)
    soya.set_root_widget(self.root)
    soya.root_widget.add_child(self.camera)
    
    pudding.ext.fpslabel.FPSLabel(soya.root_widget, position = pudding.TOP_RIGHT)
    
  # ready is called when the client has contacted the server and anything is ready.
  # In particular, we can now call self.notifier.login_player to logon the server.
  # Additional arguments to self.notifier.login_player will be pickled and sent to the
  # server, and then made available to the player (see client_side_data above).
  
  def ready(self, notifier):
    tofu4soyapudding.GameInterface.ready(self, notifier)
    
    login, password = sys.argv[-1], "test"
    self.notifier.login_player(login, password)
    
    
# Define data path (=where to find models, textures, ...)

HERE = os.path.dirname(sys.argv[0])
soya.path.append(os.path.join(HERE, "data"))
tofu.path.append(os.path.join(HERE, "data"))

# Create the scene (a world with no parent)

scene = soya.World()

# Inits Tofu with our classes.

tofu4soyapudding.init(GameInterface, Player, Level, Action, State, Character)


# For security reasons, Tofu doesn't accept unpickling any classes from network.
# The following statement allows Tofu to unpickle classes from the "soya", and so on,
# module.
# Notice that some default modules are always considered as "secure" (e.g. __builtin__,
# copy_reg, or tofu).

tofu.pickle_sec.safe_module("soya")
tofu.pickle_sec.safe_module("soya._soya")
tofu.pickle_sec.safe_module("pudding")
tofu.pickle_sec.safe_module("guicreation")
tofu.pickle_sec.safe_module("bbomber")
tofu.pickle_sec.safe_module("pudding.control")
tofu.pickle_sec.safe_module("pudding.container")
tofu.pickle_sec.safe_module("pudding.core")
tofu.pickle_sec.safe_module("pudding.sysfont")
tofu.pickle_sec.safe_module("pudding.idler")
tofu.pickle_sec.safe_module("pudding.ext")
tofu.pickle_sec.safe_module("os.Font")
tofu.pickle_sec.safe_module("string")
tofu.pickle_sec.safe_module("soya.widget")







if __name__ == "__main__":
  print """Don't run me, run run_bbomber.py instead !!!"""
