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

"""tofu.client

This module implements a Tofu client.

To lauch a server, create a GameInterface instance, import this module,
and then call serve_forever().
"""

from twisted.internet.protocol import DatagramProtocol, Protocol, Factory, ClientFactory
from twisted.protocols.basic import LineReceiver, NetstringReceiver
from twisted.python.failure import Failure
#from twisted.internet import reactor
import twisted.internet.selectreactor
#reactor = twisted.internet.selectreactor.SelectReactor()

import sys, sets, struct

import tofu

class ClientServerError(StandardError): pass


class UDP(DatagramProtocol):
  def startProtocol(self):
    a = "hello"
    self.transport.write(a, ("127.0.0.1", 9999))
    
  def datagramReceived(self, data, (host, port)):
    print "UDP received %r from %s:%d" % (data, host, port)
    
PLANNED_ARRIVAL_UIDS = set()

WAITERS = {}
class Waiter(object):
  def __init__(self, callback = lambda *args: None):
    self.callback         = callback
    self.uniques          = sets.Set([])
    self.nb_waited_unique = 0
    
  def wait_for(self, uid, ask_for_it = 1):
    if tofu.Unique.hasuid(uid): # Already available
      self.uniques.add(tofu.Unique.getbyuid(uid))
    else:
      #if ask_for_it:
      #  if not uid in tofu.NOTIFIER.uids_arrival_planned:
      #    tofu.NOTIFIER.ask_unique(uid)
      
      self.nb_waited_unique += 1
      waiters = WAITERS.get(uid)
      if not waiters: waiters = WAITERS[uid] = []
      waiters.append(self)
      
  def arrived(self, unique):
    self.uniques.add(unique)
    self.nb_waited_unique -= 1
    if self.nb_waited_unique == 0: self.callback(*self.uniques)
    
  def start(self):
    if self.nb_waited_unique == 0: self.callback(*self.uniques)
    
    
MAX_LENGTH = 99999

