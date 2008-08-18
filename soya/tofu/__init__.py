# TOFU
# Copyright (C) 2005-2007 Jean-Baptiste LAMY
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
from soya.tofu.sides import *

VERSION = "0.1"

CODE_LOGIN_PLAYER  = ">"
CODE_ERROR         = "E"
CODE_OBJ           = "+"
CODE_REMOVE_MOBILE = "-"
CODE_ACTION        = "A"
CODE_STATE         = "S"
CODE_ACK_STATE     = "!"
CODE_MESSAGE       = "M"
CODE_NOOP          = " "

PORT           = 6902
HOST           = "localhost"
GAME           = "game"
SAVED_GAME_DIR = ""
PLAYER_IDS     = []

soya.set_file_format(cerealizer, cerealizer)

def _check_path(d):
  if not os.path.exists(d): os.mkdir(d)
  
def _set_path_current(player_filename, enable):
  _check_path(SAVED_GAME_DIR)
  
  d = os.path.join(SAVED_GAME_DIR, player_filename)
  _check_path(d)
  _check_path(os.path.join(d, "players"))
  _check_path(os.path.join(d, "levels"))
  
  d = os.path.join(SAVED_GAME_DIR, player_filename)
  if enable: soya.path.insert(0, d)
  else:      soya.path.remove(d)

class NetworkError(StandardError): pass

