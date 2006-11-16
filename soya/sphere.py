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

from math import sin, cos
from soya import World, Face, Vertex


def Sphere(parent = None, material = None, slices = 20, stacks = 20, smooth_lit = 1, insert_into = None, min_tex_x = 0.0, max_tex_x = 1.0, min_tex_y = 0.0, max_tex_y = 1.0):
	"""Sphere(parent = None, material = None, slices = 20, stacks = 20, insert_into = None, min_tex_x = 0.0, max_tex_x = 1.0, min_tex_y = 0.0, max_tex_y = 1.0) -> World

Creates and returns a World in PARENT, containing a sphere of 1 radius centered
on the origin, with material MATERIAL.

SLICES and STACKS can be used to control the quality of the sphere.

If INSERT_INTO is not None, the sphere's faces are inserted into it, instead of
creating a new world.

MIN/MAX_TEX_X/Y can be used to limit the range of the texture coordinates to the given
values."""
	
	sphere = insert_into or World(parent)
	
	step1 = 6.28322 / slices
	step2 = 3.14161 / stacks
	
	angle1 = 0.0
	for i in xrange(slices):
		angle2 = 0.0
		j = 0
		
		face = Face(sphere, [
			Vertex(sphere, cos(angle1        ) * sin(angle2        ), cos(angle2        ), sin(angle1        ) * sin(angle2        ), min_tex_x + (max_tex_x - min_tex_x) * float(i    ) / slices, min_tex_y + (max_tex_y - min_tex_y) * float(j    ) / stacks),
			Vertex(sphere, cos(angle1 + step1) * sin(angle2 + step2), cos(angle2 + step2), sin(angle1 + step1) * sin(angle2 + step2), min_tex_x + (max_tex_x - min_tex_x) * float(i + 1) / slices, min_tex_y + (max_tex_y - min_tex_y) * float(j + 1) / stacks),
			Vertex(sphere, cos(angle1        ) * sin(angle2 + step2), cos(angle2 + step2), sin(angle1        ) * sin(angle2 + step2), min_tex_x + (max_tex_x - min_tex_x) * float(i    ) / slices, min_tex_y + (max_tex_y - min_tex_y) * float(j + 1) / stacks),
			], material)
		face.smooth_lit = smooth_lit
		angle2 += step2
		
		for j in range(1, stacks - 1):
			face = Face(sphere, [
				Vertex(sphere, cos(angle1        ) * sin(angle2        ), cos(angle2        ), sin(angle1        ) * sin(angle2        ), min_tex_x + (max_tex_x - min_tex_x) * float(i    ) / slices, min_tex_y + (max_tex_y - min_tex_y) * float(j    ) / stacks),
				Vertex(sphere, cos(angle1 + step1) * sin(angle2        ), cos(angle2        ), sin(angle1 + step1) * sin(angle2        ), min_tex_x + (max_tex_x - min_tex_x) * float(i + 1) / slices, min_tex_y + (max_tex_y - min_tex_y) * float(j    ) / stacks),
				Vertex(sphere, cos(angle1 + step1) * sin(angle2 + step2), cos(angle2 + step2), sin(angle1 + step1) * sin(angle2 + step2), min_tex_x + (max_tex_x - min_tex_x) * float(i + 1) / slices, min_tex_y + (max_tex_y - min_tex_y) * float(j + 1) / stacks),
				Vertex(sphere, cos(angle1        ) * sin(angle2 + step2), cos(angle2 + step2), sin(angle1        ) * sin(angle2 + step2), min_tex_x + (max_tex_x - min_tex_x) * float(i    ) / slices, min_tex_y + (max_tex_y - min_tex_y) * float(j + 1) / stacks),
				], material)
			face.smooth_lit = smooth_lit
			angle2 += step2

		j = stacks - 1
		
		face = Face(sphere, [
			Vertex(sphere, cos(angle1        ) * sin(angle2        ), cos(angle2        ), sin(angle1        ) * sin(angle2        ), min_tex_x + (max_tex_x - min_tex_x) * float(i    ) / slices, min_tex_y + (max_tex_y - min_tex_y) * float(j    ) / stacks),
			Vertex(sphere, cos(angle1 + step1) * sin(angle2        ), cos(angle2        ), sin(angle1 + step1) * sin(angle2        ), min_tex_x + (max_tex_x - min_tex_x) * float(i + 1) / slices, min_tex_y + (max_tex_y - min_tex_y) * float(j    ) / stacks),
			Vertex(sphere, cos(angle1        ) * sin(angle2 + step2), cos(angle2 + step2), sin(angle1        ) * sin(angle2 + step2), min_tex_x + (max_tex_x - min_tex_x) * float(i    ) / slices, min_tex_y + (max_tex_y - min_tex_y) * float(j + 1) / stacks),
			], material)
		face.smooth_lit = smooth_lit
		
		angle1 += step1
		
	return sphere
