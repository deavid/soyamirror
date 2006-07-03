# -*- indent-tabs-mode: t -*-

#!BPY

""" Registration info for Blender menus:
Name: 'Soya'
Blender: 235
Group: 'Export'
Tip: 'Export mesh data to a Soya World (then compilable to a Model).'
"""

__author__  = "Jean-Baptiste 'Jiba' Lamy"
__url__     = "Soya3d's homepage http://home.gna.org/oomadness/en/soya/"
__bpydoc__  = """blender2soya.py

			 This file must be executed from within blender
			 version 2.28 or above.  

			 To execute this script:
				 1. Switch a blender text editor type window inside blender
							This can done from the lower left corner of most blender windows
				 2. Load this file.
				 3. Press Alt-P
				 4. Fill in the required values
				 5. Press OK
"""

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

import sys, os, os.path
try: import Blender
except ImportError:
	print DESCRIPTION
	
# Default values :
PATH                  = os.path.join(os.path.dirname(Blender.Get("filename")), "..")
FILENAME              = os.path.splitext(os.path.basename(Blender.Get("filename")))[0]
KEEP_POINTS_AND_LINES = 0
LAUNCH_EDITOR         = 0

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



# Set this param to 0 is you want the script exports immediately, using the above default
# values, instead of showing a dialog box.
SHOW_DIALOG = 1


# File format (currently, "pickle" or "cerealizer")
FILE_FORMAT = "pickle"


# WARNING : there are some hack on this script since Blender python module
# is very few documented...
# (e.g. for vertices color)


try:
	import soya
except ImportError, e:
	sys.excepthook(*sys.exc_info())
	
	if "undefined symbol" in e:
		print """
ERROR: It seems that Soya is installed, but Blender is unable to load it.
This is a known bug with some version of Blender.
A work-around is to launch Blender as following:

  LD_PRELOAD=/usr/lib/libpython2.4.so.1.0 blender

(you may have to change /usr/lib/libpython2.4.so.1.0 according to your version of Python)
"""
		
	else:
		print """
ERROR: Cannot find Soya!
You need to install Soya!
"""
		print __bpydoc__
		#sys.exit()
	

import string
PARAMS_NAMES = [attr for attr in globals().keys() if (attr[0] in string.uppercase) and (attr[1] in string.uppercase)]


from Blender.BGL import * # Using Blenders modules this way is dangerous
from Blender.Draw import * # Both the Draw and Window Module have a Redraw
from Blender import Draw # method which are incompatable and using them this
from Blender.Window import * # way causes a name space collision.

import soya.facecutter as facecutter

# GUI Events
EVENT_NOEVENT     = 0
EVENT_OK          = 1
EVENT_CANCEL      = 2
EVENT_PATHCHANGE  = 3
EVENT_CHOOSE_PATH = 4

