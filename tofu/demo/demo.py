# TOFU
# Copyright (C) 2005 Jean-Baptiste LAMY
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

# This is a small Tk-based demo using Tofu.
# To run it, execute the run_demo.py script.
# Try   python ./run_demo.py --help   for more info.


import sys, random, Tkinter
import tofu, tofu.pickle_sec


# Tofu provide some base classes that you must extend, and finally you call
# tofu.init() and pass these classes to it.

# The first class is the Level class. A level is a level in the game.

class Level(tofu.Level):
  def __init__(self, filename):
    
    # Don't forget to call Tofu's implmentation when you override a method!!!
    
    tofu.Level.__init__(self, filename)
    
    print "* Demo * creating level %s..." % filename
    
    # The level contains a 10x10 square array. 3 of them are randomly choosen to
    # contain a wall.
    
    self.walls     = [0] * 100
    for i in range(3): self.walls[random.randrange(0, 100)] = 1
    
    # These attribute are used when drawing the level in the Tk Canvas.
    
    self.canvas     = None
    self.level_tags = []
    
    # Add a bot (see the Bot class below)
    
    if filename == "1_0":
      bot = Bot()
      self.add_mobile(bot)
      bot.y = 6

  # When we load a level, if the level is not found, we create a new one.
  # (By default, an error is risen)
  
  def load(clazz, filename):
    try:               return tofu.Level.load(filename)
    except ValueError: return Level(filename)
  load = classmethod(load)
  
  # Returns the level located next to this one (e.g. if delta_x = 1 and delta_y = 0,
  # returns the level at the left of this one).
  
  def neighbour(self, delta_x, delta_y):
    x, y = map(int, self.filename.split("_"))
    x += delta_x
    y += delta_y
    return Level.get("%s_%s" % (x, y))
  
  def __repr__(self):
    s = "level %s : \n" % (self.filename,)
    for y in xrange(10):
      for x in xrange(10): s += str(self.walls[x + y * 10]) + " "
      s += "\n"
    s += "characters :\n"
    for character in self.mobiles: s = s + "  " + `character` + "\n"
    return s

  # Sets the Tk canvas and draws the level in this canvas. If the canvas is None, the
  # level's canva items are destroyed.
  
  def set_canvas(self, canvas):
    if canvas:
      self.canvas = canvas
      self._draw()
    else:
      if self.canvas: self._clear()
      self.canvas = self.tag = None
      
    # Sets the canvas for all mobiles in the level.
    
    for mobile in self.mobiles: mobile.set_canvas(canvas)
    
  # Draw the level in the Tk canvas.
  # Canvas items are stored in self.level_tags for _clear()
  
  def _draw (self):
    self._clear()
    self.level_tags = [self.canvas.create_rectangle(x * 20, y * 20, (x + 1) * 20, (y + 1) * 20, fill = "black")
                       for x in xrange(10)
                       for y in xrange(10)
                       if self.walls[x + y * 10]
                       ]
    
  # Destroy all canvas items used to draw the level.
  
  def _clear(self): self.canvas.delete(*self.level_tags)
  
  # set_active is called when the level is activated or de-activated.
  # An active level is a level that contains at least a player, and thus
  # active levels should be drawn.
  
  def set_active(self, active):

    # tofu.GAME_INTERFACE is the current game interface, i.e. the visible part of the
    # game (see GameInterface below).
    # if tofu.GAME_INTERFACE is None, we are running the server, and so we don't have
    # to draw anything !
    
    if tofu.GAME_INTERFACE:
      
      # If the level is active, we set its canvas to the game interface Tk canvas in
      # order to make the level visible.
      # Else, we set the canvas to None to hide the level.
      
      if active: self.set_canvas(tofu.GAME_INTERFACE.canvas)
      else:      self.set_canvas(None)
      
    # Delegates AFTER, because set_active(0) can call save(), and we DON'T WANT to
    # save the Tk canvas !
    tofu.Level.set_active(self, active)
    
  def discard(self):
    # When the level is discarded, we hide it by setting the canavas to None.
    # Remove the canvas BEFORE discarding, because discard may save the character, and
    # we DON'T WANT to save the Tk canvas !
    self.set_canvas(None)
    
    tofu.Level.discard(self)
    
  # add_mobile is called when a mobile is added into the level.
  # When a mobile is added in the level, we set the mobile's canvas to the level canvas,
  # and thus if the level is displayed in the game interface canvas, the mobile will be
  # displayed too.
  
  def add_mobile(self, mobile):
    tofu.Level.add_mobile(self, mobile)
    mobile.set_canvas(self.canvas)
    
  # remove_mobile is called when a mobile is removed from the level.
  # When a mobile is removed from the level, we set the mobile's canvas to None,
  # in order to hide the mobile if it was displayed.
  
  def remove_mobile(self, mobile):
    mobile.set_canvas(None)
    tofu.Level.remove_mobile(self, mobile)
    
  # add_wall is called when a wall is added in the level.
  # After adding the wall, we redraw the level if needed.
  
  def add_wall(self, x, y):
    self.walls[x + y * 10] = 1
    if self.canvas: self._draw()
    

