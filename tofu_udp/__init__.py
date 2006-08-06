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

import sys, os.path, time, weakref, struct, socket, select
from cStringIO import StringIO
import cerealizer, soya
from tofu_udp.sides import *

#__all__ = sides.__all__ + ["init", "Notifier", "GameInterface", "MainLoop", "Unique", "SavedInAPath", "Player", "Level", "Action", "State", "Mobile", "LocalController", "RemoteController", "LocalDoer", "RemoteDoer"]

VERSION = "0.1"

CODE_LOGIN_PLAYER  = ">"
CODE_ERROR         = "E"
CODE_RECEIVE       = "R"
CODE_OWN_CONTROL   = "+"
CODE_REMOVE_MOBILE = "-"
CODE_ACTION        = "A"
CODE_STATE         = "S"
CODE_ACK_STATE     = "!"
CODE_MESSAGE       = "M"
CODE_NOOP          = " "

PORT     = 6902
HOST     = ""
LOGIN    = "jiba"
PASSWORD = "test"
OPT_DATA = ""

soya.set_file_format(cerealizer, cerealizer)

class NetworkError(StandardError): pass

class PacketSocket(object):
  def __init__(self, sock):
    self.sock                     = sock
    self.current_packet           = ""
    self.current_packet_size      = -1
    self.current_packet_size_part = ""
    self.closed                   = 0
    
    self.current_writing = ""
    self.writen          = 0
    
  def fileno(self):
    try: return self.sock.fileno()
    except:
      print "bad fileno!"
      self.closed = 1
      return None
  
  def write(self, s):
    self.current_writing += struct.pack("!I", len(s)) + s
    try:
      nb = self.sock.send(self.current_writing)
    except: pass
    else:
      self.current_writing = self.current_writing[nb:]
    if self.current_writing: soya.MAIN_LOOP.socks_writing.append(self)
    
  def _write(self):
    try:
      nb = self.sock.send(self.current_writing)
    except: pass
    else:
      self.current_writing = self.current_writing[nb:]
      if not self.current_writing: soya.MAIN_LOOP.socks_writing.remove(self)
      
  def read(self):
    if (len(self.current_packet_size_part) == 4) and (self.current_packet_size == -1): oepjf
    nothing_read = 1
    if self.current_packet_size == -1:
      try: data = self.sock.recv(4 - len(self.current_packet_size_part))
      except: return
      if len(data) == 0:
        print "* Tofu * Socket from %s:%s seems closed." % self.getpeername()
        self.closed = 1
        return
      nothing_read = 0
      self.current_packet_size_part += data
      if len(self.current_packet_size_part) == 4:
        self.current_packet_size = struct.unpack("!I", self.current_packet_size_part)[0]
      else: return
      
    while self.current_packet_size > len(self.current_packet):
      try:
        data = self.sock.recv(min(8192, self.current_packet_size - len(self.current_packet)))
      except: return
      nothing_read = 0
      if not data:
        if nothing_read:
          print "* Tofu * Socket from %s:%s seems closed." % self.getpeername()
          self.closed = 1
        return
      self.current_packet += data
      
    packet = self.current_packet
    self.current_packet_size      = -1
    self.current_packet_size_part = ""
    self.current_packet           = ""
    return packet
  
  def getpeername(self):
    try: return self.sock.getpeername()
    except: return ("???", 0)
    
  def close(self):
    self.closed = 1
    self.sock.shutdown(2)
    self.sock.close()
    
    
