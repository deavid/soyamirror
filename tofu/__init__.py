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

"""tofu -- a practical high-level network game engine, based on Twisted

Tofu is designed for games where players play one or several characters accross
several levels. This includes jump'n run games, RPG or RTS, but not Tetris-like
games or board game (chess, go,...).

Using the same code, Tofu can prodide single-player game (module tofu.single),
server (module tofu.server) and client (module tofu.client). The same architecture
should also allow a peer-to-peer game, but it is not implemented yet.

Tofu defines base classes for game-related objects. To create a Tofu-based game,
you need to subclass these classes : tofu.GameInterface, tofu.Player, tofu.Level,
tofu.Action, tofu.State, tofu.Mobile. Then you must call tofu.init and pass it your
classes.

In addition to network, Tofu also manages, loads and saves Player and Levels data.
All data are stored in files on the server. tofu.path is the list of directory where
these files are located; by default the list is empty by you must add your own data
directory in it.

For tranfering object through network and for saving them locally, Tofu can use either
cPickle or Cerealizer. As cPickle is not secure, you SHOULD NOT use it for network
transfer though.

The tofu module has the following global variables:
 - IDLER: the current Idler
 - NOTIFIER: the current Notifier (for internal purpose)
 - GAME_INTERFACE: the current GameInterface (None for the server)


HOW IT WORK ?

This modules define classes for Mobile, i.e. anything that moves of evolve in the
network game. In particular, both human-played and computer-played (=bot) characters
are Mobile.

Tofu uses a 3-level system; the 3 levels are: Controllers, Doers and Mobiles. Mobiles
are anything that can move, including both player's characters and bots. Controllers
determine which Action a Mobile will do (by reading input like keyboard, or by AI for
bots). Doers execute these Actions and return the new States for the Mobile. Finally
the Mobile State is updated.

The last step (updating Mobile's State) occurs on both client and server. The 2 first
ones can be done locally (LocalController, LocalDoer) or remotely (RemoteController,
RemoteDoer).
Typical configurations are:


* single player game
Everything is local.

            | client A
------------|-----------------
Mobile      | LocalController
played by A | LocalDoer
------------|-----------------
Bot         | LocalController
            | LocalDoer


* client-server multiplayer game
On the client-side, Mobile always have a RemoteDoer

            | client A         | server           | client B
------------|------------------|------------------|------------------
Mobile      | LocalController  | RemoteController | RemoteController
played by A | RemoteDoer       | LocalDoer        | RemoteDoer
------------|------------------|------------------|------------------
Bot         | RemoteController | LocalController  | RemoteController
            | RemoteDoer       | LocalDoer        | RemoteDoer


* peer-to-peer multiplayer game (NOT YET IMPLEMENTED)

            |client A          | client B
------------|------------------|------------------
Mobile      | LocalController  | RemoteController
played by A | LocalDoer        | RemoteDoer
------------|------------------|------------------
Mobile      | RemoteController | LocalController
played by B | RemoteDoer       | LocalDoer
------------|------------------|------------------
Bot         | LocalController  | RemoteController
            | LocalDoer        | RemoteDoer
"""

import os.path, time, weakref, struct
import twisted.internet.selectreactor
from bisect import insort

import cerealizer

try: set
except: from sets import Set as set

__all__ = ["init", "Notifier", "GameInterface", "Idler", "Unique", "SavedInAPath", "Player", "Level", "Action", "State", "Mobile", "LocalController", "RemoteController", "LocalDoer", "RemoteDoer"]

path = []

VERSION = "0.5"

CODE_LOGIN_PLAYER  = ">"
CODE_LOGOUT_PLAYER = "<"
CODE_CHECK_VERSION = "V"
CODE_ASK_UNIQUE    = "u"
CODE_DATA_UNIQUE   = "U"
CODE_DATA_STATE    = "S"
CODE_DATA_ACTION   = "A"
CODE_OWN_CONTROL   = "+"
CODE_ADD_MOBILE    = "M"
CODE_REMOVE_MOBILE = "m"
CODE_ENTER_LEVEL   = "L"
CODE_ERROR         = "E"



