import soya
from soya import sdlconst

from math import fabs

import traceback

class ExplorerIdler(soya.Idler):
  """
  ASWD    
    - quake style keys
  F11     
    - Toggle wireframe
  middle mouse button  
    - mouse look  
  cntrl + middle mouse 
    - "zoom"
  t 
    - teleport. ( attempts to pick something straight in front of the camera
      and jumps to it )
  """
  
  def __init__(self, camera, *scenes):
    soya.Idler.__init__(self,*scenes)

    print self.__doc__

    self.speed=soya.Vector(camera)
    
    # are we grabbing the cursor?
    self.grab_cursor=0

    self.camera = camera

    # are we zooming?
    self.zoom=0

    # camera rotation
    self.roty=0.
    self.rotx=0.

    self.scene=scenes[0]

    self.stop_mouse_grab()
    self.selection = None

    self.move_speed = 1.

  def idle(self):
    # warping the mouse or init'ing sdl seems to cause a few to many
    # mouse events. this clears all the events that are currently in the
    # queue
    soya.clear_events()

    soya.Idler.idle(self)

  def select_object(self,obj=None):
    if obj!=None:
      self.selection=obj
    else:
      self.selection=None

  def on_key_down(self,event):
    if event[1]==sdlconst.K_ESCAPE:
      # i have always used sys.exit but i noticed that this is probably nicer
      self.stop()
    
    elif event[1]==sdlconst.K_w:
      self.speed.z+=-self.move_speed
    elif event[1]==sdlconst.K_s:
      self.speed.z+=self.move_speed

    elif event[1]==sdlconst.K_a:
      self.speed.x+=-self.move_speed
    elif event[1]==sdlconst.K_d:
      self.speed.x+=self.move_speed

    elif event[1]==sdlconst.K_LCTRL:
      self.zoom=1
    
    elif event[1]==sdlconst.K_SPACE:
      self.speed.x=0.
      self.speed.y=0.
      self.speed.z=0.

      #soya.Idler(scene).idle()

    elif event[1]==sdlconst.K_t:
      # see if we can pick something and then "teleport" to it 
      context=self.scene.RaypickContext(self.camera.position(),50.)
      r=context.raypick(self.camera.position(),soya.Vector(self.camera,0.0,0.0,-1.0),50.0,3)

      if r:
        self.camera.move(r[0]-soya.Vector(self.camera,0.,0.,-3.))

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

    elif event[1]==sdlconst.K_F11:
      soya.toggle_wireframe()
    
  def on_mouse_button_down(self,event):
    if event[1]==2:
      self.start_mouse_grab()

  def on_mouse_button_up(self,event):
    self.stop_mouse_grab()

    if event[1]==1:
      mouse = self.camera.coord2d_to_3d(event[2], event[3])
      
      result = self.scene.raypick(self.camera, self.camera.vector_to(mouse))
      
      obj=None
      
      if result:
        obj = result[0].parent
       
      self.select_object(obj)

    self.speed.z=0

  def start_mouse_grab(self):
    soya.cursor_set_visible(0)
    soya.set_grab_input(1)
    soya.set_mouse_pos(self.camera.width/2,self.camera.height/2)
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
    
    else:  
      rotx=self.rotx+rx
      
      roty=self.roty+ry

      self.roty=roty
      self.rotx=rotx

      self.camera.turn_vertical(ry)
      self.camera.rotate_lateral(rx)

  def resize(self):
    pass

  def get_events(self):
    return soya.process_event()
  
  def begin_round(self):
    for event in self.get_events():
      if self.on_event(event):
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
    
    soya.Idler.begin_round(self)

  def advance_time(self,proportion):
    soya.Idler.advance_time(self,proportion)
    self.camera.add_mul_vector(proportion,self.speed)

  def on_event(self,event):
    """ returning true here will stop event propogation """
    return False

try: 
  import pudding
except ImportError:
  pass

class PuddingExplorerIdler(ExplorerIdler):
  def get_events(self):
    return pudding.process_event()
  