class MainLoop(soya.MainLoop, Multisided):
  @side("single", "server", "client")
  def __init__(self, scene):
    soya.MainLoop.__init__(self, scene or soya.World())
    self.levels = []
    
    
  @side("single")
  def __init__(self, scene):
    player = Player.get_or_create(LOGIN, PASSWORD, OPT_DATA)
    player.login(1, 1)
    
    
  @side("server")
  def __init__(self, scene):
    self.action_queues      = weakref.WeakKeyDictionary()
    self.sock2player        = {}
    self.udp_address2player = {}
    self.tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self.tcp.bind((HOST, PORT))
    self.tcp.listen(3)
    self.udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    self.udp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self.udp.bind((HOST, PORT + 1))
    self.socks = [self.tcp, self.udp]
    self.socks_writing = []
    
  @side("server")
  def main_loop(self):
    print "* Tofu * Server ready."
    try: soya.MainLoop.main_loop(self)
    finally:
      for player in self.sock2player.values(): player.logout()
      self.tcp.shutdown(2)
      self.tcp.close()
      self.udp.close()
  @side("server")
  def sock_closed(self, sock):
    if self.sock2player.get(sock):
      player = self.sock2player[sock]
      del self.udp_address2player[player.udp_address]
      del self.sock2player[sock]
      player.logout()
    self.socks.remove(sock)
    
  @side("server")
  def wait(self, duration):
    if 1:
      try: readable_socks, writeable_socks, dropit = select.select(self.socks, self.socks_writing, [], duration)
      except TypeError: # A PacketSocket is closed
        for sock in self.socks:
          if isinstance(sock, PacketSocket) and sock.closed: self.sock_closed(sock)
        return
      
      for sock in readable_socks:
        if   sock is self.udp:
          data, address = self.udp.recvfrom(65000)
          if not data: continue
          code = data[0]
          
          if   code == CODE_ACK_STATE:
            #import random
            #if random.random() < 0.2: continue
            
            player = self.udp_address2player.get(address)
            if player: player.ack_state(Unique.undumpsuid(data[1:3]), struct.unpack("!Q", data[3:11])[0])
            
          elif code == CODE_NOOP: pass
          
        elif sock is self.tcp:
          sock, address = sock.accept()
          sock.setblocking(0)
          sock = PacketSocket(sock)
          self.socks.append(sock)
          print "* Tofu * Connection from %s:%s." % address
          
        else:
          data = sock.read()
          if not data:
            if sock.closed: self.sock_closed(sock)
            continue
            
          code = data[0]
          try:
            if   code == CODE_ACTION:
              mobile = Unique.undumpsuid(data[1:3])
              round  = struct.unpack("!Q", data[3:11])[0]
              player = self.sock2player.get(sock)
              if mobile and player:
                if not mobile in player.mobiles: raise ValueError("Player %s cannot send action for mobile %s!" % (player, mobile))
                action = data[11:]
                queue = self.action_queues.get(mobile)
                if queue: queue.append((round, action))
                else:     self.action_queues[mobile] = [(round, action)]
                
            elif code == CODE_LOGIN_PLAYER:
              if self.sock2player.get(sock): raise ValueError("Cannot log twice!")
              data2 = data[1:]
              udp_port, nb, data2 = data2.split("\n", 2)
              udp_port = int(udp_port)
              udp_address = (sock.sock.getpeername()[0], udp_port)
              nb = int(nb)
              login, data2 = data2[:nb], data2[nb:]
              nb, data2 = data2.split("\n", 1)
              nb = int(nb)
              password, data2 = data2[:nb], data2[nb:]
              player = Player.get_or_create(login, password, data2)
              if player.sock: raise ValueError("Player %s already logged!" % login)
              player.login(sock, udp_address)
              self.sock2player[sock] = self.udp_address2player[udp_address] = player
              
            else: raise ValueError("Unkown code '%s'!" % code)
            
          except:
            sys.excepthook(*sys.exc_info())
            print "* Tofu * Error while receiving from %s %s code:%s" % (self.sock2player.get(sock), sock.getpeername(), code)
            sock.write("""%s%s: %s""" % (CODE_ERROR, sys.exc_info()[0], sys.exc_info()[1]))
            sock.close()
            
      for sock in writeable_socks:
        sock._write()
      
  @side("server")
  def begin_round(self):
    soya.MainLoop.begin_round(self)
    
    
  @side("client")
  def __init__(self, scene):
    #self.state_queues = {}
    self.tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.tcp.connect((HOST, PORT))
    self.tcp.setblocking(0)
    self.tcp = PacketSocket(self.tcp)
    self.udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    self.udp.connect((HOST, PORT + 1))
    self.socks = [self.tcp, self.udp]
    
    self.udp.send(CODE_NOOP)
    self.udp.setblocking(0)
    
    self.tcp.write("""%s%s\n%s\n%s%s\n%s%s""" % (
      CODE_LOGIN_PLAYER,
      self.udp.getsockname()[1],
      len(LOGIN   ), LOGIN, len(PASSWORD), PASSWORD, OPT_DATA,))
    
  @side("client")
  def main_loop(self):
    
    self.nb_round = self.nb_state = self.nb_byte = 0
    
    try: soya.MainLoop.main_loop(self)
    finally:
      self.tcp.close()
      self.udp.close()
      print "STAT: %s states received in %s rounds (%s states per second)" % (self.nb_state, self.nb_round, self.nb_state / (0.03 * self.nb_round))
      print "STAT: %s bytes sent in %s rounds (%s bytes per second)" % (self.nb_byte, self.nb_round, self.nb_byte / (0.03 * self.nb_round))
      
      for unique in Unique._alls.values(): unique.discard()
      
  @side("client")
  def wait(self, duration):
    if 1:
      socks, dropit, dropit = select.select(self.socks, [], [], duration)
      if not socks: return
      
      for sock in socks:
        if   sock is self.udp:
          data = self.udp.recv(65000)
          code = data[0]
          
          self.nb_byte  += len(data) + 8 # 8 is for UDP header
          
          
          if   code == CODE_STATE:
            
            self.nb_state += 1
            
            #import random
            #if random.random() < 0.2: continue
            
            self.udp.send(CODE_ACK_STATE + data[1:13])
            
            level = Unique.undumpsuid(data[1:3])
            round = struct.unpack("!Q", data[3:11])[0]
            
            if level and level.queued_state_round < round:
              level.queued_state       = data[11:]
              level.queued_state_round = round
              
          else: raise NetworkError("Unknown code '%s'!" % code)
          
        elif sock is self.tcp:
          data = sock.read()
          if not data:
            if sock.closed: raise NetworkError("Connexion to server closed!")
            continue
          
          self.nb_byte  += 4 + len(data) + 8
          
          
          print "DATA", len(data), "'%s'" % data[0]
          code = data[0]
          if   code == CODE_MESSAGE:
            obj = Unique.undumpsuid(data[1:3])
            obj.message_received(data[3:])
            
          elif code == CODE_RECEIVE:
            obj = soya.loads(data[1:])
            obj.loaded() # This calls level.add_mobile if needed
            if   isinstance(obj, Mobile): print "* Tofu * %s received in level %s." % (obj, obj.level)
            elif isinstance(obj, Level ): print "* Tofu * %s received with %s." % (level, ", ".join([repr(mobile) for mobile in level.mobiles]))
            else:                         print "* Tofu * %s received." % obj
            
          elif code == CODE_REMOVE_MOBILE:
            mobile = Unique.undumpsuid(data[1:3])
            print "* Tofu * %s removed from %s." % (mobile, mobile.level)
            mobile.level.remove_mobile(mobile)
            mobile.discard()
            
          elif code == CODE_OWN_CONTROL:
            mobile = Unique.undumpsuid(data[1:3])
            mobile.control_owned()
            
          elif code == CODE_ERROR:
            error = data[1:]
            print "* Tofu * Server say: ERROR: %s" % error
            raise NetworkError(error)
          
          else: raise ValueError("Unknown code '%s'!" % code)
  
    
  @side("client")
  def begin_round(self):
    soya.MainLoop.begin_round(self)

    
    self.nb_round += 1


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
    self.sock        = None
    self.udp_address = None
    
  @side("server")
  def ack_state(self, level, round):
    for mobile in self.states_sent.pop((level, round), ()): self.mobiles_states_ack[mobile] = round
    
  @side("single", "server")
  def login(self, sock, udp_address):
    print "* Tofu * Player %s login." % self.filename
    
    if self.mobiles and (self.mobiles[0].parent is None):
      for mobile in self.mobiles: mobile.loaded() # Do not consider the mobiles loaded BEFORE the login! E.g. password may be wrong,...
      
    self.sock = sock
    self.udp_address = udp_address
    
  @side("single")
  def login(self, sock, udp_port):
    for mobile in self.mobiles:
      mobile.control_owned()
      
  @side("server")
  def login(self, sock, udp_port):
    self.mobiles_states_ack = weakref.WeakKeyDictionary() # Map mobile to the last round their states were acknoledged by the player
    self.levels_states_sent = weakref.WeakKeyDictionary() # Map mobile to the last round their states were sent to the player
    self.states_sent        = {}                          # Map (level, round) to mobile UID the state contains
    
    levels = set([mobile.level for mobile in self.mobiles])
    
    for level in levels:
      self.sock.write(CODE_ENTER_LEVEL + level.dumps())
      
    for mobile in self.mobiles:
      mobile.local = 0
      self.sock.write(CODE_OWN_CONTROL + mobile.dumpsuid())
      
    for level in levels: level.check_active()
    
  @side("single", "server")
  def logout(self, save = 1):
    if self.sock:
      print "* Tofu * Player %s logout." % self.filename
      
      self.sock        = None
      self.udp_address = None
      self.mobiles_states_ack = None
      self.levels_states_sent = None
      self.states_sent        = None
      if save: self.save()
      
      for mobile in self.mobiles: # Do this AFTER discard => when discard saves the player's mobiles, the mobiles still have their level, and so the level is saved.
        if mobile.level: mobile.level.remove_mobile(mobile)
        
      self.filename = "" # Discard the player
      for mobile in self.mobiles: mobile.discard()
      
  @side("single", "server")
  def add_mobile(self, mobile):
    if not mobile.level: raise ValueError("You must add the mobile inside a level before!")
    mobile.player_name = self.filename
    mobile.bot         = 0
    self.mobiles.append(mobile)
    
  @side("single", "server")
  def remove_mobile(self, mobile):
    self.mobiles.remove(mobile)
    mobile.player_name = ""
    mobile.bot         = 1
    #if not self.mobiles: self.kill(mobile)
    