class PacketSocket(object):
  def __init__(self, sock):
    self.sock                     = sock
    self.current_packet           = ""
    self.current_packet_size      = -1
    self.current_packet_size_part = ""
    self.closed                   = 0
    self.current_writing          = ""
    
  def fileno(self):
    try: return self.sock.fileno()
    except: self.closed = 1
  
  def write(self, s):
    if isinstance(s, unicode): raise TypeError
    
    self.current_writing += struct.pack("!I", len(s)) + s
    try: nb = self.sock.send(self.current_writing)
    except: pass
    else: self.current_writing = self.current_writing[nb:]
    if self.current_writing: soya.MAIN_LOOP.socks_writing.append(self)
    
  def _write(self):
    try: nb = self.sock.send(self.current_writing)
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
      if len(self.current_packet_size_part) == 4: self.current_packet_size = struct.unpack("!I", self.current_packet_size_part)[0]
      else: return
      
    while self.current_packet_size > len(self.current_packet):
      try: data = self.sock.recv(min(8192, self.current_packet_size - len(self.current_packet)))
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
  def __init__(self, scene = None):
    soya.MainLoop.__init__(self, scene or soya.World())
    self.levels             = []
    self.local_player_names = []
    
  @side("server", "client")
  def __init__(self, scene = None):
    global HOST, PORT
    s = HOST.split(":")
    if len(s) == 2:
      HOST = s[0]
      PORT = int(s[1])
      
  @side("single", "client")
  def __init__(self, scene = None): self.init_interface()
  def init_interface(self): pass
  
  @side("single")
  def __init__(self, scene = None):
    _set_path_current(GAME, 1)
    self.players = []
    for player_id in PLAYER_IDS:
      player = Player.get_or_create(player_id)
      self.players.append(player)
      player.login(1, 1)
      
  @side("single")
  def sock_closed(self, sock): pass
  
  @side("single")
  def main_loop(self):
    try:
      try: soya.MainLoop.main_loop(self)
      except: sys.excepthook(*sys.exc_info())
    finally:
      for player in self.players: player.logout()
      self.players = []
      _set_path_current(GAME, 0)
      
  @side("server")
  def __init__(self, scene = None):
    _set_path_current("_server", 1)
    self.action_queues      = weakref.WeakKeyDictionary()
    
    self.sock2client        = {}
    self.udp_address2client = {}
    
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
    try:
      try:
        self.running = 1
        late = 0.0
        start = time.time()
        while self.running:
          for task in self.next_round_tasks: task()
          self.next_round_tasks.__imul__(0)
          self.begin_round()
          self.advance_time(1.0)
          self.end_round()
          self.render()
          end = time.time()
          duration = self.round_duration - (end - start) + late
          if duration > 0.0:
            self.wait(duration)
            late = 0.0
            start = end + duration
          else:
            late = duration
            start = end
      except: sys.excepthook(*sys.exc_info())
      
    finally:
      for client in self.sock2client.values():
        for player in client.players[:]:
          player.logout()
          client.remove_player(player)
      self.tcp.shutdown(2)
      self.tcp.close()
      self.udp.close()
      _set_path_current("_server", 0)
      
  @side("server")
  def sock_closed(self, sock):
    client = self.sock2client.pop(sock, None)
    if client:
      self.udp_address2client.pop(client.udp_address, None)
      for player in client.players[:]:
        player.logout()
        client.remove_player(player)
        
    #self.next_round_tasks.append(do_hack)
    import gc
    gc.collect()
    gc.collect()
    gc.collect()
    #print gc.collect()
    #print gc.collect()
    #print gc.collect()
    #print len(gc.get_objects())
    
    if sock in self.socks: self.socks.remove(sock)
    
  @side("server")
  def poll(self):
    while 1:
      try: readable_socks, writeable_socks, dropit = select.select(self.socks, self.socks_writing, [], 0.0)
      except TypeError: # A PacketSocket is closed
        for sock in self.socks:
          if isinstance(sock, PacketSocket) and sock.closed: self.sock_closed(sock)
        continue
      
      for sock in readable_socks:
        if   sock is self.udp:
          data, address = self.udp.recvfrom(65000)
          if not data: continue
          code = data[0]
          
          if   code == CODE_ACK_STATE:
            #import random
            #if random.random() < 0.2: continue
            
            client = self.udp_address2client.get(address)
            if client: client.ack_state(Unique.undumpsuid(data[1:3]), struct.unpack("!Q", data[3:11])[0])
            
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
              client = self.sock2client.get(sock)
              if mobile and client:
                for player in client.players:
                  if mobile in player.mobiles: break
                else: raise ValueError("Player %s cannot send action for mobile %s!" % (player, mobile))
                action = data[11:]
                queue = self.action_queues.get(mobile)
                if queue: queue.append((round, action))
                else:     self.action_queues[mobile] = [(round, action)]
                
            elif code == CODE_LOGIN_PLAYER:
              data2 = data[1:]
              udp_port, data2 = data2.split("\n", 1)
              udp_port = int(udp_port)
              udp_address = (sock.sock.getpeername()[0], udp_port)
              
              #player_ids = cerealizer.loads(data2)
              player_ids = []
              data2 = StringIO(data2)
              nb = int(data2.readline())
              for i in range(nb):
                player_ids.append(LOAD_PLAYER_ID(data2))
                
              if player_ids:
                client = self.sock2client.get(sock)
                if not client:
                  client = Client(sock, udp_address)
                  self.sock2client[sock] = self.udp_address2client[udp_address] = client
                  
                for player_id in player_ids:
                  player = Player.get_or_create(player_id)
                  client.add_player(player)
                  player.login(sock, udp_address)
                  
            else: raise ValueError("Unkown code '%s'!" % code)
            
          except:
            sys.excepthook(*sys.exc_info())
            print "* Tofu * Error while receiving from %s %s code:%s" % (self.sock2client.get(sock), sock.getpeername(), code)
            sock.write("""%s%s: %s""" % (CODE_ERROR, sys.exc_info()[0], sys.exc_info()[1]))
            sock.close()
            
      for sock in writeable_socks: sock._write()
      if not readable_socks: break
      
  @side("server")
  def begin_round(self):
    self.poll()
    soya.MainLoop.begin_round(self)
    
    
  @side("client")
  def __init__(self, scene = None):
    self.tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.tcp.connect((HOST, PORT))
    self.tcp.setblocking(0)
    self.tcp = PacketSocket(self.tcp)
    self.udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    self.udp.connect((HOST, PORT + 1))
    self.socks = [self.tcp, self.udp]
    self.socks_writing = []
    
    self.udp.send(CODE_NOOP)
    self.udp.setblocking(0)
    
    s = ""
    for player_id in PLAYER_IDS:
      s2 = player_id.dumps()
      s += s2

    self.tcp.write("""%s%s\n%s\n%s""" % (CODE_LOGIN_PLAYER, self.udp.getsockname()[1], len(PLAYER_IDS), s))
    
  @side("client")
  def main_loop(self):
    self.nb_round = self.nb_state = self.nb_byte = 0
    
    try:
      try: soya.MainLoop.main_loop(self)
      except: sys.excepthook(*sys.exc_info())
    finally:
      self.tcp.close()
      self.udp.close()
      print "STAT: %s states received in %s rounds (%s states per second)" % (self.nb_state, self.nb_round, self.nb_state / (0.03 * self.nb_round))
      print "STAT: %s bytes sent in %s rounds (%s bytes per second)" % (self.nb_byte, self.nb_round, self.nb_byte / (0.03 * self.nb_round))
      
      for level  in Level ._alls.values(): level.set_active(0)
      for unique in Unique._alls.values(): unique.discard()
      
  @side("client")
  def poll(self):
    while 1:
      readable_socks, writeable_socks, dropit = select.select(self.socks, self.socks_writing, [], 0.0)
      for sock in readable_socks:
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
          
          #print "DATA", len(data), "'%s'" % data[0]
          code = data[0]
          if   code == CODE_MESSAGE:
            obj = Unique.undumpsuid(data[1:3])
            #print "MESSAGE FOR", struct.unpack("!H", data[1:3])[0], data[3:]
            if obj: obj.do_message(data[3:])
            
          elif code == CODE_OBJ:
            #open("/tmp/log", "w").write(data)
            obj = cerealizer.loads(data[1:])
            obj.loaded() # This calls level.add_mobile if needed
            if   isinstance(obj, Mobile): print "* Tofu * %s received in level %s." % (obj, obj.level)
            elif isinstance(obj, Level ): print "* Tofu * %s received with %s." % (obj, ", ".join([repr(mobile) for mobile in obj.mobiles]))
            else:                         print "* Tofu * %s received." % obj
            
          elif code == CODE_REMOVE_MOBILE:
            mobile = Unique.undumpsuid(data[1:3])
            print "* Tofu * %s removed from %s." % (mobile, mobile.level)
            mobile.level.remove_mobile(mobile)
            mobile.discard()
            
          elif code == CODE_ERROR:
            error = data[1:]
            print "* Tofu * Server say: ERROR: %s" % error
            raise NetworkError(error)
          
          else: raise ValueError("Unknown code '%s'!" % code)
          
      for sock in writeable_socks: sock._write()
      if not readable_socks: break
    
  @side("client")
  def begin_round(self):
    
    self.nb_round += 1
    
    self.poll()
    soya.MainLoop.begin_round(self)