class Notifier(NetstringReceiver, tofu.Notifier):
  def __init__(self):
    tofu.Notifier.__init__(self)
    
    self.errors = []
    self.MAX_LENGTH           = MAX_LENGTH
    self.uids_arrival_planned = set()
    
  def connectionMade(self):
    self.sendString(tofu.CODE_CHECK_VERSION + tofu.VERSION)
    tofu.GAME_INTERFACE.ready(self)
    
  def login_player(self, filename, password, client_side_data = ""):
    self.sendString("%s%s\n%s\n%s" % (tofu.CODE_LOGIN_PLAYER, filename, password, client_side_data))
    
  def logout_player(self):
    self.sendString(tofu.CODE_LOGOUT_PLAYER)
    
  def stringReceived(self, data):
    #print "TCP receive:", repr(data)
    #print len(data)
    
    code = data[0]
    #print "* Tofu * receiving code %s..." % code
    if   code == tofu.CODE_DATA_STATE:
      state = tofu.YourState.undump(data[5:])
      uid   = struct.unpack("!i", data[1:5])[0]
      if tofu.Unique.hasuid(uid): tofu.Unique.getbyuid(uid).doer.push(state)
      elif state.is_crucial():
        pass
      #  XXX
      #  waiter = Waiter(lambda mobile: mobile.doer.push(state))
      #  waiter.wait_for(uid)
      #  waiter.start()
      
    elif code == tofu.CODE_OWN_CONTROL:
      uid = struct.unpack("!i", data[1:])[0]
      print "* Tofu * Owning mobile %s..." % uid
      #def own_control(mobile):
      #  print "own_control", mobile.level
      #  tofu.IDLER.next_round_tasks.append(mobile.control_owned)
      #waiter = Waiter(own_control)
      
      waiter = Waiter(lambda mobile: mobile.control_owned())
      
      waiter.wait_for(uid, 0)
      waiter.start()
      
    elif code == tofu.CODE_REMOVE_MOBILE:
      uid = struct.unpack("!i", data[1:])[0]
      print "* Tofu * Removing mobile %s..." % uid
      def remove_mobile(mobile):
        mobile.level.remove_mobile(mobile)
        mobile.discard()
      #def remove_mobile(mobile):
      #  def remove_mobile2():
      #    print "* Tofu * Mobile %s removed !" % mobile.uid
      #    mobile.level.remove_mobile(mobile)
      #    mobile.discard()
      #  tofu.IDLER.next_round_tasks.append(remove_mobile2)
      waiter = Waiter(remove_mobile)
      waiter.wait_for(uid, 0)
      waiter.start()
      
    elif code == tofu.CODE_ADD_MOBILE:
      mobile_uid = struct.unpack("!i", data[1:5])[0]
      level_uid  = struct.unpack("!i", data[5:9])[0]
      print "* Tofu * Adding mobile %s in level %s..." % (mobile_uid, level_uid)
      def add_mobile(*args):
        mobile = tofu.Unique.getbyuid(mobile_uid)
        level  = tofu.Unique.getbyuid(level_uid )
        if not mobile in level.mobiles: mobile.level.add_mobile(mobile)
      waiter = Waiter(add_mobile)
      waiter.wait_for(mobile_uid)
      waiter.wait_for(level_uid)
      waiter.start()
      
    elif code == tofu.CODE_DATA_UNIQUE:
      print "* Tofu * Receiving unique..."
      unique = tofu.Unique.undump(data[1:])
      unique.received()
      assert (not hasattr(unique, "level")) or (not unique.level) or (unique.level in unique.level._alls2.values()), "Level sent with non-level unique !"
      self.arrived(unique)
      
    elif code == tofu.CODE_ENTER_LEVEL:
      uid = struct.unpack("!i", data[1:])[0]
      print "* Tofu * Entering level %s..." % uid
      #self.uids_arrival_planned.add(uid) # The server will send it
      # Previous level is outdated => drop it
      if tofu.Unique.hasuid(uid): tofu.Unique.getbyuid(uid).set_active(0)
      waiter = Waiter(lambda *uniques: None)
      waiter.wait_for(uid)
      waiter.start()
      
    elif code == tofu.CODE_ERROR:
      print "* Tofu * Server error: %s" % data[1:]
      #self.errors.append(data[1:])
      raise ClientServerError(data[1:])
      
  def arrived(self, unique):
    print "* Tofu * Received unique %s %s." % (unique.uid, unique)
    
    waiters = WAITERS.get(unique.uid)
    if waiters:
      for waiter in waiters: waiter.arrived(unique)
      del WAITERS[unique.uid]
    if hasattr(unique, "mobiles"):
      for mobile in unique.mobiles: self.arrived(mobile)
      
    self.uids_arrival_planned.discard(unique.uid)
      
  def ask_unique(self, uid):
    print "* Tofu * Ask for UID %s..." % uid
    self.uids_arrival_planned.add(uid)
    self.sendString(tofu.CODE_ASK_UNIQUE + struct.pack("!i", uid))
    
  def notify_action(self, mobile, action):
    self.sendString(tofu.CODE_DATA_ACTION + "%s%s" % (mobile.dumpuid(), action.dump()))
    
  def notify_add_mobile   (self, mobile): pass
  def notify_remove_mobile(self, mobile): pass
  
  def check_level_activity(self, level):
    for mobile in level.mobiles:
      if not mobile.controller.remote:
        level.set_active(1)
        return
      
    # No local user for this level => we can inactive it
    level.set_active(0)
    
  def notify_discard(self, unique):
    # The client NEVER saves data
    pass
  
  
  
class TCPFactory(ClientFactory):
  protocol = Notifier
  
  def clientConnectionFailed(self, connector, reason):
    m = reason.getErrorMessage()
    print "* Tofu * Connection failed:", m
    tofu.GAME_INTERFACE.network_error(m)
    
  def clientConnectionLost(self, connector, reason):
    m = reason.getErrorMessage()
    print "* Tofu * Connection lost:", m
    tofu.GAME_INTERFACE.network_error(m)
    
      
def serve_forever(host = "localhost", port = 6900, *args, **kargs):
  """serve_forever(host = "localhost", port = 6900, *ARGS, **KARGS)

Starts a game client, and connect to HOST on port PORT.
ARGS and KARGS are passed to GameInterface.__init__()."""
  #reactor.listenUDP(0, UDP())
  #twisted.internet.selectreactor.install()
  reactor = twisted.internet.reactor
  
  tofu.YourGameInterface(*args, **kargs)
  
  factory = TCPFactory()
  twisted.internet.reactor.connectTCP(host, port, factory)

  try:
    return tofu.IDLER.idle()
  finally:
    tofu.NOTIFIER.transport.loseConnection()
    tofu.IDLER.reactor.iterate()
    tofu.IDLER.reactor.runUntilCurrent()
    
    tofu.IDLER.reactor.removeAll()
    tofu.IDLER.reactor.disconnectAll()
    
    # We need to start the reactor in order to be able to stop it !!!
    # Else the program cannot ends normally.
    tofu.IDLER.reactor.callLater(0.0, reactor.stop); reactor.run()
    
