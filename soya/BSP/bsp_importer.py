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
import soya.widget as widget

SCALE_FACTOR = 0.1
TESSELATE_LEVEL = 5
SPEED = 10.

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
		self.plane_indices    = []

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

class BSPGeomBox(object):
	def __init__(self, cluster, center_x, center_y, center_z, length_x, length_y, length_z, base_x, base_y, base_z):
		self.cluster = cluster
		self.x       = center_x
		self.y       = center_y
		self.z       = center_z
		self.lx      = length_x
		self.ly      = length_y
		self.lz      = length_z
		self.base_x  = base_x
		self.base_y  = base_y
		self.base_z  = base_z

def get_lump(lump):
	bsp_file.seek(lumps[lump.entry].offset)
	data = bsp_file.read(lumps[lump.entry].length)
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

def point_from_3_planes(p1, p2, p3):
	denom = p1.normal.dot_product(p2.normal.cross_product(p3.normal))
	print "pp", p1.d
	p = (p2.normal.cross_product(p3.normal))*p1.d + \
			(p3.normal.cross_product(p1.normal))*p2.d + \
			(p1.normal.cross_product(p2.normal))*p3.d
	return p

def brush_is_cube(brush_planes):
	if len(brush_planes) == 6:
		for i in range(1, 6):
			angle = planes[brush_planes[0]].normal.angle_to(planes[brush_planes[i]].normal)
			if not ((angle > 89. and angle < 91.) or (angle > 179. and angle < 181.)):
				return False
		else:
			return True
	return False

class moving_camera(soya.Camera):
	def __init__(self, parent):
		soya.Camera.__init__(self, parent)
		self.speed            = soya.Vector(self, 0.0, 0.0, 0.0)
		self.rotation_y_speed = 0.0
	
	def begin_round(self):
		soya.Camera.begin_round(self)
		for event in soya.process_event():
			if event[0] == soya.sdlconst.KEYDOWN:
				if   event[1] == soya.sdlconst.K_UP:     self.speed.z = -SPEED
				elif event[1] == soya.sdlconst.K_DOWN:   self.speed.z =  SPEED
				elif event[1] == soya.sdlconst.K_a:      self.speed.y =  SPEED
				elif event[1] == soya.sdlconst.K_q:      self.speed.y =  -SPEED
				elif event[1] == soya.sdlconst.K_LEFT:   self.rotation_y_speed =  3.0
				elif event[1] == soya.sdlconst.K_RIGHT:  self.rotation_y_speed = -3.0
				elif event[1] == soya.sdlconst.K_ESCAPE: soya.MAIN_LOOP.stop()
				elif event[1] == soya.sdlconst.K_o:      self.parent.enable_area_visibility(0, 1)
				elif event[1] == soya.sdlconst.K_i:      self.parent.disable_area_visibility(0, 1)
			elif event[0] == soya.sdlconst.KEYUP:
				if   event[1] == soya.sdlconst.K_UP:     self.speed.z = 0.0
				elif event[1] == soya.sdlconst.K_DOWN:   self.speed.z = 0.0
				elif event[1] == soya.sdlconst.K_a:      self.speed.y =  0.
				elif event[1] == soya.sdlconst.K_q:      self.speed.y =  0.
				elif event[1] == soya.sdlconst.K_LEFT:   self.rotation_y_speed = 0.0
				elif event[1] == soya.sdlconst.K_RIGHT:  self.rotation_y_speed = 0.0
			elif event[0] == soya.sdlconst.QUIT:
				soya.MAIN_LOOP.stop()
		
	def advance_time(self, proportion):
		soya.Camera.advance_time(self, proportion)
		self.add_mul_vector(proportion, self.speed)
		self.rotate_y(proportion * self.rotation_y_speed)








# Open file and read header
bsp_file = open('demo.bsp', 'rb')
data = bsp_file.read(8)
header = unpack('<4ci', data)
magic  = ""
for i in range(0, 4): magic += header[i]
version = header[4]
# Magic should be IBSP and version 46. Else your file is not a quake 3 bsp level !
print "magic =", magic
print "version =", version
if magic != "IBSP" or version != 46:
	print "This is not a Quake 3 BSP level !"
	sys.exit()

