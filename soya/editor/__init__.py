# -*- indent-tabs-mode: t -*-

# Soya 3D
# Copyright (C) 2001-2002 Jean-Baptiste LAMY
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

import Tkinter, dircache, os, os.path, sets
import editobj, editobj.main, editobj.editor as editor, editobj.custom as custom
import soya, soya.editor.material, soya.editor.world
import soya.laser        as laser
import soya.ray          as ray
import soya.facecutter   as facecutter
import soya.widget

#
# Config and hacks for EditObj.
#

custom.register_method("rotate_y", soya.CoordSyst, editor.FloatEditor)
custom.register_method("rotate_x", soya.CoordSyst, editor.FloatEditor)
custom.register_method("rotate_z", soya.CoordSyst, editor.FloatEditor)

custom.register_children_attr("children"  , "add", "__delitem__", clazz = soya.World)
custom.register_children_attr("vertices"  , clazz = soya.Face)
custom.register_children_attr("generators", clazz = soya.Particles)

soya.Particles.generators = property(lambda self: [self.generator], None)

# Register properties' editors

class XTextureCoordEditor(editor.Editor, Tkinter.Frame):
	require_right_menu = 0
	
	def __init__(self, master, obj, attr):
		editor.Editor.__init__(self, master, obj, attr)
		
		Tkinter.Frame.__init__(self, master)
		self.columnconfigure(0, weight = 1)
		
		if obj.face.material and obj.face.material.texture:
			try:
				import Image, ImageTk

				self.image = Image.open(os.path.join(soya.path[0], obj.face.material.texture.filename))
				
				self.image_width = self.image_height = 0
				
				self.label = Tkinter.Label(self, bd = 0, width = 500)
				self.label.grid(row = 0, column = 0, sticky = "EWN")
				self.label.bind("<Configure>"     , self.label_conf)
				self.label.bind("<Button-1>"      , self.motion)
				self.label.bind("<Button1-Motion>", self.motion)
			except ImportError: # PIL is not installed !
				self.label = None
				
		self.internal_editor = editor.FloatEditor(self, obj, attr)
		self.internal_editor.grid(row = 1, column = 0, sticky = "EWS")
		self.cancel = self.master.cancel
		
	def label_conf(self, event = None):
		import Image, ImageTk
		
		if self.image_width != self.label.winfo_width():
			self.image_width  = self.label.winfo_width()
			self.image_height = (self.image.size[1] / float(self.image.size[0])) * self.image_width
			
			self.imagetk = ImageTk.PhotoImage(self.image.resize((int(self.image_width), int(self.image_height))))
			
			self.label.configure(image = self.imagetk)
			
	def get_value(self): return self.internal_editor.get_value()
	def set_value(self, value): self.internal_editor.set_value(value)
	def update(self): self.internal_editor.update()
	
	def motion(self, event):
		self.obj.tex_x = max(0.0, min(1.0, float(event.x) / self.image_width ))
		self.obj.tex_y = max(0.0, min(1.0, float(event.y) / self.image_height))
		
