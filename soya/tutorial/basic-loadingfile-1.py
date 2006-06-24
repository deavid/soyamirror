# -*- indent-tabs-mode: t -*-

# Soya 3D tutorial
# Copyright (C) 2001-2004 Jean-Baptiste LAMY
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


# basic-loadingfile-1: Load a file : load the rotating volume

# This lesson loads the rotating model from a file, using either Cerealizer or cPickle.
#
# The file should be created by running either the basic-savingfile-cerealizer-1 or the
# basic-savingfile-pickle-1 tutorial. Notice than loading a file is INDEPENDENT
# of its file format (Cerealizer or Pickle); Soya being able to determine the format
# by itself.

# Imports Soya and cerealizer.

import sys, os, os.path, soya
import cerealizer

# Import the module that defines the RotatingVolume class. Cerealizer or Pickle saves the
# object data, but NOT the source or executable code of their class.
#
# Here, we use "execfile" since the file "basic-savingfile-cerealizer-1.py" is not a valid
# Python module name, due to the "-" character in it.
# However, you should normally use something like:
#
#import basic-savingfile-cerealizer-1
#
# Wether we import "basic-savingfile-cerealizer-1.py" or "basic-savingfile-pickle-1.py"
# has no importance, since the 'module part' (=before the "if __name__ == "__main__") is
# the same in the two tutorial.

execfile(os.path.join(os.path.dirname(sys.argv[0]), "basic-savingfile-cerealizer-1.py"))


# Inits Soya and sets the data directory.

soya.init()
soya.path.append(os.path.join(os.path.dirname(sys.argv[0]), "data"))

# Load the scene we have saved previously. "a_scene_with_a_rotating_volume" is the filename
# we have given to this scene.
# The "World.load" method is similar to "Shape.get", except that "load" ALWAYS returns a new
# object read from the file, whereas "get" cache its result.

scene = soya.World.load("a_scene_with_a_rotating_volume")


# Creates a camera.
#
# For technical reasons, camera are not saveable yet. This is not really a problem since the
# camera is not really scene-dependent by rather configuration-dependent.
# We thus add the camera AFTER loading the scene.

camera = soya.Camera(scene)
camera.z = 3.0
soya.set_root_widget(camera)

soya.Idler(scene).idle()
