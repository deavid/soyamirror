import os,sys

import soya
import soya.widget as widget
from soya.opengl import *

from math import fabs

HERE = os.path.dirname(__file__)
DATADIR=os.path.normpath(os.path.join(HERE, "../data"))
soya.path.append(DATADIR)
sys.path.append(os.path.normpath(os.path.join(HERE, "../")))

import threading

import traceback

from LevelReader import *
LevelReader.HERE=HERE
LevelReader.DATAIDR=DATADIR
LevelReader.FONTDIR=os.path.join(DATADIR,'fonts')

class ExplorerIdler(soya.Idler):
  XAXIS=0
  YAXIS=1
  ZAXIS=2
  NOAXIS=4

  def __init__(self,*scenes):
    """ ghost like mouse look idler
    
    expects to find globals "camera" and "lblRotInfo"

    use mouse to look 
    first mouse button to move forward
    right mouse button to select an object ( selection is taken from middle of the screen not mouse pointer! )
    left cntrl and mouse to "zoom" blender style
    F1 to turn mouse grab on and off
    t "teleports" to a location. get object in center of screen and press z to move there
    g to grab and move the selected object
    r to turn on rotation of the selected object
      when rotating press x,y or z to change rotation axis
    """

    soya.Idler.__init__(self,*scenes)

    self.speed=soya.Vector(camera)
    
    # are we grabbing the cursor?
    self.grab_cursor=0

    # are we zooming?
    self.zoom=0

    # are we dragging the selected object?
    self.drag=0

    # are we rotateing the selected object?
    self.rotating=0

    self.axis=self.XAXIS

    # camera rotation
    self.roty=0.
    self.rotx=0.

    self.selectedObject=None

    self.scene=scenes[0]

    self.stop_mouse_grab()

  def idle(self):
    # warping the mouse or init'ing sdl seems to cause a few to many
    # mouse events. this clears all the events that are currently in the
    # queue
    soya.clear_events()

    soya.Idler.idle(self)

  def select_object(self,obj=None):
    if obj!=None:
      self.selectedObject=obj
    else:
      self.selectedObject=None

  def on_key_down(self,event):
    if event[1]==sdlconst.K_ESCAPE:
      # i have always used sys.exit but i noticed that this is probably nicer
      self.stop()
    
    elif event[1]==sdlconst.K_w:
      self.speed.z+=-.8
    elif event[1]==sdlconst.K_s:
      self.speed.z+=.8

    elif event[1]==sdlconst.K_a:
      self.speed.x+=-.8
    elif event[1]==sdlconst.K_d:
      self.speed.x+=.8

    elif event[1]==sdlconst.K_LCTRL:
      self.zoom=1
    
    elif event[1]==sdlconst.K_SPACE:
      self.speed.x=0.
      self.speed.y=0.
      self.speed.z=0.

      #soya.Idler(scene).idle()

    elif event[1]==sdlconst.K_F1:
      if soya.get_grab_input()==0:
        soya.cursor_set_visible(0)
        soya.set_grab_input(1)
      else:
        soya.cursor_set_visible(1)
        soya.set_grab_input(0)
    elif event[1]==sdlconst.K_F2:
      print "save"
      level.save(options.output)

    elif event[1]==sdlconst.K_g and self.selectedObject:
      if self.drag==0:
        self.drag=1
        self.axis=self.NOAXIS
      else:
        self.drag=0

    elif event[1]==sdlconst.K_r and self.selectedObject:
      if self.rotating==0:
        self.rotating=1
      else:
        self.rotating=0

    elif event[1]==sdlconst.K_x:
      self.axis=self.XAXIS
    elif event[1]==sdlconst.K_y:
      self.axis=self.YAXIS
    elif event[1]==sdlconst.K_z:
      self.axis=self.ZAXIS
    elif event[1]==sdlconst.K_n:
      self.axis=self.NOAXIS

    elif event[1]==sdlconst.K_t:
      # see if we can pick something and then "teleport" to it 
      context=scene.RaypickContext(camera.position(),50.)
      r=context.raypick(camera.position(),soya.Vector(camera,0.0,0.0,-1.0),50.0,3)

      if r:
        camera.move(r[0]-soya.Vector(camera,0.,0.,-3.))

  def on_key_up(self,event):
    if event[1]==sdlconst.K_w:
      self.speed.z=0
      if self.speed.z<-1.: self.speed.z=-1.
    elif event[1]==sdlconst.K_s:
      self.speed.z=0
      if self.speed.z>1.: self.speed.z=1.

    elif event[1]==sdlconst.K_a:
      self.speed.x=0
    elif event[1]==sdlconst.K_d:
      self.speed.x=0

    elif event[1]==sdlconst.K_LCTRL:
      self.zoom=0
      self.speed.z=0.
    
  def on_mouse_button_down(self,event):
    if event[1]==2:
      self.start_mouse_grab()
    elif event[1]==1:
      mouse = camera.coord2d_to_3d(event[2], event[3])
      
      result = scene.raypick(camera, camera.vector_to(mouse))
      
      obj=None
      
      if result:
        obj = result[0].parent
       
      self.select_object(obj)

    return
    
    self.rotating=0
    self.drag=0

    if event[1]==1:
      self.speed.z=-.8
    if event[1]==3:
      # see if we can pick something and then "teleport" to it 
      context=scene.RaypickContext(camera.position(),50.)
      r=context.raypick(camera.position(),soya.Vector(camera,0.0,0.0,-1.0),50.0,3)
      
      if r:
        self.select_object(r[0].parent)
      else:
        self.select_object()

  def on_mouse_button_up(self,event):
    self.stop_mouse_grab()

    self.speed.z=0

  def start_mouse_grab(self):
    soya.cursor_set_visible(0)
    soya.set_grab_input(1)
    soya.set_mouse_pos(camera.width/2,camera.height/2)
    soya.clear_events()
    Rx,ry=soya.get_mouse_rel_pos()
    
    self.grab_cursor=1

  def stop_mouse_grab(self):
    self.grab_cursor=0
    soya.cursor_set_visible(1)
    soya.set_grab_input(0)

  def on_mouse_motion(self,event):
    if not self.grab_cursor:
      return
    
    #event_type,mx,my,relx,rely,buttons=event

    # scale the rotation amount by some arbitary amounts 
    rx=-float(event[3])/4.
    ry=-float(event[4])/6.

    # my mouse is too sensitive!
    if rx<1. and rx>-1.:
      rx=0.

    if ry<1. and ry>-1.:
      ry=0.

    if self.zoom==1:
      self.speed.z-=ry/10.
    
    elif self.drag==1:
      if not self.selectedObject: return 

      if self.axis==self.NOAXIS:
         self.selectedObject.add_vector(soya.Vector(camera,-rx/2.,ry/2.,0.))
      elif self.axis==self.XAXIS:
         self.selectedObject.add_vector(soya.Vector(camera,-rx/2.,0.,0.))
      elif self.axis==self.YAXIS:
         self.selectedObject.add_vector(soya.Vector(camera,0.,ry/2.,0.))
      elif self.axis==self.ZAXIS:
         self.selectedObject.add_vector(soya.Vector(camera,0.,0.,ry/2.))

    elif self.rotating==1:
      if not self.selectedObject: return 

      if self.axis==self.XAXIS:
        self.selectedObject.rotate_lateral(rx)
      elif self.axis==self.YAXIS:
        self.selectedObject.rotate_vertical(rx)
      elif self.axis==self.ZAXIS:
        self.selectedObject.rotate_incline(rx)
      
    else:  
      # constrain the rotation to <360
      rotx=self.rotx+rx
      if rotx>360. or rotx<-360.: rotx = rotx % 360.
      
      roty=self.roty+ry

      # constrain y rotation so we cant break our necks
      if roty<-90.:
        ry=0.
        roty=-90.

      if roty>90.:
        ry=0.
        roty=90.

      self.roty=roty
      self.rotx=rotx

      camera.turn_vertical(ry)
      camera.rotate_lateral(rx)

      # update our label 
      #lblRotInfo.text="%.2f %.2f %.2f %.2f %.2f" % (camera.x,camera.y,camera.z,self.rotx,self.roty)

  def resize(self):
    pass

  def event_filter(self,event):
    return False

  def begin_round(self):
    for event in soya.process_event():
      if self.event_filter(event):
        pass
      elif event[0]==sdlconst.QUIT:
        self.stop()
      elif event[0]==sdlconst.VIDEORESIZE:
        self.resize()
      elif event[0]==sdlconst.KEYDOWN:
        self.on_key_down(event)
      elif event[0]==sdlconst.KEYUP:
        self.on_key_up(event)
      elif event[0]==sdlconst.MOUSEBUTTONDOWN:
        self.on_mouse_button_down(event)
      elif event[0]==sdlconst.MOUSEBUTTONUP:
        self.on_mouse_button_up(event)
      elif event[0]==sdlconst.MOUSEMOTION:
        self.on_mouse_motion(event)
    
    #lblRotInfo.text="%.2f %.2f %.2f %.2f %.2f" % (camera.x,camera.y,camera.z,self.rotx,self.roty)
    soya.Idler.begin_round(self)

  def advance_time(self,proportion):
    soya.Idler.advance_time(self,proportion)
    camera.add_mul_vector(proportion,self.speed)

