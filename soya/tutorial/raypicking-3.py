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


# raypicking-3: Laser on Cal3D animated object

# This lesson shows that raypicking (e.g. laser) also works for Cal3D animated models.


import sys, os, os.path, soya, soya.cube, soya.laser, soya.sdlconst

soya.init()
soya.path.append(os.path.join(os.path.dirname(sys.argv[0]), "data"))

# Creates the scene.

scene = soya.World()

# Adds an animated sorcerer (see character-animation-1.py for animated characters).

sorcerer_shape = soya.Cal3dShape.get("balazar")

sorcerer = soya.Cal3dVolume(scene, sorcerer_shape)
sorcerer.rotate_lateral(-120.0)
sorcerer.animate_blend_cycle("marche")
sorcerer.set_xyz(-1.0, -1.0, 0.0)
sorcerer.solid = 1

#sorcerer.scale(0.5, 0.5, 0.5)
#sorcerer.scale(2.0, 2.0, 2.0)

# Adds a light.

light = soya.Light(scene)
light.set_xyz(0.0, 0.2, 1.0)

# Creates a camera.

camera = soya.Camera(scene)
camera.set_xyz(0.0, 0.0, 3.0)

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
laser.x = 2.0


# Main loop

soya.Idler(scene).idle()
