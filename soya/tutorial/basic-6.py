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


# basic-6: Event management : a mouse-controlled caterpillar

# This time, we'll use the mouse to control the caterpillar.


# Import the Soya module.

import sys, os, os.path, soya, soya.sdlconst

soya.init()
soya.path.append(os.path.join(os.path.dirname(sys.argv[0]), "data"))

# Creates a scene.

scene = soya.World()

# The CaterpillarHead class is very similar to the CaterpillarHead class of the previous
# lesson.

class CaterpillarHead(soya.Volume):
  def __init__(self, parent):
    soya.Volume.__init__(self, parent, soya.Shape.get("caterpillar_head"))
    self.speed                  = soya.Vector(self, 0.0, 0.0, 0.0)
    self.rotation_lateral_speed = 0.0
    self.mouse_x                = 0
    self.mouse_y                = 0
    
  def begin_round(self):
    soya.Volume.begin_round(self)
    
    # Loops over all Soya / SDL events.
    
    for event in soya.process_event():
      
      # Checks for mouse motion events, and store the mouse cursor X, Y coordinates.
      
      if event[0] == soya.sdlconst.MOUSEMOTION:
        self.mouse_x = event[1]
        self.mouse_y = event[2]
        
    # Computes the mouse coordinates in 3D. Camera.coord2d_to_3d takes the X and Y mouse 2D
    # coordinates, and an optional Z coordinates (as it canoot guess the third coordinate ;
    # Z default to -1.0).
    
    # Here, we use for Z the Z coordinates of the caterpillar in the camera coordinate
    # system: we consider the mouse cursor to be at the same depth that the caterpillar.
    # The % operator is used for coordinate system conversion:
    #     position % coordinate_system
    # returns position converted into coordinate_system (possibly position itself if it
    # is already in the right coordinate system).
    
    mouse_pos = camera.coord2d_to_3d(self.mouse_x, self.mouse_y, (self % camera).z)
    
    # Then, converts the mouse position into the scene coordinate system, and set its Y
    # coordinate to 0.0, because we don't want the caterpillar to start flying !
    # (remember, Y is the upper direction).
    
    mouse_pos.convert_to(scene)
    mouse_pos.y = 0.0
    
    # Computes the speed Z coordinate ; we don't want a constant speed: the farther the
    # mouse cursor is, the faster the caterpillar moves.
    # Thus the speed Z coordinate is the distance from the caterpillar to the mouse,
    # and it must be negative (cause -Z is front).
    
    self.speed.z = -self.distance_to(mouse_pos)
    
    # Rotations toward the mouse.
    
    self.look_at(mouse_pos)
    
  def advance_time(self, proportion):
    soya.Volume.advance_time(self, proportion)
    self.add_mul_vector(proportion, self.speed)


# We change CaterpillarPiece, so it can deal with the variable-speed head.

class CaterpillarPiece(soya.Volume):
  def __init__(self, parent, previous):
    soya.Volume.__init__(self, parent, soya.Shape.get("caterpillar"))
    self.previous = previous
    self.speed = soya.Vector(self, 0.0, 0.0, -0.2)
    
  def begin_round(self):
    soya.Volume.begin_round(self)
    
    # As the speed can be very high, we need to take into account the speed of the previous
    # piece (the one we are moving toward).
    # Computes the next position of the previous piece, by translating the piece by the
    # piece's speed vector.
    
    previous_next_pos = self.previous + self.previous.speed
    
    # Looks toward the previous piece's next position.
    
    self.look_at(previous_next_pos)
    
    # Computes the speed's Z coordinate. We use the distance between this piece and the
    # next position of the previous one, and we remove 1.5 because we want each piece
    # to be sepaarated by 1.5 distance units.
    
    self.speed.z = -(self.distance_to(previous_next_pos) - 1.5)
    
  def advance_time(self, proportion):
    soya.Volume.advance_time(self, proportion)
    self.add_mul_vector(proportion, self.speed)
    

# Creates a caterpillar head and 10 caterpillar piece of body.

caterpillar_head = CaterpillarHead(scene)
caterpillar_head.rotate_lateral(90.0)

previous_caterpillar_piece = caterpillar_head
for i in range(10):
  previous_caterpillar_piece = CaterpillarPiece(scene, previous_caterpillar_piece)
  previous_caterpillar_piece.x = i + 1
  
# Creates a light.

light = soya.Light(scene)
light.set_xyz(2.0, 5.0, 1.0)

# Creates a camera.

camera = soya.Camera(scene)
camera.set_xyz(0.0, 15.0, 15.0)
camera.look_at(caterpillar_head)
soya.set_root_widget(camera)

soya.Idler(scene).idle()