# A Player represent a human player.

class Player(tofu.Player):

  # Player.__init__ is called when a NEW player is created (NOT when an existent player
  # logon !).
  # filename and password are the player's login and password. An additional string data 
  # can be passed by the client, here we ignore them.
  
  # Player.__init__ must create at least one mobile for the player, then add this mobile
  # in a level and finally add the mobile in the player.
  
  def __init__(self, filename, password, client_side_data = ""):
    tofu.Player.__init__(self, filename, password)
    
    level     = Level.get("0_0")
    character = PlayerCharacter(self.filename)
    level.add_mobile(character)
    self .add_mobile(character)
    

# An Action is an action a mobile can accomplish.
# Here, we have 5 actions: 4 moves, and wall creation. 

ACTION_MOVE_LEFT   = 1
ACTION_MOVE_RIGHT  = 2
ACTION_MOVE_UP     = 3
ACTION_MOVE_DOWN   = 4
ACTION_CREATE_WALL = 5

class Action(tofu.Action):
  def __init__(self, action = 0):
    tofu.Action.__init__(self)
    self.action = action

# A state is the state of a mobile, here its current X,Y position.
# spc is used to indicate special action like wall creation.

class State(tofu.State):
  def __init__(self, x, y, spc = 0):
    tofu.State.__init__(self)
    self.x   = x
    self.y   = y
    self.spc = spc
    
  # is_crucial must returns true if the state is crucial.
  # Non-crucial states can be dropped, either for optimization purpose or because of
  # network protocol (currently we use TCP, but in the future we may use UDP to send
  # non-crucial states).
  
  def is_crucial(self): return self.spc
  

# A mobile is anything that can move and evolve in a level. This include player characters
# but also computer-controlled objects (also named bots).
  
