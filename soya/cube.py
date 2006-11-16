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

from soya import World, Face, Vertex


def Cube(parent = None, material = None, insert_into = None,size=1):
	"""Cube(parent = None, material = None, insert_into = None) -> World

Creates and returns a World in PARENT, containing a cube of 1 length centered
on the origin, with material MATERIAL.

If INSERT_INTO is not None, the cube's faces are inserted into it, instead of
creating a new world."""
	
	cube = insert_into or World(parent)
	s=size
	Face(cube, [Vertex(cube,  0.5*s,  0.5*s,  0.5*s, 1.0*s, 1.0*s),
							Vertex(cube, -0.5*s,  0.5*s,  0.5*s, 0.0, 1.0*s),
							Vertex(cube, -0.5*s, -0.5*s,  0.5*s, 0.0, 0.0),
							Vertex(cube,  0.5*s, -0.5*s,  0.5*s, 1.0*s, 0.0),
							], material)
	Face(cube, [Vertex(cube,  0.5*s,  0.5*s, -0.5*s, 0.0, 1.0*s),
							Vertex(cube,  0.5*s, -0.5*s, -0.5*s, 0.0, 0.0),
							Vertex(cube, -0.5*s, -0.5*s, -0.5*s, 1.0*s, 0.0),
							Vertex(cube, -0.5*s,  0.5*s, -0.5*s, 1.0*s, 1.0*s),
							], material)
	
	Face(cube, [Vertex(cube,  0.5*s,  0.5*s,  0.5*s, 1.0*s, 0.0),
							Vertex(cube,  0.5*s,  0.5*s, -0.5*s, 1.0*s, 1.0*s),
							Vertex(cube, -0.5*s,  0.5*s, -0.5*s, 0.0, 1.0*s),
							Vertex(cube, -0.5*s,  0.5*s,  0.5*s, 0.0, 0.0),
							], material)
	Face(cube, [Vertex(cube,  0.5*s, -0.5*s,  0.5*s, 1.0*s, 0.0),
							Vertex(cube, -0.5*s, -0.5*s,  0.5*s, 1.0*s, 1.0*s),
							Vertex(cube, -0.5*s, -0.5*s, -0.5*s, 0.0, 1.0*s),
							Vertex(cube,  0.5*s, -0.5*s, -0.5*s, 0.0, 0.0),
							], material)
	
	Face(cube, [Vertex(cube,  0.5*s,  0.5*s,  0.5*s, 1.0*s, 1.0*s),
							Vertex(cube,  0.5*s, -0.5*s,  0.5*s, 1.0*s, 0.0),
							Vertex(cube,  0.5*s, -0.5*s, -0.5*s, 0.0, 0.0),
							Vertex(cube,  0.5*s,  0.5*s, -0.5*s, 0.0, 1.0*s),
							], material)
	Face(cube, [Vertex(cube, -0.5*s,  0.5*s,  0.5*s, 0.0, 1.0*s),
							Vertex(cube, -0.5*s,  0.5*s, -0.5*s, 1.0*s, 1.0*s),
							Vertex(cube, -0.5*s, -0.5*s, -0.5*s, 1.0*s, 0.0),
							Vertex(cube, -0.5*s, -0.5*s,  0.5*s, 0.0, 0.0),
							], material)
	
	return cube
