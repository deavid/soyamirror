# Soya 3D tutorial
# Copyright (C) 2004 Jean-Baptiste LAMY
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


# basic-3: Time management : a randomly moving sphere

# In this lesson, we'll create a spherish head that moves around randomly.
# You'll learn about time management (second part), vectors and coordinate-system
# conversion.


# Import the Soya module.

import sys, os, os.path, random, soya

soya.init()
soya.path.append(os.path.join(os.path.dirname(sys.argv[0]), "data"))

# Creates a scene.

scene = soya.World()


# Creates the randomly moving sphere's class. We call it head, because we'll use
# a head-like shape.
# This class inherits from soya.Volume, so it can have a shape (the head).
    
class Head(soya.Volume):
  
  # Redefine the constructor.
  
  def __init__(self, parent):
    
    # Calls the soya.Volume constructor (remember, calling the super implementation is
    # always a good idea), and use the shape called 'caterpillar_head'.
    
    soya.Volume.__init__(self, parent, soya.Shape.get("caterpillar_head"))
    
    # Adds a speed attribute to our new object.
    # The speed is a Vector object. A Vector is a mathematical object, used for
    # computation ; contrary to other object (Light, Camera, Volume, World,...) it does not
    # modify the rendering in any way.
    
    # A vector is defined by a coordinate system and 3 coordinates (X, Y, Z) ; here the
    # speed is defined in 'self', i.e. the Head, and with coordinates 0.0, 0.0, -0.2.
    # Remember that in Soya, the -Z direction is the front. So the speed
    # This means that the speed vector is parallel to the direction the head is looking
    # at, and has a length of 0.2.
    
    self.speed = soya.Vector(self, 0.0, 0.0, -0.2)

  # Like advance_time, begin_round is called by the idler.
  # But contrary to advance_time, begin_round is called regularly, at the beginning of each
  # round ; thus it receive no 'proportion' argument.
  # Decision process should occurs in begin_round.
    
  def begin_round(self):
    
    # Calls the super implementation.
    
    soya.Volume.begin_round(self)
    
    # Changes the direction of the head, by rotating it around the Y axis, of a random
    # angle between -25.0 and 25.0 degrees.
    
    # Notice that after the rotation, the speed vector is still parallel to the direction
    # the head is looking at, since the vector is defined 'inside' the head. 
    
    self.rotate_lateral((random.random() - 0.5) * 50.0)
    
  # In advance_time, we make the head advance.
  
  def advance_time(self, proportion):
    soya.Volume.advance_time(self, proportion)
    
    # Moves the head according to the speed vector.
    # add_mul_vector is identical to: self.add_vector(proportion * self.speed), but faster.
    
    # Notice that the head is defined is the head.parent coordinate system (e.g. the scene)
    # though the speed vector is defined in the head coordinate system. 
    
    self.add_mul_vector(proportion, self.speed)


# Creates a Head in the scene.

head = Head(scene)

# Creates a light.

light = soya.Light(scene)
light.set_xyz(2.0, 5.0, 0.0)

# Creates a camera.

camera = soya.Camera(scene)
soya.set_root_widget(camera)
camera.set_xyz(0.0, 15.0, 15.0)

# Makes the camera looking at the head's initial position.
# The look_at method is another rotation method ; it makes any 3D object looking toward
# the given position (a 3D object or a Point), or in the given direction (if the argument
# is a Vector).

camera.look_at(head)

soya.Idler(scene).idle()