def do_hack():
  print "do_hack"
  import gc
  print gc.collect()
  print gc.collect()
  print gc.collect()
  print len(gc.get_objects())
  
  import memtrack
  memtrack.stat_types()
  
  for i in gc.get_objects():
    #if isinstance(i, soya.Terrain): print "!!!", i
    if isinstance(i, soya._CObj): print "!!!", i
    #if isinstance(i, Level): print "!!!", i
    #if isinstance(i, Player): print "!!!", i
  
  print gc.garbage
  #print len(gc.get_referrers(L()))
  #for i in gc.get_referrers(L()): print i
  #import memtrack
  #memtrack.track(L())


class Client(soya._CObj, Multisided):
  """Client

The Client class represents a remote Client on the Tofu server.
This class is used internally and should not be used or modified."""
  def __init__(self, sock, udp_address):
    self.players     = []
    self.sock        = sock
    self.udp_address = udp_address
    
    self.mobiles_states_ack = weakref.WeakKeyDictionary() # Map mobile to the last round their states were acknoledged by the player
    self.levels_states_sent = weakref.WeakKeyDictionary() # Map mobile to the last round their states were sent to the player
    self.states_sent        = {}                          # Map (level, round) to mobile UID the state contains
    
  def __repr__(self):
    return "<Client UDP:%s Players: %s>" % (self.udp_address, self.players)
  
  def add_player(self, player):
    player.client = self
    self.players.append(player)
    
  def remove_player(self, player):
    player.client = None
    if player in self.players: self.players.remove(player)
    
  def ack_state(self, level, round):
    for mobile in self.states_sent.pop((level, round), ()): self.mobiles_states_ack[mobile] = round
    
  def forget_mobile_state(self, mobile):
    self.mobiles_states_ack.pop(mobile, None)
    

class PlayerID(soya._CObj):
  """PlayerID

The PlayerID class is used to identify Players. The default tofu.PlayerID has just a filename
(i.e. the player's name) and a password.

If you need additional attributes, you can extend PlayerID. In this case, you have to set
tofu.LOAD_PLAYER_ID to your PlayerID class loads function."""
  def __init__(self, filename, password):
    """PlayerID(filename, password) -> PlayerID

Creates a new PlayerID with the given filename and password."""
    self.filename = filename
    self.password = password
    
  def __repr__(self): return "<PlayerID %s>" % self.filename

  def dumps(self):
    """PlayerID.dumps() -> string

Saves the PlayerID's data in a string"""
    return "%s\n%s%s\n%s"% (len(self.filename), self.filename, len(self.password), self.password)
  
  @classmethod
  def loads(Class, s):
    """PlayerID.loads(file_object) -> PlayerID

This *class method* loads a PlayerID from a file object.
The PlayerID should have been saved with PlayerID.dumps."""
    nb = int(s.readline())
    filename = s.read(nb)
    nb = int(s.readline())
    password = s.read(nb)
    return PlayerID(filename, password)