# Read lump entry
data = bsp_file.read(Q3BSPLumpEntry.size * NB_BSP_LUMPS)
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
facegroups  = get_lump(Q3BSPFaceGroup)
lightmaps   = get_lump(Q3BSPLightmap)
lightvols   = get_lump(Q3BSPLightvol)
visdata     = get_lump(Q3BSPVisData)

# Don't need the file any more
bsp_file.close()

# An attempt to use ODE in BSPWorld
"""
for leaf in leafs:
	#if leaf.cluster < 0:
	#	continue
	#leaf_brushs = brushes[leaf.leaf_brush_start : leaf.leaf_brush_start+leaf.nb_leaf_brush]
	#print len(leaf_brushs), "brushs in leaf"
	leaf_brush_indices = range(leaf.leaf_brush_start, leaf.leaf_brush_start+leaf.nb_leaf_brush)
	print len(leaf_brush_indices), "brushs in leaf"
	for i in leaf_brush_indices:
		for leaf2 in leafs:
			if leaf2 == leaf:
				continue
			leaf_brush_indices2 = range(leaf2.leaf_brush_start, leaf2.leaf_brush_start+leaf2.nb_leaf_brush)
			if i in leaf_brush_indices2:
				print "brush", i, "from leaf", leafs.index(leaf), "also in leaf", leafs.index(leaf2)

sys.exit()
"""
"""
bsp_geoms = []
for leaf in leafs:
	# Get ride of invalid leaf
	if leaf.cluster < 0 or leaf.nb_leaf_brush <= 0:
		continue
	# Get brushes
	leaf_leafbrushes = leafbrushes[leaf.leaf_brush_start : leaf.leaf_brush_start+leaf.nb_leaf_brush]
	leaf_brushes     = []
	for leafbrush in leaf_leafbrushes:
		leaf_brushes.append(brushes[leafbrush])
	# Transform brushes into geoms
	for brush in leaf_brushes:
		# Get brush planes
		brush_sides = brushsides[brush.brush_side_start : brush.brush_side_start+brush.nb_brush_side]
		brush_planes = []
		for brushside in brush_sides:
			brush_planes.append(brushside.plane)
		# Test if brush is a box
		if brush_is_box(brush_planes):
			# Brush is a box, we will transform into an ODE box
			# Compute two opposed points of the box
			box_point1 = point_from_3_planes(planes[brush_planes[0]], planes[brush_planes[2]], planes[brush_planes[4]])
			box_point2 = point_from_3_planes(planes[brush_planes[1]], planes[brush_planes[3]], planes[brush_planes[5]])
			# Compute box dimensions and position
			length_x = abs(box_point1.x - box_point2.x)
			length_y = abs(box_point1.y - box_point2.y)
			length_z = abs(box_point1.z - box_point2.z)
			if box_point1.x < box_point2.x: center_x = box_point1.x + length_x/2.
			else:                           center_x = box_point2.x + length_x/2.
			if box_point1.y < box_point2.y: center_y = box_point1.y + length_y/2.
			else:                           center_y = box_point2.y + length_y/2.
			if box_point1.z < box_point2.z: center_z = box_point1.z + length_z/2.
			else:                           center_z = box_point2.z + length_z/2.
			# Get box base vectors, used to compute box rotation matrix
			vect_x = planes[brush_planes[1]].normal
			vect_y = planes[brush_planes[5]].normal
			vect_z = planes[brush_planes[3]].normal
			# Creat box geom
			bsp_geoms.append(BSPGeomBox(center_x, center_y, center_z, \
																	length_x, length_y, length_z, \
																	vect_x, vect_y, vect_z))
		else:
			# Brush is not a box, we will transform into an ODE trimesh
			pass
"""

soya.path.append(os.path.join(os.path.dirname(sys.argv[0]), "../tutorial/data"))

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