class BlenderDialog:
	"""Class which creates the blender GUI dialog boxes.
It passes the set values to an instance of 
blender2soya which is defined below"""
	def __init__(self):
		pass
	
	def draw(self):
		"""Generates the blender UI panel upon script execution."""
		global PATH
		
		glClear(GL_COLOR_BUFFER_BIT)
		
		glRasterPos2d(8, 230)
		Text("Blender2Soya Exporter")
		
		######### Parameters GUI Buttons
		glRasterPos2d(8, 210)
		Text("Save file to:")
		self.path_button = Button(
			"Set Path",EVENT_CHOOSE_PATH,420,180,80,18,
			"Choose the data path with the file browser"
			)
		self.path_widget = String(
			"Soya data path (soya.path): ", EVENT_NOEVENT,20, 180, 400, 18,
			PATH, 50, "Soya data path",
			)
		
		self.model_name_widget = String(
			"Model Filename: ", EVENT_NOEVENT,20, 160, 400, 18, 
			FILENAME, 50, "Model filename",
			)
		
		glRasterPos2d(8, 110)
		Text("Options:")

		self.keep_points_and_lines_widget = Toggle(
			"Keep points/lines", EVENT_NOEVENT, 20, 80, 210, 20, 
			KEEP_POINTS_AND_LINES, "Keep points and lines (faces with less than 3 vertices) ; this option is usefull since creating useless lines or points is easy in Blender",
			)
		self.launch_editor_widget = Toggle(
			"Launch Editor", EVENT_NOEVENT, 20, 60, 210, 20,
			LAUNCH_EDITOR, "Launch Soya editor instead of saving",
			)
		
		######### Draw and Exit Buttons
		Button("OK"  , EVENT_OK     ,  20, 10, 40, 18)
		Button("Exit", EVENT_CANCEL , 190, 10, 40, 18)

	def event(self, evt, val):        
		"""Process blender keyboard events."""
		if evt == QKEY and not val: Exit()

	def bevent(self, evt):
		"""Process blender widget events."""
		if   evt == EVENT_CANCEL: Exit()
		elif evt == EVENT_CHOOSE_PATH:
				FileSelector(set_path, "Set","")
				self.path_widget.val = "'%s'" % PATH
				Draw.Redraw()
		elif evt == EVENT_OK:
			exporter = Blender2Soya(
				path                  = ("%s" % self.path_widget                 )[1:-1],
				filename              = ("%s" % self.model_name_widget           )[1:-1],
				keep_points_and_lines = int("%s" % self.keep_points_and_lines_widget),
				launch_editor         = int("%s" % self.launch_editor_widget        ),
				)
			exporter.export()
			
			Exit() # TODO: Should present a status dialog on completion?
			
			
def set_path(path):
	global PATH
	PATH = path
		
def pointbymatrix(p, m):
	return [p[0] * m[0][0] + p[1] * m[1][0] + p[2] * m[2][0] + m[3][0],
					p[0] * m[0][1] + p[1] * m[1][1] + p[2] * m[2][1] + m[3][1],
					p[0] * m[0][2] + p[1] * m[1][2] + p[2] * m[2][2] + m[3][2]]


def get_material(filename):
	try: return soya.Material.get(filename)
	except ImportError:
		print "Warning, you are running Blender's Python, which does not have PIL !"
		print "I'm trying to run system python..."
		path = str(soya.path)
		command = """python -c "import soya; soya.path = %s; soya.Material.get('%s')" """ % (path, filename)
		print command
		r = os.system(command)
		if r: print "Failed -- Please install PIL (Python Imaging Library)"
		else:
			print "OK !"
			return soya.Material.get(filename)
		
