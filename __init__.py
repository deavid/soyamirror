# Soya 3D
# Copyright (C) 2001-2004 Jean-Baptiste LAMY -- jiba@tuxfamily.org
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

import sys, os, os.path, weakref,cPickle as  pickle

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
          
        

# try:
#   from twisted.spread.jelly import Jellyable
# except ImportError:
#   class Jellyable  : pass
  
# class PythonObj(Jellyable, object):
#   def getStateFor(self, jellier):
#     # Needed, because recursive tuples cannot be loaded by Jelly
#     state = list(self.__getstate__())
#     if isinstance(state[0], tuple): state[0] = list(state[0])
#     return state
  
#   def _unjellyable_factory(clazz, state):
#     o = clazz.__new__(clazz)
#     print state
#     o.__setstate__(state)
#     return o
#   _unjellyable_factory = classmethod(_unjellyable_factory)
  
  
  
path = []

_SAVING = None # The object currently being saved. XXX not thread-safe, hackish

def _getter(klass, filename): return klass._reffed(filename)
_loader = _getter

class SavedInAPath(object):
  """SavedInAPath

Base class for all objects that can be saved in a path, such as Material,
World,..."""
  DIRNAME = ""
  
  def _check_export(klass, exported_filename, filename, *source_dirnames):
    """_check_export(FILENAME, *(SOURCE_DIRNAME, SOURCE_FILENAME)) -> (SOURCE_DIRNAME, SOURCE_FULL_FILENAME, FULL_FILENAME)

Search soya.path for a file FILENAME.data in the self.DIRNAME directory,
and check if the file needs to be re-exporter from any of the SOURCE_DIRNAMES directory.

Returned tuple :
FULL_FILENAME is the complete filename of the object.
If SOURCE_DIRNAME is None, the exported object is up-to-date.
If SOURCE_DIRNAME is one of SOURCE_DIRNAMES, the source object of this directory have been
modified more recently that the exported one, and SOURCE_FULL_FILENAME is the complete
filename of the source that needs to be re-exported."""
    filename        = filename.replace("/", os.sep)
    #source_filename = filename[:filename.index("@")]
    for p in path:
      file        = os.path.join(p, klass.DIRNAME , exported_filename)
      
      if   os.path.exists(file):
        for source_dirname, source_filename in source_dirnames:
          source_file = os.path.join(p, source_dirname, source_filename)
          if os.path.exists(source_file) and (os.path.getmtime(file) < os.path.getmtime(source_file)):
            print "* Soya * Converting %s to %s..." % (source_file, klass.__name__)
            return source_dirname, source_file, file
        return None, None, file
      else:
        for source_dirname, source_filename in source_dirnames:
          source_file = os.path.join(p, source_dirname, source_filename)
          if os.path.exists(source_file):
            print "* Soya * Converting %s to %s..." % (source_file, klass.__name__)
            return source_dirname, source_file, file
          
    raise ValueError("No %s or %s named %s" % (klass.__name__, source_dirnames, filename))
  _check_export = classmethod(_check_export)
  
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
    filename = filename.replace("/", os.sep)
    for p in path:
      file = os.path.join(p, klass.DIRNAME, filename + ".data")
      if os.path.exists(file):
        obj = klass._alls[filename] = pickle.loads(open(file, "rb").read())
        obj.loaded()
        return obj
    raise ValueError("No %s named %s" % (klass.__name__, filename))
  load = classmethod(load)
  _reffed = get
  
  def loaded(self): pass
  
  def save(self, filename = None):
    """SavedInAPath.save(filename = None)

Saves this object. If no FILENAME is given, the object is saved in the path,
using its filename attribute. If FILENAME is given, it is saved at this
location."""
    global _SAVING
    try:
      _SAVING = self # Hack !!
      #pickle.dump(self, open(filename or os.path.join(path[0], self.DIRNAME, self.filename.replace("/", os.sep)) + ".data", "wb"), 1)
      # Avoid destroying the file if the serialization causes an error.
      data = pickle.dumps(self, 1)
      open(filename or os.path.join(path[0], self.DIRNAME, self.filename.replace("/", os.sep)) + ".data", "wb").write(data)
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
  
