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


# ray-1: Ray : the light sword

# This lesson is a light sword, which can be controlled with the mouse.

import sys, os, os.path, soya, soya.cube, soya.ray, soya.widget as widget, soya.sdlconst

soya.init()
soya.path.append(os.path.join(os.path.dirname(sys.argv[0]), "data"))

# Creates the scene.

scene = soya.World()

sword = soya.World(scene)
sword.set_shape(soya.Shape.get("sword"))
sword.y = -1.5

# Adds a light, and a camera

light = soya.Light(scene)
light.set_xyz(0.0, 0.2, 1.0)

camera = soya.Camera(scene)
camera.set_xyz(0.0, -0.5, 2.0)
soya.set_root_widget(camera)

# Creates the material for the ray.

material = soya.Material()
material.shininess = 0.5
material.diffuse   = (0.6, 0.5, 0.7, 1.0)
material.additive_blending = 1 # Additive blending istypically used for FX

# Creates the ray.

ray = soya.ray.Ray(sword, length = 20)
ray.z = -0.2
ray.endpoint = soya.Point(sword, 0.0, 0.0, -1.95)
ray.material = material

# Hide the mouse cursor

soya.cursor_set_visible(0)



def begin_round():
  # Processes the events
  
  # soya.cursor.coalesce_motion_event() removes all mouse motion events, except
  # the last one -- we use it for speed gain, since many mouse motion event
  # often occur at the same time.
  
  for event in soya.process_event():
    if event[0] == soya.sdlconst.MOUSEMOTION:
      
      # For mouse motion event, rotate the laser (quite) toward the mouse.
      # The formulas are empirical; see soya.cursor for a better algorithm
      # if you want to translate mouse positions into 3D coordinates.
      
      mouse = soya.Point(
        scene,
        (float(event[1]) / camera.get_screen_width () - 0.5) *  2.0,
        (float(event[2]) / camera.get_screen_height() - 0.5) * -4.0,
        (float(event[2]) / camera.get_screen_height() - 0.5) * -1.0 + 0.25,
        )
      sword.look_at(mouse)
        
sword.begin_round = begin_round

# Main loop

soya.Idler(scene).idle()


# TODO (left as an exercice):
# Turn this tutorial lesson into a full Doom-like game!
