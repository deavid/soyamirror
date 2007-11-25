#! /usr/bin/python
# -*- indent-tabs-mode: t -*-
# -*- coding: utf-8 -*-

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
# Quake 3 BSP importer. Turn a quake 3 bsp file into a soya BSPWorld.
#

from struct import *
from math import *
import sys, os, os.path
import soya

TESSELATE_LEVEL = 3
SHELL_TESSELATE_LEVEL = 3

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

CONTENT_SOLID         = 1


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
		texture       = data[0].rstrip('\x00')
		file_index    = texture.rfind('/')
		self.name     = texture[file_index+1:]
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
		self.normal = soya.Vector(None, self.a, self.b, self.c)

class Q3BSPNode(Q3BSPObject):
	format = "<9i"
	size = calcsize(format)
	entry = 3
	
	def __init__(self, data):
		self.plane   = data[0]
		self.front   = data[1]
		self.back    = data[2]
		self.box_min = data[3:6]
		self.box_max = data[6:9]

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
		self.brush_indices    =  []
		self.model_part       = -1

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
		self.plane_indices    = None
		self.triangle_list    = None

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

class Q3BSPFaceGroup(Q3BSPObject):
	format = "<12i12f2i"
	size = calcsize(format)
	entry = 13
	
	def __init__(self, data):
		self.texture           =  data[0]
		self.effect            =  data[1]
		self.face_type         =  data[2]
		self.vertex_start      =  data[3]
		self.nb_vertex         =  data[4]
		self.indices_start     =  data[5]
		self.nb_indices        =  data[6]
		self.lightmap          =  data[7]
		self.lightmap_x        =  data[8]
		self.lightmap_y        =  data[9]
		self.lightmap_size_x   =  data[10]
		self.lightmap_size_y   =  data[11]
		self.lightmap_origin_x =  data[12]
		self.lightmap_origin_y =  data[13]
		self.lightmap_origin_z =  data[14]
		self.lightmap_vect_s_x =  data[15]
		self.lightmap_vect_s_y =  data[16]
		self.lightmap_vect_s_z =  data[17]
		self.lightmap_vect_t_x =  data[18]
		self.lightmap_vect_t_y =  data[19]
		self.lightmap_vect_t_z =  data[20]
		self.normal_x          =  data[21]
		self.normal_y          =  data[23]
		self.normal_z          = -data[22]
		self.patch_size_x      =  data[24]
		self.patch_size_y      =  data[25]
		self.facegroup_index   =  -1

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

def get_lump(lump, lumps, file):
	file.seek(lumps[lump.entry].offset)
	data = file.read(lumps[lump.entry].length)
	return lump.unpack(data)

def tesselate_grid(grid, widh, height, level):
	collumns   = []
	rows       = []
	# Create collums
	for i in range(0, widh):
		col = []
		collumns.append(col)
	# Interpolate collumns
	for i in range(0, level+1):
		factor = float(i) / float(level)
		for j in range(0, widh):
			for k in range(1, height-1):
				collumns[j].append(grid[j][k-1].interpolate(grid[j][k], grid[j][k+1], factor))
	# Create rows
	for i in range(0, level+1):
		row = []
		rows.append(row)
	# Interpolate rows
	for i in range(0, level+1):
		factor = float(i) / float(level)
		# There is  level+1 rows
		for j in range(0, level+1):
			for k in range(1, widh-1):
				rows[j].append(collumns[k-1][j].interpolate(collumns[k][j], collumns[k+1][j], factor))
	return rows




