# TOFU
# Copyright (C) 2005-2006 Jean-Baptiste LAMY
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


import sys, os.path, time, weakref, struct
from cStringIO import StringIO

import cerealizer, soya, enet

#import tofu.sides as sides; from tofu.sides import *
import tofu_enet.sides as sides; from tofu_enet.sides import *

__all__ = sides.__all__ + ["init", "Notifier", "GameInterface", "MainLoop", "Unique", "SavedInAPath", "Player", "Level", "Action", "State", "Mobile", "LocalController", "RemoteController", "LocalDoer", "RemoteDoer"]

VERSION = "0.6"

CODE_LOGIN_PLAYER  = ">"
CODE_ERROR         = "E"
CODE_ENTER_LEVEL   = "L"
CODE_OWN_CONTROL   = "+"
CODE_ADD_MOBILE    = "M"
CODE_REMOVE_MOBILE = "m"
CODE_ACTION        = "A"
CODE_STATE         = "S"



PORT     = 6900
HOST     = ""
LOGIN    = "jiba"
PASSWORD = "test"
OPT_DATA = ""

soya.set_file_format(cerealizer, cerealizer)

class NetworkError(StandardError): pass

class MainLoop(soya.MainLoop, Multisided):
  @server_side
  @client_side
  @single_side
  def __init__(self, scene):
    soya.MainLoop.__init__(self, scene or soya.World())
    self.levels = []
    
    
  @single_side
  def __init__(self, scene):
    player = Player.get_or_create(filename, password, data)
    player.login(1)
  
  @single_side
  def begin_round(self): soya.MainLoop.begin_round(self)
  
  
  @server_side
  def __init__(self, scene):
    self.ID2players    = {}
    self.action_queues = {}
    self.host = enet.Host(enet.Address(HOST, PORT), 32)
    
  @server_side
  def main_loop(self):
    print "* Tofu * Server ready."
    soya.MainLoop.main_loop(self)
    
  @server_side
  def begin_round(self):
    event = self.host.service(0) # XXX use a blocking call to service() instead of the time.sleep() done in soya.MainLoop (for regulating FPS) ?
    while event.type != 0:
      if   event.type == enet.EVENT_TYPE_CONNECT:
        print "* Tofu * Connection from %s:%s." % (event.peer.address.host, event.peer.address.port)
        
      elif event.type == enet.EVENT_TYPE_DISCONNECT:
        #print "* Tofu * %s:%s disconnected." % (event.peer.address.host, event.peer.address.port)
        player = self.ID2players.get(event.peer.ID)
        if player: player.logout()
        
      elif event.type == enet.EVENT_TYPE_RECEIVE:
        data = event.packet.data
        #print "* Tofu * Received from %s:%s data:\n%s" % (event.peer.address.host, event.peer.address.port, data)
        try:
          code, data2 = data[0], data[1:]
          if   code == CODE_LOGIN_PLAYER:
            nb, data2 = data2.split("\n", 1)
            nb = int(nb)
            login, data2 = data2[:nb], data2[nb:]
            nb, data2 = data2.split("\n", 1)
            nb = int(nb)
            password, data2 = data2[:nb], data2[nb:]
            player = Player.get_or_create(login, password, data2)
            player.login(event.peer)
            self.ID2players[event.peer.ID] = player
            
          elif code == CODE_ACTION:
            action = LOAD_ACTION(data2)
            queue = self.action_queues.get(action.mobile_uid)
            if not queue: queue = self.action_queues[action.mobile_uid] = []
            queue.append(action)
            
          else: raise ValueError("Unknown code '%s'!" % code)
          
        except :
          sys.excepthook(*sys.exc_info())
          print "* Tofu * Error while receiving from %s:%s data:\n%s" % (event.peer.address.host, event.peer.address.port, data)
          packet = enet.Packet("""%s%s: %s""" % (CODE_ERROR, sys.exc_info()[0], sys.exc_info()[1]), enet.PACKET_FLAG_RELIABLE)
          event.peer.send(0, packet)
          #event.peer.disconnect()
          
          
      event = self.host.service(0)
      
    soya.MainLoop.begin_round(self)
    

  @client_side
  def __init__(self, scene):
    self.state_queues = {}
    self.client = enet.Host(None, 1)
    self.peer = self.client.connect(enet.Address(HOST, PORT), 4)
    if not self.peer: raise NetworkError("No peer available!")
    event = self.client.service(5000)
    if event.type == enet.EVENT_TYPE_CONNECT:
      print "* Tofu * Connection to server %s:%s established." % (HOST, PORT)
    else:
      self.peer.reset()
      raise NetworkError("Connection to %s:%s failed!" % (HOST, PORT))
    
    packet = enet.Packet("""%s%s\n%s%s\n%s%s""" % (
      CODE_LOGIN_PLAYER,
      len(LOGIN   ), LOGIN,
      len(PASSWORD), PASSWORD,
      OPT_DATA,
      ), enet.PACKET_FLAG_RELIABLE)
    self.peer.send(0, packet)
    self.client.flush()
    
  @client_side
  def main_loop(self):
    try: soya.MainLoop.main_loop(self)
    finally:
      self.peer.disconnect()
      self.client.flush()
      
  @client_side
  def begin_round(self):
    event = self.client.service(0) # XXX use a blocking call to service() instead of the time.sleep() done in soya.MainLoop (for regulating FPS) ?
    while event.type != 0:
      if   event.type == enet.EVENT_TYPE_DISCONNECT:
        print "* Tofu * disconnected."
        self.stop()
        
      elif event.type == enet.EVENT_TYPE_RECEIVE:
        data = event.packet.data
        try:
          code, data2 = data[0], data[1:]
          if   code == CODE_ERROR:
            print "* Tofu * Server say: ERROR: %s" % data2
            event.peer.disconnect()
            self.client.flush()
            
          elif code == CODE_ENTER_LEVEL:
            level = soya.loads(data2)
            level.loaded()
            print "* Tofu * %s received with %s." % (level, ", ".join([repr(mobile) for mobile in level.mobiles]))
            
          elif code == CODE_OWN_CONTROL:
            mobile = Unique.getbyuid(int(data2))
            mobile.control_owned()
            
          elif code == CODE_ADD_MOBILE:
            mobile = soya.loads(data2)
            mobile.loaded()
            print "* Tofu * Adding %s in %s..." % (mobile, mobile.level)
            mobile.level.add_mobile(mobile)
            
          elif code == CODE_REMOVE_MOBILE:
            mobile = Unique.getbyuid(int(data2))
            print "* Tofu * Removing %s from %s..." % (mobile, mobile.level)
            mobile.level.remove(mobile)
            
          elif code == CODE_STATE:
            uid   = struct.unpack("!i", data2[:4])[0]
            round = struct.unpack("!q", data2[4:12])[0]
            self.state_queues[uid] = round, data2[12:]
            
          else: raise ValueError("Unknown code '%s'!" % code)
          
        except:
          sys.excepthook(*sys.exc_info())
          print "* Tofu * Error while receiving data:\n%s" % data
          event.peer.disconnect()
          self.client.flush()
          
      event = self.client.service(0)
      
    soya.MainLoop.begin_round(self)


