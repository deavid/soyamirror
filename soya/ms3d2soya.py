# -*- indent-tabs-mode: t -*-

#!/usr/bin/python

import re
import sys
import os
import soya

def decode_ms3d(f):
	"""Decode a milkmodel 3d ascii file (sort of)"""

	data = ''
	m = None
	
	while m is None:
		line = f.readline()
		m = re.match('Meshes: (\d+)', line)
		
	num_meshes = int(m.group(1))

	meshes = []
	
	for i in range(num_meshes):
		line = f.readline()
		print line
		
		line = f.readline()
		num_vertices = int(line)
		
		world = soya.World()
		vertices = []
		for j in range(num_vertices):
			line = f.readline()
			vertex = [float(s) for s in line.split()[1:-1]]
			vertices.append(soya.Vertex(world, vertex[0], vertex[1], vertex[2], vertex[3], vertex[4]))
			
		line = f.readline()
		num_normals = int(line)
		
		for j in range(num_normals):
			# Skip the normals for now
			line = f.readline()
			
		line = f.readline()
		num_triangles = int(line)
		
		triangles = []
		for j in range(num_triangles):
			line = f.readline()
			triangle = [int(s) for s in line.split()[1:]]
			triangles.append(triangle)

		line = ''
		m = None

		while m is None:
			line = f.readline()
			m = re.match("Materials: (\d+)", line)
			
		num_materials = int(m.group(1))
		
		materials = []
		
		for i in range(num_materials):
			material = soya.Material()
			
			material_name = f.readline().strip()
			
			ambient = [float(s) for s in f.readline().split()]
			material.diffuse = [float(s) for s in f.readline().split()]
			material.specular = [float(s) for s in f.readline().split()]
			material.emissive = [float(s) for s in f.readline().split()]
			material.shininess = float(f.readline())
			alpha = float(f.readline())
			texture_filename = f.readline().strip().strip('"')
			print repr(texture_filename)
			material.texture = soya.Image.get(texture_filename)
			alphamap_filename = f.readline().strip().strip('"')
			
			materials.append(material)

		for triangle in triangles:
			face = soya.Face(world)
			face.material = materials[triangle[6]-1]
			for k in range(3):
				# Three vertices in a triangle
				vertex = vertices[triangle[k]]
	 			#texcoord = vertices[triangle[k+3]]
				face.append(vertex)
				
	return world


def main():
	soya.init()
	soya.path.append(os.path.abspath(os.path.dirname(sys.argv[0])))
	print soya.path
	
	filename = sys.argv[1]
	
	world = decode_ms3d(open(filename))
	model = world.to_model()
	model.filename=sys.argv[2]
	model.save()
	
	
	
if __name__ == '__main__':
	main()

