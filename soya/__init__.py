# -*- indent-tabs-mode: t -*-

# Soya 3D
# Copyright (C) 2006 Jean-Baptiste LAMY -- jiba@tuxfamily.org
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

import sys, os, os.path, weakref,cPickle as pickle

if os.path.exists(os.path.join(__path__[0], "build")):
	# We are using a source directory.
	# We need to get the binary library in "./build/xxx"
	import distutils.util
	__path__.append(os.path.join(__path__[0], "build", "lib.%s-%s" % (distutils.util.get_platform(), sys.version[0:3]), "soya"))

from soya._soya import *
from soya._soya import _CObj

#from soya import _soya

_soya = sys.modules["soya._soya"]

#from soya import opengl
#from soya import sdlconst

# For file compatibility
sys.modules["soyapyrex"] = _soya

# Other oddity... cPickle seems to like it ;-)
sys.modules["_soya"    ] = _soya


dumps = pickle.dumps
_loadss = [pickle.loads]
AUTO_EXPORTERS_ENABLED = 1
try:
	import cerealizer
	_loadss.insert(0, cerealizer.loads)
except ImportError: pass

def loads(s):
	try:
		for loads_func in _loadss:
			if loads_func.__module__ == "cerealizer":
				import soya.cerealizer4soya
				if s.startswith("cereal"): return loads_func(s)
			else:
				try: return loads_func(s)
				except:
					sys.excepthook(*sys.exc_info())
	finally:
		_soya._chunk_check_error()
	raise ValueError("Cannot read file / data!")
	
def set_file_format(dumps_func, loads_funcs = None):
	"""set_file_format(dumps_func, loads_funcs = None)

Sets the file format used when saving or loading files.
DUMPS_FUNC is a function or module called to serialize objects.
It can be either a function similar to pickle.dumps, or a module with a dumps function.
The following are known to work:
	- cPickle
	- cerealizer

LOADS_FUNCS is a function, a module or a list of functions or modules called to de-serialize objects.
It can be either a function similar to pickle.loads, or a module with a loads function, or a list
of several of these function or module. If a list is given, the functions are tried in order.
If LOADS_FUNCS is not given, the file formats supported for loading are not modified.
The following are known to work:
	- cPickle
	- cerealizer

AUTO_EXPORTERS is true for enabling auto-exporters (default) or false to disable them.

The actual default (which will probably change) is equivalent to:
	set_file_format(cPickle, [cerealizer, cPickle])  if Cerealizer is available
	set_file_format(cPickle, cPickle)                if Cerealizer is not available

To use Cerealizer while still being able to read cPickle files:
	set_file_format(cerealizer, [cerealizer, cPickle])

To use only Cerealizer (especially ineresting if you need security, e.g. for networking games):
	set_file_format(cerealizer, cerealizer)

To use only cPickle (for compatibility with older apps):
	set_file_format(cPickle, cPickle)
"""
	global dumps, _loadss
	
	dumps = (callable(dumps_func) and dumps_func) or dumps_func.dumps
	
	if   loads_funcs:
		if not hasattr(loads_funcs, "__iter__"): loads_funcs = [loads_funcs]
		_loadss = [(callable(loads_func) and loads_func) or loads_func.loads for loads_func in loads_funcs]
		
	if "cerealizer" in [dumps.__module__] + [loads_func.__module__ for loads_func in _loadss]:
		import soya.cerealizer4soya

	
def set_root_widget(widget):
	"""set_root_widget(WIDGET)

Sets the root widget to WIDGET. The root widget is the widget that is rendered first.
It defaults to the first Camera you create."""
	global root_widget
	root_widget = widget
	_soya.set_root_widget(widget)
	

def coalesce_motion_event(events):
	"""coalesce_motion_event(events) -> sequence

Prunes from EVENTS all mouse motion events except the last one.
This is usefull since only the last one is usually releavant (Though
be carrefull if you use the relative mouse coordinate !).

EVENTS should be a list of events, as returned by soya.process_event().
The returned list has the same structure."""
	import soya.sdlconst
	
	events = list(events)
	events.reverse()
	
	def keep_last(event):
		if event[0] == soya.sdlconst.MOUSEMOTION:
			if keep_last.last_found: return 0
			else: keep_last.last_found = 1
		return 1
	keep_last.last_found = 0
	
	events = filter(keep_last, events)
	events.reverse()
	return events


DATADIR = os.path.join(os.path.dirname(__file__), "data")
if not os.path.exists(DATADIR):
	DATADIR = "/usr/share/soya"
	if not os.path.exists(DATADIR):
		DATADIR = "/usr/local/share/soya"
		if not os.path.exists(DATADIR):
			DATADIR = "/usr/share/python-soya"
			if not os.path.exists(DATADIR):
				DATADIR = os.path.join(os.getcwd(), "data")
				if not os.path.exists(DATADIR):
					import warnings
					warnings.warn("Soya's data directory cannot be found !")
	
	
path = []

_SAVING = None # The object currently being saved. XXX not thread-safe, hackish

def _getter(klass, filename): return klass._reffed(filename)
_loader = _getter

