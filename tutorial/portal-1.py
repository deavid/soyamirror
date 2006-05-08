# Soya 3D tutorial 
# Copyright (C) 2004      Jean-Baptiste 'Jiba'  LAMY
# Copyright (C) 2001-2003 Bertrand      'blam!' LAMY
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


# portal-1: Portal

# A portal is a 2D rectangle used to link 2 worlds just as if the world
# beyond was seen through an open door.
# Portals are usefull to compute visibility and avoid renderering the
# world beyond when it is not visible.


import sys, os, os.path, soya, soya.cube, soya.widget, soya.sdlconst

soya.init()
soya.path.append(os.path.join(os.path.dirname(sys.argv[0]), "data"))

m1 = soya.Material(soya.Image.get("block2.png"))
m2 = soya.Material(soya.Image.get("metal1.png"))

scene = soya.World()

# Create world 1

w1 = soya.World(scene)
w1.set_xyz(0.0, 0.0, 0.0)
w1.atmosphere = soya.Atmosphere()
w1.atmosphere.bg_color = (0.0, 0.0, 1.0, 1.0)
w1.atmosphere.ambient  = (0.0, 0.5, 0.0, 1.0)
w1.atmosphere.fog_color = (0.0, 0.0, 1.0, 1.0)
w1.atmosphere.fog_start = 10.0
w1.atmosphere.fog_end = 50.0
w1.atmosphere.fog = 1
w1.atmosphere.fog_type = 0
w1.set_shape(soya.cube.Cube(None, m1).shapify())

# Create world 2
# Notice that w2 doesn't have the same atmosphere than w1

w2 = soya.World(scene)
w2.set_xyz(0.0, 0.0, -10.0)
w2.atmosphere = soya.SkyAtmosphere()
w2.atmosphere.bg_color  = (1.0, 0.0, 0.0, 1.0)
w2.atmosphere.ambient   = (0.5, 0.5, 0.0, 1.0)
w2.atmosphere.skyplane  = 1
w2.atmosphere.sky_color = (1.0, 1.0, 0.0, 1.0)
w2.atmosphere.cloud = soya.Material(soya.Image.get("cloud.png"))
w2.set_shape(soya.cube.Cube(None, m2).shapify())


# Add a light in world 2.
# The light will not light the objects in world 1 unless light.top_level is true.

light = soya.Light(w2)
light.top_level = 0
light.ambient = (1.0, 1.0, 0.0, 1.0)
light.set_xyz(0.0, 2.0, 0.0)


# Portal creation
# Create a portal that link to world 2. The attribute "beyond" is the world beyond
# the portal

portal1 = soya.Portal(w1)
portal1.beyond = w2
portal1.set_xyz(0.0, 0.0, -5.0)

# To change the size of the portal, we scale it (the z scale factor has no meaning)

portal1.scale(4.0, 4.0, 1.0)
#   Attr bound_atm must be set to 1 if the 2 worlds linked doesn't have the
#   same atmosphere (else set the value to 0).
#portal1.bound_atmosphere = 1
#   Setting use_clip_plane to 1 will affect object rendered in world beyond,
#   this means only the part of the objects that are visible through the portal
#   2D rectangle will be rendered.
#portal1.nb_clip_planes = 4

# Create a portal that link world 2 to world 1

portal2 = soya.Portal(w2)
portal2.rotate_lateral(180.0)
portal2.beyond = w1
portal2.scale(4.0, 4.0, 1.0)
portal2.set_xyz(0.0, 0.0, 5.0)

#portal1.nb_clip_planes = 0
#portal2.nb_clip_planes = 0

# ASCII art representation of the two world :
#                           \
#               \            |
#    +-+         |           |
#    | |\        |           |
#    +-+ +        > world2   |
#     \ \|       |           |
#      +-+       |           |
#                |           |
# <-portal2->   /            |
#--------------+             |
# <-portal1->   \            |
#                |            > scene
#    +-+         |           |
#    | |\        |           |
#    +-+ +       |           |
#     \ \|       |           |
#      +-+        > world1   |
#                |           |
#     ___        |           |
#     \^/        |           |
#      V         |           |
#    camera     /            |
#                           /

class MovableCamera(soya.Camera):
  def __init__(self, parent):
    soya.Camera.__init__(self, parent)
    
    self.speed = soya.Vector(self)
    self.rotation_lateral_speed  = 0.0
    self.rotation_vertical_speed = 0.0
    
  def begin_round(self):
    soya.Camera.begin_round(self)
    
    for event in soya.process_event():
      if event[0] == soya.sdlconst.KEYDOWN:
        if   event[1] == soya.sdlconst.K_UP:     self.speed.z = -1.0
        elif event[1] == soya.sdlconst.K_DOWN:   self.speed.z =  1.0
        elif event[1] == soya.sdlconst.K_LEFT:   self.rotation_lateral_speed =  10.0
        elif event[1] == soya.sdlconst.K_RIGHT:  self.rotation_lateral_speed = -10.0
        elif event[1] == soya.sdlconst.K_q:      soya.IDLER.stop()
        elif event[1] == soya.sdlconst.K_ESCAPE: soya.IDLER.stop()
      if event[0] == soya.sdlconst.KEYUP:
        if   event[1] == soya.sdlconst.K_UP:     self.speed.z = 0.0
        elif event[1] == soya.sdlconst.K_DOWN:   self.speed.z = 0.0
        elif event[1] == soya.sdlconst.K_LEFT:   self.rotation_lateral_speed = 0.0
        elif event[1] == soya.sdlconst.K_RIGHT:  self.rotation_lateral_speed = 0.0
    
    # Checks if the camera has passed through a portal.
    # First, collects all portals in the camera's root world.
    # the World.search_all method take a predicat (a one argument callable), and
    # returns a list of all items (recursively) in the world that satisfy the predicat.
    
    portals = camera.to_render.search_all(lambda item: isinstance(item, soya.Portal))
    
    # Then for each portal, checks if the camera has pass through it, and if so,
    # transfers the camera in the world beyond the portal.
    # The has_passed_through method takes two argument : the old position of the object
    # and the new one or (as here) the speed vector.
    
    for portal in portals:
      if portal.has_passed_through(self, self.speed):
        print "pass !", self.position(), self.speed
        portal.pass_through(camera)
        
  def advance_time(self, proportion):
    self.add_mul_vector(proportion, self.speed)
    self.turn_lateral (self.rotation_lateral_speed  * proportion)
    self.turn_vertical(self.rotation_vertical_speed * proportion)


# Creates a movable camera, that render the world 1 only (to_render attribute)

camera = MovableCamera(scene)
camera.to_render = w1
camera.set_xyz(0.0, 0.0, 8.0)

root = soya.widget.Group()

root.add(camera)

label = soya.widget.Label(root, " - Portal demo - use cursor keys to move.")
label.resize_style = soya.widget.WIDGET_RESIZE_MAXIMIZE

soya.set_root_widget(root)

soya.Idler(scene).idle()
