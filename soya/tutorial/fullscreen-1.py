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


# fullscreen-1: Setting up : displaying a 3D model

# Soya can also render in fullscreen.
# Beware: you MUST write a way to exit the program, e.g. by processing SDL events!


# Imports sys, os modules and the Soya module.

import sys, os, os.path, soya, soya.sdlconst

# Inits Soya in 800x600 fullscreen mode (the last argument, 1, stands for fullscreen).
# The first argument in the window name, which is only visible in window mode.

soya.init("Soya fullscreen tutorial", 800, 600, 1)

soya.path.append(os.path.join(os.path.dirname(sys.argv[0]), "data"))


# The rest of the tutorial is identical to basic-5.py

scene = soya.World()


class CaterpillarHead(soya.Volume):
  def __init__(self, parent):
    soya.Volume.__init__(self, parent, soya.Shape.get("caterpillar_head"))
    self.speed                  = soya.Vector(self, 0.0, 0.0, 0.0)
    self.rotation_lateral_speed = 0.0
    
  def begin_round(self):
    soya.Volume.begin_round(self)
    
    for event in soya.process_event():
      if event[0] == soya.sdlconst.KEYDOWN:
        if   event[1] == soya.sdlconst.K_UP:     self.speed.z = -0.2
        elif event[1] == soya.sdlconst.K_DOWN:   self.speed.z =  0.1
        
        elif event[1] == soya.sdlconst.K_LEFT:   self.rotation_lateral_speed =  10.0
        elif event[1] == soya.sdlconst.K_RIGHT:  self.rotation_lateral_speed = -10.0
        elif event[1] == soya.sdlconst.K_q:      soya.IDLER.stop()
        elif event[1] == soya.sdlconst.K_ESCAPE: soya.IDLER.stop()
      
      if event[0] == soya.sdlconst.KEYUP:
        if   event[1] == soya.sdlconst.K_UP:     self.speed.z = 0.0
        elif event[1] == soya.sdlconst.K_DOWN:   self.speed.z = 0.0
        elif event[1] == soya.sdlconst.K_LEFT:   self.rotation_lateral_speed = 0.0
        elif event[1] == soya.sdlconst.K_RIGHT:  self.rotation_lateral_speed = 0.0
    
    self.rotate_lateral(self.rotation_lateral_speed)
    
  def advance_time(self, proportion):
    soya.Volume.advance_time(self, proportion)
    self.add_mul_vector(proportion, self.speed)


class CaterpillarPiece(soya.Volume):
  def __init__(self, parent, previous):
    soya.Volume.__init__(self, parent, soya.Shape.get("caterpillar"))
    self.previous = previous
    self.speed = soya.Vector(self, 0.0, 0.0, -0.2)
    
  def begin_round(self):
    soya.Volume.begin_round(self)
    self.look_at(self.previous)
    if self.distance_to(self.previous) < 1.5: self.speed.z =  0.0
    else:                                     self.speed.z = -0.2
    
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
light.set_xyz(2.0, 5.0, 0.0)

# Creates a camera.

camera = soya.Camera(scene)
camera.set_xyz(0.0, 15.0, 15.0)
camera.look_at(caterpillar_head)
soya.set_root_widget(camera)

soya.Idler(scene).idle()