#   def getStateFor(self, jellier):
#     if (not _SAVING is self) and self._filename: # self is saved in another file, save filename only
#       return self._filename
#     return super(SavedInAPath, self).getStateFor(jellier)
  
#   def _unjellyable_factory(clazz, state):
#     if isinstance(state, basestring):
#       if issubclass(clazz, CoordSyst): return clazz.load(state)
#       else:                            return clazz.get (state)
#     return super(SavedInAPath, clazz)._unjellyable_factory(state)
#   _unjellyable_factory = classmethod(_unjellyable_factory)
  
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
      for filename in dircache.listdir(os.path.join(p, klass.DIRNAME)):
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
    filename = filename.replace("/", os.sep)
    for p in path:
      file = os.path.join(p, klass.DIRNAME, filename)
      if os.path.exists(file): return open_image(file)
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
  _alls = weakref.WeakValueDictionary()
  
  def load(klass, filename):
    need_export, image_file, file = klass._check_export(filename + ".data", filename, (Image.DIRNAME, filename + ".png"), (Image.DIRNAME, filename + ".jpeg"))
    if need_export:
      image = Image.get(os.path.basename(image_file))
      if os.path.exists(file): material = pickle.loads(open(file, "rb").read())
      else:
        material = Material()
        material._filename = filename
      material.texture = image
      try: material.save()
      except:
        sys.excepthook(*sys.exc_info())
        print "* Soya * WARNING : can't save material %s!" % filename
      return material
    else:
      obj = pickle.loads(open(file, "rb").read())
      obj.loaded()
      return obj

  load = classmethod(load)

class PythonMaterial(_soya._PythonMaterial, Material):
  pass

class PythonIdleingMaterial(_soya._PythonIdleingMaterial, Material):
  pass

class Shape(SavedInAPath, _soya._Shape):
  """Shape

A Shape is an optimized model. Shapes cannot be modified, but they are rendered very
quickly, and they can be used several time, e.g. if you want to 2 same cubes in a scene.
Shapes are used in conjunction with Volume."""
  DIRNAME = "shapes"
  _alls = weakref.WeakValueDictionary()
  
  def load(klass, filename):
    need_export, world_file, file = klass._check_export(filename + ".data", filename, (World.DIRNAME, filename + ".data"), ("blender", filename.split("@")[0] + ".blend"), ("obj", filename + ".obj"), ("obj", filename + ".mtl"), ("3ds", filename + ".3ds"))
    if need_export:
      shape = World.get(filename).shapify()
      shape._filename = filename
      try: shape.save()
      except:
        sys.excepthook(*sys.exc_info())
        print "* Soya * WARNING : can't save compiled shape %s!" % filename
      return shape
    else:
      obj = pickle.loads(open(file, "rb").read())
      obj.loaded()
      return obj
  load = classmethod(load)
  
  def availables(klass): return World.availables()
  availables = classmethod(availables)
  
  
class SimpleShape(Shape, _soya._SimpleShape):
  """SimpleShape

The most basic class of Shape."""
  
class SolidShape(_soya._SolidShape, SimpleShape):
  """SolidShape

Like SimpleShape, but when the shape intersects the camera, the section is drawn.
Usefull for light effects."""
  
class TreeShape(Shape, _soya._TreeShape):
  """TreeShape

A Shape that use a BSP-like tree to optimize rendering and raypicking."""

class CellShadingShape(Shape, _soya._CellShadingShape):
  """CellShadingShape

A Shape that use cell-shading for rendering."""


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
  
  
class Volume(_soya._Volume):
  """Volume

A Volume is a Soya 3D object that display a Shape. The Volume contains data about the
position, the orientation and the scaling, and the Shape contains the geometric data.

This separation allows to use several time the same Shape at different position, without
dupplicating the geometric data.

Attributes are (see also CoordSyst for inherited attributes):

 - shape : the Shape (a Shape object, defaults to None).
"""
  pass

