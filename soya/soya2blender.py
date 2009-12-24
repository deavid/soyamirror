# -*- indent-tabs-mode: t -*-
#!BPY
"""
Name: 'Soya2Blender'
Blender: 236
Group: 'Import'
Tooltip: 'Import Soya worlds in Blender.'
"""

# Soya 3D
# Copyright (C) 2005 Jean-Baptiste LAMY -- jiba@tuxfamily.org
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

import os
import soya
import Blender


def import_soya_model(model):
	scene = soya.World()
	scene.add(model)
	model.rotate_x(90.0)
	
	mesh = Blender.NMesh.New(model.filename or "")
	
	for i in model.recursive():
		print i
		
		if isinstance(i, soya.Face):
			vertices = []
			for v in i.vertices:
				p = v % scene
				vertex = Blender.NMesh.Vert(p.x, p.y, p.z)
				mesh.verts.append(vertex)
				vertices.append(vertex)
			face = Blender.NMesh.Face(vertices)
			for j in range(len(i.vertices)):
				face.uv.append((i.vertices[j].tex_x, 1.0 - i.vertices[j].tex_y))
				
			if i.smooth_lit:   face.smooth = 1
			if i.double_sided: face.mode |= Blender.NMesh.FaceModes.TWOSIDE
			# XXX TODO vertex color
			
			if i.material.texture:
				#print i.material.texture.filename
				face.image = Blender.Image.Load(os.path.join(soya.path[0], "images", i.material.texture.filename))
				
			mesh.faces.append(face)
			
	Blender.NMesh.PutRaw(mesh)
	
	model.rotate_x(-90.0)
	
soya.path.append("/home/jiba/src/arkanae3")

import_soya_model(soya.World.get("room_0_0"))