LOAD_PLAYER_ID = PlayerID.loads


class Player(soya._CObj, soya.SavedInAPath, Multisided):
  """Player

The Player class is used for representing the Player in server and single modes.
Player is responsible for creating the Player first Mobiles, and putting them in the right Levels.
Player can also stores Player stats, like score, that are managed on server-side.

You need to extend the Player class."""
  DIRNAME = "players"
  _alls = {}
  
  @classmethod
  def get_or_create(Class, player_id):
    """Player.get_or_create(player_id) -> Player

Returns the Player identified by PlayerID.

If the Player already exists, it is returned.
Else, if there is a file for this Player, loads it and returns the Player.
Else, a new Player is created and returned."""
    if not player_id.filename in Class.availables(): return CREATE_PLAYER(player_id)
    player = Class.get(player_id.filename)
    if player_id.password != player.password: raise ValueError("Wrong password!")
    return player
    
  def __init__(self, player_id):
    """Player(player_id) -> Player

Creates a new Player with the given PlayerID.
Player.__init__ is in charge of creating the initial Mobile the Player controls, and putting
these Mobiles in their initial levels."""
    if (".." in player_id.filename) or ("/" in player_id.filename) or (not player_id.filename): raise ValueError("Invalide Player name %s (need a valid filename)!" % player_id.filename)
    
    soya.SavedInAPath.__init__(self)
    
    print "* Tofu * Creating new player %s..." % player_id.filename
    self._filename   = ""
    self.filename    = player_id.filename
    self.password    = player_id.password
    self.mobiles     = []
    self.sock        = None
    self.udp_address = None
    self.client      = None
    
  @side("single", "server")
  def login(self, sock, udp_address):
    """Player.login(sock, udp_address)

Connects the Player to the game."""
    if self.sock: raise ValueError("Player %s is already logged!" % self.filename)
    print "* Tofu * Player %s login." % self.filename
    
    self.sock        = sock
    self.udp_address = udp_address
    
    for mobile in self.mobiles:
      mobile.discard()
      mobile.loaded () # Do not consider the mobiles received BEFORE the login! E.g. password may be wrong,...
      mobile.level._send_mobile(mobile)
      
  @side("single", "server")
  def logout(self, save = 1):
    if self.sock:
      print "* Tofu * Player %s logout." % self.filename
      
      sock = self.sock
      
      self.client             = None
      self.sock               = None
      self.udp_address        = None
      if save: self.save()
      
      soya.MAIN_LOOP.sock_closed(sock)
      
      for mobile in self.mobiles: # Do this AFTER discard => when discard saves the player's mobiles, the mobiles still have their level, and so the level is saved.
        if mobile.level: mobile.level.remove_mobile(mobile)
        
      self.filename = "" # Discard the player
      for mobile in self.mobiles: mobile.discard()
      
  @side("single")
  def logout(self, save = 1):
    """Player.logout(save = 1)

Disconnects the Player from the game.
If SAVE is true, saves the Player."""
    soya.MAIN_LOOP.stop()
    
  @side("single", "server")
  def add_mobile(self, mobile):
    """Player.add_mobile(mobile)

Gives the control of MOBILE to the Player."""
    if not mobile.level: raise ValueError("You must set mobile.level to the level the mobile is, before calling Player.add_mobile!")
    mobile.player_name = self.filename
    mobile.local       = 0
    mobile.bot         = 0
    self.mobiles.append(mobile)
    
  @side("single", "server")
  def remove_mobile(self, mobile):
    """Player.remove_mobile(mobile)

Removes the control of MOBILE from the Player.
Usually called when the Mobile is dead."""
    self.mobiles.remove(mobile)
    mobile.player_name = ""
    mobile.bot         = 1
    if not self.mobiles: self.killed()
    
  @side("single", "server")
  def killed(self, save = 0):
    """Player.killed(save = 0)

Called when the Player no longer controls any Mobile.
If SAVE is true, saves the Player."""
    self.logout(save)
    
CREATE_PLAYER = Player


