# -*- indent-tabs-mode: t -*-

# Soya 3D
# Copyright (C) 2001-2002 Jean-Baptiste LAMY
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

import Tkinter
import soya, soya.cube as cube


class MaterialEditor:
	def __init__(self, material, dialog):
		self.active = 0
		self.dialog = dialog
		
		self.material = material
		
		self.scene  = soya.World()
		self.camera = soya.Camera(self.scene)
		soya.set_root_widget(self.camera)
		
		soya.Light(self.scene).set_xyz(0.2, 2.0, 0.2)
		
		#self.cube = cube.Cube(self.scene, material)
		cube_world = cube.Cube(None, material)
		self.cube = soya.Body(self.scene, cube_world.to_model())
		self.cube.set_xyz(0.0, 0.0, -2.0)
		self.cube.rotate_x(30.0)
		
	def rotate(self):
		if self.active:
			self.cube.rotate_y(5.0)
			self.render()
			
			events = soya.process_event()
			
			self.cancel = self.dialog.after(50, self.rotate)
			
	def render(self):
		if self.active: soya.render()
			
	def activate(self, event = None):
		if not self.active:
			self.active = 1
			soya.set_root_widget(self.camera)
			self.render()
			
			self.cancel = self.dialog.after(50, self.rotate)
			
	def deactivate(self, event = None):
		if self.active:
			self.active = 0
			
			self.dialog.after_cancel(self.cancel)
			
