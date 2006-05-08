import os

import soya

import traceback

import soya
import soya.widget as widget
import soya.particle
import soya.sdlconst as sdlconst
import soya.cube 

import Image
import ImageDraw
import ImageFilter
import ImageChops

from math import fabs

import sys

sys.path.insert(0,'..')

import snowballz
import flying

# http://effbot.org/downloads/
from elementtree import ElementTree,ElementInclude

HERE = os.path.dirname(__file__)
DATADIR=os.path.normpath(os.path.join(HERE, "../data"))

class LevelError(Exception):
  pass

class NoCameraError(Exception):
  pass

def readColor(e):
  return (float(e.attrib['r']),float(e.attrib['g']),float(e.attrib['b']),float(e.attrib['a']))

def readXYZ(e):
  return (float(e.get('x',0.)),float(e.get('y',0.)),float(e.get('z',0)))

def readScale(e):
  sx=sy=sz=float(e.get('scale',1.0))

  sx=float(e.get('scale_x',sx))
  sy=float(e.get('scale_y',sy))
  sz=float(e.get('scale_z',sz))
    
  return (sx,sy,sz)

def rotate(obj,e):
  lateral=float(e.get('lateral',0.0))
  vertical=float(e.get('vertical',0.0))
  incline=float(e.get('incline',0.0))

  obj.rotate_lateral(lateral)
  obj.rotate_incline(incline)
  obj.rotate_vertical(vertical)

def simpleEditObj(obj=soya.root_widget):
  def run(o):
    import Tkinter
    editobj.edit(o)
    
    # tkinter does not like making more than one loop but
    # we dont need to worry about it 
    try:
      Tkinter.mainloop()
    except:
      pass

  t=threading.Thread(target=run,args=(obj,))
  t.setDaemon(True)
  t.start()