class SavedInAPath(object):
	"""SavedInAPath

Base class for all objects that can be saved in a path, such as Material,
World,..."""
	DIRNAME = ""
	SRC_DIRNAMES_EXTS = []
	
	def _get_directory_for_loading(klass, filename, ext = ".data"):
		if os.pardir in filename: raise ValueError("Cannot have .. in filename (security reason)!", filename)
		
		if klass.DIRNAME in ("models", "animated_models"):
			for p in path:
				if os.path.exists(os.path.join(p, klass.DIRNAME)): break
			else:
				Model.DIRNAME = AnimatedModel.DIRNAME = "shapes"
				return klass._get_directory_for_loading(filename, ext)
			
		src_filename = filename.split("@")[0]
		for p in path:
			d = os.path.join(p, klass.DIRNAME, filename + ext)
			if os.path.exists(d): return p
			for src_dirname, src_ext in klass.SRC_DIRNAMES_EXTS:
				d = os.path.join(p, src_dirname, src_filename + src_ext)
				if os.path.exists(d): return p
				
		raise ValueError("Cannot find a %s named %s!" % (klass, filename))
			
	_get_directory_for_loading = classmethod(_get_directory_for_loading)
	
	def _get_directory_for_saving(klass, filename, ext = ".data"):
		if os.pardir in filename: raise ValueError("Cannot have .. in filename (security reason)!", filename)
		
		if klass.DIRNAME in ("models", "animated_models"):
			for p in path:
				if os.path.exists(os.path.join(p, klass.DIRNAME)): break
			else:
				Model.DIRNAME = AnimatedModel.DIRNAME = "shapes"
				return klass._get_directory_for(filename, ext, raise_error)
			
		src_filename = filename.split("@")[0]
		for p in path:
			d = os.path.join(p, klass.DIRNAME)
			if os.path.exists(d): return p
		raise RuntimeError("Unable to find a %s directory to save %s"%(klass.DIRNAME,filename))
			
	_get_directory_for_saving = classmethod(_get_directory_for_saving)
	
	def _get_directory_for_loading_and_check_export(klass, filename, ext = ".data"):
		dirname = klass._get_directory_for_loading(filename, ext)
		if AUTO_EXPORTERS_ENABLED:
			src_filename  = filename.split("@")[0]
			full_filename = os.path.join(dirname, klass.DIRNAME, filename + ext)
			if os.path.exists(full_filename): exported_date = os.path.getmtime(full_filename)
			else:                             exported_date = 0
			for src_dirname, src_ext in klass.SRC_DIRNAMES_EXTS:
				d = os.path.join(dirname, src_dirname, src_filename + src_ext)
				if os.path.exists(d) and exported_date < os.path.getmtime(d):
					print "* Soya * Converting %s to %s..." % (d, klass.__name__)
					klass._export(d, filename)
					break
		return dirname
	
	_get_directory_for_loading_and_check_export = classmethod(_get_directory_for_loading_and_check_export)
	
	def _export(klass, src, filename): raise NotImplementedError
	_export = classmethod(_export)
	
# 	def _check_export(klass, exported_filename, filename, *source_dirnames):
# 		"""_check_export(FILENAME, *(SOURCE_DIRNAME, SOURCE_FILENAME)) -> (SOURCE_DIRNAME, SOURCE_FULL_FILENAME, FULL_FILENAME)

# Search soya.path for a file FILENAME.data in the self.DIRNAME directory,
# and check if the file needs to be re-exporter from any of the SOURCE_DIRNAMES directory.

# Returned tuple :
# FULL_FILENAME is the complete filename of the object.
# If SOURCE_DIRNAME is None, the exported object is up-to-date.
# If SOURCE_DIRNAME is one of SOURCE_DIRNAMES, the source object of this directory have been
# modified more recently that the exported one, and SOURCE_FULL_FILENAME is the complete
# filename of the source that needs to be re-exported."""
# 		if (not os.path.exists(os.path.join(path[0], klass.DIRNAME))) and os.path.exists(os.path.join(path[0], "shapes")): # Backward compatibility
# 			if   klass.DIRNAME == "models"         : klass.DIRNAME = "shapes"
# 			elif klass.DIRNAME == "animated_models": klass.DIRNAME = "shapes"
			
# 		filename = filename.replace("/", os.sep)
# 		for p in path:
# 			file = os.path.join(p, klass.DIRNAME , exported_filename)
			
# 			if   os.path.exists(file):
# 				if AUTO_EXPORTERS_ENABLED:
# 					for source_dirname, source_filename in source_dirnames:
# 						source_file = os.path.join(p, source_dirname, source_filename)
# 						if os.path.exists(source_file) and (os.path.getmtime(file) < os.path.getmtime(source_file)):
# 							print "* Soya * Converting %s to %s..." % (source_file, klass.__name__)
# 							return source_dirname, source_file, file
# 				return None, None, file
# 			else:
# 				if AUTO_EXPORTERS_ENABLED:
# 					for source_dirname, source_filename in source_dirnames:
# 						source_file = os.path.join(p, source_dirname, source_filename)
# 						if os.path.exists(source_file):
# 							print "* Soya * Converting %s to %s..." % (source_file, klass.__name__)
# 							return source_dirname, source_file, file
						