class SelectionMarker(soya.PythonCoordSyst):
  def __init__(self,parent=None,material=None):
    soya.PythonCoordSyst.__init__(self,parent)

    self._material=material or soya.DEFAULT_MATERIAL

  def batch(self):
    return 2,self,None

  def render(self):
    glDisable(GL_CULL_FACE)
    glDisable(GL_DEPTH_TEST)
    glDisable(GL_LIGHTING)
    
    glColor4f(1.,0.,0.,1.)

    glBegin(GL_LINES)
    glColor4f(1.,0.,0.,1.)
    glVertex3f(0.,0.,0.)
    glVertex3f(1.,0.,0.)
    glColor4f(0.,1.,0.,1.)
    glVertex3f(0.,0.,0.)
    glVertex3f(0.,1.,0.)
    glColor4f(0.,0.,1.,1.)
    glVertex3f(0.,0.,0.)
    glVertex3f(0.,0.,1.)
    glEnd()

    glEnable(GL_LIGHTING)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_CULL_FACE)

class WidgetedExplorerIdler(ExplorerIdler):
  def __init__(self,*scenes):
    ExplorerIdler.__init__(self,*scenes)

    import pyui
    
    self.renderer=renderer=soyapyui.OpenGLSoya(camera.width,camera.height,'title',0)
    theme=SoyaTheme(renderer)
    self.desktop=desktop=pyui.desktop.Desktop(renderer,camera.width,camera.height,0,theme)

    # erg... im not sure about all this 
    self.desktop.registerHandler(pyui.locals.MOUSEMOVE, self.pyui_mousemove)
    self.desktop.registerHandler(pyui.locals.LMOUSEBUTTONDOWN, self.pyui_lmousedown)
    self.desktop.registerHandler(pyui.locals.LMOUSEBUTTONUP  , self.pyui_lmouseup)
    self.desktop.registerHandler(pyui.locals.RMOUSEBUTTONDOWN, self.pyui_rmousedown)
    self.desktop.registerHandler(pyui.locals.RMOUSEBUTTONUP  , self.pyui_rmouseup)
    self.desktop.registerHandler(pyui.locals.MMOUSEBUTTONDOWN, self.pyui_mmousedown)
    self.desktop.registerHandler(pyui.locals.MMOUSEBUTTONUP  , self.pyui_mmouseup)
    self.desktop.registerHandler(pyui.locals.KEYDOWN, self.pyui_keydown)
    self.desktop.registerHandler(pyui.locals.KEYUP  , self.pyui_keyup)

    pyw=soyapyui.PyuiWrapper(desktop)

    import pyui.colors
    pyui.colors.init(renderer)

    pyui.core.gRenderer=renderer
    pyui.core.gDesktop=desktop

    def set_all_dirty():
      for w in desktop.windows:
        w.setDirty()

    self.next_round_tasks.append(set_all_dirty)
   
    self.create_widgets()

    #mat=soya.Material(texture=soya.Image.get('littlestar.png'))
    #mat2=soya.Material(texture=soya.Image.get('sun.png'))
    self.selectedObjectMarker=SelectionMarker()
    
  def update_marker(self):
    self.selectedObjectMarker.matrix=self.selectedObject.matrix
    #self.selectedObjectMarker.move(self.selectedObject)
    #self.selectedObjectMarker.scale_x=self.selectedObject.scale_x
    #self.selectedObjectMarker.scale_y=self.selectedObject.scale_y
    #self.selectedObjectMarker.scale_z=self.selectedObject.scale_z
    print dir(self.selectedObject)

  def handleEvent(self,e):
    print "weird event!!",e
  
  def pyui_mousemove(self,event):
    #event_type,mx,my,relx,rely,buttons=event
    rx,ry=soya.get_mouse_rel_pos()
    self.on_mouse_motion((event.type,event.pos[0],event.pos[1],rx,ry))

  def pyui_lmousedown(self,event):
    self.on_mouse_button_down((event.type,1,event.pos[0],event.pos[1]))

  def pyui_lmouseup(self,event):
    self.on_mouse_button_up((event.type,1,event.pos[0],event.pos[1]))

  def pyui_mmousedown(self,event):
    self.on_mouse_button_down((event.type,2,event.pos[0],event.pos[1]))

  def pyui_mmouseup(self,event):
    self.on_mouse_button_up((event.type,2,event.pos[0],event.pos[1]))

  def pyui_rmousedown(self,event):
    self.on_mouse_button_down((event.type,3,event.pos[0],event.pos[1]))

  def pyui_rmouseup(self,event):
    self.on_mouse_button_up((event.type,3,event.pos[0],event.pos[1]))

  def pyui_keyup(self,event):
    self.on_key_up((event.type,event.key))
    
  def pyui_keydown(self,event):
    self.on_key_down((event.type,event.key))

  def create_widgets(self):
    soya.root_widget.add(widget.FPSLabel())

    self.menuBar=pyui.widgets.MenuBar()

    self.mnuFile=self.MnuFile(self)
    self.menuBar.addMenu(self.mnuFile)
    
    self.mnuView=self.MnuView(self)
    self.menuBar.addMenu(self.mnuView)
    
    self.mnuWindows=self.MnuWindows(self)
    self.menuBar.addMenu(self.mnuWindows)

    self.mnuHelp=pyui.widgets.Menu('Help')
    self.menuBar.addMenu(self.mnuHelp)
    
    #self.wndSelected=self.WndSelected(self,10,100,250,200,'Selected Info')
    
    self.wndTransform=self.WndTransform(self,camera.width-160,100,120,200,'Transform')
    
    self.wndSelected=self.WndOutliner(self,10,300,250,200,'Outliner')
    self.wndInfo=self.WndInfo(self,10,camera.height-100,250,80,'Info')
    
    self.wndInfo.update_widgets(self)
    self.wndInfo.lblSelInfo.setText("Sel:" +str(self.selectedObject))
    #self.wndSelected.update_widgets(self)

  def update_widgets(self):
    self.wndInfo.update_widgets(self)

  def begin_round(self):
    soya.Idler.begin_round(self)
    #ExplorerIdler.begin_round(self)

    self.renderer.update()
    self.desktop.update()
    
    self.update_widgets()
  
  def advance_time(self,proportion):
    ExplorerIdler.advance_time(self,proportion)

  def select_object(self,obj=None):
    if self.selectedObjectMarker.parent:
      self.selectedObjectMarker.parent.remove(self.selectedObjectMarker)

    ExplorerIdler.select_object(self,obj)

    if self.selectedObject:
      self.selectedObject.parent.add(self.selectedObjectMarker)
      self.update_marker()

    #self.wndInfo.lblSelInfo.setText("Sel:" +str(self.selectedObject))
    #self.wndSelected.update_widgets(self)
 