class Unique(Multisided):
  """Unique

A Unique is an object that has a unique identifier (UID), which can be used to identify the object
on the server and all clients. The UID can be acessed by the uid attribute.

Only the server or the single mode can create Uniques.

Mobiles and Levels are Uniques."""
  _alls = weakref.WeakValueDictionary()
  _next_uid = 1
  @side("single", "server")
  def gen_uid(self):
    """Unique.gen_uid()

Generate a new UID for the Unique object."""
    while Unique._next_uid < 65000:
      if not Unique._alls.has_key(Unique._next_uid): break
      Unique._next_uid += 1
    else:
      Unique._next_uid = 1
      while Unique._next_uid < 65000:
        if not Unique._alls.has_key(Unique._next_uid): break
        Unique._next_uid += 1
      else:
        raise ValueError("All UID are used!")
    self.uid = Unique._next_uid
    Unique._alls[self.uid] = self
    Unique._next_uid += 1
    
  def __init__(self):
    """Unique() -> Unique

Creates a new Unique, with a unique UID."""
    self.gen_uid()
    
  @staticmethod
  def getbyuid(uid):
    """Unique.getbyuid(uid) -> Unique

This static method returns the object of the given UID (or None if it doesn't exist)."""
    return Unique._alls.get(uid)
  
  @side("single", "server")
  def loaded(self): self.gen_uid()
  @side("client")
  def loaded(self):
    if Unique._alls.has_key(self.uid): raise ValueError("Cannot load %s: already have a Unique with the same UID: %s!" % (self, Unique._alls[self.uid]))
    Unique._alls[self.uid] = self

  def discard(self):
    """Unique.discard()

Discards the Unique object, and makes its UID available for any another object."""
    Unique._alls.pop(self.uid, None)
    self.uid = 0
    
  @staticmethod
  def undumpsuid(data):
    """Unique.undumpsuid(string of 2 chars) -> Unique

Loads a Unique from a string of 2 chars (as returned by Unique.dumpsuid)."""
    return Unique.getbyuid(struct.unpack("!H", data)[0])
  @staticmethod
  def dumpsuid_or_none(self):
    if not self: return "\x00\x00"
    return struct.pack("!H", self.uid)
  def dumpsuid  (self):
    """Unique.dumpsuid() -> string of 2 chars

Saves the UID of the unique, in a string of 2 chars."""
    return struct.pack("!H", self.uid)
  
  def __repr__(self): return "<%s UID:%s>" % (self.__class__.__name__, self.uid)
  
  def dumps(self):
    """Unique.dumps() -> string

Saves the Unique object to a string. The default implementation uses Cerealizer."""
    soya._SAVING = self
    s = cerealizer.dumps(self, 1)
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
    
  #def __del__(self):
  #  print "del", self
  
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
  
  @side("server")
  def get_clients(self): return set([player.client for player in self.get_players()])
  
  @side("client")
  def save(self): pass
  
  @side("single", "client")
  def add_mobile(self, mobile, _send_later = 0):
    mobile.level = self
    self.mobiles.append(mobile)
    self.add(mobile)
    mobile.added_into_level(self)
    self.check_active()
  @side("server")
  def add_mobile(self, mobile, _send_later = 0):
    if not mobile.bot:
      for m in self.mobiles:
        #if (m.player_name == mobile.player_name) and (not m is mobile): break
        if m.player_name and (Player.get(m.player_name).client is Player.get(mobile.player_name).client) and (not m is mobile): break
      else:
        msg = CODE_OBJ + self.dumps()
        Player.get(mobile.player_name).sock.write(msg)
        
    mobile.level = self
    self.mobiles.append(mobile)
    self.add(mobile)
    mobile.added_into_level(self)
    self.check_active()
    
    if not _send_later: self._send_mobile(mobile)
    
  @side("single")
  def _send_mobile(self, mobile): pass
  @side("server")
  def _send_mobile(self, mobile):
    msg = CODE_OBJ + mobile.dumps()
    for client in self.get_clients(): client.sock.write(msg)
    
  @side("server")
  def remove_mobile(self, mobile):
    msg = CODE_REMOVE_MOBILE + mobile.dumpsuid()
    for client in self.get_clients(): client.sock.write(msg)
  @side("single", "server", "client")
  def remove_mobile(self, mobile):
    mobile.added_into_level(None)
    self.mobiles.remove(mobile)
    mobile.parent.remove(mobile)
    mobile.level = None
    self.check_active()
  @side("client")
  def remove_mobile(self, mobile):
    if mobile.local and not mobile.bot: mobile.control_lost()
    
  @side("server")
  def check_active(self):
    for mobile in self.mobiles:
      if not mobile.local:
        self.set_active(1)
        break
    else: self.set_active(0)
  @side("single", "client")
  def check_active(self):
    for mobile in self.mobiles:
      if mobile.local and not mobile.bot:
        self.set_active(1)
        break
    else: self.set_active(0)
    
  @side("single", "server", "client")
  def set_active(self, active):
    if active != self.active:
      if active: print "* Tofu * Level %s UID:%s activated."   % (self.filename, self.uid)
      else:      print "* Tofu * Level %s UID:%s inactivated." % (self.filename, self.uid)
      self.active = active
      if active: soya.MAIN_LOOP.scenes[0].add(self)
      else:
        self.parent.remove(self)
        self.discard()
  @side("single", "client")
  def set_active(self, active):
    if not active:
      for mobile in self.mobiles:
        if mobile.local and not mobile.bot: mobile.control_lost()
        
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
      if self.state_counter > MAX_ROUNDS_PER_STATE:
        sync = 1
        self.state_counter = 0
      else:
        sync = 0
      
      mobile2state = {}
      for client in self.get_clients():
        if client.levels_states_sent.get(self, 0) > self.round - MIN_ROUNDS_PER_STATE: continue
        msg  = ""
        mobiles = []
        for mobile in self.mobiles:
          ack  = client.mobiles_states_ack.get(mobile, 0)
          if ((ack < mobile.last_important_round) or
             ((ack < mobile.last_noticeable_round - MAX_ROUNDS_PER_STATE) and sync) ):
            msg = msg + (mobile2state.get(mobile) or mobile2state.setdefault(mobile, mobile.dumpsuid() + mobile.get_network_state()))
            mobiles.append(mobile)
            
        if msg:
          msg = CODE_STATE + self.dumpsuid() + struct.pack("!Q", self.round) + msg
          soya.MAIN_LOOP.udp.sendto(msg, client.udp_address)
          client.states_sent[self, self.round] = mobiles
          client.levels_states_sent[self] = self.round
          
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
          if mobile: mobile.read_network_state(f)
        self.queued_state = ""
      soya.World.begin_round(self)
      
      
  def advance_time(self, proportion):
    if self.active: soya.World.advance_time(self, proportion)
      
  def end_round(self):
    if self.active: soya.World.end_round(self)
    
  def __repr__(self): return "<%s %s UID:%s>" % (self.__class__.__name__, self.filename, self.uid)
  