class Notifier(object):
  def __init__(self):
    global NOTIFIER
    NOTIFIER = self
    
  def notify_action(self, mobile, action): pass
  def notify_state (self, mobile, state ): pass
  
  def notify_add_mobile   (self, mobile): pass
  def notify_remove_mobile(self, mobile): pass
  
  def notify_enter_level(self, level): pass
  
  def check_level_activity(self, level): pass
  
  def notify_discard(self, unique): pass
  
  def login_player (self, filename, password, *client_side_data): pass
  def logout_player(self): pass
NOTIFIER = Notifier()


GAME_INTERFACE = None
class GameInterface(object):
  """GameInterface

The game visible interface. A GameInterface is created for each client, but NOT for
the server.

You must subclass this class to make a game-specific GameInterface class, and create an
instance of your GameInterface when the client starts."""
  def __init__(self, *args, **kargs):
    global GAME_INTERFACE
    GAME_INTERFACE = self
    
  def ready(self, notifier):
    """GameInterface.ready()

Called when the network connection is ready.
You should override this method, and call NOTIFIER.login_player()."""
    self.notifier = notifier
    
  def network_error(self, reason):
    """GameInterface.network_error(reason)

Called when the network connection fails or have been lost.
You should override this method, and ends the game."""
    pass
  
  def end_game(self, *return_values):
    """GameInterface.end_game()

Ends the game."""
    NOTIFIER.logout_player()
    IDLER.stop(*return_values)
    
IDLER = None
class Idler:
  """Idler

Tofu's main loop.

WARNING: the default Tofu Idler is very limited (no FPS regulation,...).
You should provide your own Idler (Soya 3D includes a very good one)."""
  def __init__(self):
    self.levels           = []
    self.next_round_tasks = []
    self.active           = 0
    self.round_duration   = 0.030
    self.return_values    = None
    
    twisted.internet.selectreactor.install()
    self.reactor = twisted.internet.reactor
    
    global IDLER
    IDLER = self
    
    print "* Tofu * IDLER created !"
    
  def stop(self, *return_values):
    """Idler.stop()

Stops the Idler."""
    self.active = 0
    self.return_values = return_values
    
  def idle(self):
    """Idler.idle()

Starts the main loop."""
    self.active       = 1
    self.current_time = time.time()
    
    while self.active:
      self.begin_round()
      time.sleep(self.round_duration)
      
    return self.return_values
  
  def begin_round(self):
    """Idler.begin_round()

Called repeatedly when the Idler start idling.
You may want to override this method."""
    if self.next_round_tasks:
      for task in self.next_round_tasks: task()
      self.next_round_tasks = []
    self.reactor.iterate()
    for level in self.levels: level.begin_round()
    Level.discard_inactives()
    
  def add_level(self, level):
    """Idler.add_level(level)

Adds LEVEL in the list of played level. This method is automatically called by
Level.set_active(), so you shouldn't care about it."""
    self.levels.append(level)
    
  def remove_level(self, level):
    """Idler.remove_level(level)

Removes LEVEL in the list of played level. This method is automatically called by
Level.set_active(), so you shouldn't care about it."""
    self.levels.remove(level)


class _Base(object):
  pass


def _getterbyuid(klass, filename): return klass.getbyuid(filename)

