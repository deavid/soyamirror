#! /usr/bin/python

# Souvarine souvarine@aliasrobotique.org
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

#
# Quick and dirty Quake 3 BSP importer. Turn a quake 3 bsp file into a saved soya world.
# For testing purpose only.
#

from struct import *
from math import *
import sys, os, os.path
import soya

SCALE_FACTOR = 0.1
TESSELATE_LEVEL = 5

BSP_ENTITIES_LUMP     = 0
BSP_TEXTURES_LUMP     = 1
BSP_PLANES_LUMP       = 2
BSP_NODES_LUMP        = 3
BSP_LEAFS_LUMP        = 4
BSP_LEAF_FACES_LUMP   = 5
BSP_LEAF_BRUSHES_LUMP = 6
BSP_MODELS_LUMP       = 7
BSP_BRUSHES_LUMP      = 8
BSP_BRUSHE_SIDES_LUMP = 9
BSP_VERTEXS_LUMP      = 10
BSP_INDICES_LUMP      = 11
BSP_EFFECTS_LUMP      = 12
BSP_FACES_LUMP        = 13
BSP_LIGHTMAPS_LUMP    = 14
BSP_LIGHTVOLS_LUMP    = 15
BSP_VISDATA_LUMP      = 16
NB_BSP_LUMPS          = 17


class Q3BSPObject(object):
	@classmethod
	def unpack(cls, data):
		object_list = []
		for i in range(0, len(data), cls.size):
			raw = unpack(cls.format, data[i:i+cls.size])
			object_list.append(cls(raw))
		return object_list

class Q3BSPLumpEntry(Q3BSPObject):
	format = "<2i"
	size = calcsize(format)
	
	def __init__(self, data):
		self.offset = data[0]
		self.length = data[1]

class Q3BSPEntitie(Q3BSPObject):
	entry = 0
	
	@classmethod
	def unpack(cls, data):
		data = data.replace('\n', ' ')
		entitys_list = data.split('} {')
		entitys_list[0]  = entitys_list[0][1:]
		entitys_list[-1] = entitys_list[-1][:-3]
		return entitys_list

class Q3BSPTexture(Q3BSPObject):
	format = "<64s2i"
	size = calcsize(format)
	entry = 1
	
	def __init__(self, data):
		self.name     = data[0].rstrip('\x00')
		self.flags    = data[1]
		self.contents = data[2]

class Q3BSPPlane(Q3BSPObject):
	format = "<4f"
	size = calcsize(format)
	entry = 2
	
	def __init__(self, data):
		self.a =  data[0]
		self.b =  data[2]
		self.c = -data[1]
		self.d =  data[3]

class Q3BSPNode(Q3BSPObject):
	format = "<9i"
	size = calcsize(format)
	entry = 3
	
	def __init__(self, data):
		self.plane       = data[0]
		self.front = data[1]
		self.back  = data[2]
		self.box_min     = data[3:6]
		self.box_max     = data[6:9]

class Q3BSPLeaf(Q3BSPObject):
	format = "<12i"
	size = calcsize(format)
	entry = 4
	
	def __init__(self, data):
		self.cluster          =  data[0]
		self.area             =  data[1]
		self.box_min_x        =  data[2]
		self.box_min_y        =  data[4]
		self.box_min_z        = -data[3]
		self.box_max_x        =  data[5]
		self.box_max_y        =  data[7]
		self.box_max_z        = -data[6]
		self.sphere_x         =  self.box_max_x - self.box_min_x
		self.sphere_y         =  self.box_max_y - self.box_min_y
		self.sphere_z         =  self.box_max_z - self.box_min_z
		dx = self.box_max_x - self.sphere_x
		dy = self.box_max_y - self.sphere_y
		dz = self.box_max_z - self.sphere_z
		self.sphere_r         =  sqrt(dx*dx + dy*dy + dz*dz)
		self.leaf_face_start  =  data[8]
		self.nb_leaf_face     =  data[9]
		self.leaf_brush_start =  data[10]
		self.nb_leaf_brush    =  data[11]

class Q3BSPLeafFace(Q3BSPObject):
	format = "<i"
	size = calcsize(format)
	entry = 5
	
	def __init__(self, data):
		self.face = data[0]

class Q3BSPLeafBrush(Q3BSPObject):
	format = "<i"
	size = calcsize(format)
	entry = 6
	
	def __init__(self, data):
		self.brush = data[0]

class Q3BSPModel(Q3BSPObject):
	format = "<6f4i"
	size = calcsize(format)
	entry = 7
	
	def __init__(self, data):
		self.box_min_x   =  data[0]
		self.box_min_y   =  data[1]
		self.box_min_z   = -data[2]
		self.box_max_x   =  data[3]
		self.box_max_y   =  data[4]
		self.box_max_z   = -data[5]
		self.face_start  =  data[6]
		self.nb_face     =  data[7]
		self.brush_start =  data[8]
		self.nb_brush    =  data[9]

