# Soya 3D tutorial
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

# This shows how to use 2 cameras simultaneously.

import soya, soya.cube, soya.sphere, soya.widget

soya.init()

# Creates 2 worlds, one with a cube and the other with a sphere.

w1 = soya.World()
w2 = soya.World()
w1.atmosphere = soya.Atmosphere()
w2.atmosphere = soya.Atmosphere()
w2.atmosphere.bg_color = 0.5, 0.0, 0.3, 1.0
soya.cube.Cube(w1)
soya.sphere.Sphere(w2)


# Create a normal camera in w1.

c1 = soya.Camera(w1)
c1.z = 12


# By default, Soya automatically adapt the camera's viewport to fill the whole screen.
# If you want to use multiple cameras, you must inhibits this by overriding Camera.resize.

class FixedViewportCamera(soya.Camera):
  def __init__(self, parent, left, top, width, height):
    soya.Camera.__init__(self, parent)
    
    self.set_viewport(left, top, width, height)
    
  def resize(self, left, top, width, height):
    pass


# Create a FixedViewportCamera in w2, and put this second rendering in the upper right
# corner of the screen.
# Notice that viewport dimension are given in pixels (soya.get_screen_width and
# soya.get_screen_height will probably be usefull for you :-).

c2 = FixedViewportCamera(w2, 400, 20, 220, 100)
c2.z = 12

# We set the camera c2 as "partial", i.e. a camera that doesn't clear the whole screen.

c2.partial = 1

g = soya.widget.Group()
g.add(c1)
g.add(c2)

soya.set_root_widget(g)

soya.Idler().idle()

