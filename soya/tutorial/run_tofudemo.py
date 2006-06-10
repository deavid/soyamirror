# -*- indent-tabs-mode: t -*-

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

from tofudemo import *


# Print usage

if (not sys.argv[1:]) or ("--help" in sys.argv):
	print """run_tofudemo.py -- Launch Soya Tofu Demo
Usages :

	python run_demo.py --single <login> [<password>]
Starts a single player game

	python run_demo.py --server
Starts the server

	python run_demo.py --client <host> <login> [<password>]
Starts a client and connect to server <host> with login <login>
and password <password>. If login doesn't exist, a new player is
created.
"""

else:
	
	# Creates and run an Idler
	# To enable Tofu, we must use soya.tofu4soya.Idler; this special Idler combine
	# soya.Idler and tofu.Idler in a single one.
	
	soya.tofu4soya.Idler(scene)
	
	
	# Lauch a single player game, a server or a client.
	# For both client and single player game, we initialize Soya. For server, we DON'T
	# initialize Soya, in order to not show the 3D rendering window.
	# Calling serve_forever will start the idler.
	
	if   sys.argv[1] == "--single":
		soya.init()
		
		import tofu.single
		tofu.single.serve_forever()
		
	elif sys.argv[1] == "--server":
		import tofu.server
		tofu.server.serve_forever()
		
	elif sys.argv[1] == "--client":
		soya.init()
		
		import tofu.client
		hostname = sys.argv[2]
		tofu.client.serve_forever(hostname)
		