#class SavedInAPath(soya.SavedInAPath):
  

class Player(soya._CObj, soya.SavedInAPath, Multisided):
  DIRNAME = "players"
  _alls = {}
  
  @classmethod
  def get_or_create(Class, filename, password, opt_data = ""):
    try: player = Class.get(filename)
    except: return CREATE_PLAYER(filename, password, opt_data)
    if password != player.password: raise ValueError("Wrong password!")
    return player
    
  def __init__(self, filename, password, opt_data = ""):
    if (".." in filename) or ("/" in filename): raise ValueError("Invalide Player name %s (need a valid filename)!" % filename)
    
    soya.SavedInAPath.__init__(self)
    
    print "* Tofu * Creating new player %s..." % filename
    self._filename   = ""
    self.filename    = filename
    self.password    = password
    self.mobiles     = []
    self.peer        = None
    self._was_loaded = 0
    
  @single_side
  @server_side
  def login(self, peer):
    print "* Tofu * Player %s login." % self.filename
    
    if self._was_loaded:
      for mobile in self.mobiles: mobile.loaded() # Do not consider the mobiles loaded BEFORE the login! E.g. password may be wrong,...
      
    self.peer = peer
    
  @server_side
  def login(self, peer):
    levels = set([mobile.level for mobile in self.mobiles])
    
    for level in levels:
      packet = enet.Packet("""%s%s""" % (CODE_ENTER_LEVEL, level.dumps()), enet.PACKET_FLAG_RELIABLE)
      peer.send(0, packet)
      
    for mobile in self.mobiles:
      mobile.local = 0
      packet = enet.Packet("""%s%s""" % (CODE_OWN_CONTROL, mobile.uid), enet.PACKET_FLAG_RELIABLE)
      peer.send(0, packet)
      
    for level in levels: level.check_active()
    
  @server_side
  @single_side
  def logout(self, save = 1):
    if self.peer:
      print "* Tofu * Player %s logout." % self.filename
      
      self.peer  = None
      if save: self.save()
      
      # Do this AFTER discard => when discard saves the player's mobiles, the mobiles still have their level, and so the level is saved.
      for mobile in self.mobiles:
        if mobile.level: mobile.level.remove_mobile(mobile)
        
      self.filename = "" # Discard the player
      for mobile in self.mobiles: mobile.discard()
      
  @server_side
  @single_side
  def add_mobile(self, mobile):
    if not mobile.level: raise ValueError("You must add the mobile inside a level before!")
    mobile.player_name = self.filename
    mobile.bot         = 0
    self.mobiles.append(mobile)
    
  @server_side
  @single_side
  def remove_mobile(self, mobile):
    self.mobiles.remove(mobile)
    mobile.player_name = ""
    mobile.bot         = 1
    #if not self.mobiles: self.kill(mobile)
    
  @server_side
  @single_side
  def loaded(self):
    soya.SavedInAPath.loaded(self)
    self._was_loaded = 1
    