class Q3BSPBrush(Q3BSPObject):
	format = "<3i"
	size = calcsize(format)
	entry = 8
	
	def __init__(self, data):
		self.brush_side_start = data[0]
		self.nb_brush_side    = data[1]
		self.texture          = data[2]

class Q3BSPBrushSide(Q3BSPObject):
	format = "<2i"
	size = calcsize(format)
	entry = 9
	
	def __init__(self, data):
		self.plane   = data[0]
		self.texture = data[1]

class Q3BSPVertex(Q3BSPObject):
	format = "<10f4B"
	size = calcsize(format)
	entry = 10
	
	def __init__(self, data = None):
		if not data is None:
			self.x          =  data[0]
			self.y          =  data[2]
			self.z          = -data[1]
			self.texture_x  =  data[3]
			self.texture_y  =  data[4]
			self.lightmap_x =  data[5]
			self.lightmap_y =  data[6]
			self.normal_x   =  data[7]
			self.normal_y   =  data[8]
			self.normal_z   =  data[9]
			self.color      =  data[10:14]
	
	def __mul__(self, scal):
		result = Q3BSPVertex()
		result.x          = self.x          * scal
		result.y          = self.y          * scal
		result.z          = self.z          * scal
		result.texture_x  = self.texture_x  * scal
		result.texture_y  = self.texture_y  * scal
		result.lightmap_x = self.lightmap_x * scal
		result.lightmap_y = self.lightmap_y * scal
		return result
	
	def __add__(self, vertex):
		result = Q3BSPVertex()
		result.x          = self.x          + vertex.x
		result.y          = self.y          + vertex.y
		result.z          = self.z          + vertex.z
		result.texture_x  = self.texture_x  + vertex.texture_x
		result.texture_y  = self.texture_y  + vertex.texture_y
		result.lightmap_x = self.lightmap_x + vertex.lightmap_x
		result.lightmap_y = self.lightmap_y + vertex.lightmap_y
		return result
	
	def interpolate(self, v2, v3, factor):
		result = self*(1.-factor)*(1.-factor) + v2*2.*factor*(1.-factor) + v3*factor*factor
		return result


class Q3BSPIndice(Q3BSPObject):
	format = "<i"
	size = calcsize(format)
	entry = 11
	
	def __init__(self, data):
		self.indice = data[0]

class Q3BSPEffect(Q3BSPObject):
	format = "<64s2i"
	size = calcsize(format)
	entry = 12
	
	def __init__(self, data):
		self.name   = data[0]
		self.brush  = data[1]
		self.unknow = data[2]

class Q3BSPFace(Q3BSPObject):
	format = "<12i12f2i"
	size = calcsize(format)
	entry = 13
	
	def __init__(self, data):
		self.texture           = data[0]
		self.effect            = data[1]
		self.face_type         = data[2]
		self.vertex_start      = data[3]
		self.nb_vertex         = data[4]
		self.indices_start     = data[5]
		self.nb_indices        = data[6]
		self.lightmap          = data[7]
		self.lightmap_x        = data[8]
		self.lightmap_y        = data[9]
		self.lightmap_size_x   = data[10]
		self.lightmap_size_y   = data[11]
		self.lightmap_origin_x = data[12]
		self.lightmap_origin_y = data[13]
		self.lightmap_origin_z = data[14]
		self.lightmap_vect_s_x = data[15]
		self.lightmap_vect_s_y = data[16]
		self.lightmap_vect_s_z = data[17]
		self.lightmap_vect_t_x = data[18]
		self.lightmap_vect_t_y = data[19]
		self.lightmap_vect_t_z = data[20]
		self.normal_x          = data[21]
		self.normal_y          = data[22]
		self.normal_z          = data[23]
		self.patch_size_x      = data[24]
		self.patch_size_y      = data[25]

class Q3BSPLightmap(Q3BSPObject):
	format = "<49152B"
	size = calcsize(format)
	entry = 14
	
	def __init__(self, data):
		self.data = data

class Q3BSPLightvol(Q3BSPObject):
	format = "<8B"
	size = calcsize(format)
	entry = 15
	
	def __init__(self, data):
		self.ambient     = data[0:3]
		self.directional = data[3:6]
		self.direction   = data[6:8]

class Q3BSPVisData(Q3BSPObject):
	entry = 16
	
	@classmethod
	def unpack(cls, data):
		nb_vector   = unpack('<i', data[0:4])
		nb_vector   = nb_vector[0]
		vector_size = unpack('<i', data[4:8])
		vector_size = vector_size[0]
		vis_data    = []
		for i in range(8, len(data)):
			byte = unpack('<B', data[i])
			vis_data.append(byte[0])
		return cls(nb_vector, vector_size, vis_data)
	
	def __init__(self, nb_vector, vector_size, data):
		self.nb_vector   = nb_vector
		self.vector_size = vector_size
		self.data        = data