# Creat all faces
# A Quake face is actually a group of faces
# Every face is a triangle
# Every face in a facegroup have the same texture
for facegroup in facegroups:
	model_face_group = []
	# Retriving materials
	material   = soya.Material()
	file_index = textures[facegroup.texture].name.rfind('/')
	directory  = textures[facegroup.texture].name[0:file_index]
	texname    = textures[facegroup.texture].name[file_index+1:]
	try:
		material.texture = soya.Image.get(texname + ".png")
	except ValueError:
		print "impossible to use texture", texname
	
	# If the facegroup is a polygon or mesh
	if facegroup.face_type == 1 or facegroup.face_type == 3:
		bsp_indices = indices[facegroup.indices_start:facegroup.indices_start+facegroup.nb_indices]
		if len(bsp_indices) % 3 != 0:
			print "ERROR face num vertices not a multiple of 3 !!!"
			sys.exit()
		
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
						if l % 2:
							v = soya.Vertex(world,  bsp_vertexs[bsp_indices[(k*triangle_per_row)+l]].x, \
																			bsp_vertexs[bsp_indices[(k*triangle_per_row)+l]].y, \
																			bsp_vertexs[bsp_indices[(k*triangle_per_row)+l]].z)
							v.tex_x = bsp_vertexs[bsp_indices[(k*triangle_per_row)+l]].texture_x
							v.tex_y = bsp_vertexs[bsp_indices[(k*triangle_per_row)+l]].texture_y
							f.append(v)
							v = soya.Vertex(world,  bsp_vertexs[bsp_indices[(k*triangle_per_row)+l-1]].x, \
																			bsp_vertexs[bsp_indices[(k*triangle_per_row)+l-1]].y, \
																			bsp_vertexs[bsp_indices[(k*triangle_per_row)+l-1]].z)
							v.tex_x = bsp_vertexs[bsp_indices[(k*triangle_per_row)+l-1]].texture_x
							v.tex_y = bsp_vertexs[bsp_indices[(k*triangle_per_row)+l-1]].texture_y
							f.append(v)
							v = soya.Vertex(world,  bsp_vertexs[bsp_indices[(k*triangle_per_row)+l-2]].x, \
																			bsp_vertexs[bsp_indices[(k*triangle_per_row)+l-2]].y, \
																			bsp_vertexs[bsp_indices[(k*triangle_per_row)+l-2]].z)
							v.tex_x = bsp_vertexs[bsp_indices[(k*triangle_per_row)+l-2]].texture_x
							v.tex_y = bsp_vertexs[bsp_indices[(k*triangle_per_row)+l-2]].texture_y
						else:
							v = soya.Vertex(world,  bsp_vertexs[bsp_indices[(k*triangle_per_row)+l-2]].x, \
																			bsp_vertexs[bsp_indices[(k*triangle_per_row)+l-2]].y, \
																			bsp_vertexs[bsp_indices[(k*triangle_per_row)+l-2]].z)
							v.tex_x = bsp_vertexs[bsp_indices[(k*triangle_per_row)+l-2]].texture_x
							v.tex_y = bsp_vertexs[bsp_indices[(k*triangle_per_row)+l-2]].texture_y
							f.append(v)
							v = soya.Vertex(world,  bsp_vertexs[bsp_indices[(k*triangle_per_row)+l-1]].x, \
																			bsp_vertexs[bsp_indices[(k*triangle_per_row)+l-1]].y, \
																			bsp_vertexs[bsp_indices[(k*triangle_per_row)+l-1]].z)
							v.tex_x = bsp_vertexs[bsp_indices[(k*triangle_per_row)+l-1]].texture_x
							v.tex_y = bsp_vertexs[bsp_indices[(k*triangle_per_row)+l-1]].texture_y
							f.append(v)
							v = soya.Vertex(world,  bsp_vertexs[bsp_indices[(k*triangle_per_row)+l]].x, \
																			bsp_vertexs[bsp_indices[(k*triangle_per_row)+l]].y, \
																			bsp_vertexs[bsp_indices[(k*triangle_per_row)+l]].z)
							v.tex_x = bsp_vertexs[bsp_indices[(k*triangle_per_row)+l]].texture_x
							v.tex_y = bsp_vertexs[bsp_indices[(k*triangle_per_row)+l]].texture_y
						f.append(v)
						model_face_group.append(f)
	model_face_groups.append(model_face_group)
	facegroup.facegroup_index = model_face_groups.index(model_face_group)