class Unique(_Base):
  """Unique

A Unique object is an object that has a unique identifiant (UID) on each remote host
(server or client).

"""
  _alls = weakref.WeakValueDictionary()
  
  def __init__(self):
    self.uid = id(self)
    Unique._alls[self.uid] = self
    
  def getbyuid(uid):
    """Unique.getbyuid(uid) -> Unique

This static method returns the object of the given UID."""
    return Unique._alls.get(uid) or Unique.not_found(uid)
  getbyuid = staticmethod(getbyuid)
  
  def not_found(uid): raise ValueError("No uid %s !" % uid)
  not_found = staticmethod(not_found)
  
  def hasuid(uid):
    """Unique.hasuid(uid) -> bool

This static method returns true if an object with the given UID exists."""
    return Unique._alls.has_key(uid)
  hasuid = staticmethod(hasuid)
  
  def loaded(self):
    """Unique.loaded()

Called when the Unique is loaded from a local file."""
    self.uid = id(self)
    Unique._alls[self.uid] = self
    
  def received(self):
    """Unique.received()

Called when the Unique is received from the network."""
    Unique._alls[self.uid] = self
    
  def discard(self):
    """Unique.discard()

Discards the Unique, i.e. this object won't be used any more.
If the Unique is needed later, it will be either loaded from a local file, or recovered
through network.
If the Unique is saveable, this method may call save(), in order to save the Unique
before it is garbage collected."""
    try:
      del Unique._alls[self.uid]
    except: pass
    else:
      NOTIFIER.notify_discard(self)
      
  def dumpuid  (self): return struct.pack("!i", self.uid)
  def undumpuid(data): return Unique.getbyuid(struct.unpack("!i", data)[0])
  undumpuid = staticmethod(undumpuid)
  
  def __repr__(self): return "<%s UID:%s>" % (self.__class__.__name__, self.uid)
  
  def dump  (self): return network_serializer.dumps(self, 1)
  def undump(data): return network_serializer.loads(data)
  undump = staticmethod(undump)


# Comes from Soya
_SAVING = None

def _getter(klass, filename): return klass.get (filename)

class SavedInAPath(Unique):
  """SavedInAPath

A special class of Unique that can be saved in a file.
When a SavedInAPath object is serialized, only the filename is serialized, and not all the
object data."""
  DIRNAME = ""

  def __init__(self):
    Unique.__init__(self)
    self._filename = ""
    
  def __repr__(self): return "<%s %s UID:%s>" % (self.__class__.__name__, self.filename, self.uid)
  
  def get(klass, filename):
    """SavedInAPath.get(filename) -> SavedInAPath

This class method gets a SavedInAPath object from its filename.
The object will be loaded if needed, but if it is already loaded, the same reference will
be returned."""
    return klass._alls2.get(filename) or klass._alls2.setdefault(filename, klass.load(filename))
  get = classmethod(get)
  
  def load(klass, filename):
    """SavedInAPath.load(filename) -> SavedInAPath

This class method loads a SavedInAPath object from its file."""
    if ".." in filename: raise ValueError("Cannot have .. in filename (security reason)!")
    filename = filename.replace("/", os.sep)
    for p in path:
      file = os.path.join(p, klass.DIRNAME, filename + ".data")
      if os.path.exists(file):
        obj = local_serializer.loads(open(file, "rb").read())
        obj.loaded()
        klass._alls2[filename] = obj
        return obj
    raise ValueError("No %s named %s" % (klass.__name__, filename))
  load = classmethod(load)
  
  def save(self, filename = None):
    """SavedInAPath.save(filename = None)

Saves a SavedInAPath object in the associated file."""
    global _SAVING
    try:
      _SAVING = self # Hack !!
      data = local_serializer.dumps(self, 1) # Avoid destroying the file if the serialization causes an error.
      open(filename or os.path.join(path[0], self.DIRNAME, self.filename.replace("/", os.sep)) + ".data", "wb").write(data)
    finally:
      _SAVING = None
      
  def delete(self, filename = None):
    """SavedInAPath.delete(filename = None)

Delete a SavedInAPath's file."""
    del self._alls2[self.filename]
    Unique.discard(self)
    
    filename = filename or os.path.join(path[0], self.DIRNAME, self.filename.replace("/", os.sep)) + ".data"
    print "* Tofu * Deleting %s %s (file %s) !" % (self.__class__.__name__, self.filename, filename)
    os.remove(filename)
    
  def get_filename(self): return self._filename
  def set_filename(self, filename):
    if self._filename:
      try: del self._alls2[self.filename]
      except KeyError: pass
    if filename: self._alls2[filename] = self
    self._filename = filename
  filename = property(get_filename, set_filename)
  
  def availables(klass):
    """SavedInAPath.availables()

This class method returns a list of all available files (e.g. a list of all Levels or
all Players)."""
    import dircache
    filenames = dict(klass._alls2)
    for p in path:
      for filename in dircache.listdir(os.path.join(p, klass.DIRNAME)):
        if filename.endswith(".data"): filenames[filename[:-5]] = 1
    filenames = filenames.keys()
    filenames.sort()
    return filenames
  availables = classmethod(availables)
  
  def discard(self):
    print "* Tofu * Discard %s %s %s..." % (self.__class__.__name__.lower(), self.filename, self.uid)
    del self._alls2[self.filename]
    Unique.discard(self)
    
  def loaded(self):
    assert not self._alls2.get(self.filename), "Dupplicated SavedInAPath object %s !" % self.filename
    Unique.loaded(self)
    self._alls2[self.filename] = self
    
  def received(self):
    assert not self._alls2.get(self.filename), "Dupplicated SavedInAPath object %s !" % self.filename
    Unique.received(self)
    self._alls2[self.filename] = self
    
  def dump(self):
    """SavedInAPath.dump() -> str

Serialize the object."""
    global _SAVING
    try:
      _SAVING = self # Hack !!
      return network_serializer.dumps(self, 1)
    finally:
      _SAVING = None
      
  def __reduce_ex__(self, i = 0):
    if (not _SAVING is self) and self._filename: # self is saved in another file, save filename only
      return (_getter, (self.__class__, self.filename))
    return object.__reduce_ex__(self, i)

  