# 		raise ValueError("No %s or %s named %s" % (klass.__name__, source_dirnames, filename))
# 	_check_export = classmethod(_check_export)
	
	def get(klass, filename):
		"""SavedInAPath.get(filename)

Gets the object of this class with the given FILENAME attribute.
The object is loaded from the path if it is not already loaded.
If it is already loaded, the SAME object is returned.
Raise ValueError if the file is not found in soya.path."""
		return klass._alls.get(filename) or klass._alls.setdefault(filename, klass.load(filename))
	get = classmethod(get)
	
	def load(klass, filename):
		"""SavedInAPath.get(filename)

Loads the object of this class with the given FILENAME attribute.
Contrary to get, load ALWAYS returns a new object.
Raise ValueError if the file is not found in soya.path."""
		dirname  = klass._get_directory_for_loading_and_check_export(filename)
		filename = filename.replace("/", os.sep)
		obj = loads(open(os.path.join(dirname, klass.DIRNAME, filename + ".data"), "rb").read())
		obj.loaded()
		return obj
	load = classmethod(load)
	_reffed = get
	
	def loaded(self):
		if self.filename: self._alls[self.filename] = self
		
	def save(self, filename = None):
		"""SavedInAPath.save(filename = None)

Saves this object. If no FILENAME is given, the object is saved in the path,
using its filename attribute. If FILENAME is given, it is saved at this
location."""
		if os.pardir in self.filename: raise ValueError("Cannot have .. in filename (security reason)!", filename)
		if not filename: filename = os.path.join(self._get_directory_for_saving(self.filename, ".data"), self.DIRNAME, self.filename + ".data")
		
		global _SAVING
		try:
			_SAVING = self # Hack !!
			data = dumps(self, 1) # Avoid destroying the file if the serialization causes an error.
			open(filename or os.path.join(p, self.filename.replace("/", os.sep)) + ".data", "wb").write(data)
		finally:
			_SAVING = None
			
	def __reduce_ex__(self, arg):
		if (not _SAVING is self) and self._filename: # self is saved in another file, save filename only
			return (_getter, (self.__class__, self.filename)) # can be shared
		return _CObj.__reduce_ex__(self, arg)
	
	def __reduce__(self):
		if (not _SAVING is self) and self._filename: # self is saved in another file, save filename only
			return (_getter, (self.__class__, self.filename)) # can be shared
		return _CObj.__reduce__(self)
	
	def get_filename(self): return self._filename
	def set_filename(self, filename):
		if self._filename:
			try: del self._alls[self.filename]
			except KeyError: pass
		if filename: self._alls[filename] = self
		self._filename = filename
	filename = property(get_filename, set_filename)
	
	def availables(klass):
		"""SavedInAPath.availables() -> list

Returns the list of the filename all the objects available in the current path."""
		import dircache
		filenames = dict(klass._alls)
		for p in path:
			p = os.path.join(p, klass.DIRNAME)
			if os.path.exists(p):
				for filename in dircache.listdir(p):
					if filename.endswith(".data"): filenames[filename[:-5]] = 1
		filenames = filenames.keys()
		filenames.sort()
		return filenames
	availables = classmethod(availables)
	
	def __setstate__(self, state):
		super(SavedInAPath, self).__setstate__(state)

# We MUST extends all Pyrex classes in Python,
# at least for weakref-ing their instance.

class Image(SavedInAPath, _soya._Image):
	"""A Soya image, suitable for e.g. texturing.

Attributes are:

 - pixels : the raw image data (e.g. in a form suitable for PIL).

 - width.

 - height.

 - nb_color: the number of color channels (1 => monochrome, 3 => RGB, 4 => RGBA).
"""
	DIRNAME = "images"
	_alls = weakref.WeakValueDictionary()
	def __reduce__(self): return _CObj.__reduce__(self)
	def __reduce_ex__(self, arg): return _CObj.__reduce_ex__(self, arg)
		
	palette = None
	
	def load(klass, filename):
		if filename[0] == "/": # Old-style, non-relative filename
			filename = filename.split(os.sep)[-1]
		if ".." in filename: raise ValueError("Cannot have .. in filename (security reason)!", filename)
		filename = filename.replace("/", os.sep)
		for p in path:
			file = os.path.join(p, klass.DIRNAME, filename)
			if os.path.exists(file):
				image = open_image(file)
				image._filename = filename
				return image
		raise ValueError("No %s named %s" % (klass.__name__, filename))
	load = classmethod(load)
	
	def save(klass, filename = None): raise NotImplementedError("Soya cannot save image.")
	
	def availables(klass):
		"""SavedInAPath.availables() -> list

Returns the list of the filename all the objects available in the current path."""
		import dircache
		filenames = dict(klass._alls)
		for p in path:
			for filename in dircache.listdir(os.path.join(p, klass.DIRNAME)):
				filenames[filename] = 1
		filenames = filenames.keys()
		filenames.sort()
		return filenames
	availables = classmethod(availables)

	
class Material(_soya._Material, SavedInAPath):
	"""Material

A material regroups all the surface attributes, like colors, shininess and
texture. You should NEVER use None as a material, use soya._DEFAULT_MATERIAL instead.

Attributes are:

- diffuse: the diffuse color.

- specular: the specular color; used for shiny part of the surface.

- emissive: the emissive color; this color is applied even in the dark.

- separate_specular: set it to true to enable separate specular; this usually
	results in a more shiny specular effect.

- shininess: the shininess ranges from 0.0 to 128.0; 0.0 is the most metallic / shiny
	and 128.0 is the most plastic.

- texture: the texture (a soya.Image object, or None if no texture).

- clamp: set it to true if you don't want to repeat the texture when the texture
	coordinates are out of the range 0 - 1.0.

- additive_blending: set it to true for additive blending. For semi-transparent surfaces
	(=alpha blended) only. Usefull for special effect (Ray, Sprite,...).

- mip_map: set it to true to enable mipmaps for this materials texture. (default: True)
"""

	DIRNAME = "materials"
	SRC_DIRNAMES_EXTS = [("images", ".png"), ("images", ".jpeg")]
	_alls = weakref.WeakValueDictionary()
	
	def _export(klass, src, filename):
		image = Image.get(os.path.basename(src))
		p = os.path.join(os.path.dirname(src), os.pardir, klass.DIRNAME, filename + ".data")
		if os.path.exists(p): material = loads(open(p, "rb").read())
		else:
			material = Material()
			material.filename = filename
		material.texture = image
		material.save()
	_export = classmethod(_export)