CREATE_PLAYER = Player


class Unique(Multisided):
  _alls = weakref.WeakValueDictionary()
  
  def gen_uid(self):
    i = 1
    while Unique._alls.has_key(i): i += 1
    self.uid = i
    Unique._alls[self.uid] = self
    
  def __init__(self):
    self.gen_uid()
    
  @staticmethod
  def getbyuid(uid):
    """Unique.getbyuid(uid) -> Unique

This static method returns the object of the given UID (or None if it doesn't exist)."""
    return Unique._alls.get(uid)
  
  @side("single", "server")
  def loaded(self):
    self.gen_uid()
  @side("client")
  def loaded(self):
    if Unique._alls.has_key(self.uid): raise ValueError("Cannot load %s: already have a Unique with the same UID: %s!" % (self, Unique._alls[self.uid]))
    Unique._alls[self.uid] = self
    
  def discard(self):
    try: del Unique._alls[self.uid]
    except: pass
    
  @staticmethod
  def undumpsuid(data): return Unique.getbyuid(struct.unpack("!H", data)[0])
  def dumpsuid  (self): return struct.pack("!H", self.uid)
  
  def __repr__(self): return "<%s UID:%s>" % (self.__class__.__name__, self.uid)
  
  def dumps(self):
    soya._SAVING = self
    s = soya.dumps(self, 1)
    soya._SAVING = None
    return s