if __name__=='__main__':
  import optparse

  parser=optparse.OptionParser()
  parser.add_option("-f","--file",dest="filename", help="xml file to process",metavar="FILE")
  parser.add_option("-o","--output",dest="output", help="output filename",metavar="FILE",default=None)
  parser.add_option("","--flying",dest="flying",action="store_true",help="make a level for the flying game",default=False)
  parser.add_option("","--racing",dest="racing",action="store_true",help="make a level for the racing game",default=False)
  parser.add_option("","--snowballz",dest="snowballz",action="store_true",help="make a level for the main game",default=False)
  parser.add_option("-v","--verbose",dest="verbose",action="store_true",help="output more stuff",default=False)
  parser.add_option("-p","--view",dest="view",action="store_true",help="view the scene after conversion",default=False)

  options,args=parser.parse_args()

  if not options.filename:
    print "must specifiy input file!"
    sys.exit()
    
  if options.output==None:
    name,ext=os.path.splitext(options.filename)
    path,name=os.path.split(name)
    options.output=name
    print "+",options.output

  setModuleScene=None

  if options.flying:
    import flying
    r=FlyingLevelReader(options.filename,verbose=options.verbose,level=flying.Level)
    setModuleScene=flying
  elif options.racing:
    import racing
    r=RacingLevelReader(options.filename,verbose=options.verbose,level=racing.Level)
    setModuleScene=racing
  elif options.snowballz:
    import snowballz
    r=SnowballzLevelReader(options.filename,verbose=options.verbose,level=snowballz.Level)
    setModuleScene=snowballz
  else:
    r=LevelReader(options.filename,verbose=options.verbose)
  
  r.save(options.output)

  if not options.view:
    print "done."
  else:
    soya.init(title="LevelXML",width=1024,height=768)

    soya.set_use_unicode(1)

    scene=soya.World()

    if setModuleScene:
      setModuleScene.scene=scene
    
    level=soya.World.get(options.output)
    scene.add(level)

    camera=r.get_camera(scene=scene)
    camera.back=500.

    soya.set_root_widget(widget.Group())
    soya.root_widget.add(camera)

    idler=ExplorerIdler(scene)

    idler.idle()