CREATE_PLAYER = Player


class Unique(Multisided):
  _alls = weakref.WeakValueDictionary()
  
  def gen_uid(self):
    i = 1
    while Unique._alls.has_key(i): i += 1
    self.uid = i
    
  def __init__(self):
    self.gen_uid()
    Unique._alls[self.uid] = self
    
  @staticmethod
  def getbyuid(uid):
    """Unique.getbyuid(uid) -> Unique

This static method returns the object of the given UID (or None if it doesn't exist)."""
    return Unique._alls.get(uid)
  
  @server_side
  @single_side
  def loaded(self):
    self.gen_uid()
    Unique._alls[self.uid] = self
  @client_side
  def loaded(self): Unique._alls[self.uid] = self
  
  def discard(self):
    try: del Unique._alls[self.uid]
    except: pass
    
  @staticmethod
  def undumpsuid(data): return Unique.getbyuid(struct.unpack("!i", data)[0])
  def dumpsuid  (self): return struct.pack("!i", self.uid)
  
  def __repr__(self): return "<%s UID:%s>" % (self.__class__.__name__, self.uid)

  def dumps(self):
    soya._SAVING = self
    s = soya.dumps(self, 1)
    soya._SAVING = None
    return s


class Level(soya.World, Unique):
  DIRNAME = "levels"
  _alls = {}
  
  def __init__(self):
    Unique.__init__(self)
    soya.World.__init__(self)
    self.mobiles = []
    self.active  = 0 # Replace "self.active" by "self in soya.MAIN_LOOP.scenes[0]" ?
    self.round   = 0
    
  def loaded(self):
    self.active = 0
    Unique.loaded(self)
    soya.World.loaded(self)
    
  def discard(self):
    Unique.discard(self)
    for mobile in self.mobiles: mobile.discard()
    self.save()
    
  @server_side
  def get_players(self): return set([Player.get(i.player_name) for i in self.mobiles if i.player_name and Player.get(i.player_name).peer])
  
  @client_side
  def save(self): raise TypeError("Cannot save level on the client-side!")
  
  @server_side
  @client_side
  @single_side
  def add_mobile(self, mobile):
    mobile.level = self
    self.mobiles.append(mobile)
    self.add(mobile)
    self.check_active()
  @server_side
  def add_mobile(self, mobile):
    packet = enet.Packet("%s%s" % (CODE_ADD_MOBILE, mobile.dumps()), enet.PACKET_FLAG_RELIABLE)
    for player in self.get_players(): player.peer.send(0, packet)
    
  @server_side
  @client_side
  @single_side
  def remove_mobile(self, mobile):
    self.mobiles.remove(mobile)
    self.remove(mobile)
    mobile.level = None
    self.check_active()
  @server_side
  def remove_mobile(self, mobile):
    packet = enet.Packet("%s%s" % (CODE_REMOVE_MOBILE, mobile.uid), enet.PACKET_FLAG_RELIABLE)
    for player in self.get_players(): player.peer.send(0, packet)
    
  @server_side
  def check_active(self):
    for mobile in self.mobiles:
      if not mobile.local: self.set_active(1); break
    else: self.set_active(0)
  @client_side
  @single_side
  def check_active(self):
    for mobile in self.mobiles:
      if mobile.local and not mobile.bot: self.set_active(1); break
    else: self.set_active(0)
    
  def set_active(self, active):
    if active != self.active:
      if active: print "* Tofu * Level %s UID:%s activated."  % (self.filename, self.uid)
      else:      print "* Tofu * Level %s UID:%s inactivated." % (self.filename, self.uid)
      if self.active: self.parent.remove(self)
      self.active = active
      if active: soya.MAIN_LOOP.scenes[0].add(self)
      else:      self.discard()
      
  @single_side
  def begin_round(self):
    if self.active: soya.World.begin_round(self)
  @server_side
  def begin_round(self):
    if self.active:
      self.round += 1
      soya.World.begin_round(self)
      
      if (self.round % 10) == 0:
        f = StringIO()
        f.write(self.dumpsuid())
        f.write(struct.pack("!q", self.round))
        for mobile in self.mobiles: mobile.write_network_state(f)
        
        packet = enet.Packet("%s%s" % (CODE_STATE, f.getvalue()))
        for player in self.get_players(): player.peer.send(0, packet)
        
  @client_side
  def begin_round(self):
    if self.active:
      soya.World.begin_round(self)
      round, state = soya.MAIN_LOOP.state_queues.pop(self.uid, (0, None))
      if state:
        self.round = round
        f = StringIO(state)
        for mobile in self.mobiles: mobile.read_network_state(f)
        
        
  def advance_time(self, proportion):
    if self.active:
      soya.World.advance_time(self, proportion)
      
  def end_round(self):
    if self.active:
      soya.World.end_round(self)
      
  def __repr__(self): return "<%s %s UID:%s>" % (self.__class__.__name__, self.filename, self.uid)
  