MIN_ROUNDS_PER_STATE = 4
MAX_ROUNDS_PER_STATE = 66

class Level(soya.World, Unique):
  DIRNAME = "levels"
  _alls = {}
  
  def __init__(self):
    Unique.__init__(self)
    soya.World.__init__(self)
    self.mobiles       = []
    self.active        = 0 # Replace "self.active" by "self in soya.MAIN_LOOP.scenes[0]" ?
    self.round         = 0
    self.state_counter = 0
    
  @side("single", "server", "client")
  def loaded(self):
    self.active = 0
    Unique.loaded(self)
    soya.World.loaded(self)
    
  @side("client")
  def loaded(self):
    self.queued_state       = ""
    self.queued_state_round = -1
    
  def discard(self):
    Unique.discard(self)
    for mobile in self.mobiles: mobile.discard()
    self.save()
    self._alls.pop(self.filename, None)
    
  @side("server")
  def get_players(self): return set([Player.get(i.player_name) for i in self.mobiles if i.player_name and Player.get(i.player_name).sock])
  
  @side("client")
  def save(self): pass
  
  @side("single", "server", "client")
  def add_mobile(self, mobile):
    mobile.level = self
    self.mobiles.append(mobile)
    self.add(mobile)
    self.check_active()
  @side("server")
  def add_mobile(self, mobile):
    msg = CODE_ADD_MOBILE + mobile.dumps()
    for player in self.get_players(): player.sock.write(msg)
    
  @side("single", "server", "client")
  def remove_mobile(self, mobile):
    self.mobiles.remove(mobile)
    self.remove(mobile)
    mobile.level = None
    self.check_active()
  @side("server")
  def remove_mobile(self, mobile):
    msg = CODE_REMOVE_MOBILE + mobile.dumpsuid()
    for player in self.get_players(): player.sock.write(msg)
    
  @side("server")
  def check_active(self):
    for mobile in self.mobiles:
      if not mobile.local: self.set_active(1); break
    else: self.set_active(0)
  @side("single", "client")
  def check_active(self):
    for mobile in self.mobiles:
      if mobile.local and not mobile.bot: self.set_active(1); break
    else: self.set_active(0)
    
  def set_active(self, active):
    if active != self.active:
      if active: print "* Tofu * Level %s UID:%s activated."  % (self.filename, self.uid)
      else:      print "* Tofu * Level %s UID:%s inactivated." % (self.filename, self.uid)
      self.active = active
      if active: soya.MAIN_LOOP.scenes[0].add(self)
      else:      self.parent.remove(self); self.discard()
      
  @side("single")
  def begin_round(self):
    if self.active:
      self.round += 1
      soya.World.begin_round(self)
    
  @side("server")
  def begin_round(self):
    if self.active:
      self.round += 1
      soya.World.begin_round(self)
      
      self.state_counter += 1
      if self.state_counter > MAX_ROUNDS_PER_STATE: sync = 1; self.state_counter = 0
      else:                                         sync = 0
      
      mobile2state = {}
      for player in self.get_players():
        if player.levels_states_sent.get(self, 0) > self.round - MIN_ROUNDS_PER_STATE: continue
        msg  = ""
        mobiles = []
        for mobile in self.mobiles:
          ack  = player.mobiles_states_ack.get(mobile, 0)
          if ((ack < mobile.last_important_round) or
             ((ack < mobile.last_noticeable_round - MAX_ROUNDS_PER_STATE) and sync) ):
            msg = msg + (mobile2state.get(mobile) or mobile2state.setdefault(mobile, mobile.dumpsuid() + mobile.get_network_state()))
            mobiles.append(mobile)
            
        if msg:
          msg = CODE_STATE + self.dumpsuid() + struct.pack("!Q", self.round) + msg
          soya.MAIN_LOOP.udp.sendto(msg, player.udp_address)
          player.states_sent[self, self.round] = mobiles
          player.levels_states_sent[self] = self.round
          
  @side("client")
  def begin_round(self):
    if self.active:
      if self.queued_state:
        self.round = self.queued_state_round
        f = StringIO(self.queued_state)
        while 1:
          uid = f.read(2)
          if not uid: break # End of the state
          mobile = Unique.undumpsuid(uid)
          mobile.read_network_state(f)
        self.queued_state = ""
      soya.World.begin_round(self)
      
      
  def advance_time(self, proportion):
    if self.active: soya.World.advance_time(self, proportion)
      
  def end_round(self):
    if self.active: soya.World.end_round(self)
    
  def __repr__(self): return "<%s %s UID:%s>" % (self.__class__.__name__, self.filename, self.uid)
  