def loadObj(fileName):
	# Open file and read header
	bsp_file = open(fileName, 'rb')
	data = bsp_file.read(8)
	header = unpack('<4ci', data)
	magic  = ""
	for i in range(0, 4): magic += header[i]
	version = header[4]
	# Magic should be IBSP and version 46. Else your file is not a quake 3 bsp level !
	if magic != "IBSP" or version != 46:
		print "magic =", magic
		print "version =", version
		print "This is not a Quake 3 BSP level !"
		return None
	# Read lump entry
	data = bsp_file.read(Q3BSPLumpEntry.size * NB_BSP_LUMPS)
	lumps = Q3BSPLumpEntry.unpack(data)
	# Read all lumps
	entities    = get_lump(Q3BSPEntitie, lumps, bsp_file)
	textures    = get_lump(Q3BSPTexture, lumps, bsp_file)
	planes      = get_lump(Q3BSPPlane, lumps, bsp_file)
	nodes       = get_lump(Q3BSPNode, lumps, bsp_file)
	leafs       = get_lump(Q3BSPLeaf, lumps, bsp_file)
	leaffaces   = get_lump(Q3BSPLeafFace, lumps, bsp_file)
	leafbrushes = get_lump(Q3BSPLeafBrush, lumps, bsp_file)
	models      = get_lump(Q3BSPModel, lumps, bsp_file)
	brushes     = get_lump(Q3BSPBrush, lumps, bsp_file)
	brushsides  = get_lump(Q3BSPBrushSide, lumps, bsp_file)
	vertexs     = get_lump(Q3BSPVertex, lumps, bsp_file)
	indices     = get_lump(Q3BSPIndice, lumps, bsp_file)
	facegroups  = get_lump(Q3BSPFaceGroup, lumps, bsp_file)
	lightmaps   = get_lump(Q3BSPLightmap, lumps, bsp_file)
	lightvols   = get_lump(Q3BSPLightvol, lumps, bsp_file)
	visdata     = get_lump(Q3BSPVisData, lumps, bsp_file)
	# Don't need the file any more
	bsp_file.close()
	
	# Creat a soya world
	# We will put the whole level inside this world
	world = soya.World()
	# model_face_groups is a list of all face groups used in the model
	# It contains lists of faces
	model_face_groups = []
	# model_parts is a list of all parts used in the model
	# it contains lists of indexs in model_face_groups
	# some face groups can be in several model parts
	model_parts       = []
	# leaf2model_part
	leaf2model_part   = {}
	# Patch brush
	facegroup2patch_brush_index = {}
	
	# Process every brush
	# A brush is a list of planes that creat a convex volume used for collision detection
	# Here we collect the planes of the brush
	for brush in brushes:
		# Get brush planes indices
		brush.plane_indices = []
		brush_sides = brushsides[brush.brush_side_start : brush.brush_side_start+brush.nb_brush_side]
		for brushside in brush_sides:
			brush.plane_indices.append(brushside.plane)
	
	# Creat all faces
	# A Quake face is actually a group of faces
	# Every face is a triangle
	# Every face in a facegroup have the same texture
	for facegroup in facegroups:
		model_face_group = []
		# Retriving materials
		material = soya.Material()
		texname  = textures[facegroup.texture].name
		try:
			material.texture = soya.Image.get(texname + ".png")
		except ValueError:
			print "impossible to use texture", texname
			return None
		
		# If the facegroup is a polygon or mesh
		if facegroup.face_type == 1 or facegroup.face_type == 3:
			bsp_indices = indices[facegroup.indices_start:facegroup.indices_start+facegroup.nb_indices]
			if len(bsp_indices) % 3 != 0:
				print "ERROR face num vertices not a multiple of 3 !!!"
				return None
			for i in range(0, len(bsp_indices), 3):
				f = soya.Face(world)
				f.material = material
				bsp_vertices = []
				bsp_vertices.append(vertexs[facegroup.vertex_start+bsp_indices[i].indice])
				bsp_vertices.append(vertexs[facegroup.vertex_start+bsp_indices[i+2].indice])
				bsp_vertices.append(vertexs[facegroup.vertex_start+bsp_indices[i+1].indice])
				for vertex in bsp_vertices:
					v = soya.Vertex(world, vertex.x, vertex.y, vertex.z)
					v.tex_x = vertex.texture_x
					v.tex_y = vertex.texture_y
					f.append(v)
				model_face_group.append(f)
		
		# If the facegroup is a Bezier path
		elif facegroup.face_type == 2:
			# A patch is composed of several 3x3 control grids
			# We need to get all the control points
			patch_width    =  facegroup.patch_size_x
			patch_height   =  facegroup.patch_size_y
			nb_grib_width  = (facegroup.patch_size_x-1) / 2
			nb_grid_height = (facegroup.patch_size_y-1) / 2
			# Get control points
			control_points = []
			for i in range(0, (patch_width * patch_height)):
				control_points.append(vertexs[facegroup.vertex_start + i])
			# Build Grid
			grid = []
			for i in range(0, patch_width):
				col = []
				grid.append(col)
				for j in range(0, patch_height):
					col.append(control_points[i*patch_width + j])
			# Subdivide grid
			tesselated_grid = tesselate_grid(grid, patch_width, patch_height, TESSELATE_LEVEL)
			# Make faces from grid
			for i in range(0, nb_grib_width*TESSELATE_LEVEL):
				for j in range(0, nb_grid_height*TESSELATE_LEVEL):
					# Use every square of the grid to make two triangle faces
					# First triangle
					f = soya.Face(world)
					f.material = material
					v = soya.Vertex(world, tesselated_grid[i][j].x, tesselated_grid[i][j].y, tesselated_grid[i][j].z)
					v.tex_x = tesselated_grid[i][j].texture_x
					v.tex_y = tesselated_grid[i][j].texture_y
					f.append(v)
					v = soya.Vertex(world, tesselated_grid[i+1][j].x, tesselated_grid[i+1][j].y, tesselated_grid[i+1][j].z)
					v.tex_x = tesselated_grid[i+1][j].texture_x
					v.tex_y = tesselated_grid[i+1][j].texture_y
					f.append(v)
					v = soya.Vertex(world, tesselated_grid[i+1][j+1].x, tesselated_grid[i+1][j+1].y, tesselated_grid[i+1][j+1].z)
					v.tex_x = tesselated_grid[i+1][j+1].texture_x
					v.tex_y = tesselated_grid[i+1][j+1].texture_y
					f.append(v)
					model_face_group.append(f)
					# Second triangle
					f = soya.Face(world)
					f.material = material
					v = soya.Vertex(world, tesselated_grid[i+1][j+1].x, tesselated_grid[i+1][j+1].y, tesselated_grid[i+1][j+1].z)
					v.tex_x = tesselated_grid[i+1][j+1].texture_x
					v.tex_y = tesselated_grid[i+1][j+1].texture_y
					f.append(v)
					v = soya.Vertex(world, tesselated_grid[i][j+1].x, tesselated_grid[i][j+1].y, tesselated_grid[i][j+1].z)
					v.tex_x = tesselated_grid[i][j+1].texture_x
					v.tex_y = tesselated_grid[i][j+1].texture_y
					f.append(v)
					v = soya.Vertex(world, tesselated_grid[i][j].x, tesselated_grid[i][j].y, tesselated_grid[i][j].z)
					v.tex_x = tesselated_grid[i][j].texture_x
					v.tex_y = tesselated_grid[i][j].texture_y
					f.append(v)
					model_face_group.append(f)
			
			# Make patch brush from grid if patch is solid
			#if textures[facegroup.texture].contents & CONTENT_SOLID:
				#triangle_list = []
				## Subdivide grid again but with lower tesselation level
				#tesselated_grid = tesselate_grid(grid, patch_width, patch_height, SHELL_TESSELATE_LEVEL)
				## Make triangle from grid
				#for i in range(0, nb_grib_width*SHELL_TESSELATE_LEVEL):
					#for j in range(0, nb_grid_height*SHELL_TESSELATE_LEVEL):
						## Use every square of the grid to make two triangle
						## First triangle
						#tri = soya.PatchShellTriangle()
						#tri.right = soya.Point(world, x = tesselated_grid[i][j].x,     y = tesselated_grid[i][j].y,     z = tesselated_grid[i][j].z)
						#tri.apex  = soya.Point(world, x = tesselated_grid[i+1][j].x,   y = tesselated_grid[i+1][j].y,   z = tesselated_grid[i+1][j].z)
						#tri.left  = soya.Point(world, x = tesselated_grid[i+1][j+1].x, y = tesselated_grid[i+1][j+1].y, z = tesselated_grid[i+1][j+1].z)
						#triangle_list.append(tri)
						## Second triangle
						#tri = soya.PatchShellTriangle()
						#tri.right = soya.Point(world, x = tesselated_grid[i+1][j+1].x, y = tesselated_grid[i+1][j+1].y, z = tesselated_grid[i+1][j+1].z)
						#tri.apex  = soya.Point(world, x = tesselated_grid[i][j+1].x,   y = tesselated_grid[i][j+1].y,   z = tesselated_grid[i][j+1].z)
						#tri.left  = soya.Point(world, x = tesselated_grid[i][j].x,     y = tesselated_grid[i][j].y,     z = tesselated_grid[i][j].z)
						## Set triangles neighbors
						#triangle_list[-1].base_neighbor = tri
						#tri.base_neighbor = triangle_list[-1]
						#if j > 0:
							#triangle_list[-1].right_neighbor = triangle_list[-2]
							#triangle_list[-2].right_neighbor = triangle_list[-1]
						#if i > 0:
							#tri.left_neighbor = triangle_list[-((nb_grid_height*SHELL_TESSELATE_LEVEL*2)+1)]
							#triangle_list[-((nb_grid_height*SHELL_TESSELATE_LEVEL*2)+1)].left_neighbor = tri
						#triangle_list.append(tri)
				#patch_brush = Q3BSPBrush((0, 0, textures[facegroup.texture]))
				#patch_brush.triangle_list = triangle_list
				#brushes.append(patch_brush)
				#facegroup2patch_brush_index[facegroup] = brushes.index(patch_brush)
		model_face_groups.append(model_face_group)
		facegroup.facegroup_index = model_face_groups.index(model_face_group)
	
	# Process brushes in leafs
	for leaf in leafs:
		# Zero sized leaf, door or moving plateform
		if leaf.box_min_x == 0 and leaf.box_max_x == 0:
			continue
		# Leaf without brush
		if leaf.nb_leaf_brush == 0:
			continue
		# Add normal brush indices to leaf's brush list
		# Patch brush will be added when processing facegroups in leaf
		leaf_leafbrushes = leafbrushes[leaf.leaf_brush_start : leaf.leaf_brush_start+leaf.nb_leaf_brush]
		for leafbrush in leaf_leafbrushes:
			if brushes[leafbrush.brush].nb_brush_side > 0 and (textures[brushes[leafbrush.brush].texture].contents & CONTENT_SOLID):
				leaf.brush_indices.append(leafbrush.brush)
	
	# Process every cluster
	# A cluster is a visible leaf (a leaf with faces inside)
	# Those cluster will be the parts of our splited model
	for leaf in leafs:
		# Discarde leaf wich are not cluster
		# Invalid leaf, outside the level or inside a wall
		if leaf.cluster == -1:
			continue
		# Zero sized leaf, door or moving plateform
		if leaf.box_min_x == 0 and leaf.box_max_x == 0:
			continue
		# Leaf without faces
		if leaf.nb_leaf_face == 0:
			continue
		# Get a list of all facegroups in that leaf
		# Discare billboard faces (not implemented) and bad patchs (craps in bsp flies)
		# BSP files use some kind of facegroup pointer called leaffaces
		leaf_leaffaces  = leaffaces[leaf.leaf_face_start:leaf.leaf_face_start+leaf.nb_leaf_face]
		leaf_facegroups = []
		for leafface in leaf_leaffaces:
			if facegroups[leafface.face].face_type == 4:
				continue
			if facegroups[leafface.face].face_type == 2 and (facegroups[leafface.face].nb_vertex <= 0 or facegroups[leafface.face].patch_size_x <= 0):
				continue
			leaf_facegroups.append(facegroups[leafface.face])
			# If there is a patch brush for this facegroup
			if facegroup2patch_brush_index.has_key(facegroups[leafface.face]):
				leaf.brush_indices.append(facegroup2patch_brush_index[facegroups[leafface.face]])
		
		# Creat the model part corresponding to the leaf
		# The model part is a list contaning every facegroups of the leaf
		model_part = []
		for facegroup in leaf_facegroups: model_part.append(facegroup.facegroup_index)
		model_parts.append(model_part)
		# This dict will be used when creaing the BSP world
		#leaf2model_part[leaf] = model_parts.index(model_part)
		leaf.model_part = model_parts.index(model_part)
	
	
	
	# Creat a splited model from our world
	splited_model = soya.SplitedModel(world, model_face_groups, model_parts, 80., 0, None)
	del(world)
	
	# Creat the corresponding BSP world and save it
	bsp_world = soya.BSPWorld(splited_model, nodes, leafs, planes, brushes, visdata)
	return bsp_world

