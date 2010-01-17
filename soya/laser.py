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

"""soya.laser

Provide a Laser -- a red ray that starts at a given position in a given
direction, and ends when it encounter something.

See tutorial lesson 105.

Usefull to debug raypicking !

Properties:

- color:   the color of the ray
- reflect: true (1) if you want the laser to be reflected on wall (default to false)"""

from soya       import PythonCoordSyst, Point, Vector, DEFAULT_MATERIAL
from soya.opengl import *


class Laser(PythonCoordSyst):
	def __init__(self, parent = None, color = (1.0, 0.0, 0.0, 1.0), reflect = 0,
	             collide=True, max_reflect=50):
		PythonCoordSyst.__init__(self, parent)
		
		self.color   = color
		self.reflect = reflect
		self.max_reflect = max_reflect
		self.points  = []
		self.collide = collide
		
	def batch(self):
		if self.color[3] < 1.0: return 2, self, None
		else:                   return 1, self, None
		
	def render(self):
		
		self.points = []

		#list containing points
		to_draw = []
		
		pos   = self.position()
		direc = Vector(self, 0.0, 0.0, -1.0)
		if self.collide:
			i = 0
			raypicker = self.get_root()
			while direc is not None and (i <= self.max_reflect):
				i = i + 1

				impact = raypicker.raypick(pos, direc, -1.0)
				if not impact:
					pos   = pos + (direc * 32000.0)
					direc = None
				else:
					pos = impact[0]
					
					if self.reflect:
						normal = impact[1] % self
						normal.normalize() # changing coordsys can alterate normal size
						normal.set_length(-2.0 * direc.dot_product(normal))
						direc = normal + direc
						
					else:
						direc = None
						
				to_draw.append(pos)
				self.points.append(pos)
		else:
			pos   = pos + (direc * 32000.0)
			to_draw.append(pos)

		#rendering part
		DEFAULT_MATERIAL.activate()
		glDisable(GL_TEXTURE_2D)
		glDisable(GL_LIGHTING)
		
		glColor4f(*self.color)
		glBegin(GL_LINE_STRIP)
		glVertex3f(0.0, 0.0, 0.0)
		for pos in to_draw:
			glVertex3f(*self.transform_point(pos.x, pos.y, pos.z, pos.parent))
			
		glEnd()
		
		glEnable(GL_LIGHTING)
		glEnable(GL_TEXTURE_2D)
	