class Player(SavedInAPath):
  """Player

A Player. Player is a subclass of SavedInAPath, and thus Players are associated
to a filename. When the Player logout, it is automatically saved into the corresponding
file. If he login later, the Player will be loaded from the file.

Interesting attributes are :
 - mobiles: the list of mobile controled by the human Player (no bots)
 - filename: the Player's login and also the file in which the Player data will be stored
 - password: the password
 - address: the address of the remote host, 1 for single player game, and None if not connected.
 - notifier: the Player's notifier

You must subclass this class to make a game-specific Player class."""
  DIRNAME = "players"
  _alls2 = {}
  
  def __init__(self, filename, password, client_side_data = ""):
    """Player(filename, password, client_side_data = "") -> Player

Creates a new Player with the given FILENAME and PASSWORD.

__init__ is ONLY called for NEW Player at their FIRST login.
You must override this contructor, in order to create at least one Mobile for the new
Player, and add these Mobiles in some Levels.

CLIENT_SIDE_DATA contains additional data given by the client; you can use them to
store some data on the client side. Default implementation ignore them."""
    if (".." in filename) or ("/" in filename): raise ValueError("Invalide Player name %s (need a valid filename) !" % filename)
    
    SavedInAPath.__init__(self)
    
    print "* Tofu * Creating new player %s..." % filename
    
    self.filename = filename
    self.password = password
    self.mobiles  = []
    self.notifier = None
    self.address  = None
    
  def add_mobile(self, mobile):
    if not mobile.level: raise ValueError("You must add the mobile inside a level before !")
    mobile.player_name = self.filename
    self.mobiles.append(mobile)
    
  def remove_mobile(self, mobile):
    self.mobiles.remove(mobile)
    mobile.player_name = ""
    if not self.mobiles: self.kill(mobile)
    
  def kill(self, last_mobile):
    self.logout(0)
    
  def login(self, notifier, address, client_side_data = ""):
    """Player.login(notifier, address, client_side_data = "")

Login the Player.

CLIENT_SIDE_DATA contains additional data given by the client; you can use them to
store some data on the client side. Default implementation ignore them."""
    if self.address: raise ValueError("Player %s is already logged !" % self.filename)
    print "* Tofu * Player %s login !" % self.filename
    
    for mobile in self.mobiles:
      if not mobile in mobile.level.mobiles: mobile.level.add_mobile(mobile)
      
    self.notifier = notifier
    self.address  = address
    
    for mobile in self.mobiles:
      mobile.send_control_to(self)
      
    for level in set([mobile.level for mobile in self.mobiles]):
      notifier.notify_enter_level(level)
      
  def logout(self, save = 1):
    """Player.logout(SAVE = 1)

Logout the Player."""
    if self.address:
      print "* Tofu * Player %s logout !" % self.filename
      try: self.notifier.transport.loseConnection()
      except: pass
      self.notifier = None
      self.address  = None
      if save: self.discard()
      
      # Do this AFTER discard => when discard saves the player's mobiles, the mobiles still have their level, and so the level is saved.
      for mobile in self.mobiles:
        if mobile.level: mobile.level.remove_mobile(mobile)

      if GAME_INTERFACE: GAME_INTERFACE.end_game()
      
  def loaded(self):
    SavedInAPath.loaded(self)
    for mobile in self.mobiles: mobile.loaded()
    
  def discard(self):
    for mobile in self.mobiles: mobile.discard()
    SavedInAPath.discard(self)