# 	def load(klass, filename):
# 		if ".." in filename: raise ValueError("Cannot have .. in filename (security reason)!", filename)
# 		need_export, image_file, file = klass._check_export(filename + ".data", filename, (Image.DIRNAME, filename + ".png"), (Image.DIRNAME, filename + ".jpeg"))
# 		if need_export and AUTO_EXPORTERS_ENABLED:
# 			image = Image.get(os.path.basename(image_file))
# 			if os.path.exists(file): material = loads(open(file, "rb").read())
# 			else:
# 				material = Material()
# 				material._filename = filename
# 			material.texture = image
# 			try: material.save()
# 			except:
# 				sys.excepthook(*sys.exc_info())
# 				print "* Soya * WARNING : can't save material %s!" % filename
# 			return material
# 		else:
# 			obj = loads(open(file, "rb").read())
# 			obj.loaded()
# 			return obj

# 	load = classmethod(load)

class PythonMaterial(_soya._PythonMaterial, Material):
	pass

class PythonMainLoopingMaterial(_soya._PythonMainLoopingMaterial, Material):
	pass

class Model(SavedInAPath, _soya._Model):
	"""Model

A Model is an optimized model. Models cannot be modified, but they are rendered very
quickly, and they can be used several time, e.g. if you want to 2 same cubes in a scene.
Models are used in conjunction with Body."""
	DIRNAME = "models"
	SRC_DIRNAMES_EXTS = [("blender", ".blend"), ("obj", ".obj"), ("obj", ".mtl"), ("3ds", ".3ds"), ("worlds", ".data")]
	_alls = weakref.WeakValueDictionary()
	
	def _export(klass, src, filename):
		model = World.get(filename).to_model()
		model.filename = filename
		model.save()
	_export = classmethod(_export)

# 	def load(klass, filename):
# 		if ".." in filename: raise ValueError("Cannot have .. in filename (security reason)!", filename)
# 		need_export, world_file, file = klass._check_export(filename + ".data", filename, (World.DIRNAME, filename + ".data"), ("blender", filename.split("@")[0] + ".blend"), ("obj", filename + ".obj"), ("obj", filename + ".mtl"), ("3ds", filename + ".3ds"))
# 		if need_export and AUTO_EXPORTERS_ENABLED:
# 			model = World.get(filename).to_model()
# 			model._filename = filename
# 			try: model.save()
# 			except:
# 				sys.excepthook(*sys.exc_info())
# 				print "* Soya * WARNING : can't save compiled model %s!" % filename
# 			return model
# 		else:
# 			obj = loads(open(file, "rb").read())
# 			obj.loaded()
# 			return obj
# 	load = classmethod(load)
	
	def availables(klass): return World.availables()
	availables = classmethod(availables)
	
	
class SimpleModel(Model, _soya._SimpleModel):
	"""SimpleModel

The most basic class of Model."""
	
class SolidModel(_soya._SolidModel, SimpleModel):
	"""SolidModel

Like SimpleModel, but when the model intersects the camera, the section is drawn.
Usefull for light effects."""
	
class TreeModel(Model, _soya._TreeModel):
	"""TreeModel

A Model that use a BSP-like tree to optimize rendering and raypicking."""

class CellShadingModel(Model, _soya._CellShadingModel):
	"""CellShadingModel

A Model that use cell-shading for rendering."""

class SplitedModel(Model, _soya._SplitedModel):
	"""SplitedModel

A model splited in several parts so that it is possible to render only
the visibles parts. Must be used with BSPWorld or futur OctreeWorld."""

class Point(_soya._Point):
	"""A Point is just a 3D position. It is used for math computation, but it DOESN'T display
anything."""

class Vector(_soya._Vector):
	"""A Vector is a 3D vector (and not a kind of list or sequence ;-). Vectors are
useful for 3D math computation. 

Most of the math operators, such as +, -, *, /, abs,... work on Vectors and do
what they are intended to do ;-)"""

class Vertex(_soya._Vertex):
	"""Vertex

A Vertex is a subclass of Point, which is used for building Faces.
A Vertex doesn't display anything ; you MUST put it inside a Face.

Attributes are (see also Point for inherited attributes):

 - diffuse: the vertex diffuse color (also aliased to 'color' for compatibility)
 - emissive: the vertex emissive color (lighting-independant color)
 - tex_x, tex_y: the text
ure coordinates (sometime called U and V).
"""
	
	
class Body(_soya._Body):
	"""Body

A Body is a Soya 3D object that display a Model. The Body contains data about the
position, the orientation and the scaling, and the Model contains the geometric data.

This separation allows to use several time the same Model at different position, without
dupplicating the geometric data.

Attributes are (see also CoordSyst for inherited attributes):

 - model : the Model (a Model object, defaults to None).
"""

def do_cmd(cmd):
	print "* Soya * Running '%s'..." % cmd
	os.system(cmd)
	
def do_cmd_popen(cmd):
	print "* Soya * Running '%s'..." % cmd
	p = os.popen(cmd)
	import time; time.sleep(1.0)
	return p.read()
	