Level._reffed = Level.get


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

  @side("single", "client")
  def added_into_level(self, level):
    self.init_interface()
    
  @side("server")
  def added_into_level(self, level):
    if self.level:
      for client in self.level.get_clients(): client.forget_mobile_state(self)
    self.last_noticeable_round = 0
    self.last_important_round  = 0
    
  @side("single", "server")
  def kill(self):
    soya.MAIN_LOOP.next_round_tasks.append(self.killed)
    
  def killed(self):
    if self.level:
      self.level.remove_mobile(self)
      player = Player._alls.get(self.player_name, None)
      if player: player.remove_mobile(self)
      
  @side("single", "client")
  def set_current_state_importance(self, importance): pass
  
  @side("server")
  def set_current_state_importance(self, importance):
    if importance >= 1:
      self.last_noticeable_round = self.level.round
      if importance >= 2: self.last_important_round = self.level.round
      
  def generate_actions(self): pass
  
  @side("single", "server")
  def send_action(self, action): return self.do_action(action)
  @side("client")
  def send_action(self, action): soya.MAIN_LOOP.tcp.write(CODE_ACTION + self.dumpsuid() + struct.pack("!Q", self.level.round) + action)
  
  def do_action    (self, action): pass
  def do_physics   (self): pass
  def do_collisions(self): pass
  
  def get_network_state(self): return ""
  def read_network_state(self, f): pass
  
  @side("single")
  def begin_round(self):
    self.generate_actions()
    self.do_physics()
    self.do_collisions()
    soya.World.begin_round(self)
    
  @side("server")
  def begin_round(self):
    if self.bot and self.local: self.generate_actions()
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
    if self.local: self.generate_actions()
    self.do_physics()
    soya.World.begin_round(self)
    
  @side("single", "client")
  def control_owned(self):
    print "* Tofu * Owning control of %s." % self
    self.local = 1
    self.bot   = 0
    self.level.check_active()
    
  @side("single", "client")
  def control_lost(self):
    print "* Tofu * Loosing control of %s." % self
    self.local = 0
    if self.level: self.level.check_active()
    
  def __repr__(self): return "<%s UID:%s>" % (self.__class__.__name__, self.uid)

  def init_interface(self): pass
  
  @side("single", "server", "client")
  def loaded(self):
    Unique.loaded(self)
    soya.World.loaded(self)
    if self.level and not (self in self.level.mobiles): self.level.add_mobile(self, 1)
  @side("client")
  def loaded(self):
    if self.bot: self.local = 0
    
  @side("single", "client")
  def loaded(self):
    if self.player_name:
      for player_id in PLAYER_IDS:
        if self.player_name == player_id.filename:
          self.control_owned()
          break
    self.init_interface()
        
  @side("single")
  def send_message(self, s): self.do_message(s)
  @side("server")
  def send_message(self, s):
    msg = CODE_MESSAGE + self.dumpsuid() + s
    for client in self.level.get_clients(): client.sock.write(msg)
    self.do_message(s)
    
  def do_message(self, s): raise NotImplementedError("You must override this method if you want to send message to this object!")
  