class Level(SavedInAPath):
  """Level

A game Level. Level is a subclass of SavedInAPath, and thus Levels are associated
to a filename. When the Level is useless, it is automatically saved into the corresponding
file. If needed later, the Level will be loaded from the file.

You must subclass this class to make a game-specific Level class."""
  DIRNAME = "levels"
  _alls2 = weakref.WeakValueDictionary()
  
  def __init__(self, filename = ""):
    """Level(filename = "") -> Level

Creates a Level called FILENAME."""
    SavedInAPath.__init__(self)
    
    if filename: self.filename = filename
    self.mobiles  = []
    self.round    = 0
    self.active   = 0
    
  def add_mobile(self, mobile):
    """Level.add_mobile(mobile)

Adds a Mobile in the Level.
If needed, the addition will be notified to remote users, and the level active state will
be updated.
"""
    mobile._added_into_level(self)
    self.mobiles.append(mobile)
    
    NOTIFIER.notify_add_mobile(mobile)
    
    NOTIFIER.check_level_activity(self)
    
  def remove_mobile(self, mobile):
    """Level.remove_mobile(mobile)

Removes a Mobile from the Level.
If needed, the removal will be notified to remote users, and the level active state will
be updated."""
    if mobile.doer.remote: mobile.doer.purge()
    
    NOTIFIER.notify_remove_mobile(mobile) # Notify BEFORE removals => we can use mobile.level
    self.mobiles.remove(mobile)
    mobile._added_into_level(None)
    
    NOTIFIER.check_level_activity(self)
    
  def set_active(self, active):
    """Level.set_active(active)

Sets the level active state. If the level is active, the Mobile in the Level will be
played.

You should not call this method directly; the level active state is automatically
determined by the Mobile of the Level.
You may want to override this method, e.g. to display an active level."""
    if active != self.active:
      if active: print "* Tofu * Level %s %s activated !"  % (self.filename, self.uid)
      else:      print "* Tofu * Level %s %s inactivated." % (self.filename, self.uid)
      if self.active: IDLER.remove_level(self)
      self.active = active
      if self.active: IDLER.add_level(self)
      
      if not active: self.discard()
      
  def begin_round(self):
    """Level.begin_round()

If the Level is active, this method is called repeatedly by the Idler.
You may override this method; the default implementation calls all Mobile's begin_round."""
    if self.active:
      self.round += 1
      for mobile in self.mobiles: mobile.begin_round()
      
  def received(self):
    SavedInAPath.received(self)
    self.active   = 0
    for mobile in self.mobiles: mobile.received()
    
    NOTIFIER.check_level_activity(self)
    
  def loaded(self):
    SavedInAPath.loaded(self)
    
    self.active = 0
    for mobile in self.mobiles: mobile.loaded()
    
  def discard(self):
    if not Unique.hasuid(self.uid): return # Already discarded
    
    for mobile in self.mobiles: mobile.discard()
    SavedInAPath.discard(self)
    
  def discard_inactives(clazz):
    """Level.discard_inactives()

This class method discards ALL non-active levels.
It is called by the Idler each begin_round."""
    for level in clazz._alls2.values():
      if not level.active: level.discard()
  discard_inactives = classmethod(discard_inactives)
  