class Mobile(tofu.Mobile):
  def __init__(self, name):
    tofu.Mobile.__init__(self)
    
    # x and y are the position of the mobile. name is the text displayed in the interface.
    # canvas and tag are the tk canvas in which the mobile is drawn, and the
    # corresponding canvas item.
    
    self.x      = 4
    self.y      = 4
    self.name   = name[:4]
    self.canvas = None
    self.tag    = None

  # Sets the Tk canvas and draws the mobile in this canvas. If the canvas is None, the
  # mobile's canva items are destroyed.
  
  def set_canvas(self, canvas):
    if self.canvas:
      self.canvas.delete(self.tag)
      self.tag = None
      
    self.canvas = canvas
    
    if canvas:
      self.tag = canvas.create_text(self.x * 20 + 10, self.y * 20 + 10, text = self.name)
      
  # do_action is called when the mobile executes the given action. It is usually called
  # on the server side.
  # It must return the new State of the Mobile, after the action is executed.
  
  def do_action(self, action):
    if action:
      
      # Computes the new X,Y position.
      
      new_x, new_y = self.x, self.y
      if   action.action == ACTION_MOVE_LEFT : new_x -= 1
      elif action.action == ACTION_MOVE_RIGHT: new_x += 1
      elif action.action == ACTION_MOVE_UP   : new_y -= 1
      elif action.action == ACTION_MOVE_DOWN : new_y += 1
      
      # Checks if we are out of the level, i.e. if the mobile moves to a new level.
      
      new_level = self.level
      if new_x < 0: new_x += 10; new_level = self.level.neighbour(-1,  0)
      if new_x > 9: new_x -= 10; new_level = self.level.neighbour( 1,  0)
      if new_y < 0: new_y += 10; new_level = self.level.neighbour( 0, -1)
      if new_y > 9: new_y -= 10; new_level = self.level.neighbour( 0,  1)
      
      # Checks if the new position is inside a wall.
      
      if not new_level.walls[new_x + new_y * 10]:
        if not new_level is self.level:
          
          # Change to new level.
          
          self.level.remove_mobile(self)
          new_level.add_mobile(self)

        # Return a state with the new position.
        self.doer.action_done(State(new_x, new_y, action.action))
        return
        #return State(new_x, new_y, action.action)
      
    # Else, the mobile doesn't move => we return a state with the previous position.
    self.doer.action_done(State(self.x, self.y))
    #return State(self.x, self.y)
  
  # set_state is called when the mobile's state change, due to the execution of an
  # action. It is called BOTH server-side and client-side.
  
  def set_state(self, state):
    tofu.Mobile.set_state(self, state)
    
    # If the new position is different than the old one, update the mobile and, if
    # needed, move the corresponding canvas item.
    
    if (self.x, self.y) != (state.x, state.y):
      self.x = state.x
      self.y = state.y
      if self.tag: self.canvas.coords(self.tag, self.x * 20 + 10, self.y * 20 + 10)
      
    # If the action was "create wall", create the wall !
    
    if state.spc == ACTION_CREATE_WALL: self.level.add_wall(self.x, self.y)
    
  def discard(self):
    # When the mobile is discarded, we hide it by setting the canavas to None.
    # Remove the canvas BEFORE discarding, because discard may save the character, and
    # we DON'T WANT to save the Tk canvas !
    self.set_canvas(None)
    
    tofu.Mobile.discard(self)
    

# A PlayerCharacter is a Mobile controlled by a human player.

class PlayerCharacter(Mobile):
  def __init__(self, name):
    Mobile.__init__(self, name)
    
    # action is the next action the character will do; it is set by the game interface.
    
    self.action = None
    
  # next_action is called when the character must choose its next action.
  # Here we simply return self.action.
  
  def next_action(self):
    if self.action:
      action, self.action = self.action, None
      return action
    
  # control_owned is called on the client-side when the player gets the control of the
  # mobile (i.e. the mobile is not a bot).
  
  def control_owned(self):
    tofu.Mobile.control_owned(self)
    
    # Set the game interface player character to this mobile.
    # The game interface will set the action for this mobile.
    
    tofu.GAME_INTERFACE.player_character = self
    
    
# A Bot is a Mobile controlled by the computer player.

class Bot(Mobile):
  def __init__(self, name = "bot"):
    Mobile.__init__(self, name = "bot")
    
    # Set the bot attribute to true. Tofu will now consider this Mobile as a bot.
    
    self.bot = 1
    self.direction = -40
    
  # next_action is called when the character must choose its next action.
  # Here, the bot moves horizontally.
    
  def next_action(self):
    dir = cmp(self.direction, 0)
    self.direction += 1
    if self.direction > 40: self.direction = -49
    if self.direction / 10.0 == self.direction // 10 :
      if   self.direction < 0: return Action(ACTION_MOVE_LEFT)
      elif self.direction > 0: return Action(ACTION_MOVE_RIGHT)
      
      
# GameInterface is the interface of the game. Here, we use Tk and thus GameInterface
# inherits from Tk toplevel window.

