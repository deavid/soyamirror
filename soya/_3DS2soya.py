# -*- indent-tabs-mode: t -*-

#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 3DS Import
# Copyright (C) 2004 Thomas Paviot, Bob Holcomb
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

"""3ds2soya

This script is a 3DS exporter for Soya.

"""

import soya, soya.sdlconst
import sys, struct, string, types
from types import *
import os

######################################################
# Data Structures
######################################################

#Some of the chunks that we will see
#----- Primary Chunk, at the beginning of each file
PRIMARY=19789 #0x4D4D

#------ Mtextureain Chunks
OBJECTINFO=15677	#0x3D3D				// This gives the version of the mesh and is found right before the material and object information
VERSION=2			#0x0002				// This gives the version of the .3ds file
EDITKEYFRAME=45056	#0xB000				// This is the header for all of the key frame info

#------ sub defines of OBJECTINFO
MATERIAL=45055		#0xAFFF				// This stored the texture info
OBJECT=16384		#0x4000				// This stores the faces, vertices, etc...

#------ sub defines of MATERIAL
MATNAME=40960		#0xA000				// This holds the material name
MATAMBIENT=40976	#0xA010
MATDIFFUSE=40992	#0xA020				// This holds the color of the object/material
MATSPECULAR=41008	#0xA030
MATMAP=41472		#0xA200				// This is a header for a new material
MATMAPFILE=41728	#0xA300				// This holds the file name of the texture

OBJECT_MESH=16640	#0x4100				// This lets us know that we are reading a new object

#------ sub defines of OBJECT_MESH
OBJECT_VERTICES=16656	#0x4110			// The objects vertices
OBJECT_FACES=16672		#0x4120			// The objects faces
OBJECT_MATERIAL=16688	#0x4130			// This is found if the object has a material, either texture map or color
OBJECT_UV=16704			#0x4140			// The UV texture coordinates
OBJECT_TRANS_MATRIX=16736	#0x4160		// The translation matrix of the object 54 bytes

############################################################
# Mesh and Materialclass definition
############################################################
materials=[] #array of materials
meshes=[] #array of meshes
mat_index=0

class Mesh:        
	
	def __init__(self):
		self.world=soya.World()
		self.verts=[]
		self.faces=[]
		self.materials=[]
		self.name=""
		
		
class Material(soya.Material):
	def __init__(self):
		self.name=""
		
	def setName(self,name):
		self.name=name
		
class chunk:
	ID=0
	length=0
	bytes_read=0	
	binary_format="<HI"
	def __init__(self):
		self.ID=0
		self.length=0
		self.bytes_read=0

	def dump(self):
		print "ID: ", self.ID
		print "ID in hex: ", hex(self.ID)
		print "length: ", self.length
		print "bytes_read: ", self.bytes_read


def read_chunk(file, chunk):
	temp_data=file.read(struct.calcsize(chunk.binary_format))
	data=struct.unpack(chunk.binary_format, temp_data)
	chunk.ID=data[0]
	chunk.length=data[1]
	#update the bytes read function
	chunk.bytes_read=6

def read_string(file):
	s=""
	index=0
	
	temp_data=file.read(struct.calcsize("c"))
	data=struct.unpack("c", temp_data)
	s=s+(data[0])
	
	while(ord(s[index])!=0):
		index+=1
		temp_data=file.read(struct.calcsize("c"))
		data=struct.unpack("c", temp_data)
		s=s+(data[0])
	
	the_string=s[:-1]
	return str(the_string)