class Action(_Base):
  """Action

An Action is something a Mobile (like a character) wants to accomplish.
Typical example of Action are: move forward, turn left,...

You must subclass this class to make a game-specific Action class."""
  def __init__(self): pass

  def is_crucial(self):
    """Action.is_crucial() -> bool

Returns true if the Action is crucial, i.e. it MUST not be lost in the network
hyperspace (like UDP protocol sometimes does).

Default implementation always returns true. You can override it if you have non-crucial
Action."""
    return 1
  
  def dump(self):
    """Action.dump() -> str

Serialize the Action."""
    return network_serializer.dumps(self, 1)
  
  def undump(data):
    """Action.undump(data) -> Action

Static method that deserialize an Action (previously serialized by Action.dump)."""
    return network_serializer.loads(data)
  undump = staticmethod(undump)
  
  
class State(_Base):
  """State

A State is the current position of a Mobile (like a character).
Typical example of State is: (X, Y) coordinates == (10.0, 5.0),...

You must subclass this class to make a game-specific State class."""
  droppable = 0
  def __init__(self):
    self.round  = -1 # XXX needed ?

  def __cmp__(self, other): return cmp(self.round, other.round)
  def is_crucial(self):
    """State.is_crucial() -> bool

Returns true if the State is crucial, i.e. it MUST not be lost in the network
hyperspace (like UDP protocol sometimes does).

Default implementation always returns true. You can override it if you have non-crucial
State."""
    return 1
  
  def dump(self):
    """State.dump() -> str

Serialize the State."""
    return network_serializer.dumps(self, 1)
  
  def undump(data):
    """State.undump(data) -> Action

Static method that deserialize a State (previously serialized by State.dump)."""
    return network_serializer.loads(data)
  undump = staticmethod(undump)
  

QUEUE_LENGTH = 3

class LocalController(_Base):
  """LocalController

The Controller is the object responsible for determining the Actions a Mobile will do.

The default LocalController implementation delegates this task to Mobile.next_action(),
but you may want to subclass the LocalController class, e.g. in KeybordController and
AIController."""
  remote = 0
  def __init__(self, mobile):
    self.mobile = mobile
    
  def begin_round(self):
    action = self.mobile.next_action()
    self.mobile.doer.do_action(action)
    
    
class RemoteController(_Base):
  """RemoteController

A RemoteController is a Controller for a remotely-controled Mobile, i.e. a Mobile who
receives its Actions from a remote server."""
  remote = 1
  def __init__(self, mobile):
    self.mobile = mobile
    self.actions = []
    
  def push(self, action): self.actions.append(action)

  def begin_round(self):
    if self.actions:
      while len(self.actions) > QUEUE_LENGTH:
        action = self.actions.pop(0)
        if action.is_crucial(): self.mobile.doer.do_action(action)
      self.mobile.doer.do_action(self.actions.pop(0))
    else:
      self.mobile.doer.do_action(None)
      
class LocalDoer(_Base):
  """LocalDoer

The Doer is the object responsible for doing a Mobile's Action, and returning
the resulting State.

The default LocalDoer implementation delegates this task to Mobile.do_action(action),
you probably won't have to subclass the LocalDoer class."""
  remote = 0
  def __init__(self, mobile):
    self.mobile = mobile
    
  def do_action(self, action):
    self.mobile.do_action(action)
    
  def action_done(self, state):
    if state:
      state.round = self.mobile.round
      if (not state.droppable) or state.is_crucial(): NOTIFIER.notify_state(self.mobile, state)
      self.mobile.set_state(state)
      
  def begin_round(self): pass
  
      