def do_cmd(cmd):
  print "* Soya * Running '%s'..." % cmd
  os.system(cmd)
  
class World(SavedInAPath, _soya._World, Volume):
  """World

A World is a Soya 3D object that can contain other Soya 3D objects, including other Worlds.
Worlds are used to group 3D objects ; when a World is moved, all the objects it contains
are moved too, since they are part of the World.
Mostly for historical reasons, World is a subclass of Volume, and thus can display a Shape.

Worlds can be saved in the "worlds" directory ; see SavedInAPath.

Attributes are (see also Volume, CoordSyst and SavedInAPath for inherited attributes):

 - children : the list of 3D object contained in the World (default to an empty list).
   use World.add(coordsyst) and World.remove(coordsyst) for additions and removals.

 - atmosphere : the atmosphere specifies atmospheric properties of the World (see
   Atmosphere). Default is None.

 - shapifier : the shapifier specifies how the World is compiled into Shape.
   Default is None, which result in the use of the default Shapifier, which is
   SimpleShapifier().
"""

  DIRNAME = "worlds"
  _alls = weakref.WeakValueDictionary()
  
  def load(klass, filename):
    need_export, source_file, file = klass._check_export(filename + ".data", filename, ("blender", filename.split("@")[0] + ".blend"), ("obj", filename + ".obj"), ("obj", filename + ".mtl"), ("3ds", filename + ".3ds"))
    if need_export:
      if   need_export == "blender":
        extra = ""
        if "@" in filename:
          extra += "CONFIG_TEXT=%s" % filename[filename.index("@") + 1:]
            
        do_cmd("blender %s -P %s --blender2soya FILENAME=%s %s" % (
          source_file,
          os.path.join(os.path.dirname(__file__), "blender2soya.py"),
          filename,
          extra,
          ))
        
      elif need_export == "obj":
        import soya.objmtl2soya
        world = soya.objmtl2soya.loadObj(os.path.splitext(source_file)[0] + ".obj")
        world.filename = filename
        world.save()
        return world
      
      elif need_export == "3ds":
        import soya._3DS2soya
        world = soya._3DS2soya.load_3ds(os.path.splitext(source_file)[0] + ".3ds")
        world.filename = filename
        world.save()
        return world
      
    obj = pickle.loads(open(file, "rb").read())
    obj.loaded()
    return obj
  load = classmethod(load)
  _reffed = load
  

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
 - cast_shadow : True if the light cast shadows on Shapes that have shadows enabled.
   Default is true.
 - shadow_color : the color of the shadow . Default is a semi-transparent black
   (0.0, 0.0, 0.0, 0.5).
 - top_level : XXX ???
 - static : True if the light can be used for static lighting when compiling a World into
   a Shape. Default is true.
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
then compile the World into a Shape (see the modeling-X.py tutorial series).

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

The following options are used when compiling the Face into a Shape,
but does not affect the rendering of the Face itself:

 - static_lit: true to enable static lighting (faster). If true, when compiling the Face
   into a Shape, all Lights available will be applied as static lighting. Default is true.

 - smooth_lit: true to compute per-vertex normal vectors, instead of per-face normal vector.
   This makes the Shape looking smooth (see tutorial modeling-smoothlit-1.py).
   Notice that Soya automatically disable smooth_lit between 2 faces that makes a sharp
   angle (see Shapifier.max_face_angle attribute).
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
    IDLER.next_round_tasks.append(do_it)
    
    
class Land(_soya._Land):
  pass

class WaterCube(_soya._WaterCube):
  pass

class TravelingCamera(_soya._TravelingCamera):
  pass

class ThirdPersonTraveling(_soya._ThirdPersonTraveling):
  pass

