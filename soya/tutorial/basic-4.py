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


# basic-4: Time management : a randomly moving caterpillar

# In this lesson, we'll creates a caterpillar composed of a head (we've already done it
# in the previous lesson ; now you understand why i have called it a 'head') and ten
# spherish piece of body. Each piece of body follows the previous one, or the head for
# first piece.

# Run the tutorial if you don't understand well what is the caterpillar.


# Import the Soya module.

import sys, os, os.path, random, soya

soya.init()
soya.path.append(os.path.join(os.path.dirname(sys.argv[0]), "data"))

# Creates a scene.

scene = soya.World()

# CaterpillarHead is the class for the head of the caterpillar.
# It is identical to the Head class of lesson basic-3.py, except the class name.
# So... no comment!

class CaterpillarHead(soya.Volume):
  def __init__(self, parent):
    soya.Volume.__init__(self, parent, soya.Shape.get("caterpillar_head"))
    self.speed = soya.Vector(self, 0.0, 0.0, -0.2)
    
  def begin_round(self):
    soya.Volume.begin_round(self)
    
    self.rotate_lateral((random.random() - 0.5) * 50.0)
    
  def advance_time(self, proportion):
    soya.Volume.advance_time(self, proportion)
    
    self.add_mul_vector(proportion, self.speed)


# A CaterpillarPiece is a piece of the body of the caterpillar.
# It follows another object -- the previous piece, or the head for the first one.

class CaterpillarPiece(soya.Volume):
  
  # The constructor takes two arguments: the parent and the previous piece of body that
  # we must follow.
  # Similarly to the head, we define a speed vector.
  
  def __init__(self, parent, previous):
    soya.Volume.__init__(self, parent, soya.Shape.get("caterpillar"))
    self.previous = previous
    self.speed = soya.Vector(self, 0.0, 0.0, -0.2)
    
  def begin_round(self):
    soya.Volume.begin_round(self)
    
    # We rotates the caterpillar piece so as it looks toward the previous piece.
    
    self.look_at(self.previous)
    
    # The distance_to method returns the distance between two position.
    # If we are too close to the previous piece of body, we set the speed's Z to 0.0,
    # and thus the speed is a null vector : this piece no longer moves.
    
    # Else, we reset the speed's Z to -0.2.
    
    if self.distance_to(self.previous) < 1.5: self.speed.z =  0.0
    else:                                     self.speed.z = -0.2
    
  # advance_time is identical to the CaterpillarHead ones.
  
  def advance_time(self, proportion):
    soya.Volume.advance_time(self, proportion)
    
    self.add_mul_vector(proportion, self.speed)
    

# Creates a caterpillar head.

caterpillar_head = CaterpillarHead(scene)
caterpillar_head.rotate_lateral(90.0)

# Creates 10 caterpillar piece of body.

previous_caterpillar_piece = caterpillar_head
for i in range(10):
  previous_caterpillar_piece = CaterpillarPiece(scene, previous_caterpillar_piece)
  previous_caterpillar_piece.x = i + 1
  
# Creates a light.

light = soya.Light(scene)
light.set_xyz(2.0, 5.0, 0.0)

# Creates a camera.

camera = soya.Camera(scene)
camera.set_xyz(0.0, 15.0, 15.0)
camera.look_at(caterpillar_head)
soya.set_root_widget(camera)

soya.Idler(scene).idle()


# For information, the caterpillar textures were done in the Gimp, and the model were
# generated with this code (see modeling-*.py to understand it) :

# import soya.sphere
# caterpillar_material      = soya.Material(soya.Image.get("chenille.png"     ))
# caterpillar_head_material = soya.Material(soya.Image.get("chenille_tete.png"))
# caterpillar_material     .filename = "caterpillar"
# caterpillar_head_material.filename = "caterpillar_head"
# caterpillar_material     .save()
# caterpillar_head_material.save()

# caterpillar      = soya.sphere.Sphere(slices = 12, stacks = 12, material = caterpillar_material)
# caterpillar_head = soya.sphere.Sphere(slices = 12, stacks = 12, material = caterpillar_head_material)
# caterpillar_head.scale(1.2, 1.2, 1.2)
# caterpillar     .filename = "caterpillar"
# caterpillar_head.filename = "caterpillar_head"
# caterpillar     .save()
# caterpillar_head.save()












# XXX put this elsewhere

# Lots of Soya methods have also an operator :
#
# Position +  Vector    => Point
# Position += Vector     Position.add_vector(Vector)
# Position >> Position   Position.vector_to (Position) => Vector 
# Position %= CoordSyst  Position.convert_to(CoordSyst)
# Vector   *  float      

# Position +  Vector => Point

# Position += Vector
# Position.add_vector(Vector)
# Translation or vectorial addition (if the Position is a Vector).

# Position >> Position => Vector
# Position.vector_to (Position) => Vector 
# Creates a vector from a strating and an ending position.

# Position %= CoordSyst  Position.convert_to(CoordSyst)
# Vector   *  float      