class RemoteDoer(_Base):
  """RemoteDoer

A RemoteDoer is a Doer for a remotely-played Mobile, i.e. a Mobile whoose Action are
executed on a remote host, and who receives its States from the remote host."""
  remote = 1
  def __init__(self, mobile):
    self.mobile = mobile
    self.states = []
    
  def push(self, state):
    insort(self.states, state)
    
  def do_action(self, action):
    if action:
      NOTIFIER.notify_action(self.mobile, action)
      
  def begin_round(self):
    if self.states:
      while len(self.states) > QUEUE_LENGTH:
        state = self.states.pop(0)
        if state.is_crucial(): self.mobile.set_state(state)
          
      self.mobile.set_state(self.states.pop(0))
      
  def purge(self):
    if self.states:
      while len(self.states) > 1:
        state = self.states.pop(0)
        if state.is_crucial(): self.mobile.set_state(state)
        
      self.mobile.set_state(self.states.pop(0))
      
      
class Mobile(Unique):
  """Mobile

A Mobile is anything that moves of evolve in the network game. In particular, both
human-played and computer-played (=bot) characters are Mobile. You must subclass
the Mobile class to create your own game-specific Mobiles.

Attributes are:
 - controller: the Mobile's Controller
 - doer: the Mobile's Doer
 - round: the round counter
 - bot: true if the Mobile is an AI-played bot, false if it is a human-played
   character. Defaults to false.
"""
  def __init__(self):
    """Mobile() -> Mobile

Create a new Mobile. Mobile creation should only be done on the server, i.e. either
in Mobile.do_action() or in Player.__init__(), both being called only server-side.
Then, when calling Level.add_mobile(mobile), the server will automatically send the
mobile to clients.

By default, the Mobile has a LocalController and a LocalDoer, i.e. it is totally locally
managed. If you want to transfert the control to another player, use
Mobile.send_control_to(player).
"""
    Unique.__init__(self)
    
    self.round       = 0
    self.level       = None
    self.controller  = LocalController(self)
    self.doer        = LocalDoer     (self)
    self.bot         = 0
    self.player_name = ""
    
  def _added_into_level(self, level):
    """Mobile._added_into_level(level)

Called when the Mobile is added inside a Level, or removed from a Level (in this case,
LEVEL is None)."""
    self.level = level
    
  def begin_round(self):
    """Mobile.begin_round()

If the Mobile's Level is active, this method is called repeatedly by the Idler.
You don't have to override this method; override rather next_action, do_action and
set_state."""
    self.round += 1
    self.controller.begin_round()
    self.doer      .begin_round()
    
  def next_action(self):
    """Mobile.next_action() -> Action or None

Called by LocalController, to get the next Action for this Mobile.
You must override this method."""
    return None
  
  def do_action(self, action):
    """Mobile.do_action(action)

Called by LocalDoer, to accomplish the given ACTION and compute the resulting new State
for the Mobile.
You must override this method, create the new State and then call :

  self.doer.action_done(new_state)

Notice that, if needed, you can create more than one state, and call self.doer.action_done
several time (one per state)."""
    return None
  
  def set_state(self, state):
    """Mobile.set_state(state) -> State

Set the new State of the Mobile. This method is called BOTH server-side and client-side.
You must override this method."""
    pass
  
  def send_control_to(self, player):
    """Mobile.send_control_to(player)

Transfer the control of this Mobile to PLAYER.
This method replace the Mobile's Controller by a RemoteController, and notify PLAYER."""
    # XXX P2P
    if not self.controller.remote: self.controller = RemoteController(self)
    if player: player.notifier.notify_own_control(self)
    
    NOTIFIER.check_level_activity(self.level)
    
  def control_owned(self):
    """Mobile.control_owned()

Called when the control of a Mobile is acquired locally.
This method replace the Mobile's Controller by a LocalController.
You can override it, in order to know which Mobile are locally controled."""
    self.controller = LocalController(self)
    
    NOTIFIER.check_level_activity(self.level)

  def received(self):
    Unique.received(self)
    if not self.controller.remote: self.controller = RemoteController(self)
    else:                          self.controller.actions *= 0
    if not self.doer      .remote: self.doer       = RemoteDoer      (self)
    
  def kill(self):
    IDLER.next_round_tasks.append(self.killed)
    
  def killed(self):
    if self.level:
      self.level.remove_mobile(self)
    player = Player._alls2.get(self.player_name, None)
    if player: player.remove_mobile(self)
    