class World(SavedInAPath, _soya._World, Body):
	"""World

A World is a Soya 3D object that can contain other Soya 3D objects, including other Worlds.
Worlds are used to group 3D objects ; when a World is moved, all the objects it contains
are moved too, since they are part of the World.
Mostly for historical reasons, World is a subclass of Body, and thus can display a Model.

Worlds can be saved in the "worlds" directory ; see SavedInAPath.

Attributes are (see also Body, CoordSyst and SavedInAPath for inherited attributes):

 - children : the list of 3D object contained in the World (default to an empty list).
	 use World.add(coordsyst) and World.remove(coordsyst) for additions and removals.

 - atmosphere : the atmosphere specifies atmospheric properties of the World (see
	 Atmosphere). Default is None.

 - model_builder : the model_builder specifies how the World is compiled into Model.
	 Default is None, which result in the use of the default ModelBuilder, which is
	 SimpleModelBuilder().
"""

	DIRNAME = "worlds"
	SRC_DIRNAMES_EXTS = [("blender", ".blend"), ("obj", ".obj"), ("obj", ".mtl"), ("3ds", ".3ds")]
	_alls = weakref.WeakValueDictionary()
	
	def loaded(self):
		SavedInAPath.loaded(self)
		_soya._World.loaded(self)
		for i in self:
			if hasattr(i, "loaded"): i.loaded()
			
	def _export(klass, src, filename):
		if   src.endswith(".blend"):
			import tempfile
			tmp_file = tempfile.mkstemp()[1]
			do_cmd("blender %s -P %s FILENAME=%s TMP_FILE=%s %s" % (
				src,
				os.path.join(os.path.dirname(__file__), "blender2soya_batch.py"),
				filename,
				tmp_file,
				(" CONFIG_TEXT=%s" % filename.split("@")[-1]) * bool("@" in filename),
				))
			code = open(tmp_file).read()
			try: os.unlink(tmp_file)
			except: pass
			exec code
			
		elif src.endswith(".obj") or src.endswith(".mtl"):
			import soya.objmtl2soya
			world = soya.objmtl2soya.loadObj(os.path.splitext(src)[0] + ".obj")
			world.filename = filename
			world.save()
			
		elif src.endswith(".3ds"):
			import soya._3DS2soya
			world = soya._3DS2soya.load_3ds(os.path.splitext(src)[0] + ".3ds")
			world.filename = filename
			world.save()
	_export = classmethod(_export)
	
# 	def load(klass, filename):
# 		global path
		
# 		if ".." in filename: raise ValueError("Cannot have .. in filename (security reason)!", filename)
# 		need_export, source_file, file = klass._check_export(filename + ".data", filename, ("blender", filename.split("@")[0] + ".blend"), ("obj", filename + ".obj"), ("obj", filename + ".mtl"), ("3ds", filename + ".3ds"))
# 		if need_export and AUTO_EXPORTERS_ENABLED:
# 			if   need_export == "blender":
# 				if dumps is pickle.dumps: file_format = "pickle"
# 				else:                     file_format = "cerealizer"
				
# 				extra = ""
# 				if "@" in filename:
# 					extra += " CONFIG_TEXT=%s" % filename[filename.index("@") + 1:]

# 				import tempfile
# 				tmp_file = tempfile.mkstemp()[1]
# 				do_cmd("blender %s -P %s --blender2soya FILENAME=%s FILE_FORMAT=%s TMP_FILE=%s %s" % (
# 					source_file,
# 					os.path.join(os.path.dirname(__file__), "blender2soya_batch.py"),
# 					filename,
# 					file_format,
# 					tmp_file,
# 					extra,
# 					))
# 				code = open(tmp_file).read()
# 				os.unlink(tmp_file)
				
# 				old_path = path
				
# 				exec code
				
# 				path = old_path
				
# 			elif need_export == "obj":
# 				import soya.objmtl2soya
# 				world = soya.objmtl2soya.loadObj(os.path.splitext(source_file)[0] + ".obj")
# 				world.filename = filename
# 				world.save()
# 				return world
			
# 			elif need_export == "3ds":
# 				import soya._3DS2soya
# 				world = soya._3DS2soya.load_3ds(os.path.splitext(source_file)[0] + ".3ds")
# 				world.filename = filename
# 				world.save()
# 				return world
			
# 		obj = loads(open(file, "rb").read())
# 		obj.loaded()
# 		return obj
# 	load = classmethod(load)
World._reffed = World.load
	

class BSPWorld(SavedInAPath, _soya._BSPWorld, Body):
        """BSPWorld

A world designed to render a BSP level with maximum optimisation"""

	DIRNAME = "worlds"
	SRC_DIRNAMES_EXTS = [("bsp", ".bsp")]
	_alls = weakref.WeakValueDictionary()
	
	def _export(klass, src, filename):
		if src.endswith(".bsp"):
			import soya.q3bsp2soya
			bspworld = soya.q3bsp2soya.loadObj(os.path.splitext(src)[0] + ".bsp")
			bspworld.filename = filename
			bspworld.save()
	
	_export = classmethod(_export)

class Light(_soya._Light):
	"""Light

A Light is a 3D object that enlights the other objects.

Attributes are (see also CoordSyst for inherited attributes):

 - directional : True for a directional light (e.g. like the sun), instead of a
	 positional light. The position of a directional light doesn't matter, and only
	 the constant component of the attenuation is used. Default is false.
 - constant, linear and quadratic : the 3 components of the light attenuation. Constant
	 reduces the light independently of the distance, linear increase with the distance,
	 and quadratic increase the squared distance. Default is 1.0, 0.0 and 0.0.
 - cast_shadow : True if the light cast shadows on Models that have shadows enabled.
	 Default is true.
 - shadow_color : the color of the shadow . Default is a semi-transparent black
	 (0.0, 0.0, 0.0, 0.5).
 - top_level : XXX ???
 - static : True if the light can be used for static lighting when compiling a World into
	 a Model. Default is true.
 - ambient : the light's ambient color, which is not affected by the light's orientation
	 or attenuation. Default is black (no ambient).
 - diffuse : the light's color. Default is white.
 - specular : the light's specular color. Default is white.
 - angle : if angle < 180.0, the light is a spotlight.
 - exponent : modify how the spotlight's light is spread.
"""