Level._reffed = Level.get


class Action(Multisided):
  def __init__(self, mobile):
    self.mobile_uid = mobile.uid
    self.round      = mobile.level.round
    
  def dumps(self): return cerealizer.dumps(self)
  
LOAD_ACTION = cerealizer.loads


class Mobile(soya.World, Unique):
  def __init__(self):
    Unique.__init__(self)
    soya.World.__init__(self)
    self.local       = 1
    self.bot         = 1
    self.player_name = ""
    self.level       = None
    
  def compute_action(self): pass
  
  @server_side
  @single_side
  def plan_action(self, action): return self.do_action(action)
  @client_side
  def plan_action(self, action):
    if action:
      packet = enet.Packet("""%s%s""" % (CODE_ACTION, action.dumps()), enet.PACKET_FLAG_RELIABLE)
      soya.MAIN_LOOP.peer.send(0, packet)
      
  @server_side
  @single_side
  def do_action(self, action): pass
  
  def write_network_state(self, f): pass
  def read_network_state (self, f): pass
  
  @single_side
  def begin_round(self):
    self.compute_action()
    soya.World.begin_round(self)
    
  @server_side
  def begin_round(self):
    if self.bot and self.local: self.compute_action()
    else:
      queue = soya.MAIN_LOOP.action_queues.get(self.uid)
      if queue:
        round = queue[0].round
        while queue and (queue[0].round == round): self.do_action(queue.pop(0))
        
    soya.World.begin_round(self)
    
  @client_side
  def begin_round(self):
    if self.local: self.compute_action()
    soya.World.begin_round(self)
    
  @client_side
  @single_side
  def control_owned(self):
    print "* Tofu * Owning control of %s." % self
    self.local = 1
    self.bot   = 0
    self.level.check_active()
    
  def __repr__(self): return "<%s UID:%s>" % (self.__class__.__name__, self.uid)
  
  def loaded(self):
    Unique.loaded(self)
    soya.World.loaded(self)
    if self.level and not self in self.level.mobiles: self.level.add_mobile(self)



class InterpolatedMobile(Mobile):
  def write_network_state(self, f):
    f.write(struct.pack("!" + 19 * "f", *self.matrix))
    
  def read_network_state (self, f):
    matrix = struct.unpack("!" + 19 * "f", f.read(76))
    self.current_state_round = self.next_state_round
    self.next_state_round    = self.level.round
    
    self.current_state = soya.CoordSystState(self)
    #self.current_state = self.next_state
    self.next_state    = soya.CoordSystState(self)
    self.next_state.matrix = matrix
    self.round_since_last_state = 0.0
    #self.matrix = matrix
    #print self.current_state.distance_to(self.next_state)
    
  @client_side
  def advance_time(self, proportion):
    soya.World.advance_time(self, proportion)
    self.round_since_last_state += proportion
    self.interpolate(self.current_state, self.next_state, self.round_since_last_state / (self.next_state_round - self.current_state_round))
    
    
  @client_side
  def loaded(self):
    self.current_state = soya.CoordSystState(self)
    self.next_state    = soya.CoordSystState(self)
    self.round_since_last_state = 0.0
    self.current_state_round    = 0
    self.next_state_round       = 1