YourGameInterface = YourPlayer = YourAction = YourState = None

def init(game_interface_class, player_class, level_class, action_class, state_class, mobile_class):
  """init(game_interface_class, player_class, level_class, action_class, state_class, mobile_class)

Initializes Tofu with the given classes. They should be subclasses of the corresponding
Tofu base classes."""
  global YourGameInterface, YourPlayer, YourAction, YourState
  YourGameInterface  = game_interface_class
  YourPlayer         = player_class
  YourAction         = action_class
  YourState          = state_class
  # Currently, Level and Mobile are not needed.

  #if (not local_serializer) or (not network_serializer): raise StandardError("You must define serializer before calling init(). See enable_pickle() and enable_cerealizer().")
    
    
local_serializer   = None
network_serializer = None

def enable_pickle(local, network):
  """enable_pickle(local, network)

Use the cPickle serialization module for LOCAL and/or NETWORK serialization.
Set LOCAL to 1 to use cPickle for local serialization (else use 0).
Set NETWORK to 1 to use cPickle for remote serialization (else use 0) -- CAUTION! cPickle by
itself is not sure!
IF YOU USE CPICKLE OVER NETWORK, YOU ASSUME YOU TRUST THE REMOTE COMPUTER!

E.g. to use cPickle for local file only, do:
  enable_pickle(1, 0)
"""
  import cPickle as pickle
  global local_serializer, network_serializer
  if local  : local_serializer   = pickle
  if network: network_serializer = pickle
  

def enable_cerealizer(local, network):
  """enable_cerealizer(local, network)

Use the Cerealizer serialization module for LOCAL and/or NETWORK serialization.
Set LOCAL to 1 to use Cerealizer for local serialization (else use 0).
Set NETWORK to 1 to use Cerealizer for remote serialization (else use 0).

E.g. to use Cerealizer for both local file and network transfer, do:
  enable_cerealizer(1, 1)
and to use Cerealizer for only for network transfer, do:
  enable_cerealizer(0, 1)
"""
  cerealizer.register(LocalController)
  cerealizer.register(LocalDoer)
  cerealizer.register(RemoteController)
  cerealizer.register(RemoteDoer)
  
  global local_serializer, network_serializer
  if local  : local_serializer   = cerealizer
  if network: network_serializer = cerealizer


# Cerealizer Handler for SavedInAPath and subclass.
class SavedInAPathHandler(cerealizer.ObjHandler):
  def collect(self, obj, dumper):
    if (not _SAVING is obj) and obj._filename: # self is saved in another file, save filename only
      return cerealizer.Handler.collect(self, obj, dumper)
    else: return cerealizer.ObjHandler.collect(self, obj, dumper)

  def dump_obj(self, obj, dumper, s):
    cerealizer.ObjHandler.dump_obj(self, obj, dumper, s)
    if (not _SAVING is obj) and obj._filename: # self is saved in another file, save filename only
      dumper.dump_ref(obj._filename, s)
    else: dumper.dump_ref("", s)

  def dump_data(self, obj, dumper, s):
    if (not _SAVING is obj) and obj._filename: # self is saved in another file, save filename only
      return cerealizer.Handler.dump_data(self, obj, dumper, s)
    else: cerealizer.ObjHandler.dump_data(self, obj, dumper, s)

  def undump_obj(self, dumper, s):
    filename = dumper.undump_ref(s)
    if filename: return self.Class.get(filename)
    return cerealizer.ObjHandler.undump_obj(self, dumper, s)

  def undump_data(self, obj, dumper, s):
    if not getattr(obj, "_filename", 0): # else, has been get'ed
      cerealizer.ObjHandler.undump_data(self, obj, dumper, s)