def process_next_object_chunk(file, previous_chunk, mesh):
	new_chunk=chunk()
	temp_chunk=chunk()

	while (previous_chunk.bytes_read<previous_chunk.length):		
		read_chunk(file, new_chunk)

		if (new_chunk.ID==OBJECT_MESH):			
			process_next_object_chunk(file, new_chunk, mesh)
			

		elif (new_chunk.ID==OBJECT_VERTICES):
			
			temp_data=file.read(struct.calcsize("H"))
			data=struct.unpack("H", temp_data)
			new_chunk.bytes_read+=2
			num_verts=data[0]
			
			for counter in range (0,num_verts):
				temp_data=file.read(struct.calcsize("3f"))
				new_chunk.bytes_read+=12 #3 floats x 4 bytes each
				data=struct.unpack("3f", temp_data)
				v=soya.Vertex(mesh.world,data[0],data[1],data[2])
				mesh.verts.append(v)
			
		elif (new_chunk.ID==OBJECT_FACES):
			
			temp_data=file.read(struct.calcsize("H"))
			data=struct.unpack("H", temp_data)
			new_chunk.bytes_read+=2
			num_faces=data[0]
			
												
			for counter in range(0,num_faces):
				
				temp_data=file.read(struct.calcsize("4H"))
				new_chunk.bytes_read+=8 #4 short ints x 2 bytes each
				data=struct.unpack("4H", temp_data)
						
				face=soya.Face(mesh.world,[mesh.verts[data[0]],mesh.verts[data[1]],mesh.verts[data[2]]])				
				face.double_sided=1
				mesh.faces.append(face)
			
		elif (new_chunk.ID==OBJECT_MATERIAL):			
			material_name=""
			material_name=str(read_string(file))
			new_chunk.bytes_read+=(len(material_name)+1)
			
			material_found=0
			for mat in materials:                                
				if(mat.name==material_name):
					if(len(mesh.materials)>=2):
						print "Cannot assign more than 2 materials to a mesh: Continue?%t|OK"
						break;
					else:						
						material_found=1
						for mat_index,material in enumerate(materials):
							if material.name == material_name:
								break
						break
							
				else:
					material_found=0
					
					
			if(material_found==1):
				#read the number of faces using this material
				temp_data=file.read(struct.calcsize("H"))
				data=struct.unpack("H", temp_data)
				new_chunk.bytes_read+=2
				num_faces_using_mat=data[0]
				
				for face_counter in range(0,num_faces_using_mat):
					temp_data=file.read(struct.calcsize("H"))
					new_chunk.bytes_read+=2
					data=struct.unpack("H", temp_data)					
					mesh.faces[data[0]].material=materials[mat_index]
					
			else:				
				
				buffer_size=new_chunk.length-new_chunk.bytes_read
				binary_format=str(buffer_size)+"c"
				temp_data=file.read(struct.calcsize(binary_format))
				new_chunk.bytes_read+=buffer_size


		elif (new_chunk.ID==OBJECT_UV):			
			temp_data=file.read(struct.calcsize("H"))
			data=struct.unpack("H", temp_data)
			new_chunk.bytes_read+=2
			num_uv=data[0]
			
			for counter in range(0,num_uv):
				temp_data=file.read(struct.calcsize("2f"))
				new_chunk.bytes_read+=8 #2 float x 4 bytes each
				data=struct.unpack("2f", temp_data)				
				mesh.verts[counter].tex_x=data[0]				
				mesh.verts[counter].tex_y=data[1]
			

		else:
			
			buffer_size=new_chunk.length-new_chunk.bytes_read
			binary_format=str(buffer_size)+"c"
			temp_data=file.read(struct.calcsize(binary_format))
			new_chunk.bytes_read+=buffer_size
			

		previous_chunk.bytes_read+=new_chunk.bytes_read
		

def process_next_material_chunk(file, previous_chunk, mat):
	new_chunk=chunk()
	temp_chunk=chunk()

	while (previous_chunk.bytes_read<previous_chunk.length):
		#read the next chunk
		read_chunk(file, new_chunk)

		if (new_chunk.ID==MATNAME):			
			material_name=""
			material_name=str(read_string(file))		
			new_chunk.bytes_read+=(len(material_name)+1)		
			mat.setName(material_name)
			

		elif (new_chunk.ID==MATAMBIENT):			
			read_chunk(file, temp_chunk)
			temp_data=file.read(struct.calcsize("3B"))
			data=struct.unpack("3B", temp_data)
			temp_chunk.bytes_read+=3
			r=data[0]
			g=data[1]
			b=data[2]			
			mat.emissive=(float(r)/255, float(g)/255, float(b)/255,1.0)
			#mat.shininess=128
			new_chunk.bytes_read+=temp_chunk.bytes_read

		elif (new_chunk.ID==MATDIFFUSE):			
			read_chunk(file, temp_chunk)
			temp_data=file.read(struct.calcsize("3B"))
			data=struct.unpack("3B", temp_data)
			temp_chunk.bytes_read+=3
			r=data[0]
			g=data[1]
			b=data[2]			
			mat.diffuse=(float(r)/255, float(g)/255, float(b)/255,1.0)
			new_chunk.bytes_read+=temp_chunk.bytes_read

		elif (new_chunk.ID==MATSPECULAR):			
			read_chunk(file, temp_chunk)
			temp_data=file.read(struct.calcsize("3B"))
			data=struct.unpack("3B", temp_data)
			temp_chunk.bytes_read+=3
			r=data[0]
			g=data[1]
			b=data[2]
			mat.specular=(float(r)/255, float(g)/255, float(b)/255,1.0)
			new_chunk.bytes_read+=temp_chunk.bytes_read

		elif (new_chunk.ID==MATMAP):						
			process_next_material_chunk(file, new_chunk, mat)

		elif (new_chunk.ID==MATMAPFILE):			
			texture_name=""
			texture_name=str(read_string(file))
			texture_f=os.path.join(soya.path[0],'images',texture_name)
			mat.texture = soya.open_image(texture_f)#name)
			new_chunk.bytes_read+=(len(texture_name)+1)

		else:			
			buffer_size=new_chunk.length-new_chunk.bytes_read
			binary_format=str(buffer_size)+"c"
			temp_data=file.read(struct.calcsize(binary_format))
			new_chunk.bytes_read+=buffer_size

		previous_chunk.bytes_read+=new_chunk.bytes_read