class Camera(_soya._Camera):
	"""Camera

The Camera specifies from where the scene is viewed.

Attributes are (see also CoordSyst and Widget for inherited attributes):

 - front, back : objects whose distance from the camera is not between front and back
	 are clipped. Front defaults to 0.1 and back to 100.0.
	 If the back / front ratio is too big, you loose precision in the depth buffer.

 - fov : the field of vision (or FOV), in degrees. Default is 60.0.

 - to_render : the world that is rendered by the camera. Default is None, which means
	 the root scene (as returned by get_root()).

 - left, top, width, height : the viewport rectangle, in pixel. Use it if you want to
	 render only on a part of the screen. It defaults to the whole screen.

 - ortho : True for orthogonal rendering, instead of perspective. Default is false.

 - partial : XXX ???. probably DEPRECATED by NoBackgroundAtmosphere.
"""

class Face(_soya._Face):
	"""Face

A Face displays a polygon composed of several Vertices (see the Vertex class).
Notice that Face are SLOW ; Faces are normally used for building model but not for
rendering them. To get a fast rendering, you should put several Faces in a World, and
then compile the World into a Model (see the modeling-X.py tutorial series).

According to the number of Vertices, the result differs:
 - 1 Vertex => Plot
 - 2        => Line
 - 3        => Triangle
 - 4        => Quad

All the vertices are expected to be coplannar.

Interesting properties are:

 - vertices: the list of Vertices

 - material: the material used to draw the face's surface

 - double_sided: true if you want to see both sides of the Face. Default is false.

 - solid: true to enable the use of this Face for raypicking. Default is true.

 - lit: true to enable lighting on the Face. Default is true.

The following options are used when compiling the Face into a Model,
but does not affect the rendering of the Face itself:

 - static_lit: true to enable static lighting (faster). If true, when compiling the Face
	 into a Model, all Lights available will be applied as static lighting. Default is true.

 - smooth_lit: true to compute per-vertex normal vectors, instead of per-face normal vector.
	 This makes the Model looking smooth (see tutorial modeling-smoothlit-1.py).
	 Notice that Soya automatically disable smooth_lit between 2 faces that makes a sharp
	 angle (see ModelBuilder.max_face_angle attribute).
	 Default is false.
"""

class Atmosphere(_soya._Atmosphere):
	"""Atmosphere

An Atmosphere is an object that defines all the atmospheric attributes of a World, such
as fog, background or ambient lighting.

To apply an Atmosphere to a World, as well as everything inside the World, do :

		world.atmosphere = my_atmosphere

You can safely put several Worlds one inside the other, with different Atmospheres.

Attributes are :

 - fog: true to activate fog, false to disable fog (default value).

 - fog_color: the fog color (an (R, G, B, A) tuple of four floats). Defaults to black.

 - fog_type: the type of fog. fog_type can take 3 different values :
	 - 0, linear fog: the fog range from fog_start to fog_end (default value).
	 - 1, exponentiel fog: the fog the fog increase exponentially to fog_density and the distance.
	 - 2, exponentiel squared fog: the fog the fog increase exponentially to the square of fog_density and the distance.

 - fog_start: the distance at which the fog begins, if fog_type == 0. Defaults to 10.0.

 - fog_end: the distance at which the fog ends, if fog_type == 0. Defaults to 100.0.

 - fog_density: the fog density, if fog_type > 0. Defaults to 1.0.

 - ambient: the ambient lighting color (an (R, G, B, A) tuple of four floats). Defaults to (0.5, 0.5, 0.5, 1.0).

 - bg_color: the background color of the scene (an (R, G, B, A) tuple of four floats). Defaults to black.
"""

class NoBackgroundAtmosphere(_soya._NoBackgroundAtmosphere, Atmosphere):
	"""NoBackgroundAtmosphere

An Atmosphere with no background. It is usefull is you want to render a 3D scene over
another 3D scene."""

class SkyAtmosphere(_soya._SkyAtmosphere, Atmosphere):
	"""SkyAtmosphere

An Atmosphere with a skybox and/or a sky/cloud effect.

In addition to those of Atmosphere, attributes are :

 - sky_box: the sky box, a tuple of 5 or 6 materials that are displayed on the 6 faces of
	 the sky box (which is a cube). Use an empty tuple () to disable the sky box (default value).

 - sky_color: the color of the sky (an (R, G, B, A) tuple of four floats).
	 Use a sky_color with an alpha component of 0.0 to disable cloud / sky effet.

 - cloud: the cloud material, which is used to add a cloud-like effect to the sky.
	 Coulds move according to the camera.
"""

class Sprite(_soya._Sprite):
	"""Sprite

A 2D sprite, displayed as a 3D (e.g. think to very old 3D games).
Today, sprite are usefull for special effect like explosion, or halo.
The Sprite 2D texture always points toward the camera.

Attributes are :

 - material: the material of the Sprite, including the texture.

 - color: the color of the Sprite (defaults to white).

 - width and height: the size of the Sprite, in 3D coordinates values (not pixel values).
	 Both defaults to 0.5.

 - lit: if true (default), lighting affects the sprite, and if false, it doesn't."""

class CylinderSprite(_soya._CylinderSprite, Sprite):
	"""CylinderSprite

A special kind of Sprite, that points toward the camera only in X and Z dimension, but
not Y. This is usefull e.g. for lightening spell effects, for which using a normal Sprite
would give a poor rendering if seen from top."""

class Particles(_soya._Particles):
	pass

class Bonus(_soya._Bonus):
	pass

class Portal(_soya._Portal):
	
	# Implement in Python due to the lambda
	def pass_through(self, coordsyst):
		"""Portal.pass_though(self, coordsyst)

Makes COORDSYST pass through the portal. If needed (=if coordsyst.parent is self.parent),
it removes COORDSYST from its current parent and add it in the new one,
at the right location.
If coordsyst is a camera, it change the 'to_render' attribute too.

The passing through does NOT occur immediately, but after the beginning of the round
(this is usually what you need, in order to avoid that moving COORDSYST from a parent
to another makes it plays twice)."""
		def do_it():
			if isinstance(coordsyst, Camera) and coordsyst.to_render:
				coordsyst.to_render = self.beyond
			if coordsyst.parent is self.parent:
				self.beyond.add(coordsyst)
		MAIN_LOOP.next_round_tasks.append(do_it)
		
		