custom.register_attr("lefthanded"          , None)
custom.register_attr("matrix"              , None)
custom.register_attr("root_matrix"         , None)
custom.register_attr("inverted_root_matrix", None)
custom.register_attr("face"                , None)
custom.register_attr("normal"              , None)
custom.register_attr("vertices"            , None)
custom.register_attr("name"                , editor.StringEditor)
custom.register_attr("filename"            , editor.StringEditor)
custom.register_attr("x"                   , editor.FloatEditor)
custom.register_attr("y"                   , editor.FloatEditor)
custom.register_attr("z"                   , editor.FloatEditor)
custom.register_attr("scale_x"             , editor.FloatEditor)
custom.register_attr("scale_y"             , editor.FloatEditor)
custom.register_attr("scale_z"             , editor.FloatEditor)
custom.register_attr("front"               , editor.FloatEditor)
custom.register_attr("back"                , editor.FloatEditor)
custom.register_attr("fov"                 , editor.FloatEditor)
custom.register_attr("rot_y"               , editor.FloatEditor)
custom.register_attr("rot_x"               , editor.FloatEditor)
custom.register_attr("rot_z"               , editor.FloatEditor)
custom.register_attr("red"                 , editor.FloatEditor)
custom.register_attr("green"               , editor.FloatEditor)
custom.register_attr("blue"                , editor.FloatEditor)
custom.register_attr("alpha"               , editor.FloatEditor)
custom.register_attr("shininess"           , editor.FloatEditor)
custom.register_attr("point_size"          , editor.FloatEditor)
custom.register_attr("initial_speed"       , editor.FloatEditor)
custom.register_attr("exponent"            , editor.FloatEditor)
custom.register_attr("angle"               , editor.FloatEditor)
custom.register_attr("directional"         , editor.BoolEditor)
custom.register_attr("constant"            , editor.FloatEditor)
custom.register_attr("linear"              , editor.FloatEditor)
custom.register_attr("quadratic"           , editor.FloatEditor)
custom.register_attr("clamp"               , editor.BoolEditor)
custom.register_attr("additive_blending"   , editor.BoolEditor)
custom.register_attr("environment_mapping" , editor.BoolEditor)
custom.register_attr("separate_specular"   , editor.BoolEditor)
custom.register_attr("wireframed"          , editor.BoolEditor)
custom.register_attr("visible"             , editor.BoolEditor)
custom.register_attr("lit"                 , editor.BoolEditor)
custom.register_attr("static_lit"          , editor.BoolEditor)
custom.register_attr("smooth_lit"          , editor.BoolEditor)
custom.register_attr("double_sided"        , editor.BoolEditor)
custom.register_attr("solid"               , editor.BoolEditor)
custom.register_attr("bound_atm"           , editor.BoolEditor)
custom.register_attr("camera_go_through"   , editor.BoolEditor)
custom.register_attr("infinite"            , editor.BoolEditor)
custom.register_attr("use_clip_plane"      , editor.BoolEditor)
custom.register_attr("static"              , editor.BoolEditor)
custom.register_attr("static_only"         , editor.BoolEditor)
custom.register_attr("top_level"           , editor.BoolEditor)
custom.register_attr("reflect"             , editor.BoolEditor)
custom.register_attr("acceleration"        , editor.SubEditor)
custom.register_attr("endpoint"            , editor.SubEditor)
custom.register_attr("portal_linked"       , editor.BoolEditor)

def _all_parent(item):
	if isinstance(item, soya.World):
		inner_worlds = item.recursive()
		inner_worlds.append(item)
		return filter(lambda item: isinstance(item, soya.World) and (not getattr(item, "name", "").startswith("_")) and (not item in inner_worlds), item.get_root().recursive())
	else:
		return filter(lambda item: isinstance(item, soya.World) and (not getattr(item, "name", "").startswith("_")), item.get_root().recursive())
	
custom.register_attr("parent" , editor.LambdaListEditor(_all_parent))

def _get_all_texture_names(obj):
	names = sets.Set([None])
	for path in soya.path:
		print path, os.path.join(path, soya.Material.DIRNAME)
		for name in dircache.listdir(os.path.join(path, soya.Image.DIRNAME)):
			print name
			names.add(name)
	return list(names)

custom.register_attr("texture", editor.LambdaListEditor(lambda obj: [None] + soya.Image.availables(), lambda name: name and soya.Image.get(name)))
custom.register_attr("image"  , None, soya.Material)

class MaterialEditor(editor.WithButtonEditor):
	INTERNAL_EDITOR_CLASS = editor.LambdaListEditor(lambda obj: filter(lambda filename: not (filename and filename.startswith("_")), soya.Material.availables()), lambda filename: filename and soya.Material.get(filename))
	
	def __init__(self, master, obj, attr):
		editor.WithButtonEditor.__init__(self, master, obj, attr, self.INTERNAL_EDITOR_CLASS, "...")
		
	def button_click(self, event = None):
		edit(getattr(self.obj, self.attr))
		
class ModelEditor(editor.WithButtonEditor):
	INTERNAL_EDITOR_CLASS = editor.LambdaListEditor(lambda obj: filter(lambda filename: not (filename and filename.startswith("_")), soya.Model.availables()), lambda filename: filename and soya.Model.get(filename))
	
	def __init__(self, master, obj, attr):
		editor.WithButtonEditor.__init__(self, master, obj, attr, self.INTERNAL_EDITOR_CLASS, "...")
		
	def button_click(self, event = None):
		edit(getattr(self.obj, self.attr).to_world())
		
class WorldEditor(editor.WithButtonEditor):
	INTERNAL_EDITOR_CLASS = editor.LambdaListEditor(lambda obj: filter(lambda filename: not (filename and filename.startswith("_")), soya.World.availables()), lambda filename: filename and soya.World.get(filename))
	
	def __init__(self, master, obj, attr):
		editor.WithButtonEditor.__init__(self, master, obj, attr, self.INTERNAL_EDITOR_CLASS, "...")
		
	def button_click(self, event = None):
		edit(getattr(self.obj, self.attr))
		
custom.register_attr("model"            , ModelEditor)
custom.register_attr("material"         , MaterialEditor)
custom.register_attr("beyond"           , WorldEditor)