Level._reffed = Level.get


class Action(Multisided):
  def __init__(self, mobile, round = None):
    self.mobile = mobile
    if round is None: self.round = mobile.level.round
    else:             self.round = round
    
  def dumps(self): raise NotImplementedError("You must override this method!")
  

class Mobile(soya.World, Unique):
  def __init__(self):
    Unique.__init__(self)
    soya.World.__init__(self)
    self.local       = 1
    self.bot         = 1
    self.player_name = ""
    self.level       = None
    self.last_noticeable_round = 0
    self.last_important_round  = 0
    
  @side("server")
  def added_into(self, world):
    soya.World.added_into(self, world)
    self.last_noticeable_round = 0
    self.last_important_round  = 0
    
  @side("single", "client")
  def set_current_state_importance(self, importance): pass
  
  @side("server")
  def set_current_state_importance(self, importance):
    if importance >= 1:
      self.last_noticeable_round = self.level.round
      if importance >= 2: self.last_important_round = self.level.round
      
  def compute_action(self): pass
  
  @side("single", "server")
  def send_action(self, action): return self.do_action(action)
  @side("client")
  def send_action(self, action): soya.MAIN_LOOP.tcp.write(CODE_ACTION + self.dumpsuid() + struct.pack("!Q", action.round) + action)
  
  def do_action    (self, action): pass
  def do_physics   (self): pass
  def do_collisions(self): pass
  
  def get_network_state(self): pass
  def read_network_state(self, f): pass
  
  @side("single")
  def begin_round(self):
    self.compute_action()
    self.do_physics()
    self.do_collisions()
    soya.World.begin_round(self)
    
  @side("server")
  def begin_round(self):
    if self.bot and self.local: self.compute_action()
    else:
      queue = soya.MAIN_LOOP.action_queues.get(self)
      if queue:
        round = queue[0][0]
        while queue and (queue[0][0] == round): self.do_action(queue.pop(0)[1])
        
    self.do_physics()
    self.do_collisions()
    soya.World.begin_round(self)
    
  @side("client")
  def begin_round(self):
    if self.local: self.compute_action()
    self.do_physics()
    soya.World.begin_round(self)
    
  @side("single", "client")
  def control_owned(self):
    print "* Tofu * Owning control of %s." % self
    self.local = 1
    self.bot   = 0
    self.level.check_active()
    
  def __repr__(self): return "<%s UID:%s>" % (self.__class__.__name__, self.uid)
  
  @side("single", "server", "client")
  def loaded(self):
    Unique.loaded(self)
    soya.World.loaded(self)
    if self.level and not self in self.level.mobiles: self.level.add_mobile(self)
    
  @side("client")
  def loaded(self):
    if self.bot: self.local = 0
    
  @side("single")
  def send_message(self, s): self.do_message(s)
  @side("server")
  def send_message(self, s):
    msg = CODE_MESSAGE + self.dumpsuid() + s
    for player in self.level.players(): player.sock.write(msg)
    self.do_message(s)
    
  def do_message(self, s): raise NotImplementedError("You must override this method if you want to send message to this object!") 
  