class FixTraveling(_soya._FixTraveling):
  pass

class Cal3dVolume(_soya._Cal3dVolume):
  pass

class Cal3dShape(Shape, _soya._Cal3dShape):
  def load(klass, filename):
    need_export, source_file, file = klass._check_export(os.path.join(filename, filename + ".cfg"), filename, ("blender", filename.split("@")[0] + ".blend"))
    if need_export:
      if need_export == "blender":
        extra = ""
        if "@" in filename:
          extra += "CONFIG_TEXT=%s" % filename[filename.index("@") + 1:]
          
        do_cmd("blender %s -P %s --blender2cal3d FILENAME=%s EXPORT_FOR_SOYA=1 XML=0 %s" % (
          source_file,
          os.path.join(os.path.dirname(__file__), "blender2cal3d.py"),
          os.path.join(os.path.dirname(source_file), "..", "shapes", filename, filename + ".cfg"),
          extra,
          ))
        
    return parse_cal3d_cfg_file(file)
  load = classmethod(load)

_soya.Image            = Image
_soya.Material         = Material
_soya.Shape            = Shape
_soya.SimpleShape      = SimpleShape
_soya.SolidShape       = SolidShape
_soya.TreeShape        = TreeShape
_soya.CellShadingShape = CellShadingShape
_soya.Point            = Point
_soya.Vector           = Vector
_soya.Camera           = Camera
_soya.Light            = Light
_soya.Volume           = Volume
_soya.World            = World
_soya.Cal3dVolume      = Cal3dVolume
_soya.Cal3dShape       = Cal3dShape
_soya.Face             = Face
_soya.Atmosphere       = Atmosphere
_soya.Portal           = Portal
_soya.Land             = Land
_soya.WaterCube        = WaterCube
_soya.Particles        = Particles

DEFAULT_MATERIAL = Material()
DEFAULT_MATERIAL.filename  = "__DEFAULT_MATERIAL__"
DEFAULT_MATERIAL.shininess = 128.0
_soya._set_default_material(DEFAULT_MATERIAL)

PARTICLE_DEFAULT_MATERIAL = pickle.load(open(os.path.join(DATADIR, "particle_default.data"), "rb"))
PARTICLE_DEFAULT_MATERIAL.filename = "__PARTICLE_DEFAULT_MATERIAL__"
# PARTICLE_DEFAULT_MATERIAL = Material()
# PARTICLE_DEFAULT_MATERIAL.additive_blending = 1
# PARTICLE_DEFAULT_MATERIAL.texture = open_image(os.path.join(DATADIR, "fx.png"))
# PARTICLE_DEFAULT_MATERIAL.filename = "__PARTICLE_DEFAULT_MATERIAL__"
# PARTICLE_DEFAULT_MATERIAL.diffuse = (1.0, 1.0, 1.0, 1.0)
# PARTICLE_DEFAULT_MATERIAL.save("/home/jiba/src/soya/data/particle_default.data")
_soya._set_particle_default_material(PARTICLE_DEFAULT_MATERIAL)

SHADER_DEFAULT_MATERIAL = pickle.load(open(os.path.join(DATADIR, "shader_default.data"), "rb"))
SHADER_DEFAULT_MATERIAL.filename = "__SHADER_DEFAULT_MATERIAL__"
#SHADER_DEFAULT_MATERIAL = Material()
#SHADER_DEFAULT_MATERIAL.texture = open_image(os.path.join(DATADIR, "shader.png"))
#SHADER_DEFAULT_MATERIAL.filename = "__SHADER_DEFAULT_MATERIAL__"
#SHADER_DEFAULT_MATERIAL.diffuse = (1.0, 1.0, 1.0, 1.0)
#SHADER_DEFAULT_MATERIAL.save("/home/jiba/src/soya/data/shader_default.data")
_soya._set_shader_default_material(SHADER_DEFAULT_MATERIAL)


inited = 0


