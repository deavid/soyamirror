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

"""tofu.single

This module implements a Tofu single-player game (no network).

To lauch a single-player game, create a GameInterface instance, import this module,
and then call serve_forever().
"""

#from twisted.internet import reactor

import tofu


class Notifier(tofu.Notifier):
  def __init__(self):
    tofu.Notifier.__init__(self)
    self.player = None
    
  def login_player(self, filename, password, client_side_data = ""):
    try:               player = tofu.YourPlayer.get(filename)
    except ValueError: player = tofu.YourPlayer(filename, password, client_side_data)
    if password != player.password: raise ValueError("Password is wrong !")
    player.login(self, 1, client_side_data)
    self.player = player
    
  def logout_player(self):
    self.player.logout()
    self.player = None
    
  def notify_own_control(self, mobile):
    mobile.control_owned()
    
  def check_level_activity(self, level):
    # XXX bots
    
    for mobile in level.mobiles:
      if (not mobile.controller.remote) and (not mobile.bot):
        level.set_active(1)
        return
      
    # No local user for this level => we can inactive it
    level.set_active(0)
    
    
  def notify_discard(self, unique):
    # Saves all data locally
    if isinstance(unique, tofu.SavedInAPath) and unique.filename: unique.save()
    
def serve_forever(*args, **kargs):
  """serve_forever(*ARGS, **KARGS)

Starts a single-player game. ARGS and KARGS are passed to GameInterface.__init__()."""
  tofu.YourGameInterface(*args, **kargs)
  
  notifier = Notifier()
  #reactor.callLater(0.0, lambda : tofu.GAME_INTERFACE.ready(notifier))
  tofu.IDLER.next_round_tasks.append(lambda : tofu.GAME_INTERFACE.ready(notifier))
  
  return tofu.IDLER.idle()