class InterpolatedMobile(Mobile):
  def __init__(self):
    Mobile.__init__(self)
    self.speed            = soya.CoordSystSpeed(self)
    self.last_state       = soya.CoordSystState(self)
    self.next_state       = soya.CoordSystState(self)
    self.round_proportion = 0.0
    
  @side("client")
  def loaded(self):
    Mobile.loaded(self)
    self.network_last_state_round = 0
    self.network_next_state_round = 1
    self.network_last_state       = soya.CoordSystState(self)
    
  def get_network_state(self):
    return self.next_state._get_network_state() + self.speed._get_network_state()
  
  def read_network_state(self, f):
    self.network_last_state_round = self.network_next_state_round
    self.network_next_state_round = self.level.round
    print self.network_next_state_round - self.network_last_state_round
    
    self.network_last_state = soya.CoordSystState(self)
    self.network_last_state._read_network_state(f)
    self.speed._read_network_state(f)
    
  @side("single", "server")
  def begin_round(self):
    self.last_state = self.next_state
    self.next_state = soya.CoordSystState(self)
    self.next_state.add_speed(self.speed)
    self.round_proportion = 0.0
    Mobile.begin_round(self)
    
  @side("client")
  def begin_round(self):
    self.last_state = self.next_state
    if self.network_last_state:
      self.next_state = self.network_last_state
      self.network_last_state = None
    else:
      self.next_state = soya.CoordSystState(self)
    self.next_state.add_speed(self.speed)
    self.round_proportion = 0.0
    Mobile.begin_round(self)
    
  def advance_time(self, proportion):
    soya.World.advance_time(self, proportion)
    self.round_proportion += proportion
    self.interpolate(self.last_state, self.next_state, self.round_proportion)
    

class AnimatedMobile(Mobile):
  def __init__(self):
    super(AnimatedMobile, self).__init__()
    self.current_animation = ""
    
  def set_animation(self, animation):
    if self.current_animation != animation:
      if self.current_animation: self.animate_clear_cycle(self.current_animation)
      self.animate_blend_cycle(animation)
      self.current_animation = animation
      
  def get_network_state(self):
    return struct.pack("!i", self.model.animations.get(self.current_animation, -1))
  
  def read_network_state(self, f):
    i = struct.unpack("!i", f.read(4))[0]
    if i != -1:
      for animation, j in self.model.animations.items(): # XXX optimize this !!!
        if j == i:
          self.set_animation(animation)
          break
        
        
class InterpolatedAnimatedMobile(InterpolatedMobile, AnimatedMobile):
  def __init__(self):
    AnimatedMobile.__init__(self)
    
  def get_network_state(self):
    return InterpolatedMobile.get_network_state(self) + AnimatedMobile.get_network_state(self)
  
  def read_network_state(self, f):
    InterpolatedMobile.read_network_state(self, f)
    AnimatedMobile    .read_network_state(self, f)
      
