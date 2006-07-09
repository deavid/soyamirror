# -*- indent-tabs-mode: t -*-

# Copyright (C) 2003-2006 Jean-Baptiste LAMY -- jibalamy@free.fr
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


# export blender model to soya
# this file is understood to be executed directly by Soya,
# NOT manually (see blender2soya.py for that)

import sys, os, os.path, string
import Blender
	
# Default values :
PATH                  = os.path.join(os.path.dirname(Blender.Get("filename")), "..")
FILENAME              = os.path.splitext(os.path.basename(Blender.Get("filename")))[0]
KEEP_POINTS_AND_LINES = 0

# Make current the animation of the given name, at the given time / key.
# Usefull for batch mode.
ANIMATION         = ""
ANIMATION_TIME    = 0.0

# Use this dictionary if you want to change some materials
MATERIALS_MAP = {
#  "old_material_name" : "new_material_name",
	}

# Set to 1 for enabling shadows
SHADOW = 0

CELLSHADING = 0
CELLSHADING_SHADER = ""
CELLSHADING_OUTLINE_COLOR = (0.0, 0.0, 0.0, 1.0)
CELLSHADING_OUTLINE_WIDTH = 4.0
CELLSHADING_OUTLINE_ATTENUATION = 0.3

# Scale the whole model
SCALE = 1.0

# The maximum angle between two smooth-lit faces.
MAX_FACE_ANGLE = 80.0

# File format (currently, "pickle" or "cerealizer")
FILE_FORMAT = "pickle"

TMP_FILE = ""

PARAMS_NAMES = [attr for attr in globals().keys() if (attr[0] in string.uppercase) and (attr[1] in string.uppercase)]

def pointbymatrix(p, m):
	return [p[0] * m[0][0] + p[1] * m[1][0] + p[2] * m[2][0] + m[3][0],
					p[0] * m[0][1] + p[1] * m[1][1] + p[2] * m[2][1] + m[3][1],
					p[0] * m[0][2] + p[1] * m[1][2] + p[2] * m[2][2] + m[3][2]]