# Process every brush
# A brush is a list of planes that creat a convex volume
# Used for raypicking
for brush in brushes:
	# Get brush planes
	brush_sides = brushsides[brush.brush_side_start : brush.brush_side_start+brush.nb_brush_side]
	for brushside in brush_sides:
		brush.plane_indices.append(brushside.plane)

# Process brushes in leafs
for leaf in leafs:
	# Discarde leaf wich are not cluster
	# Invalid leaf, outside the level or inside a wall
	#if leaf.cluster == -1:
	#	continue
	# Zero sized leaf, door or moving plateform
	if leaf.box_min_x == 0 and leaf.box_max_x == 0:
		continue
	# Leaf without brush
	if leaf.nb_leaf_brush == 0:
		continue
	leaf_leafbrushes = leafbrushes[leaf.leaf_brush_start : leaf.leaf_brush_start+leaf.nb_leaf_brush]
	for leafbrush in leaf_leafbrushes:
		if brushes[leafbrush.brush].nb_brush_side > 0 and (textures[brushes[leafbrush.brush].texture].contents & 1):
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
		if facegroups[leafface.face].face_type == 4: continue
		if facegroups[leafface.face].face_type == 2 and (facegroups[leafface.face].nb_vertex <= 0 or facegroups[leafface.face].patch_size_x <= 0): continue
		leaf_facegroups.append(facegroups[leafface.face])
	
	# Creat the model part corresponding to the leaf
	# The model part is a list contaning every facegroups of the leaf
	model_part = []
	for facegroup in leaf_facegroups: model_part.append(facegroup.facegroup_index)
	model_parts.append(model_part)
	# This dict will be used when creaing the BSP world
	#leaf2model_part[leaf] = model_parts.index(model_part)
	leaf.model_part = model_parts.index(model_part)

# Creat a splited model from our world
print "creating optimised splited model"
print "this can take up to 10 minutes on a recent computer so be patient :)"
splited_model = soya.SplitedModel(world, model_face_groups, model_parts, 80., 0, None)
del(world)
print "creating BSP World"

# Creat the corresponding BSP world and save it
bsp_world = soya.BSPWorld(splited_model, nodes, leafs, planes, brushes, visdata)
bsp_world.filename = "imported_bsp_world"
bsp_world.save()

print "BSP World file saved"

for ent in entities:
	index = ent.find("info_player_deathmatch")
	if index >= 0:
		index += 34
		index2 = ent.find('"', index)
		start_point = ent[index:index2].split()
		start_x =  float(start_point[0])
		start_y =  float(start_point[2])
		start_z = -float(start_point[1])
		print "Found start point at", start_x, start_y, start_z
		break
else:
	print "No start point found, will start at 0, 0, 0"
	start_x = 0
	start_y = 0
	start_z = 0

# Display the imported BSP World
soya.init()
scene = soya.World()
scene.add(bsp_world)
atmosphere = soya.SkyAtmosphere()
atmosphere.ambient = (0.9, 0.9, 0.9, 1.0)
scene.atmosphere = atmosphere

#sword_model = soya.Shape.get("sword")
#sword = soya.Body(bsp_world, sword_model)
#sword.set_xyz(start_x, start_y, start_z)


# Creates a camera in the scene
camera = moving_camera(bsp_world)
camera.set_xyz(start_x, start_y, start_z)
camera.back = 1500.

# Creates a widget group, containing the camera and a label showing the FPS.
soya.set_root_widget(widget.Group())
soya.root_widget.add(camera)
soya.root_widget.add(widget.FPSLabel())

print "Use arrow keys to move, A and Q to move up and down"
print "Use key 0 and I to enable/disable visibility of area 0 and 1"

soya.MainLoop(scene).main_loop()