custom.register_attr("path"             , editor.DirnameEditor)

custom.register_attr("tex_x"            , XTextureCoordEditor)
custom.register_attr("tex_y"            , editor.FloatEditor)

def _reverse_vertices(self): self.vertices.reverse()
soya.Face.reverse_vertices = _reverse_vertices

custom.register_method("reverse_vertices", soya.Face)


def ImmatureVertex():
	vertex = soya.Vertex()
	vertex.immature = 1
	return vertex

_last_face = None

def _Gone(vertices):
	global _last_face
	
	f = soya.Face(None, vertices)
	if _last_face:
		f.double_sided = _last_face.double_sided
		f.material     = _last_face.material
		f.smooth_lit = _last_face.smooth_lit
		f.lit = _last_face.lit
		f.solid = _last_face.solid
		f.static_lit = _last_face.static_lit
	_last_face = f
	return f

soya.Triangle = lambda : _Gone([ImmatureVertex(), ImmatureVertex(), ImmatureVertex()])
soya.Quad     = lambda : _Gone([ImmatureVertex(), ImmatureVertex(), ImmatureVertex(), ImmatureVertex()])

custom.register_available_children(["soya.Triangle()", "soya.Quad()", "soya.Body()", "soya.World()", "soya.Camera()", "soya.Light()", "soya.Portal()", "soya.Fountain()", "laser.Laser()", "ray.Ray()"], soya.World)
custom.register_available_children(["soya.Vertex()"], soya.Face)

custom.register_values("color"       , ["None", "(1.0, 1.0, 1.0, 1.0)", "(0.0, 0.0, 0.0, 1.0)"])
custom.register_values("diffuse"     , ["None", "(1.0, 1.0, 1.0, 1.0)", "(0.0, 0.0, 0.0, 1.0)"])
custom.register_values("specular"    , ["None", "(1.0, 1.0, 1.0, 1.0)", "(0.0, 0.0, 0.0, 1.0)"])
custom.register_values("to_model_args", ["None", """("tree", {})""", """("cell-shading", { 'shader':'shader2', 'line_color':(0.0, 0.0, 0.0, 1.0), 'line_width':8.0 })"""])
#custom.register_values("to_model_args", ["None", """("tree", {"min_node_content":0, "min_node_radius":5.0, "min_node_distance":0.0})""", """("morph", {})"""])

editobj.EVAL_ENV.update({
	"soya"       : soya,
	"laser"      : laser,
	"ray"        : ray,
	"cut"        : facecutter.cut,
	"check_quads": facecutter.check_quads,
	})

# Better Tk look
_tk = Tkinter.Tk(className = 'EditObj')
_tk.withdraw()
_tk.option_add("*bd", 1)
_tk.option_add("*List.background", "#FFFFFF")
_tk.option_add("*Text.background", "#FFFFFF")
_tk.option_add("*Text.relief", "flat")
_tk.option_add("*Entry.background", "#FFFFFF")
_tk.option_add("*Entry.relief", "flat")


CURRENT = None

def edit_material(self, window):
	if not soya.inited: soya.init("Soya Editor")
	
	ed = soya.editor.material.MaterialEditor(self, window)
	
	def on_activate(event = None):
		global CURRENT
		
		if CURRENT: CURRENT.deactivate()
		ed.activate()
		CURRENT = ed
		
	window.bind("<FocusIn>" , on_activate)

def edit_world(self, window):
	if not self.parent:
		if not soya.inited: soya.init("Soya Editor")
		
		ed = soya.editor.world.WorldEditor(self, window)
		
		def on_activate(event = None):
			global CURRENT
			
			if CURRENT: CURRENT.deactivate()
			ed.activate()
			CURRENT = ed
			
		window.bind("<FocusIn>" , on_activate)

custom.register_on_edit(edit_material, soya.Material)
custom.register_on_edit(edit_world,    soya.World)


def _subedit(self, window):
	if hasattr(CURRENT, "select_handles_for"): CURRENT.select_handles_for(self)
	
def _subedit_face(self, window):
	if hasattr(CURRENT, "select_handles_for"):
		for vertex in self: CURRENT.select_handles_for(vertex)
		
def _editchildren(self, visible):
	if hasattr(CURRENT, "children_edited"): CURRENT.children_edited(self, visible)
	
custom.register_on_edit            (_subedit,      soya.CoordSyst)
custom.register_on_edit            (_subedit,      soya.Vertex)
custom.register_on_edit            (_subedit_face, soya.Face)
custom.register_on_children_visible(_editchildren, soya.World)

edit = editobj.edit
