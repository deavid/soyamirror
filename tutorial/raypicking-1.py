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


# raypicking-1: Laser

# This lesson includes a red laser ray and 3 rotating cubes.
# Move the mouse to move the laser.
# In particular, lasers have been used while testing raypicking function.

# BTW, the laser code (in soya/laser.py) is fully in Python and uses less that 60 lines
# of code, so you might want to take a look at it.


import sys, os, os.path, soya, soya.cube, soya.laser, soya.sdlconst

soya.init()
soya.path.append(os.path.join(os.path.dirname(sys.argv[0]), "data"))

# Creates the scene.

scene = soya.World()

# Adds 3 rotating cubes in it (see basic-2.py about rotating volume).

cube_world = soya.cube.Cube()
cube_shape = cube_world.shapify()

class RotatingCube(soya.Volume):
  def __init__(self, parent, angle_speed):
    soya.Volume.__init__(self, parent, cube_shape)
    self.angle_speed = angle_speed
    
  def advance_time(self, proportion):
    self.rotate_incline(0.2 * proportion * self.angle_speed)
    
cube_1 = RotatingCube(scene, 5.0)
cube_1.set_xyz(-1.1, 0.5, 0.0)

cube_2 = RotatingCube(scene, -5.0)
cube_2.set_xyz(-1.5, -1.5, 0.0)

cube_3 = RotatingCube(scene, 5.0)
cube_3.set_xyz(1.1, -0.5, 0.0)
cube_3.scale(0.5, 0.5, 0.5)

# Adds a light.

light = soya.Light(scene)
light.set_xyz(0.0, 0.2, 1.0)

# Creates a camera.

camera = soya.Camera(scene)
camera.set_xyz(0.0, -1.0, 3.0)

soya.set_root_widget(camera)

# Hide the mouse cursor

soya.cursor_set_visible(0)


# MouseLaser is a subclass of laser that is controlled by the mouse.

class MouseLaser(soya.laser.Laser):
  def begin_round(self):
    soya.laser.Laser.begin_round(self)
    
    # Processes the events
    
    for event in soya.process_event():
      if event[0] == soya.sdlconst.MOUSEMOTION:

        # For mouse motion event, rotate the laser (quite) toward the mouse.
        # The formulas are empirical; see soya.cursor for a better algorithm
        # if you want to translate mouse positions into 3D coordinates.

        mouse = soya.Point(
          scene,
          (float(event[1]) / camera.get_screen_width () - 0.5) *  4.0,
          (float(event[2]) / camera.get_screen_height() - 0.5) * -4.0,
          0.0,
          )
        self.look_at(mouse)
      

# Creates a red mouse-controlled laser, which reflect on walls.
# You can change the laser color with laser.color = (r, g, b, a).

laser = MouseLaser(scene, reflect = 1)
laser.y = -2.5

scene.x = 1.0

# Main loop

soya.Idler(scene).idle()


# TODO (left as an exercice):
# Turn this tutorial lesson into a full game, where the player must shoot
# with the laser a specific target (or monsters).
# The levels includes different moving and rotating obstacles.
# A multiplayer version uses two laser, one for each player, and two targets.

# Hint :
# the laser.points list contains all the points that define the laser trajectory.
# use laser.color to change the color of the laser.

# Good luck!