class Terrain(_soya._Terrain):
	pass

class TravelingCamera(_soya._TravelingCamera):
	pass

class ThirdPersonTraveling(_soya._ThirdPersonTraveling):
	pass

class FixTraveling(_soya._FixTraveling):
	pass


class AnimatedModel(Model, _soya._AnimatedModel):
	DIRNAME = "animated_models"
	SRC_DIRNAMES_EXTS = [("blender", ".blend")]
	_alls = weakref.WeakValueDictionary()
	
	def _export(klass, src, filename):
		if   src.endswith(".blend"):
			do_cmd("blender %s -P %s --blender2cal3d FILENAME=%s EXPORT_FOR_SOYA=1 XML=0 %s" % (
				src,
				os.path.join(os.path.dirname(__file__), "blender2cal3d.py"),
				os.path.join(os.path.dirname(src), os.pardir, AnimatedModel.DIRNAME, filename, filename + ".cfg"),
				(" CONFIG_TEXT=%s" % filename.split("@")[-1]) * bool("@" in filename),
				))
			
 	def _export(klass, src, filename):
 		if   src.endswith(".blend"):
 			if "@" in filename: config_text = filename.split("@")[-1]
 			else:               config_text = "-"
 			do_cmd("blender %s -P %s %s %s" % (
 				src,
 				os.path.join(os.path.dirname(__file__), "blender2cal3d_call.py"),
 				os.path.join(os.path.dirname(src), os.pardir, AnimatedModel.DIRNAME, filename, filename + ".cfg"),
 				config_text,
 				))
	_export = classmethod(_export)
	
	def load(klass, filename):
		filename = filename.replace("/", os.sep)
		dirname  = klass._get_directory_for_loading_and_check_export(filename, os.sep + filename + ".cfg")
		return parse_cal3d_cfg_file(os.path.join(dirname, klass.DIRNAME, filename, filename + ".cfg"))
	load = classmethod(load)

class CoordSystState(_soya._CoordSystState):
	"""CoordSystState

A State that take care of CoordSyst position, rotation and scaling.

CoordSystState extend CoordSyst, and thus have similar method (e.g. set_xyz, rotate_*,
scale, ...)"""
class CoordSystSpeed(_soya._CoordSystSpeed):
	"""CoordSystSpeed

A Coordinate System "speed" / derivation, taking into account position, rotation and scaling.

CoordSystSpeed extend CoordSyst, and thus have similar method (e.g. set_xyz, rotate_*,
scale, ...)"""
	
#ODE addition
class Mass(SavedInAPath, _soya._Mass):
	pass
class Joint(_soya._Joint,object):
	pass

if hasattr(_soya, "_Sound"):
	# Has sound / OpenAL support

	class Sound(SavedInAPath, _soya._Sound):
		"""Sound

	A sound.

	Use soya.Sound.get("filename.wav") for loading a sound from your data directory.

	Interesting attributes:
		- stereo: 1 if the sound is stereo, 0 otherwise.
	"""

		DIRNAME = "sounds"
		_alls = weakref.WeakValueDictionary()

		def save(klass, filename = None): raise NotImplementedError("Soya cannot save sound.")

		def load(klass, filename):
			if ".." in filename: raise ValueError("Cannot have .. in filename (security reason)!", filename)
			filename = filename.replace("/", os.sep)
			
			try:
				import pymedia
				has_pymedia = 1
			except:
				has_pymedia = 0
				
			has_pymedia = 0
				
			for p in path:
				file = os.path.join(p, klass.DIRNAME, filename)
				if os.path.exists(file):
					if has_pymedia:
						sound = PyMediaSound(file)
					else:
						if   file.endswith(".wav"): sound = WAVSound(file)
						elif file.endswith(".ogg"): sound = OGGVorbisSound(file)
						else: raise ValueError("Unsupported sound file format: %s!" % file)
					sound._filename = filename
					return sound
			raise ValueError("No %s named %s" % (klass.__name__, filename))
		load = classmethod(load)
		
		
	class PyMediaSound(_soya._PyMediaSound, Sound):
		"""PyMediaSound

	A sound loaded through PyMedia (support WAV, OGG Vorbis, MP3,...).

	Use soya.Sound.get("filename.xxx") for loading a sound from your data directory,
	or soya.PyMediaSound("/full/filename.xxx") for loading a sound from any directory."""

	class WAVSound(_soya._WAVSound, Sound):
		"""WAVSound

	A sound in WAV format.

	Use soya.Sound.get("filename.wav") for loading a sound from your data directory,
	or soya.WAVSound("/full/filename.wav") for loading a sound from any directory."""

	class OGGVorbisSound(_soya._OGGVorbisSound, Sound):
		"""OGGVorbisSound

	A sound in OGG Vorbis format.

	Use soya.Sound.get("filename.ogg") for loading a sound from your data directory,
	or soya.OGGVorbisSound("/full/filename.ogg") for loading a sound from any directory."""


	class SoundPlayer(_soya._SoundPlayer):
		"""SoundPlayer

	A SoundPlayer is a 3D object that play a sound.

	Interesting attributes:
		- sound      : the sound currently played (read-only)
		- loop       : if true, the sound restarts from the beginning when it ends; default is false
		- auto_remove: if true (default), the SoundPlayer is automatically removed when the sound ends (excepted in cases of looping!)
		- gain       : the body (default 1.0)
		- play_in_3D : if true, the sound is played as a 3D sound; if false, as a 2D sound. Notice that OpenAL cannot play stereo sound in 3D.

	Constructor is SoundPlayer(parent = None, sound = None, loop = 0, play_in_3D = 1, gain = 1.0, auto_remove = 1)

	The SoundPlayer.ended method is called when the sound ends, and can be overriden if needed.

	To stop

	"""

		def ended(self):
			"""SoundPlayer.ended()

	This method is called when the sound is over. It is NOT called if looping.

	The default implementation removes the SoundPlayer, if SoundPlayer.auto_remove is true."""
			# Implemented in Python because of the lambda
			if self.auto_remove:
				MAIN_LOOP.next_round_tasks.append(lambda: self.parent and self.parent.remove(self))
		