class Blender2Soya:
	def __init__(self, **args):
		self.use_global_args()
		
		try: self.parse_args(Blender.Text.get("soya_params").asLines())
		except: pass
		
		self.__dict__.update(args)
		
	def use_global_args(self):
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

				if attr.startswith("material_"): # A material map
					self.materials_map[attr[9:]] = val
					
				elif attr == "config_text": # Config text
					print "(reading config text %s)" % val
					self.parse_args(Blender.Text.get(val).asLines())
					
				elif attr == "config_file": # Config file
					print "(reading config file %s)" % val
					self.parse_args(open(var).read().split("\n"))
					
				else:
					setattr(self, attr, val)
					
	def export(self):
		Blender.Redraw() # Needed for GetRawFromObject
		
		print "setting file format to %s..." % self.file_format
		if   self.file_format == "pickle":
			import cPickle as pickle
			soya.set_file_format(pickle.dumps)
		elif self.file_format == "cerealizer":
			import cerealizer, soya.cerealizer4soya as cerealizer4soya
			soya.set_file_format(cerealizer.dumps)
		else:
			raise ValueError("Unsupported file format %s" % self.file_format)
		
		objs = Blender.Object.Get()
		
		if self.animation:
			for obj in objs:
				data = obj.getData()
				if (type(data) is Blender.Types.ArmatureType):
					scene     = Blender.Scene.getCurrent()
					#armature  = Blender.Armature.Get()[0]
					armature  = obj
					animation = Blender.Armature.NLA.GetActions()[self.animation]
					
					animation.setActive(armature)

					scene.getRenderingContext().currentFrame(int(self.animation_time))
					scene.makeCurrent()
			
			
			
		materials           = []
		already_warned      = []
		nb_points_and_lines = 0
		
		soya.path.insert(0, self.path) # insert at index 0 => save in this path.
		root_world = soya.World()
		root_world.filename = self.filename

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

					f = soya.Face(root_world)
					
					# face option
					if(face.smooth != 0): f.smooth_lit = 1
					if(face.mode & Blender.NMesh.FaceModes.TWOSIDE): f.double_sided = 1
						
					# vertices
					index = 0
					for vertex in face.v:
						# vertex coordinates
						co = pointbymatrix(vertex.co, matrix)
						v = soya.Vertex(root_world, co[0], co[1], co[2])
					
						# vertex color
						if (face.col != None) and (len(face.col) > 0):
							color = face.col[index]
							v.color = (color.r / 255.0, color.g / 255.0, color.b / 255.0, color.a / 255.0)
							
						# vertex texture coordinates
						if len(face.uv) > 0:
							uv = face.uv[index]
							v.tex_x = uv[0]
							v.tex_y = 1.0 - uv[1]
						
						f.append(v)
						index = index + 1
						
						
					# material
					# check for a material with the same name that the image UV texture file
					# (without extension).
					if(face.image != None):
						image_filename    = face.image.name
						if "." in image_filename:
							material_filename = image_filename[:image_filename.rfind(".")]
						material_filename = self.materials_map.get(material_filename, material_filename)
						f.material = get_material(material_filename)
						
						
		if nb_points_and_lines:
			print "blender2soya.py: removing %s points and lines..." % nb_points_and_lines
		
		# Soya has different axis conventions  
		root_world.rotate_x(-90.0)

		# Ensure quad's vertices are coplanar, and split any bugous quads
		nb_non_coplanar_quads = facecutter.check_quads(root_world)
		if nb_non_coplanar_quads:
			print "blender2soya.py: splitting %s non coplanar quads..." % nb_non_coplanar_quads
			
		if self.scale != 1.0:
			root_world.scale(self.scale, self.scale, self.scale)
			
		if self.cellshading:
			root_world.model_builder = soya.CellShadingModelBuilder(
				shader              = (self.cellshading_shader and get_material(self.cellshading_shader)) or None,
				outline_color       = self.cellshading_outline_color,
				outline_width       = self.cellshading_outline_width,
				outline_attenuation = self.cellshading_outline_attenuation,
				)
			
		if self.shadow:
			if not root_world.model_builder: root_world.model_builder = soya.SimpleModelBuilder()
			root_world.model_builder.shadow = 1
			
		if self.max_face_angle != 80.0:
			if not root_world.model_builder: root_world.model_builder = soya.SimpleModelBuilder()
			root_world.model_builder.max_face_angle = self.max_face_angle
			
			
		if self.launch_editor: self.edit(root_world, *materials)
		else:
			for material in materials:
				print "blender2soya.py: exporting material %s..." % material.filename
				material.save()
				
			print "blender2soya.py: exporting world %s..." % root_world.filename
			root_world.save()

			
	def edit(self, *objs):
		import Tkinter, soya.editor, soya.editor.main
		for obj in objs: soya.editor.edit(obj)
		Tkinter.mainloop()
		



# Check for batch mode
if "--blender2soya" in sys.argv:
	args = sys.argv[sys.argv.index("--blender2soya") + 1:]
	
	exporter = Blender2Soya()
	exporter.parse_args(args)
	exporter.export()
	
	Blender.Quit()
	
	
if __name__ == '__main__': # Only executed if ran as the main script
	if SHOW_DIALOG:
		# Create the dialog instance and register the event handlers with blender
		dialog = BlenderDialog()
		Register(dialog.draw, dialog.event, dialog.bevent)
		
	else:
		# Export immediately
		exporter = Blender2Soya()
		exporter.export()
		