class SpeedInterpolatedMobile(Mobile):
  def __init__(self):
    super(SpeedInterpolatedMobile, self).__init__()
    self.speed            = soya.CoordSystSpeed(None)
    self.last_state       = soya.CoordSystState(self)
    self.next_state       = soya.CoordSystState(self)
    self.round_proportion = 0.0
    
  def added_into(self, parent):
    super(SpeedInterpolatedMobile, self).added_into(parent)
    if self.level:
      self.last_state       = soya.CoordSystState(self)
      self.next_state       = soya.CoordSystState(self)
      
  @side("single", "server")
  def loaded(self):
    super(SpeedInterpolatedMobile, self).loaded()
    self.last_state       = soya.CoordSystState(self)
    self.next_state       = soya.CoordSystState(self)
    self.round_proportion = 0.0
  @side("client")
  def loaded(self):
    super(SpeedInterpolatedMobile, self).loaded()
    self.network_last_state_round = 0
    self.network_next_state_round = 1
    self.network_last_state       = None
    self.round_proportion         = 0.0
    
  def get_network_state(self):
    return super(SpeedInterpolatedMobile, self).get_network_state() + self.next_state._get_network_state() + self.speed._get_network_state()
  
  def read_network_state(self, f):
    super(SpeedInterpolatedMobile, self).read_network_state(f)
    self.network_last_state_round = self.network_next_state_round
    self.network_next_state_round = self.level.round
    #print self.network_next_state_round - self.network_last_state_round
    
    self.network_last_state = soya.CoordSystState(self)
    self.network_last_state._read_network_state(f)
    self.speed._read_network_state(f)
    
  def end_round(self):
    super(SpeedInterpolatedMobile, self).end_round()
    
    self.last_state = self.next_state
    self.next_state = soya.CoordSystState(self)
    self.round_proportion = 0.0
    
  @side("single", "server")
  def do_physics(self):
    super(SpeedInterpolatedMobile, self).do_physics()
    self.next_state.add_speed(self.speed)
    Mobile.do_physics(self)
    
  @side("client")
  def do_physics(self):
    super(SpeedInterpolatedMobile, self).do_physics()
    if self.network_last_state:
      self.next_state.matrix = self.network_last_state.matrix
      self.network_last_state = None
    self.next_state.add_speed(self.speed)
    Mobile.do_physics(self)
    
  def advance_time(self, proportion):
    super(SpeedInterpolatedMobile, self).advance_time(proportion)
    self.round_proportion += proportion
    self.interpolate(self.last_state, self.next_state, self.round_proportion)

        
class AnimatedMobile(Mobile):
  animable = None
  def __init__(self):
    super(AnimatedMobile, self).__init__()
    self.current_animation = ""
    
  def set_animation(self, animation, fade = 0.2):
    if self.current_animation != animation:
      if self.current_animation: (self.animable or self).animate_clear_cycle(self.current_animation, fade)
      (self.animable or self).animate_blend_cycle(animation, 1.0, fade)
      self.current_animation = animation
      
  def get_network_state(self):
    return super(AnimatedMobile, self).get_network_state() + struct.pack("!i", (self.animable or self).model.animations.get(self.current_animation, -1))
  
  def read_network_state(self, f):
    super(AnimatedMobile, self).read_network_state(f)
    
    i = struct.unpack("!i", f.read(4))[0]
    if i != -1:
      for animation, j in (self.animable or self).model.animations.items(): # XXX optimize this !!!
        if j == i:
          self.set_animation(animation)
          break



  