class Font(SavedInAPath, _soya._Font):
	DIRNAME = "fonts"
	_alls = weakref.WeakValueDictionary()

	def __init__(self, filename, width = 20, height = 30):
		_soya._Font.__init__(self, filename, width, height)
		self._filename = ""
		
	def load(klass, filename):
		width  = 20
		height = 30
		p = filename.split("@")
		filename2 = p[0]
		if len(p) > 1:
			width, height = map(int, p[1].split("x"))
		if ".." in filename2: raise ValueError("Cannot have .. in filename (security reason)!", filename2)
		filename2 = filename2.replace("/", os.sep)
		for p in path:
			file = os.path.join(p, klass.DIRNAME, filename2)
			if os.path.exists(file):
				font = Font(file, width, height)
				font._filename = filename
				return font
		raise ValueError("No %s named %s" % (klass.__name__, filename2))
	load = classmethod(load)
	
	def save(klass, filename = None): raise NotImplementedError("Soya cannot save font.")
	
	def availables(klass):
		"""SavedInAPath.availables() -> list

Returns the list of the filename all the objects available in the current path."""
		import dircache
		filenames = dict(klass._alls)
		for p in path:
			for filename in dircache.listdir(os.path.join(p, klass.DIRNAME)):
				filenames[filename] = 1
		filenames = filenames.keys()
		filenames.sort()
		return filenames
	availables = classmethod(availables)
	

class DisplayList(_soya._DisplayList):
	pass

_soya.Image            = Image
_soya.Material         = Material
_soya.Model            = Model
_soya.SimpleModel      = SimpleModel
_soya.SolidModel       = SolidModel
_soya.TreeModel        = TreeModel
_soya.CellShadingModel = CellShadingModel
_soya.Point            = Point
_soya.Vector           = Vector
_soya.Camera           = Camera
_soya.Light            = Light
_soya.Body             = Body
_soya.World            = World
#_soya.Cal3dBody        = Cal3dBody
_soya.AnimatedModel    = AnimatedModel
_soya.Face             = Face
_soya.Atmosphere       = Atmosphere
_soya.Portal           = Portal
_soya.Terrain          = Terrain
_soya.Particles        = Particles
_soya.Mass             = Mass
_soya.Joint            = Joint

DEFAULT_MATERIAL = Material()
DEFAULT_MATERIAL.filename  = "__DEFAULT_MATERIAL__"
DEFAULT_MATERIAL.shininess = 128.0
_soya._set_default_material(DEFAULT_MATERIAL)

PARTICLE_DEFAULT_MATERIAL = loads(open(os.path.join(DATADIR, "particle_default.data"), "rb").read())
PARTICLE_DEFAULT_MATERIAL.filename = "__PARTICLE_DEFAULT_MATERIAL__"
# PARTICLE_DEFAULT_MATERIAL = Material()
# PARTICLE_DEFAULT_MATERIAL.additive_blending = 1
# PARTICLE_DEFAULT_MATERIAL.texture = open_image(os.path.join(DATADIR, "fx.png"))
# PARTICLE_DEFAULT_MATERIAL.filename = "__PARTICLE_DEFAULT_MATERIAL__"
# PARTICLE_DEFAULT_MATERIAL.diffuse = (1.0, 1.0, 1.0, 1.0)
# PARTICLE_DEFAULT_MATERIAL.save("/home/jiba/src/soya/data/particle_default.data")
_soya._set_particle_default_material(PARTICLE_DEFAULT_MATERIAL)

SHADER_DEFAULT_MATERIAL = loads(open(os.path.join(DATADIR, "shader_default.data"), "rb").read())
SHADER_DEFAULT_MATERIAL.filename = "__SHADER_DEFAULT_MATERIAL__"
#SHADER_DEFAULT_MATERIAL = Material()
#SHADER_DEFAULT_MATERIAL.texture = open_image(os.path.join(DATADIR, "shader.png"))
#SHADER_DEFAULT_MATERIAL.filename = "__SHADER_DEFAULT_MATERIAL__"
#SHADER_DEFAULT_MATERIAL.diffuse = (1.0, 1.0, 1.0, 1.0)
#SHADER_DEFAULT_MATERIAL.save("/home/jiba/src/soya/data/shader_default.data")
_soya._set_shader_default_material(SHADER_DEFAULT_MATERIAL)


inited = 0


# Backward compatibility

Idler                = MainLoop
Volume               = Body
Cal3dVolume          = Body
Shape                = Model
SimpleShape          = SimpleModel
SolidShape           = SolidModel
CellShadingShape     = CellShadingModel
TreeShape            = TreeModel
Cal3dShape           = AnimatedModel
Land                 = Terrain

_soya.SimpleShapifier      = SimpleModelBuilder
_soya.CellShadingShapifier = CellShadingModelBuilder
_soya.SolidShapifier       = SolidModelBuilder
_soya.TreeShapifier        = TreeModelBuilder

Body.set_shape = Body.set_model
Body.shape     = Body.model
World.shapify  = World.to_model