def process_next_chunk(file, previous_chunk):
	#a spare chunk
	new_chunk=chunk()
	temp_chunk=chunk()

	#loop through all the data for this chunk (previous chunk) and see what it is
	while (previous_chunk.bytes_read<previous_chunk.length):
		#read the next chunk
		#print "reading a chunk"
		read_chunk(file, new_chunk)

		#is it a Version chunk?
		if (new_chunk.ID==VERSION):
			#print "found a VERSION chunk"
			#print "version: lenght: ", new_chunk.length
			#read in the version of the file
			#it's an unsigned short (H)
			temp_data=file.read(struct.calcsize("I"))
			data=struct.unpack("I", temp_data)
			version=data[0]
			new_chunk.bytes_read+=4 #read the 4 bytes for the version number
			#this loader works with version 3 and below, but may not with 4 and above
			if (version>3):
				print "Non-Fatal Error:  Version greater than 3, may not load correctly: ", version

		#is it an object info chunk?
		elif (new_chunk.ID==OBJECTINFO):
			#print "found an OBJECTINFO chunk"
			#print "object info: lenght: ", new_chunk.length
			#recursively go through the rest of the file
			process_next_chunk(file, new_chunk)

			#keep track of how much we read in the main chunk
			new_chunk.bytes_read+=temp_chunk.bytes_read

		#is it an object chunk?
		elif (new_chunk.ID==OBJECT):			
			mesh=Mesh()			
			mesh.name=str(read_string(file))			
			meshes.append(mesh)
			#plus one for the null character that gets removed
			new_chunk.bytes_read+=(len(mesh.name)+1)

			process_next_object_chunk(file, new_chunk, mesh)
	

		#is it a material chunk?
		elif (new_chunk.ID==MATERIAL):
			#print "found a MATERIAL chunk"
			
			material=Material()#soya.Material()#Material.New()
			process_next_material_chunk(file, new_chunk, material)
			materials.append(material)
		else: #(new_chunk.ID!=VERSION or new_chunk.ID!=OBJECTINFO or new_chunk.ID!=OBJECT or new_chunk.ID!=MATERIAL):
			#print "skipping to end of this chunk"
			buffer_size=new_chunk.length-new_chunk.bytes_read
			binary_format=str(buffer_size)+"c"
			temp_data=file.read(struct.calcsize(binary_format))
			new_chunk.bytes_read+=buffer_size


		#update the previous chunk bytes read
		previous_chunk.bytes_read+=new_chunk.bytes_read
		#print "Bytes left in this chunk: ", previous_chunk.length-previous_chunk.bytes_read


def load_3ds (filename):
	current_chunk=chunk()	
	file=open(filename,"rb")	
	read_chunk(file, current_chunk)
	if (current_chunk.ID!=PRIMARY):
		print "Fatal Error:  Not a valid 3ds file: ", filename
		Exit()

	process_next_chunk(file, current_chunk)

	file.close()
	if len(meshes)==1:            
		return meshes[0].world
	else:            
		_3ds_world=soya.World()
		for elem in meshes:
			_3ds_world.add(elem.world)
		return _3ds_world
		
def makeWorld(Name):
	data_f=os.path.join(soya.path[0],'worlds',Name+'.data')
	_3ds_f=os.path.join(soya.path[0],'3ds',Name+'.3ds')
	haveToDoIt=False
	if os.path.exists(data_f):
		if os.path.exists(_3ds_f):
			if os.path.getmtime(_3ds_f)>os.path.getmtime(data_f):
				haveToDoIt=True     
	else:
		haveToDoIt=True
	if haveToDoIt:
		print "* Soya * Compiling 3ds file "+_3ds_f+" to Soya world..."
		o=load_3ds(_3ds_f)
		o.filename=Name
		o.save()

def getObj(Name):
	"""getObj(NAME) -> World

Imports a "{name}.3ds" file (from the "3ds" directory) and converts it into a Soya World."""
	makeWorld(Name)  
	return soya.World.get(Name)

def getModel(Name):
	"""getModel(NAME) -> World

Imports a "{name}.3ds" file (from the "3ds" directory) and converts it into a Soya Model."""
	makeWorld(Name)
	return soya.Model.get(Name)


if __name__=="__main__":     
	soya.path.append(os.path.join(os.path.dirname(sys.argv[0])))    
	try:
		_3ds_file=sys.argv[1]
		world=getObj(_3ds_file)
	except:
		print "Usage:\npython 3ds2soya.py yourfile\nWithout .3ds extension"
		sys.exit()
	camera=soya.Camera(world)
	camera.set_xyz(0.0, 0.0, 3.0)
	light = soya.Light(world)
	light.set_xyz(0.5, 1.0, 2.0)
	soya.set_root_widget(camera)    
	soya.init()
	soya.MainLoop(world).main_loop()