_P = soya.Point()
_V = soya.Vector()
_R = None

# XXX optimize this one (by re-using Point and Vector,...)
class RaypickCollidedMobile(Mobile):
  max_y_speed =  0.5
  gravity     = -0.03
  
  def __init__(self):
    super(RaypickCollidedMobile, self).__init__()
    
    self.solid     = 0
    self.radius    = 0.8
    self.radius_y  = 1.0
    
    self.left   = soya.Vector(self, -1.0,  0.0,  0.0)
    self.up     = soya.Vector(self,  0.0,  1.0,  0.0)
    self.front  = soya.Vector(self,  0.0,  0.0, -1.0)
    self.raypick_dirs = [(self.left, 0), (self.front, 0), (self.up, 0)]
    self.center = soya.Point(self, 0.0, self.radius_y, 0.0)
    
  def do_physics(self):
    super(RaypickCollidedMobile, self).do_physics()
    
    global _R
    
    self.center.__init__(self.next_state, 0.0, self.radius_y, 0.0)
    context = _R = self.level.RaypickContext(self.center, max(self.radius, 0.1 + self.radius_y), _R)
    
    for vec, half_line in self.raypick_dirs:
      r = context.raypick(self.center, vec, self.radius, half_line, 1, _P, _V)
      if r:
        #collision, wall_normal = r
        #hypo = vec.length() * self.radius - self.center.distance_to(collision)
        #wall_normal.__imul__(hypo)
        correction = self.collide_wall(self.center, vec, _P, _V)
        
        self.next_state += correction
        self.center     += correction
        _P.parent = _V.parent = None
        
    self.set_current_state_importance(1)

  def collide_wall(self, center, vec, collision, wall_normal):
    hypo = vec.length() * self.radius - center.distance_to(collision)
    wall_normal.__imul__(hypo)
    return wall_normal
    
  
class RaypickCollidedMobileWithGravity(Mobile):
  max_y_speed = 0.5
  gravity     = -0.03
  
  def __init__(self):
    super(RaypickCollidedMobileWithGravity, self).__init__()
    
    self.solid     = 0
    self.radius    = 0.8
    self.radius_y  = 1.0
    
    self.left   = soya.Vector(self, -1.0,  0.0,  0.0)
    self.down   = soya.Vector(self,  0.0, -1.0,  0.0)
    self.up     = soya.Vector(self,  0.0,  1.0,  0.0)
    self.front  = soya.Vector(self,  0.0,  0.0, -1.0)
    self.raypick_dirs = [(self.left, 0), (self.front, 0), (self.up, 1)]
    self.center = soya.Point(self, 0.0, self.radius_y, 0.0)
    
  def do_physics(self):
    super(RaypickCollidedMobileWithGravity, self).do_physics()
    
    self.center.__init__(self.next_state, 0.0, self.radius_y, 0.0)
    global _R
    context = _R = self.level.RaypickContext(self.center, max(self.radius, 1.5 * self.radius_y), _R)
    
    r = context.raypick(self.center, self.down, 1.5 * self.radius_y, 1, 1, _P, _V)
    if r:
      #ground, ground_normal = r
      _P.convert_to(self.level)
      if (self.next_state.y < _P.y) or self.speed.y <= 0.0:
        self.next_state.y = _P.y
      if self.speed.y < 0.0: self.speed.y = 0.0
      _P.parent = _V.parent = None
      
    else:
      self.speed.y = max(self.speed.y + self.gravity, -self.max_y_speed)
      
    for vec, half_line in self.raypick_dirs:
      r = context.raypick(self.center, vec, self.radius, half_line, 1, _P, _V)
      if r:
        #collision, wall_normal = r
        #hypo = vec.length() * self.radius - self.center.distance_to(collision)
        #wall_normal.__imul__(hypo)
        correction = self.collide_wall(self.center, vec, _P, _V)
        
        self.next_state += correction
        self.center     += correction
        _P.parent = _V.parent = None
        
    self.set_current_state_importance(1)
    
  def collide_wall(self, center, vec, collision, wall_normal):
    hypo = vec.length() * self.radius - center.distance_to(collision)
    wall_normal.__imul__(hypo)
    return wall_normal

