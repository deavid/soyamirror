# -*- indent-tabs-mode: t -*-

# Soya 3D tutorial
# Copyright (C) 2006 Jean-Baptiste LAMY
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


# static-shadows-1: Drag-droppable shadowed 3D objects

# This lesson is very similar to raypicking-2, but the drag-doppable bodys cast shadows.

import sys, os, os.path, soya, soya.cube, soya.sphere, soya.sdlconst, soya.widget

soya.init()
soya.path.append(os.path.join(os.path.dirname(sys.argv[0]), "data"))

# Creates the scene.

scene = soya.World()


# DragDropWorld is a world that allows to dragdrop its content with the mouse.
# See raypicking-2 tuto.

class DragDropWorld(soya.World):
	def __init__(self, parent):
		soya.World.__init__(self, parent)
		
		self.dragdroping = None
		self.impact      = None

		self.old_statics = []
		
	def begin_round(self):
		soya.World.begin_round(self)
		
		
		if len(self.old_statics) != len(self.children):
			self.old_statics = [0] * len(self.children)
			
		for i in range(len(self.children)):
			if self.children[i].static != self.old_statics[i]:
				self.old_statics[i] = self.children[i].static
				if self.children[i].static: print self.children[i].name, "goes static"
				else:                       print self.children[i].name, "is no longer static"
			
		
		for event in soya.process_event():
			
			if   event[0] == soya.sdlconst.MOUSEBUTTONDOWN:
				mouse = camera.coord2d_to_3d(event[2], event[3])
				
				result = self.raypick(camera, camera.vector_to(mouse))
				if result:
					self.impact, normal = result
					self.dragdroping = self.impact.parent
					
					self.impact.convert_to(camera)
					self.old_mouse = camera.coord2d_to_3d(event[2], event[3], self.impact.z)
					
			elif event[0] == soya.sdlconst.MOUSEBUTTONUP:
				self.dragdroping = None
				
			elif event[0] == soya.sdlconst.MOUSEMOTION:
				if self.dragdroping:
					new_mouse = camera.coord2d_to_3d(event[1], event[2], self.impact.z)
					
					self.dragdroping.add_vector(self.old_mouse.vector_to(new_mouse))
					
					self.old_mouse = new_mouse
					

# Creates a dragdrop world.

world = DragDropWorld(scene)

# Adds some bodys with different models, at different positions.

red   = soya.Material(); red  .diffuse = (1.0, 0.0, 0.0, 1.0)
green = soya.Material(); green.diffuse = (0.0, 1.0, 0.0, 1.0)
blue  = soya.Material(); blue .diffuse = (0.0, 0.0, 1.0, 1.0)

model_builder = soya.SimpleModelBuilder()
model_builder.shadow = 1

cube1 = soya.cube.Cube(None, red  )
cube1.model_builder = model_builder
body1 = soya.Body(world, cube1.to_model())
body1.set_xyz(-1.0, -1.0, 1.0)
body1.name = "Red cube"

cube2 = soya.cube.Cube(None, green)
cube2.model_builder = model_builder
body2 = soya.Body(world, cube2.to_model())
body2.set_xyz( 0.0, -1.0, 0.0)
body2.name = "Green cube"

cube3 = soya.cube.Cube(None, blue )
cube3.model_builder = model_builder
# Worlds behave like Body:
world3 = soya.World(world, cube3.to_model())
world3.set_xyz( 1.0, -1.0, -1.0)
world3.name = "Blue cube"

# Adds a light.

light = soya.Light(scene)
light.set_xyz(0.0, 4.0, 1.5)

# Adds a ground (to receive the shadows)

ground_model = soya.World()
ground_face = soya.Face(ground_model, [
	soya.Vertex(ground_model, -5.0, 0.0, -5.0),
	soya.Vertex(ground_model, -5.0, 0.0,  5.0),
	soya.Vertex(ground_model,  5.0, 0.0,  5.0),
	soya.Vertex(ground_model,  5.0, 0.0, -5.0),
	])
ground_face.double_sided = 1
ground = soya.Body(world, ground_model.to_model())
ground.set_xyz(0.0, -3.0, 0.0)
ground.name = "Ground"


# Creates a camera.

camera = soya.Camera(scene)
camera.set_xyz(0.0, 0.0, 4.0)
camera.fov = 100.0


# Creates a widget group, containing the camera and a label showing the FPS.

soya.set_root_widget(soya.widget.Group())
soya.root_widget.add(camera)
soya.root_widget.add(soya.widget.FPSLabel())


# Main loop

main_loop = soya.MainLoop(scene)
main_loop.main_loop()