def get_lump(lump):
	f.seek(lumps[lump.entry].offset)
	data = f.read(lumps[lump.entry].length)
	return lump.unpack(data)

def tesselate_grid(grid, level):
	vertices   = []
	indices    = []
	column0    = []
	column1    = []
	column2    = []
	for i in range(0, level+1):
		factor = float(i) / float(level)
		column0.append(grid[0].interpolate(grid[3], grid[6], factor))
		column1.append(grid[1].interpolate(grid[4], grid[7], factor))
		column2.append(grid[2].interpolate(grid[5], grid[8], factor))
	for i in range(0, level+1):
		for j in range(0, level+1):
			factor = float(j) / float(level)
			vertices.append(column0[i].interpolate(column1[i], column2[i], factor))
	for i in range(0, level):
		for j in range(0, level+1):
			indice = ((i+1) * (level+1)) + j
			indices.append(indice)
			indice = (i* (level+1)) + j
			indices.append(indice)
	return vertices, indices




# Open file and read header
f = open('test1.bsp', 'rb')
data = f.read(8)
header = unpack('<4ci', data)
# Magic should be IBSP and version 46. Else your file is not a quake 3 bsp level !
print "magic =", header[0], header[1], header[2], header[3]
print "version =", header[4]
# Read lump entry
data = f.read(Q3BSPLumpEntry.size * NB_BSP_LUMPS)
lumps = Q3BSPLumpEntry.unpack(data)
i = 0
for lump in lumps:
	print i, "offset =", lump.offset, "length =", lump.length
	i += 1
# Read all lumps
entities    = get_lump(Q3BSPEntitie)
textures    = get_lump(Q3BSPTexture)
planes      = get_lump(Q3BSPPlane)
nodes       = get_lump(Q3BSPNode)
leafs       = get_lump(Q3BSPLeaf)
leaffaces   = get_lump(Q3BSPLeafFace)
leafbrushes = get_lump(Q3BSPLeafBrush)
models      = get_lump(Q3BSPModel)
brushes     = get_lump(Q3BSPBrush)
brushsides  = get_lump(Q3BSPBrushSide)
vertexs     = get_lump(Q3BSPVertex)
indices     = get_lump(Q3BSPIndice)
faces       = get_lump(Q3BSPFace)
lightmaps   = get_lump(Q3BSPLightmap)
lightvols   = get_lump(Q3BSPLightvol)
visdata     = get_lump(Q3BSPVisData)