class Blender2Soya:
	def __init__(self, args):
		self.parse_global_args()
		
		try: self.parse_args(Blender.Text.get("soya_params").asLines())
		except: pass
		
		self.parse_args(args)
		
		self.f = open(self.tmp_file, "w")
		
	def parse_global_args(self):
		for param in PARAMS_NAMES:
			setattr(self, param.lower(), globals()[param])
			
	def parse_args(self, args):
		for arg in args:
			if "=" in arg:
				attr, val = arg.split("=")
				attr = attr.lower()
				try: val = int(val)
				except:
					try: val = float(val)
					except: pass
					
				print attr, val
				if attr.startswith("material_"): # A material map
					self.materials_map[attr[9:]] = val
					
				elif attr == "config_text": # Config text
					print >> sys.stderr, "(reading config text %s)" % val
					self.parse_args(Blender.Text.get(val).asLines())
					
				elif attr == "config_file": # Config file
					print >> sys.stderr, "(reading config file %s)" % val
					self.parse_args(open(var).read().split("\n"))
					
				else: setattr(self, attr, val)
					
	def export(self):
		Blender.Redraw() # Needed for GetRawFromObject

		print >> self.f, """import soya, soya.facecutter"""
		
		if   self.file_format == "pickle":
			print >> self.f, """import cPickle as pickle; soya.set_file_format(pickle)"""
		elif self.file_format == "cerealizer":
			print >> self.f, """import cerealizer, soya.cerealizer4soya as cerealizer4soya; soya.set_file_format(cerealizer)"""
		else:
			raise ValueError("Unsupported file format %s" % self.file_format)
		print >> self.f
		
		objs = Blender.Object.Get()
		
		if self.animation:
			for obj in objs:
				data = obj.getData()
				if (type(data) is Blender.Types.ArmatureType):
					scene     = Blender.Scene.getCurrent()
					armature  = obj
					animation = Blender.Armature.NLA.GetActions()[self.animation]
					
					animation.setActive(armature)

					scene.getRenderingContext().currentFrame(int(self.animation_time))
					scene.makeCurrent()
			
			
		materials           = []
		already_warned      = []
		nb_points_and_lines = 0
		
		print >> self.f, """soya.path.insert(0, '%s') # insert at index 0 => save in this path.""" % os.path.abspath(self.path)
		print >> self.f, """root_world = soya.World()"""
		print >> self.f, """root_world.filename = '%s'""" % self.filename
		print >> self.f
		
		for obj in objs:
			data = obj.getData()
			if (type(data) is Blender.Types.NMeshType) and data.faces:
				nmesh = Blender.NMesh.GetRawFromObject(obj.getName())
				
				matrix = [[obj.mat[0][0], obj.mat[0][1], obj.mat[0][2], obj.mat[0][3]],
									[obj.mat[1][0], obj.mat[1][1], obj.mat[1][2], obj.mat[1][3]],
									[obj.mat[2][0], obj.mat[2][1], obj.mat[2][2], obj.mat[2][3]],
									[obj.mat[3][0], obj.mat[3][1], obj.mat[3][2], obj.mat[3][3]]]
				
				for face in nmesh.faces:
					if (not self.keep_points_and_lines) and (len(face.v) <= 2):
						nb_points_and_lines += 1
						continue

					print >> self.f, """f = soya.Face(root_world)"""
					
					# face option
					if(face.smooth != 0):                            print >> self.f, """f.smooth_lit = 1"""
					if(face.mode & Blender.NMesh.FaceModes.TWOSIDE): print >> self.f, """f.double_sided = 1"""
						
					# vertices
					index = 0
					for vertex in face.v:
						# vertex coordinates
						co = pointbymatrix(vertex.co, matrix)
						print >> self.f, """v = soya.Vertex(root_world, %s, %s, %s)""" % (co[0], co[1], co[2])
					
						# vertex color
						if (face.col != None) and (len(face.col) > 0):
							color = face.col[index]
							print >> self.f, """v.color = (%s, %s, %s, %s)""" % (color.r / 255.0, color.g / 255.0, color.b / 255.0, color.a / 255.0)
							
						# vertex texture coordinates
						if len(face.uv) > 0:
							uv = face.uv[index]
							print >> self.f, """v.tex_x, v.tex_y = %s, %s""" % (uv[0], 1.0 - uv[1])
							
						print >> self.f, """f.append(v)"""
						index = index + 1
						
					# material
					if(face.image != None):
						image_filename    = face.image.name
						if "." in image_filename:
							material_filename = image_filename[:image_filename.rfind(".")]
						material_filename = self.materials_map.get(material_filename, material_filename)
						print >> self.f, """f.material = soya.Material.get('%s')""" % material_filename
						print >> self.f
						
						
		if nb_points_and_lines:
			print >> sys.stderr, "blender2soya.py: removing %s points and lines..." % nb_points_and_lines
			
		# Soya has different axis conventions  
		print >> self.f, """root_world.rotate_x(-90.0)"""
		
		# Ensure quad's vertices are coplanar, and split any bugous quads
		print >> self.f, """facecutter.check_quads(root_world)"""
		
		if self.scale != 1.0:
			print >> self.f, """root_world.scale(%s, %s, %s)""" % (self.scale, self.scale, self.scale)
			
		if self.cellshading:
			print >> self.f, """root_world.model_builder = soya.CellShadingModelBuilder(
				shader              = ('%s' and get_material('%s')) or None,
				outline_color       = %s,
				outline_width       = %s,
				outline_attenuation = %s,
)""" % (self.cellshading_shader, self.cellshading_shader, self.cellshading_outline_color, self.cellshading_outline_width, self.cellshading_outline_attenuation)
			
		if self.shadow:
			print >> self.f, """if not root_world.model_builder: root_world.model_builder = soya.SimpleModelBuilder()"""
			print >> self.f, """root_world.model_builder.shadow = 1"""
			
		if self.max_face_angle != 80.0:
			print >> self.f, """if not root_world.model_builder: root_world.model_builder = soya.SimpleModelBuilder()"""
			print >> self.f, """root_world.model_builder.max_face_angle = %s""" % self.max_face_angle
			
		print >> self.f
		print >> self.f, """root_world.save()"""
		

if "--blender2soya" in sys.argv: # Check for batch mode
	args = sys.argv[sys.argv.index("--blender2soya") + 1:]
	
	exporter = Blender2Soya(args)
	exporter.export()
	
	Blender.Quit()
