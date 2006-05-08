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

"""tofu.server

This module implements a Tofu server.

To lauch a server, you just have to import this module, and then call serve_forever().
"""

from twisted.internet.protocol import DatagramProtocol, Protocol, Factory
from twisted.protocols.basic import LineReceiver, NetstringReceiver
from twisted.internet import reactor

import sys, struct, sets

import tofu


class UDP(DatagramProtocol):
  def datagramReceived(self, data, (host, port)):
    print "UDP received %r from %s:%d" % (data, host, port)
    self.transport.write(data, (host, port))
        
#reactor.listenUDP(6900, UDP())


class SecurityError(StandardError):
  pass



MAX_LENGTH = 99999

class PlayerNotifier(NetstringReceiver):
  def __init__(self):
    self.player          = None
    self.version_checked = 0
    self.MAX_LENGTH = MAX_LENGTH
    
  def stringReceived(self, data):
    #print "TCP received %r" % (data,)
    try:
      code = data[0]
      #print "* Tofu * receiving code %s..." % code
      if   code == tofu.CODE_LOGIN_PLAYER : self.login_player (*data[1:].split("\n", 2))
      elif code == tofu.CODE_LOGOUT_PLAYER: self.logout_player()
      elif code == tofu.CODE_ASK_UNIQUE   :
        #XXX Verify if the player has the rigth to see the asked unique.
        unique = tofu.Unique.undumpuid(data[1:])
        
        #print "TCP send:", tofu.CODE_DATA_UNIQUE + repr(unique.dump())
        #print len(tofu.CODE_DATA_UNIQUE + unique.dump())
        
        self.send_unique(unique)
        
      elif code == tofu.CODE_DATA_ACTION  :
        uid = struct.unpack("!i", data[1:5])[0]
        if tofu.Unique.hasuid(uid):
          mobile = tofu.Unique.undumpuid(data[1:5])
          if not mobile in self.player.mobiles: # XXX optimize this (use Set)
            raise SecurityError("Player %s does not have the right to send action for mobile %s !" % (self.player.filename, mobile.uid))
          mobile.controller.push(tofu.YourAction.undump(data[5:]))
          
      elif code == tofu.CODE_CHECK_VERSION:
        if data[1:] != tofu.VERSION: raise ValueError("Server and client use incompatible version (server: %s, client %s)" % (VERSION, data[1:]))
        self.version_checked = 1
        
    except StandardError, e:
      print "* Tofu * Error occured:"
      sys.excepthook(*sys.exc_info())
      self.sendString(tofu.CODE_ERROR + "%s: %s" % (e.__class__.__name__, str(e)))
      
  def login_player(self, filename, password, client_side_data):
    try:               player = tofu.YourPlayer.get(filename)
    except ValueError: player = tofu.YourPlayer(filename, password, client_side_data)
    if password != player.password: raise ValueError("Password is wrong !") # XXX delay that
    player.login(self, self.transport.socket.getpeername(), client_side_data)
    self.player = player
    
  def logout_player(self):
    self.player.logout()
    self.player = None
    
  def connectionLost(self, reason):
    Protocol.connectionLost(self, reason)
    if self.player:
      print "* Tofu * Connection lost with player %s:" % self.player.filename, reason.getErrorMessage()
      self.logout_player()
      
  def send_unique(self, unique):
    print "* Tofu * Sending unique %s..." % unique.uid
    self.sendString(tofu.CODE_DATA_UNIQUE + unique.dump())
    
  def notify_state(self, mobile, state):
    self.sendString(tofu.CODE_DATA_STATE + "%s%s" % (mobile.dumpuid(), state.dump()))
    
  def notify_add_mobile(self, mobile):
    self.sendString(tofu.CODE_ADD_MOBILE + mobile.dumpuid() + mobile.level.dumpuid())
    self.send_unique(mobile)
    
  def notify_remove_mobile(self, mobile):
    self.sendString(tofu.CODE_REMOVE_MOBILE + mobile.dumpuid())
    
  def notify_enter_level(self, level):
    self.sendString(tofu.CODE_ENTER_LEVEL + level.dumpuid())
    self.send_unique(level)
    
  def notify_own_control(self, mobile):
    self.sendString(tofu.CODE_OWN_CONTROL + mobile.dumpuid())
    
    
class Notifier(tofu.Notifier):
  def notify_action(self, mobile, action):
    #raise AssertionError("Server does not send action !")
    pass
  
  def notify_state(self, mobile, state):
    for player in tofu.YourPlayer._alls2.values(): # XXX optimize this (maintain a list of player for each level)
      if player.notifier:
        for m in player.mobiles:
          if m.level is mobile.level:
            player.notifier.notify_state(mobile, state)
            break
          
  def notify_add_mobile(self, mobile):
    for player in tofu.YourPlayer._alls2.values(): # XXX optimize this
      if player.notifier:
        for m in player.mobiles:
          if (not m is mobile) and (m.level is mobile.level):
            if mobile in player.mobiles:
              player.notifier.notify_own_control(mobile)
            player.notifier.notify_add_mobile(mobile)
            #def doit():
            #  if mobile in player.mobiles:
            #    print "SEND OWN_CONTROL"
            #    player.notifier.notify_own_control(mobile)
            #  print "SEND ADD_MOBILE"
            #  player.notifier.notify_add_mobile(mobile)
            #    
            #tofu.IDLER.next_round_tasks.append(doit)
            
            break
          
        else:
          if mobile in player.mobiles: # XXX optimize this
            # Not notified, because the player doesn't have the level yet
            # => send ENTER_LEVEL and OWN_CONTROL
            #player.notifier.notify_own_control(mobile)
            mobile.send_control_to(player)
            player.notifier.notify_enter_level(mobile.level)
            
  def notify_remove_mobile(self, mobile):
    for player in tofu.YourPlayer._alls2.values(): # XXX optimize this
      if player.notifier:
        for m in player.mobiles:
          if m.level is mobile.level:
            player.notifier.notify_remove_mobile(mobile)
            break
          
  def check_level_activity(self, level):
    for mobile in level.mobiles:
      if mobile.controller.remote:
        level.set_active(1)
        return
      
    # No remote user for this level => we can inactive it
    level.set_active(0)
      
  def notify_discard(self, unique):
    # The server is ALWAYS responsible for saving data
    if isinstance(unique, tofu.SavedInAPath): unique.save()
    
  def game_ended(self):
    for player in tofu.Player._alls2.values():
      if player.notifier:
        player.notifier.logout_player()
        
        
def serve_forever(port = 6900):
  """serve_forever(port = 6900)

Starts a game server on TCP port PORT."""
  tofu.NOTIFIER = Notifier()
  
  f = Factory()
  f.protocol = PlayerNotifier
  reactor.listenTCP(6900, f)
  
  print "* Tofu * Server ready !"
  try:
    tofu.IDLER.idle()
    
  except:
    sys.excepthook(*sys.exc_info())
    tofu.NOTIFIER.game_ended()


