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


# raypicking-2: Drag-dropable 3D objects

# In this lesson, you'll learn how to use raypicking to grab the object under the mouse.

# Raypicking consists in casting a ray in a 3D World, and it returns information abour
# the object the ray hit.

# Soya provides 2 raypicking functions: raypick and raypick_b ("b" stands for boolean).
# The first version returns a (IMPACT, NORMAL) tuple. IMPACT is the impact Point, and
# IMPACT.parent is the object hit. NORMAL is the normal Vector of the object at the
# impact (usefull e.g. for reflection).
# The boolean version simply returns true if something is hit.

# Both take the same arguments:
# - ORIGIN:    the origin of the ray (a Position)
# - DIRECTION: the direction of the ray (a Vector)
# - DISTANCE:  the maximum distance of the ray; -1.0 (default) for no distance limit
# - HALF_LINE: if true (default), the ray goes only in the direction of DIRECTION.
#              if false, the ray goes both in DIRECTION and -DIRECTION, and so can hit
#              objects backward.
# - CULL_FACE  if true (default), does not take into account invisible sides of non-double
#              sided faces (Face.double_sided = 0).

# For speeding up, raypick has 2 optional arguments, a Point and a Vector. If given,
# these Point and Vector will be returned in the tuple, instead of creating new objects.


import sys, os, os.path, soya, soya.cube, soya.sphere, soya.sdlconst

soya.init()
soya.path.append(os.path.join(os.path.dirname(sys.argv[0]), "data"))

# Creates the scene.

scene = soya.World()


# DragDropWorld is a world that allows to dragdrop its content with the mouse.

class DragDropWorld(soya.World):
  def __init__(self, parent):
    soya.World.__init__(self, parent)
    
    # The object we are currently dragdroping (None => no dragdrop).
    
    self.dragdroping = None
    
    # The impact point
    
    self.impact = None
    
    
  def begin_round(self):
    soya.World.begin_round(self)
    
    # Processes the events
    
    for event in soya.process_event():
      
      # Mouse down initiates the dragdrop.
      
      if   event[0] == soya.sdlconst.MOUSEBUTTONDOWN:
        
        # The event give us the 2D mouse coordinates in pixel. The camera.coord2d_to_3d
        # convert these 2D pixel coordinates into a soy.Point object.
        
        mouse = camera.coord2d_to_3d(event[2], event[3])
        
        # Performs a raypicking, starting at the camera and going toward the mouse.
        # The vector_to method returns the vector between 2 positions.
        # This raypicking grabs anything that is under the mouse. Raypicking returns
        # None if nothing is encountered, or a (impact, normal) tuple, where impact is the
        # position of the impact and normal is the normal vector at this position.
        # The object encountered is impact.parent ; here, we don't need the normal.
        
        result = self.raypick(camera, camera.vector_to(mouse))
        if result:
          self.impact, normal = result
          self.dragdroping = self.impact.parent
          
          # Converts impact into the camera coordinate system, in order to get its Z value.
          # camera.coord2d_to_3d cannot choose a Z value for you, so you need to pass it
          # as a third argument (it defaults to -1.0). Then, we computes the old mouse
          # position, which has the same Z value than impact.
          
          self.impact.convert_to(camera)
          self.old_mouse = camera.coord2d_to_3d(event[2], event[3], self.impact.z)
          
          
      # Mouse up ends the dragdrop.
      
      elif event[0] == soya.sdlconst.MOUSEBUTTONUP:
        self.dragdroping = None
        
        
      # Mouse motion moves the dragdroping object, if there is one.
      
      elif event[0] == soya.sdlconst.MOUSEMOTION:
        if self.dragdroping:
          
          # Computes the new mouse position, at the same Z value than impact.
          
          new_mouse = camera.coord2d_to_3d(event[1], event[2], self.impact.z)
          
          # Translates dragdroping by a vector starting at old_mouse and ending at
          # new_mouse.
          
          self.dragdroping.add_vector(self.old_mouse.vector_to(new_mouse))
          
          # Store the current mouse position.
          
          self.old_mouse = new_mouse
          

# Creates a dragdrop world.

world = DragDropWorld(scene)

# Adds some volumes with different shapes, at different positions.

red   = soya.Material(); red  .diffuse = (1.0, 0.0, 0.0, 1.0)
green = soya.Material(); green.diffuse = (0.0, 1.0, 0.0, 1.0)
blue  = soya.Material(); blue .diffuse = (0.0, 0.0, 1.0, 1.0)

soya.Volume(world, soya.cube.Cube(None, red  ).shapify()).set_xyz(-1.0, -1.0, 1.0)
soya.Volume(world, soya.cube.Cube(None, green).shapify()).set_xyz( 0.0, -1.0, 0.0)
soya.Volume(world, soya.cube.Cube(None, blue ).shapify()).set_xyz( 1.0, -1.0, -1.0)

soya.Volume(world, soya.sphere.Sphere().shapify()).set_xyz(1.0, 1.0, 0.0)

# Adds a light.

light = soya.Light(scene)
light.set_xyz(0.0, 0.2, 1.0)

# Creates a camera.

camera = soya.Camera(scene)
camera.set_xyz(0.0, 0.0, 4.0)
camera.fov = 100.0
soya.set_root_widget(camera)


# Main loop

soya.Idler(scene).idle()


# TODO / exercice : turn this demo into a puzzle game !