class LevelReader:
  """
  pass this an xml file and it will transform it into a soya.World for you 

  to use a subclass of soya.World you can pass level=myclass to __init__

  create functions to handle elements like do_land and do_atmosphere.

  child elements are handled like do_land_image and do_atmosphere_color

  get_camera function will attempt to create a soya.Camera  from the file 

  save(filename) will save the level and level static for you as filename and filename_static
  """

  def __init__(self,file=None,level=soya.World,verbose=False,volume_class=soya.Volume,elementtree=None):
    self.soyaVolume=volume_class
   
    self.infile=file

    if file:
      print "Reading:",file
      self.tree=ElementTree.parse(file)
    elif elementtree:
      self.tree=elementtree
      
    self.root=root=self.tree.getroot()
    ElementInclude.include(root)

    self.level=level()
    self.level_static=soya.World(self.level)
    self.materials={}

    self.verbose=verbose
    
    iter=root.getchildren()

    for element in iter:
      if verbose: print "Main Element:", element.tag,
      try:
        self.handle_element(element)
        if verbose: print "ok"
      except:
        raise LevelError('main error handling %s' % element.tag)

    self.done()
      
  def handle_element(self,e,parent='do_'):
    parent=parent+e.tag
    if self.verbose: print parent
    if hasattr(self,parent):
      try:
        getattr(self,parent)(e)
      except Exception,inst:
        traceback.print_exc()
        raise LevelError('error handling %s in %s\n msg was: %s' % (e.tag,parent,inst))

    parent+='_'

    for element in e.getchildren():
      self.handle_element(element,parent)

  def save(self,filename='xml_test'):
    path,filename=os.path.split(filename)

    level=self.level
    level_static=self.level_static
    level_static.filename=level.name=filename+"_static"
    level_static.save()
    level.filename=level.name=filename
    level.save()

  def done(self):
    pass

  def do_camera(self,e):
    # we dont really want to handle this but you might
    pass

  def get_camera(self,scene=None):
    e=self.root.find('camera')
    
    if e==None:
      raise NoCameraError("File has no camera")

    camera=soya.Camera(scene)
  
    camera.set_xyz(*readXYZ(e))
    camera.scale(5,5,5)
  
    rotate(camera,e)

    return camera

  def do_atmosphere(self,e):
    self.level.atmosphere=self.atmosphere=soya.SkyAtmosphere()
    
  def do_atmosphere_ambient(self,e):
    self.atmosphere.ambient=readColor(e)  

  def do_atmosphere_skybox(self,e):
    front=e.get('front')
    right=e.get('right')
    back=e.get('back')
    left=e.get('left')
    bottom=e.get('bottom')
    top=e.get('top')

    f=soya.Material(texture=soya.Image.get(front))
    r=soya.Material(texture=soya.Image.get(right))
    b=soya.Material(texture=soya.Image.get(back))
    l=soya.Material(texture=soya.Image.get(left))
    bt=soya.Material(texture=soya.Image.get(bottom))
    t=soya.Material(texture=soya.Image.get(top))
    
    self.atmosphere.set_sky_box(f,r,b,l,bt,t) 
  
  def do_atmosphere_fog(self,e):
    if e.attrib.has_key('on'):
      self.atmosphere.fog=int(e.attrib['on'])

    if e.attrib.has_key('type'):
      self.atmosphere.fog_type=int(e.attrib['type'])

    if e.attrib.has_key('start'):
      self.atmosphere.fog_start=float(e.attrib['start'])

    if e.attrib.has_key('end'):
      self.atmosphere.fog_end=float(e.attrib['end'])
  
  def do_atmosphere_fog_color(self,e):
      self.atmosphere.fog_color = self.atmosphere.bg_color=readColor(e)
  
  def do_atmosphere_skyplane(self,e):
    if e.attrib.has_key('on'):
      self.atmosphere.skyplane=int(e.attrib['on'])

  def do_atmosphere_bg_color(self,e):
    print self.atmosphere.bg_color
    self.atmosphere.bg_color=readColor(e)
    print self.atmosphere.bg_color

    print "bg_color"
    
  def do_atmosphere_skyplane_color(self,e):
    self.atmosphere.sky_color=readColor(e)
  
  def do_lights(self,e):
    pass

  def do_lights_light(self,e):
    print "light"
    self.currentlight=light=soya.Light(self.level)

    light.cast_shadow=int(e.get('cast_shadow',0))
    print "set shadow",light.cast_shadow
     
    if e.attrib.has_key('directional'):
      light.directional=int(e.attrib['directional'])

    if e.attrib.has_key('vertical'):
      light.rotate_vertical(float(e.attrib['vertical']))

  def do_lights_light_diffuse(self,e):
    self.currentlight.diffuse=readColor(e)

  def do_land(self,e):
    self.land=soya.Land(self.level_static)

    self.land.set_xyz(*readXYZ(e))
    self.land.scale(*readScale(e))

    # we must do this as we need the land image loaded before setting attributes
    self.first_do_land_image(e.find('image'))
    
    self.land.multiply_height(float(e.get('multiply_height',1.0)))

    self.land.map_size=int(e.get('map_size',8))

    self.land.scale_factor=float(e.get('scale_factor',1.0))

    self.land.texture_factor=float(e.get('texture_factor',1.0))

    self.land.texture_factor=float(e.get('split_factor',1.0))

  def do_land_material(self,material):
    name=material.attrib['name']
    start=material.attrib['start']
    end=material.attrib['end']

    self.land.set_material_layer(self.materials[name],float(start),float(end))

  def first_do_land_image(self,e):
    self.land.from_image(soya.Image.get(e.attrib['get']))

  def do_objects(self,e):
    pass

  def do_objects_object(self,e):
    get=e.attrib['get']
  
    print "object",get

    mat=e.get('material',None)

    obj=soya.Shape.get(get)
    
    if mat:
      obj.material=self.materials[mat]
    
    self.lastobject=vol=self.soyaVolume(self.level_static,obj)
    vol.set_xyz(*readXYZ(e))
    rotate(vol,e)
    vol.shadow=1
    vol.scale(*readScale(e))

  def do_objects_smoke(self,e):
    print "doing smoke"
    smoke=soya.particle.Smoke(self.level_static)
    smoke.nb_max_particles=10
    smoke.auto_generate_particle=True
    smoke.set_xyz(*readXYZ(e))

  def do_objects_fountain(self,e):
    print "doing fountain"
    fountain=soya.particle.Fountain(self.level_static)

  def do_materials(self,e):
    pass

  def do_materials_material(self,e):
    name=e.attrib['name']
    if e.attrib.has_key('get'):
      get=e.attrib['get']
      self.materials[name]=soya.Material.get(get)
    else:
      self.materials[name]=material=soya.Material()
      material.diffuse=readColor(e.find('diffuse'))
      material.specular=readColor(e.find('specular'))
      material.emmisive=readColor(e.find('emmisive'))
      material.shininess=float(e.get('shininess',1.0))
      material.seperate_specular=int(e.get('seperate_specular',1))

