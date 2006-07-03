# -*- indent-tabs-mode: t -*-

# Soya 3D
# Copyright (C) 2001-2002 Jean-Baptiste LAMY -- jiba@tuxfamily.org
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

"""soya.cursor

Provide a 2D and 3D (with roll) mouse-based cursor.
See soya.cursor.Cursor.__doc__
"""

import soya


class Cursor(soya.Body):
	"""soya.cursor.Cursor

A 2D and 3D (with roll) mouse-based cursor.
"""
	def __init__(self, parent = None, camera = None, model = None, grid_step = 0.0):
		"""Cursor(parent = None, camera = None, model = None) -> Cursor

Create a new cursor. A cursor is a body, and so you should provide a model
(MODEL arg) for it, if you want to see something.

CAMERA is the camera in which the cursor is used.
"""
		soya.Body.__init__(self, parent, model)
		self.camera    = camera
		self.grid_step = grid_step
		
	def mouse_moved(self, x, y):
		"""Cursor.mouse_moved(x, y)

Must be called when the mouse is moved, with the new mouse position.

X and Y are the mouse coordinate in pixel, as given by the soya event
processing function.

this function will then call Cursor.move(position), which you may want to
override.
"""
		self.mouse_x, self.mouse_y = ((-float(x) / self.camera.get_screen_width()) + 0.5) * 1.55, ((float(y) / self.camera.get_screen_height()) - 0.5) * 1.15
		
		
		mouse = self % self.camera
		mouse.x = self.mouse_x * mouse.z #/ 1.0
		mouse.y = self.mouse_y * mouse.z #/ 1.0
		
		if self.grid_step:
			mouse = mouse % self.parent
			d = self.grid_step / 2.0
			mouse.x = ((mouse.x + d) // self.grid_step) * self.grid_step
			mouse.y = ((mouse.y + d) // self.grid_step) * self.grid_step
			mouse.z = ((mouse.z + d) // self.grid_step) * self.grid_step
			
		self.move(mouse)
		
	def mouse_rolled(self, z_rel):
		"""Cursor.mouse_rolled(z_rel)

Must be called when the mouse is rolled (mouse button 4 and 5).

Z_REL is the Z amount that will be added to the current cursor's z coordinate.
Typically, Z_REL is < 0.0 for roll-up   (mouse-button 4)
					 Z_REL is > 0.0 for roll-down (mouse-button 5)

this function will then call Cursor.move(position), which you may want to
override.
"""
		mouse = self % self.camera
		new_z = min(mouse.z + z_rel, -0.1)
		
		if mouse.z != 0.0:
			mouse.x = mouse.x * new_z / mouse.z
			mouse.y = mouse.y * new_z / mouse.z
		mouse.z = new_z
		
		if self.grid_step:
			mouse = mouse % self.parent
			d = self.grid_step / 2.0
			mouse.x = ((mouse.x + d) // self.grid_step) * self.grid_step
			mouse.y = ((mouse.y + d) // self.grid_step) * self.grid_step
			mouse.z = ((mouse.z + d) // self.grid_step) * self.grid_step
			
		self.move(mouse)
		
	def front(self, z = -1.0):
		"""Cursor.front(z = -1.0) -> Vector

Returns the "front" vector for this cursor. This vector has z = Z.
If you translating any object by this vector, its position on the screen, as
viewed by the camera Cursor.camera, will not be changed -- the object will
just be more or less near.
"""
		mouse = self % self.camera
		f = (z) / mouse.z
		return soya.Vector(self.camera, mouse.x * f, mouse.y * f, z)
	
	def is_under(self, position, tolerance = 0.1):
		"""Cursor.is_under(position, tolerance = 0.1) -> boolean

Returns true if POSITION is visually "under" the cursor (or over), at tolerance
TOLERANCE.
"""
		position = position % self.camera
		mouse    = self     % self.camera
		return (
			(abs(position.x - mouse.x * (position.z / float(mouse.z))) < tolerance) and
			(abs(position.y - mouse.y * (position.z / float(mouse.z))) < tolerance)
			)
	
	def is_under_tester(self, tolerance = 0.1):
		"""Cursor.is_under_tester(tolerance = 0.1) -> Callable

Creates and returns a callable, which accepts a single argument (a position).
This callable will perform as does Cursor.is_under, but faster. It will not
be updated if the cursor is moved, though.

Use this if you have a lot of "is_under" test to do, and you can assume that
the cursor won't be moved between these test.
"""
		mouse = self % self.camera
		
		def tester(position):
			position = position % self.camera
			return (
				(abs(position.x - mouse.x * (position.z / float(mouse.z))) < tolerance) and
				(abs(position.y - mouse.y * (position.z / float(mouse.z))) < tolerance)
				)
		return tester