class GameInterface(tofu.GameInterface, Tkinter.Toplevel):
  def __init__(self):
    
    # Initialises Tk and install Twisted Tk support.
    
    tkroot = Tkinter.Tk(className = 'tofu_demo')
    tkroot.withdraw()
    import twisted.internet.tksupport
    twisted.internet.tksupport.install(tkroot)
    
    tofu.GameInterface.__init__(self)
    Tkinter.Toplevel.__init__(self, tkroot)
    
    # Creates a canvas.
    
    self.canvas = Tkinter.Canvas(self, bg = "white")
    self.canvas.place(x = 0, y = 0, width = 200, height = 200)
    
    # The character we are playing.
    
    self.player_character = None
    
    # Binds cursor keys.
    
    self.bind("<Key-Up>"   , self.on_move_up)
    self.bind("<Key-Down>" , self.on_move_down)
    self.bind("<Key-Left>" , self.on_move_left)
    self.bind("<Key-Right>", self.on_move_right)
    self.bind("<Key- >"    , self.on_create_wall)
    
    # To quite the game, we call GameInterface.end_game().
    
    self.bind("<Key-q>"    , lambda event = None: self.end_game())
    self.bind("<Destroy>"  , lambda event = None: self.end_game())

  # When a key is pressed, we set the current character's action to a new action
  # according to that key.
  
  def on_move_left  (self, event = None): self.player_character.action = Action(ACTION_MOVE_LEFT)
  def on_move_right (self, event = None): self.player_character.action = Action(ACTION_MOVE_RIGHT)
  def on_move_up    (self, event = None): self.player_character.action = Action(ACTION_MOVE_UP)
  def on_move_down  (self, event = None): self.player_character.action = Action(ACTION_MOVE_DOWN)
  def on_create_wall(self, event = None): self.player_character.action = Action(ACTION_CREATE_WALL)
  
  # ready is called when the client has contacted the server and anything is ready.
  # In particular, we can now call self.notifier.login_player to logon the server.
  
  def ready(self, notifier):
    tofu.GameInterface.ready(self, notifier)
    
    login, password = sys.argv[-1], "test"
    self.notifier.login_player(login, password)
    

# Tofu uses serialization to transfert object from server to client and vice-versa, and
# to store level and player data in local file.
# Tofu can use 4 different protocol: cPickle, tofu.pickle_sec (a cPickle with a limited
# list of classes), Cerealizer, Jelly (from Twisted). You can also use different protocols
# for local file and network.

# Some concerns about these protocols :
#  - cPickle is not safe for network and must not be used for that !!!
#  - tofu.pickle_sec, Cerealizer and Jelly require that you register the classes that are
#    safe
#  - Jelly has trouble with C-defined types (including e.g. Soya objects)


# My advice is to use cPickle for local file (faster), and Cerealizer for network.
# To each protocol corresponds a function like :
#     tofu.enable_<protocol>(enable_for_local, enable_for_network)

tofu.enable_pickle    (1, 0)
tofu.enable_cerealizer(0, 1)


# Registers our classes as safe for Cerealizer

import cerealizer
cerealizer.register_class(Action)
cerealizer.register_class(State)
cerealizer.register_class(Mobile)
cerealizer.register_class(Bot)
cerealizer.register_class(PlayerCharacter)
cerealizer.register_class(Level)
cerealizer.register_class(Player)



# To use cPickle:

# tofu.enable_pickle(1, 1)


# To use tofu.pickle_sec:

# tofu.enable_pickle_sec(1, 1)
# tofu.pickle_sec.safe_classes(
#   "demo.Action",
#   "demo.Bot",
#   "demo.Level",
#   "demo.Mobile",
#   "demo.PlayerCharacter",
#   "demo.State",
#   "demo.Player",
#   )


# To use Cerealizer:

# tofu.enable_cerealizer(1, 1)
# import cerealizer
# cerealizer.register_class(Action)
# cerealizer.register_class(State)
# cerealizer.register_class(Mobile)
# cerealizer.register_class(Bot)
# cerealizer.register_class(PlayerCharacter)
# cerealizer.register_class(Level)
# cerealizer.register_class(Player)


# To use Jelly:

# tofu.enable_jelly(1, 1)
# tofu.make_jellyable(
#   Action,
#   Bot,
#   Level,
#   Mobile,
#   PlayerCharacter,
#   State,
#   Player,
#   )


# Inits Tofu with our classes.

tofu.init(GameInterface, Player, Level, Action, State, Mobile)
