# -*- indent-tabs-mode: t -*-

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

# Ark .3d => Soya file converter.
# see http://arkhart.nekeme.net

import os, os.path, re
import soya

def parse_ark(ark):
	ark = re.sub(r"--.*\n", "", ark)
	
	list_re = r"\{\s*n\s*=\s*(\d+)\s*,([^\{\}]*)\}"
	def list_repl(match):
		return "[%s]" % match.group(2)
	
	dict_re = r"\{((?!\s*n\s*=)[^\{\}]*)\}"
	def dict_repl(match):
		return "(%s)" % match.group(1)

	while 1:
		n = re.sub(list_re, list_repl, ark)
		n = re.sub(dict_re, dict_repl, n)

		if n == ark: break
		ark = n
		
		
	ark = "{%s}" % ark.replace("=", ":").replace(";", ",").replace("(", "{").replace(")", "}")

	ark = eval(ark, dict([(a, a) for a in [
		"Model",
		"Triangles",
		"SubModels",
		"Meshes",
		"Type",
		"Indices",
		"Material",
		"VertexCount",
		"Normals",
		"Positions",
		"TexCoords0",
		"Materials",
		"Name",
		"CollisionModel",
		]]))
	ark = ark["Model"]["SubModels"]

	model = soya.World()
	for submodel in ark:
		vertices = [
			soya.Vertex(model,
						 submodel["Positions" ][3 * i], submodel["Positions" ][3 * i + 1], submodel["Positions"][3 * i + 2],
						 submodel["TexCoords0"][2 * i], submodel["TexCoords0"][2 * i + 1],
						 )
			for i in range(submodel["VertexCount"])
			]
		
		for mesh in submodel["Meshes"]:
			if   mesh["Type"] == "Triangles": nbv = 3
			elif mesh["Type"] == "Quad"     : nbv = 4
			else: raise "UnknownVertexNumber"
			
			material = soya.Material.get(mesh["Material"])
			
			indices = mesh["Indices"][:]
			while indices:
				face_vertices = [
					vertices[indices.pop(0)]
					for i in range(nbv)
					]
				face_vertices.reverse()
				face = soya.Face(model, face_vertices, material)
				face.smooth_lit = 1
				if mesh["Material"] == "arbre_feuille_pompon": face.double_sided = 1
				
	return model


def convert_ark(name, new_name = None):
	model = parse_ark(open(os.path.join(soya.path[0], "ark", name + ".3d")).read())
	
	model.filename = new_name or name
	model.save()
	return model

