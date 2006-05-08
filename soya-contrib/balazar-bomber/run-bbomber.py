#! /usr/bin/python -O

# Game Skeleton
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

# Soya gaming tutorial, lesson 6
# Network gaming with Tofu !

# Run this script to launch the demo.
# For more info, do :
# 
#     python ./run_tofudemo.py --help

from bbomber import *
tofu4soyapudding.Idler(scene)
state = ''
# Print usage

if (not sys.argv[1:]) or ("--help" in sys.argv):
 

  soya.init()
  pudding.init()
    
  import tofu.single
  state = tofu.single.serve_forever()
  print """


            The Current state is""",state
  print """
This starts balzar-bombers single and client modes
 To start the server please type

  python run_demo.py --server
Starts the server

"""
else:
 
  # Lauch a single player game, a server or a client.
  # For both client and single player game, we initialize Soya. For server, we DON'T
  # initialize Soya, in order to not show the 3D rendering window.
  # Calling serve_forever will start the idler.
    
  if sys.argv[1] == "--server":
    import tofu.server
    state = tofu.server.serve_forever()
    
    

if state == 'client':
    soya.init()
    pudding.init()
    hostname = 'localhost'
    import tofu.client
    #hostname = sys.argv[2]
    tofu.client.serve_forever(hostname)