soya.path.append(os.path.join(os.path.dirname(sys.argv[0]), "data"))
# Process every leaf
# Creat a soya world with the whole level inside
print "found", len(leafs), "leafs"
world = soya.World()
face_groups = []
leaf2facegroup = {}
for leaf in leafs:
	# Discarde strange leaf
	# Invalid leaf, outside the level or inside a wall
	if leaf.cluster == -1:
		continue
	# Zero sized leaf, dorr or moving plateform
	if leaf.box_min_x == 0 and leaf.box_max_x == 0:
		continue
	# Leaf without faces (some faces are shared between leaf)
	if leaf.nb_leaf_face == 0:
		continue
	
	# Get a list of all faces in that leaf
	leaf_leaffaces = leaffaces[leaf.leaf_face_start:leaf.leaf_face_start+leaf.nb_leaf_face]
	
	# Retrive faces
	leaf_bsp_faces = []
	for leafface in leaf_leaffaces:
		if faces[leafface.face].face_type == 4: continue
		if faces[leafface.face].face_type == 2 and (faces[leafface.face].nb_vertex <= 0 or faces[leafface.face].patch_size_x <= 0): continue
		leaf_bsp_faces.append(faces[leafface.face])
	
	# Creat corresponding soya faces in the leaf world
	current_face_list = []
	for face in leaf_bsp_faces:
		# Retriving materials
		print "loading texture", textures[face.texture].name
		material = soya.Material()
		try:
			material.texture = soya.Image.get(textures[face.texture].name + ".jpg")
		except ValueError:
			print "impossible to use texture :("
		
		# Creat sub faces (3 vertices per face)
		# For a polygon or mesh face
		if face.face_type == 1 or face.face_type == 3:
			bsp_indices = indices[face.indices_start:face.indices_start+face.nb_indices]
			if len(bsp_indices) % 3 != 0:
				print "ERROR face num vertices not a multiple of 3 !!!"
				sys.exit()
			
			for i in range(0, len(bsp_indices), 3):
				f = soya.Face(world)
				f.material = material
				f.double_sided = 1
				
				bsp_vertexs = []
				bsp_vertexs.append(vertexs[face.vertex_start+bsp_indices[i].indice])
				bsp_vertexs.append(vertexs[face.vertex_start+bsp_indices[i+1].indice])
				bsp_vertexs.append(vertexs[face.vertex_start+bsp_indices[i+2].indice])
				
				for vertex in bsp_vertexs:
					v = soya.Vertex(world, vertex.x, vertex.y, vertex.z)
					v.tex_x = vertex.texture_x
					v.tex_y = vertex.texture_y
					f.append(v)
				current_face_list.append(f)
		# For a patch face
		elif face.face_type == 2:
			# Retrives bezier patchs
			# A patch is composed of several 3x3 control grids
			# We need to get all the control points
			patch_width    = face.patch_size_x
			patch_height   = face.patch_size_y
			nb_grib_width  = (face.patch_size_x-1) / 2
			nb_grid_height = (face.patch_size_y-1) / 2
			
			# Get control points
			control_points = []
			for i in range(0, (patch_width * patch_height)):
				control_points.append(vertexs[face.vertex_start + i])
			
			for i in range(0, nb_grid_height):
				for j in range(0, nb_grib_width):
					grid = []
					grid.append(control_points[i*patch_width*2 + j*2])
					grid.append(control_points[i*patch_width*2 + j*2 + 1])
					grid.append(control_points[i*patch_width*2 + j*2 + 2])
					
					grid.append(control_points[i*patch_width*2 + patch_width + j*2])
					grid.append(control_points[i*patch_width*2 + patch_width + j*2 + 1])
					grid.append(control_points[i*patch_width*2 + patch_width + j*2 + 2])
					
					grid.append(control_points[i*patch_width*2 + patch_width*2 + j*2])
					grid.append(control_points[i*patch_width*2 + patch_width*2 + j*2 + 1])
					grid.append(control_points[i*patch_width*2 + patch_width*2 + j*2 + 2])
					
					bsp_vertexs, bsp_indices = tesselate_grid(grid, TESSELATE_LEVEL)
					
					triangle_per_row = 2*(TESSELATE_LEVEL+1)
					for k in range(0, TESSELATE_LEVEL):
						for l in range(2, triangle_per_row):
							f = soya.Face(world)
							f.material = material
							f.double_sided = 1
							v = soya.Vertex(world, bsp_vertexs[bsp_indices[(k*triangle_per_row)+l-2]].x, \
																		 bsp_vertexs[bsp_indices[(k*triangle_per_row)+l-2]].y, \
																		 bsp_vertexs[bsp_indices[(k*triangle_per_row)+l-2]].z)
							v.tex_x = bsp_vertexs[bsp_indices[(k*triangle_per_row)+l-2]].texture_x
							v.tex_y = bsp_vertexs[bsp_indices[(k*triangle_per_row)+l-2]].texture_y
							f.append(v)
							v = soya.Vertex(world, bsp_vertexs[bsp_indices[(k*triangle_per_row)+l-1]].x, \
																		 bsp_vertexs[bsp_indices[(k*triangle_per_row)+l-1]].y, \
																		 bsp_vertexs[bsp_indices[(k*triangle_per_row)+l-1]].z)
							v.tex_x = bsp_vertexs[bsp_indices[(k*triangle_per_row)+l-1]].texture_x
							v.tex_y = bsp_vertexs[bsp_indices[(k*triangle_per_row)+l-1]].texture_y
							f.append(v)
							v = soya.Vertex(world, bsp_vertexs[bsp_indices[(k*triangle_per_row)+l]].x, \
																		 bsp_vertexs[bsp_indices[(k*triangle_per_row)+l]].y, \
																		 bsp_vertexs[bsp_indices[(k*triangle_per_row)+l]].z)
							v.tex_x = bsp_vertexs[bsp_indices[(k*triangle_per_row)+l]].texture_x
							v.tex_y = bsp_vertexs[bsp_indices[(k*triangle_per_row)+l]].texture_y
							f.append(v)
							current_face_list.append(f)
	
	if len(current_face_list) > 0:
		face_groups.append(current_face_list)
		leaf2facegroup[leaf] = face_groups.index(current_face_list)

# Creat a splited model from our world
print "creating optimised splited model"
print "this can take up to 10 minutes on a recent computer so be patient :)"
splited_model = soya.SplitedModel(world, face_groups, 80., 0, None)

# Creat the corresponding BSP world and save it
bsp_world = soya.BSPWorld(splited_model, nodes, leafs, planes, leaf2facegroup, visdata)
bsp_world.filename = "imported_bsp_world"
bsp_world.save()

for ent in entities:
	print ent
