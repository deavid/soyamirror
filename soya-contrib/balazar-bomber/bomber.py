#!/usr/bin/env python

import sys
import os
from random import random, shuffle
from math import sqrt
import string

import traceback

# soya imports
try:
  import soya
  import soya.widget as widget
  import soya.sdlconst as sdlconst
  import soya.particle
  import soya.sphere
except ImportError:
  traceback.print_exc()
  raise "You dont have soya installed or your installation is bad"

import pysdl_mixer as mixer

# find and append the soya data dir
HERE = os.path.dirname(sys.argv[0])
datadir=os.path.join(HERE,"data")
# make sure the path exists
assert(os.path.isdir(datadir))
soya.path.append(datadir)

SOUNDS=os.path.join(HERE,'data','sounds')

# the star material we use for all the particle effects
material_star=soya.Material()
material_star.additive_blending=1
material_star.texture=soya.Image.get('littlestar.png')

# we use these to hold our sound effects
explosion_sound=None
bonus_sound=None

# will hold our state machine class when initialized
stateMachine=None

def getScene():
  """ helper function to return current scene object """
  return soya.IDLER.scenes[0]


class Fire(soya.particle.Smoke):
  """ Fire like particle system """
  
  def __init__(self,parent):
    soya.particle.Particles.__init__(self,parent,nb_max_particles=50,material=material_star)
    self.set_colors((1.0, 1.0, 1.0, 1.0), (1.0, 0.0, 0.0,0.5),(1.0,1.0,0.,0.5),(0.5,0.5,0.5,0.5),(0.,0.,0.,0.5))
    self.set_sizes ((0.19, 0.19), (0.35, 0.35))
    self.auto_generate_particle=1
  
  def generate(self, index):
    sx = (random()- 0.5) * .2
    sy = (random())
    sz = (random() - 0.5) * .2
    l = (0.2 * (1.0 + random())) / sqrt(sx * sx + sy * sy + sz * sz) * 0.5
    self.set_particle(index, random()*.5, sx * l, sy * l, sz * l, 0.,0.,0.)


class Explosion(soya.particle.Particles):
  """ Explosion particles when bomb explodes """
  
  def __init__(self,parent):
    soya.particle.Particles.__init__(self,parent,nb_max_particles=20,material=material_star)
    self.set_colors((1.0, 1.0, 1.0, 1.0), (1.0, 0.0, 0.0,0.5),(1.0,1.0,0.,0.5),(0.5,0.5,0.5,0.5),(0.,0.,0.,0.5))
    self.set_sizes ((0.69, 0.69), (0.95, 0.95))

  def generate(self, index):
    sx = (random() - 0.5) 
    sy = (random())
    sz = (random() - 0.5)
    l = (0.2 * (1.0 + random())) / sqrt(sx * sx + sy * sy + sz * sz) * 1.5
    self.set_particle(index, random()*2., sx * l, sy * l, sz * l, 0.,0.,0.)


class SoftCubeExplosion(soya.particle.Particles):
  """ Particle explosion for "soft cubes" """
  
  def __init__(self,parent):
    soya.particle.Particles.__init__(self,parent,nb_max_particles=50,material=material_star)
    self.set_colors((1.0, 1.0, 1.0, 1.0), (1.0, 0.0, 0.0,0.5),(1.0,1.0,0.,0.5),(0.5,0.5,0.5,0.5),(0.,0.,0.,0.5))
    self.set_sizes ((0.19, 0.19), (0.25, 0.25))

  def generate(self, index):
    sx = (random() - 0.5) *2
    sy = (random() )
    sz = (random() - 0.5) *2
    l = (0.2 * (1.0 + random())) / sqrt(sx * sx + sy * sy + sz * sz) * 1.5
    self.set_particle(index, random()*2., sx * l, sy * l, sz * l, 0.,0.,0.)


class Level(soya.World):
  """ The base class for all levels """

  def __init__(self):
    soya.World.__init__(self)
    
    self.size_y=8
    self.size_x=10
    
    # Initialize the map to some dummy state.
    # Note that there are 2*self.size_x - 1 rows and 2*self.size_y - 1 cols.
    self.map = [[None]*(2*self.size_y - 1) for r
                in range(2*self.size_x - 1)]

  def create(self):
    # squares where the player starts
    # Note that this is stored in physical, not abstract, coordinates.
    always_clear=[(-1,-1),(-2,-1),(0,-1),(-1,-2),(-1,0)]

    # r and c represent the cube positions in the grid,
    # while x and y represent the physical coordinates in the world.
    # Note the simple formula: r = x + self.size_x , c = y + self.size_y
    border_row, border_col = 2*self.size_x - 2, 2*self.size_y - 2
    for r, x in enumerate(range(-self.size_x,self.size_x-1)):
      for c, y in enumerate(range(-self.size_y,self.size_y-1)):        
        if (r % 2 == 0 and c % 2 == 0) or \
           (r == 0 or c == 0 or r == border_row  or c == border_col ):
          # This is a wall block
          block = Cube(self)
          block.set_xyz(x, 1, y)          
        else:
          # It's either a soft block or a floor tile
          if (x, y) in always_clear:
            # A floor tile
            block = Cube(self)
            block.set_xyz(x, 0, y)
          elif random() < 0.8:
            # A soft block
            block = SoftCube(self)
            block.set_xyz(x, 1, y)
          else:
            # Still a floor tile. TODO: can this be done somehow more elegantly?
            block = Cube(self)
            block.set_xyz(x, 0, y)
          
        self.map[r][c] = block


    sun = soya.Light(self)
    sun.directional = 1
    sun.diffuse = (1.0, 0.8, 0.4, 1.0)
    sun.rotate_vertical(-45.0)

    atmosphere = soya.SkyAtmosphere()
    atmosphere.ambient = (0.3, 0.3, 0.4, 1.0)
    atmosphere.fog = 1
    atmosphere.fog_type  = 0
    atmosphere.fog_start = 40.0
    atmosphere.fog_end   = 50.0
    atmosphere.fog_color = atmosphere.bg_color = (0.2, 0.5, 0.7, 1.0)
    atmosphere.skyplane  = 1
    atmosphere.sky_color = (1.5, 1.0, 0.8, 1.0)

    self.atmosphere = atmosphere

  def putBomb(self,player,x,y,z):
    cube=self.map[int(x+self.size_x)][int(z+self.size_y)]
    
    if cube.bomb is not None:
      return False

    cube.createBomb(player)

    return True


class Bomb(soya.World):
  """ Bomb object. Changes color from black to white and then explodes"""
  
  def __init__(self,parent,cube,player):
    soya.World.__init__(self,parent)
    self.cube=cube
    self.player=player

    self.material=soya.Material()
    self.material.diffuse=(0.,0.,0.,1.0)
    
    bomb=soya.sphere.Sphere(slices=10, stacks=10,material=self.material).shapify()
    
    self.sphere=soya.Volume(self,bomb)
    
    self.scale(0.3,0.3,0.3)
    self.solid=1

    self.speed=0.01

    self.strength=player.flameStrength
  
  def advance_time(self,p):
    r,g,b,a=self.material.diffuse

    s=self.speed

    r+=s*p
    g+=s*p
    b+=s*p

    if r>1. and g>1. and b>1.:
      self.player.bombExploded()

      self.solid=0

      self.cube.spreadFire(self.strength)

    self.material.diffuse=(r,g,b,a)


class Bonus:
  """ Bonus object initially attached to a softcube, if the softcube is destroyed a
  it creates a soya.bonus object parented to the level. All bonuses should be a 
  subclass of this."""

  def __init__(self,cube):
    self.softcube=cube

    self.material=material_star
    self.halo=material_star
    self.color=(1., 1., 1., 1.)

  def makeBonus(self, parent):
    """ called when the owner softcube explodes to create the soya.bonus object """
    
    b=soya.Bonus(parent,self.material,self.halo)
    b.scale(0.1,0.1,0.1)
    b.color=self.color
    b.lit=False
    b.move(self.softcube)
    b.z+=1.

    self.bonus=b

    x=int(round(self.softcube.x))
    z=int(round(self.softcube.z))

    c=parent.map[x+parent.size_x][z+parent.size_y]
    c.bonus=self

  def collect(self,player):
    """ called when a player collects the bonus """

    bonus_sound.play()
    
    self.bonus.parent.remove(self.bonus)


class BonusFire(Bonus):
  """ gives the player extra fire strength """
  
  def __init__(self,cube):
    Bonus.__init__(self,cube)

    self.color=(1., 0., 0., .7)

  def collect(self,player):
    Bonus.collect(self,player)
    player.flameStrength+=1


class BonusBomb(Bonus):
  """ gives the player extra total bombs """
  
  def __init__(self,cube):
    Bonus.__init__(self,cube)

    self.color=(0., 0., 1., 1.)

    material=soya.Material()
    material.additive_blending=1
    material.texture=soya.Image.get('bomb.png')
    self.material=material
    #self.halo=material

  def collect(self,player):
    Bonus.collect(self,player)
    player.totalBombs += 1


class SoftCube(soya.Volume):
  """ base class for a block that can be destroyed """
  
  # a little list of all the bonuses and the chance they will shown.
  # (chance, bonus )

  BONUSES=[(0.5, BonusFire),
           (0.5, BonusBomb)]
  
  def __init__(self,parent):
    shape=soya.Shape.get("soft_cube")
    soya.Volume.__init__(self,parent,shape)

    self.randomCreateBonus()

  def randomCreateBonus(self):
    self.bonus=None

    shuffle(self.BONUSES)
    
    for chance, bonus in self.BONUSES:
      if random() < chance:
        self.bonus = bonus(self)

  def explode(self):
    particles=SoftCubeExplosion(self.parent)
    particles.move(self)

    if self.bonus:
      self.bonus.makeBonus(self.parent)


class Cube(soya.Volume):
  """ base class for a block that cannot be destroyed. cubes also store what is
  "on top", it stores if there is a bomb layed, if there is a bonus, and also 
  creates fire in the required direction when a bomb explodes. """
  
  def __init__(self,parent):
    shape=soya.Shape.get("cube")

    soya.Volume.__init__(self,parent,shape)

    self.bomb=None
    self.fire=None
    self.fireStrength=0.
    
    self.bonus=None

  def createBomb(self,player):
    self.bomb=s=Bomb(self.parent,self,player)
    s.move(self)
    s.y+=1.

  def createFire(self):
    """ called to create fire on a specific square. """

    if self.bomb!=None:
      self.spreadFire(self.bomb.strength)

    elif self.fire==None:
      self.fire=Fire(self.parent)
      self.fire.move(self)
    self.fireStrength+=1.

  def spreadFire(self,dist=4):
    """ if create fire discovers a bomb this function is called to spread the fire
    in horiz and vert directions """

    e=Explosion(self.parent)
    e.move(self)

    self.parent.remove(self.bomb)
    self.bomb=None
    sx=int(round(self.x))
    sz=int(round(self.z))

    # local function to check a cube
    def checkCube(z,x):
      # If the cube is un-destructible, return True. Else, if soft, destroy it and create a floor tile in place,
      # and then return True, or create fire if it's a floor tile and return False.
      block = self.parent.map[x+self.parent.size_x][z+self.parent.size_y]
      
      if not isinstance(block, SoftCube) and block.y == 1:
        # It's a hard wall
        return True
      else:
        # It's either a floor or a soft cube
        if block.y == 0:
          # It's a floor, do nothing
          block.createFire()
          return False
        else:
          # It's a soft cube! Murder death kill!
          # But first, put a floor tile there.
          floor_tile = Cube(self.parent)
          floor_tile.set_xyz(x, 0, z)
          self.parent.map[x+self.parent.size_x][z+self.parent.size_y] = floor_tile
          block.explode()
          self.parent.remove(block)
          return True
 
    for x in range(sx,sx+dist):
      if checkCube(sz,x): break

    for x in range(sx,sx-dist,-1):
      if checkCube(sz,x): break
        
    for x in range(sz,sz+dist):
      if checkCube(x,sx): break

    for x in range(sz,sz-dist,-1):
      if checkCube(x,sx): break

  def advance_time(self,p):
    if self.fire!=None:
      self.fireStrength-=.05*p
      if self.fireStrength<0.:
        self.fire.auto_generate_particle=0
        self.fire=None


class Action:
  def __init__(self, action):
    self.action = action

# The available actions
ACTION_WAIT          = 0
ACTION_ADVANCE       = 1
ACTION_ADVANCE_LEFT  = 2
ACTION_ADVANCE_RIGHT = 3
ACTION_TURN_LEFT     = 4
ACTION_TURN_RIGHT    = 5
ACTION_GO_BACK       = 6
ACTION_GO_BACK_LEFT  = 7
ACTION_GO_BACK_RIGHT = 8
ACTION_JUMP          = 9
ACTION_FIRE          = 10


class Keyboardcontroller:
  def __init__(self):
    self.left_key_down = self.right_key_down = self.up_key_down = self.down_key_down = 0
    self.action_table = {
      (0, 0, 1, 0) : Action(ACTION_ADVANCE),
      (1, 0, 1, 0) : Action(ACTION_ADVANCE_LEFT),
      (0, 1, 1, 0) : Action(ACTION_ADVANCE_RIGHT),
      (1, 0, 0, 0) : Action(ACTION_TURN_LEFT),
      (0, 1, 0, 0) : Action(ACTION_TURN_RIGHT),
      (0, 0, 0, 1) : Action(ACTION_GO_BACK),
      (1, 0, 0, 1) : Action(ACTION_GO_BACK_LEFT),
      (0, 1, 0, 1) : Action(ACTION_GO_BACK_RIGHT),
      }
    self.default_action = Action(ACTION_WAIT)
    
  def next(self):
    jump = 0
    fire = 0
    
    for event in soya.process_event():
      if   event[0] == sdlconst.KEYDOWN:
        if   (event[1] == sdlconst.K_q) or (event[1] == sdlconst.K_ESCAPE):
          stateMachine.change_state('menu')
          
        elif event[1] == sdlconst.K_LSHIFT:
          jump = 1

        elif event[1] == sdlconst.K_SPACE:
          fire = 1
        elif event[1] == sdlconst.K_F1:
          soya.screenshot().save(os.path.join(os.path.dirname(sys.argv[0]), "results", os.path.basename(sys.argv[0])[:-3] + ".jpg"))
          
        elif event[1] == sdlconst.K_LEFT:  self.left_key_down  = 1
        elif event[1] == sdlconst.K_RIGHT: self.right_key_down = 1
        elif event[1] == sdlconst.K_UP:    self.up_key_down    = 1
        elif event[1] == sdlconst.K_DOWN:  self.down_key_down  = 1
        
      elif event[0] == sdlconst.KEYUP:
        if   event[1] == sdlconst.K_LEFT:  self.left_key_down  = 0
        elif event[1] == sdlconst.K_RIGHT: self.right_key_down = 0
        elif event[1] == sdlconst.K_UP:    self.up_key_down    = 0
        elif event[1] == sdlconst.K_DOWN:  self.down_key_down  = 0
    
    if jump: return Action(ACTION_JUMP)
    if fire: return Action(ACTION_FIRE)
    
    return self.action_table.get((self.left_key_down, self.right_key_down,
                                  self.up_key_down, self.down_key_down),
                                 self.default_action)


class Character(soya.World):
  def __init__(self,parent,controller):
    soya.World.__init__(self,parent)

    self.createCal3dVolume()

    self.controller = controller

    self.solid=0
    self.speed          = soya.Vector(self)
    self.rotation_speed = 0.0

    self.radius         = 0.4
    self.radius_y       = 1.0
    self.center         = soya.Point(self, 0.0, self.radius_y, 0.0)
    
    self.left   = soya.Vector(self, -1.0,  0.0,  0.0)
    self.right  = soya.Vector(self,  1.0,  0.0,  0.0)
    self.down   = soya.Vector(self,  0.0, -1.0,  0.0)
    self.up     = soya.Vector(self,  0.0,  1.0,  0.0)
    self.front  = soya.Vector(self,  0.0,  0.0, -1.0)
    self.back   = soya.Vector(self,  0.0,  0.0,  1.0)

    self.jumping = 0

  def createCal3dVolume(self):
    balazar=soya.Cal3dShape.get("balazar")

    self.perso=soya.Cal3dVolume(self,balazar)
    self.perso.scale(0.4,0.4,0.4)

    self.perso.animate_blend_cycle("attente")

    self.current_animation="attente"

  def play_animation(self, animation):
    if self.current_animation != animation:
      # Stops previous animation
      self.perso.animate_clear_cycle(self.current_animation, 0.2)
      
      # Starts the new one
      self.perso.animate_blend_cycle(animation, 1.0, 0.2)
      
      self.current_animation = animation
      
  def begin_round(self):
    self.begin_action(self.controller.next())
    soya.World.begin_round(self)

  def advance_time(self, proportion):
    soya.World.advance_time(self, proportion)
    
    self.add_mul_vector(proportion, self.speed)
    self.rotate_lateral(proportion * self.rotation_speed)


class Player(Character):
  def __init__(self, parent, controller):
    Character.__init__(self,parent,controller)

    self.flameStrength = 2
    self.totalBombs = 1
    self.currentBombs=0

  def layBomb(self):
    """ lay a bomb at the current position """
    if self.currentBombs<self.totalBombs:
      p=soya.Point(self.parent,round(self.x),round(self.y),round(self.z))
      if self.parent.putBomb(self,p.x,p.y,p.z):
        self.currentBombs+=1

  def bombExploded(self):
    """ called when a bomb has exploded """
    # free up the bomb space
    self.currentBombs-=1

    explosion_sound.play()
    
  def begin_action(self, action):
    self.speed.x = self.speed.z = self.rotation_speed = 0.0

    if (not self.jumping) and self.speed.y > 0.0: self.speed.y = 0.0
    
    animation = "attente"

    if action.action==ACTION_FIRE:
      self.layBomb()
      
    if   action.action in (ACTION_TURN_LEFT, ACTION_ADVANCE_LEFT, ACTION_GO_BACK_LEFT):
      self.rotation_speed = 6.0
      animation = "tourneG"
    elif action.action in (ACTION_TURN_RIGHT, ACTION_ADVANCE_RIGHT, ACTION_GO_BACK_RIGHT):
      self.rotation_speed = -6.0
      animation = "tourneD"
      
    if   action.action in (ACTION_ADVANCE, ACTION_ADVANCE_LEFT, ACTION_ADVANCE_RIGHT):
      self.speed.z = -0.10
      animation = "marche"
    elif action.action in (ACTION_GO_BACK, ACTION_GO_BACK_LEFT, ACTION_GO_BACK_RIGHT):
      self.speed.z = 0.10
      animation = "recule"
    
    new_center = self.center + self.speed
    context = getScene().RaypickContext(new_center, max(self.radius, 0.1 + self.radius_y))
    
    r = context.raypick(new_center, self.down, 0.1 + self.radius_y, 3)

    if r and not self.jumping:
      ground, ground_normal = r
      ground.convert_to(self)
      self.speed.y = ground.y
      
      if action.action == ACTION_JUMP:
        self.jumping = 1
        self.speed.y = 0.2
        
    else:
      self.speed.y = max(self.speed.y - 0.02, -0.25)
      animation = "chute"
      
      if self.speed.y < 0.0: self.jumping = 0
      
    # FIXME
    # some far too simple collision detection
    
    # make a point either in front or behind depding on speed
    if self.speed.z<0:
      new_center = self.center + self.speed+soya.Vector(self,0,0,-self.radius)
    else:
      new_center = self.center + self.speed+soya.Vector(self,0,0,self.radius)
    
    # find integer versions of x and z of the new point 
    new_center.convert_to(self.parent)
    rx, rz = int(round(new_center.x)), int(round(new_center.z))

    # get the cube at that point 
    cube=self.parent.map[rx+self.parent.size_x][rz+self.parent.size_y]

    # is the cube raised?
    if cube.y>self.y:
      # dont allow the movement
      self.speed.x=0
      self.speed.z=0

    # does the cube have a bonus on it?
    # FIXME: this is a hack that checks if cube is a SoftCube - if it is, it means that the bonus is still
    # "hidden" in the cube and thus can't be collected!
    # This probably has to do with the fact that now there's no cube underneath it. Hacks are evil.
    if cube.bonus and not isinstance(cube, SoftCube):
      # collect the bonus and destroy it 
      cube.bonus.collect(self)
      cube.bonus=None
    
    self.play_animation(animation)


class StateMachine(dict):
  """ class to handle different application states using subclasses of soya.Idler.
    
      this class is a subclass of a Dict so all methods available to dict are also
      available here.

      >>> class MyIdler1(soya.Idler):
      >>>   def begin_round(self):
      >>>     for e in soya.process_event():
      >>>       if e[0]==sdlconst.KEYDOWN:
      >>>         stateMachine.change_state('state2')
      >>> 
      >>> class MyIdler2(soya.Idler):
      >>>    pass
      >>> 
      >>> stateMachine=StateMachine()
      >>> stateMachine['state1']=MyIdler1
      >>> stateMachine['state2']=MyIdler2
      >>> stateMachine.state='state1'

      it should also be possible to do 

      >>> stateMachine=StateMachine({'state1':MyIdler1,'state2':MyIdler2})

      it is not absolutely nessacary to pass this class a soya Idler. As long as 
      the object passed has stop() and idle() methods everything will be ok.

  """
      
  def __init__(self,initialdata={}):
    dict.__init__(self,initialdata)
    self.__currentState=None

  def __getstate__(self):
    return self.__currentState

  def change_state(self,state):
    """ stop any current state and start the requested named state """
    if self.__currentState:
      self.__currentState.stop()

    try:
      idler=self[state]
    except KeyError:
      raise "%s is not a state of %s" % (state,self)

    self.__currentState=idler()
    self.__currentState.idle()
    self.__currentState=None

  state=property(__getstate__,change_state,doc='set or get the current state key.\nsetting this value will cause change_state to be called')

class WidgetedIdler(soya.Idler):
  """ This is the base class we will use for other idlers.
  You should override the create_* to methods to create the relevant
  objects. The resize function should be overidden to position any 
  widgets when the screen size changes
  """

  class RootWidget(widget.Group):
    """ used to get round having to checking the event queue for resize events.
      soya calls the root_widgets resize method automatically so we make use of that 
      here. its currently easier to resize widgets on your own.
    """

    def resize(self,parent_left,parent_top,parent_width,parent_height):
      # just in case any widgets do have a good resize function ( eg FPSLabel ) 
      # we call the ancestor function
      widget.Group.resize(self,parent_left,parent_top,parent_width,parent_height)

      # call the idlers resize method to allow the developer to specifiy positions
      # soya.IDLER should always refer to the parent class
      if soya.IDLER:
        soya.IDLER.resize()
  
  def __init__(self):
    # in theory this shouldnt need to be overriden 
    
    # create the scene. for simple menus this can probably be left alone
    self.create_scene()

    # create the camera
    self.create_camera()
    
    # set the root widget to our local class with the modified resize event 
    soya.set_root_widget(self.RootWidget())

    # add the camera
    soya.root_widget.add(self.camera)

    # create all our widgets. subclasses will override this 
    self.create_widgets()

    # resize all our widgets initially. the same function will be called for 
    # video resize events. subclasses will override this 
    self.resize()

    soya.Idler.__init__(self,self.scene)

  def create_scene(self):
    """ creates self.scene and any other objects connected to the scene apart
    from the camera
    """

    self.scene=soya.World()
  
  def create_camera(self):
    """ creates the camera """

    self.camera=soya.Camera(self.scene)
    self.camera.z=3.

  def create_widgets(self):
    """ create any widgets """
    pass

  def resize(self):
    """ called on video resize events """
    pass


class MenuIdler(WidgetedIdler):
  """ all our menu screens will be a subclass of this """

  def create_scene(self):
    WidgetedIdler.create_scene(self)

    # setup a nice background for our menu screens
    
    # some lighting 
    sun = soya.Light(self.scene)
    sun.directional = 1
    sun.diffuse = (1.0, 0.8, 0.4, 1.0)
    sun.rotate_vertical(-45.0)

    # atmosphere
    atmosphere = soya.SkyAtmosphere()
    atmosphere.ambient = (0.3, 0.3, 0.4, 1.0)
    atmosphere.fog = 1
    atmosphere.fog_type  = 0
    atmosphere.fog_start = 40.0
    atmosphere.fog_end   = 50.0
    atmosphere.fog_color = atmosphere.bg_color = (0.2, 0.5, 0.7, 1.0)
    atmosphere.skyplane  = 1
    atmosphere.sky_color = (1.5, 1.0, 0.8, 1.0)

    self.scene.atmosphere = atmosphere

    # balazar can be our center-piece
    balazar=soya.Cal3dShape.get("balazar")
    self.perso=soya.Cal3dVolume(self.scene,balazar)
    self.perso.animate_blend_cycle("attente")
    self.perso.turn_lateral(180)
    self.perso.y-=1
    self.perso.z-=1

    # some particles
    particle=Explosion(self.scene)
    particle.set_xyz(-1,0,0)

    particle=Explosion(self.scene)
    particle.set_xyz(1,0,0)

  def advance_time(self,p):
    WidgetedIdler.advance_time(self,p)

    self.perso.turn_lateral(1.*p)
  
  def create_widgets(self):  
    WidgetedIdler.create_widgets(self)

    self.title=widget.Label(soya.root_widget,"Balazar Bomber",align=1)

  def resize(self):
    WidgetedIdler.resize(self)

    self.title.width=soya.root_widget.width
    self.title.height=soya.root_widget.height


class GameIdler(WidgetedIdler):
  """ Idler for the actual game play """

  def create_scene(self):
    self.scene = soya.World()

    self.level = Level()
    self.level.create()

    # our player
    character = Player(self.level, Keyboardcontroller())
    character.y=2
    character.x=-1
    character.z=-1

    self.scene.add(self.level)

  def create_camera(self):
    self.camera = soya.Camera(self.scene)
    dist=6.
    self.camera.set_xyz(-1, dist+dist+5, dist+0)
    self.camera.look_at(soya.Point(self.level,-1.,0.,-1.))

  def create_widgets(self):
    soya.root_widget.add(widget.FPSLabel())

  def resize(self):
    pass


class FadingLabel(soya.widget.Label):
  """ A Simple fading label """

  def widget_advance_time(self,p):
    # get our current colour
    r,g,b,a=self.get_color()
    
    a-=.01*p
    
    # if alpha is < 0 then the label cannot be seen anymore so should be removed
    if a<0.:
      # see if we have an attribute called on_remove and if so call it as a function
      if hasattr(self,'on_remove'): self.on_remove()

      # remove ourselves
      soya.root_widget.remove(self)

    # set the color back with the new alpha value
    self.set_color((r,g,b,a))


class IntroIdler(MenuIdler):
  """ Idler for the splash/startup screen """
  def create_widgets(self):
    MenuIdler.create_widgets(self)

    # simple instruction label
    self.label=widget.Label(soya.root_widget,"Press any key to continue",align=1)

    # messages we will scroll thru on the intro screen
    self.messages=["A Soya Demo",
                   "http://home.gna.org/oomadness/en/soya/",
                   "Thanks to the all involved in Soya",
                   "Visit #slune irc.freenode.net",
                   ]

    # which message to show next
    self.current_message=0

    self.create_message_label()

    # there should probably be somewhere better for this 
    explosion_sound.play()

  def create_message_label(self):
    # create our FadingLabel instance with the current message 
    self.messageLabel=FadingLabel(soya.root_widget,self.messages[self.current_message],align=1)

    # set the on_remove attribute so we can create a new message at the end of its life
    self.messageLabel.on_remove=self.create_message_label

    # position the label above the simple instructions
    self.messageLabel.width=soya.root_widget.width
    self.messageLabel.top=soya.root_widget.height-150

    # incremenent the current message variable
    self.current_message+=1
    # wrap around the messages if we've gone too far
    if self.current_message>=len(self.messages):
      self.current_message=0

  def resize(self):
    MenuIdler.resize(self)

    self.label.width=soya.root_widget.width
    self.label.top=soya.root_widget.height-100
    self.label.height=soya.root_widget.height

  def begin_round(self):
    MenuIdler.begin_round(self)

    # wait for any keystroke to advance onto the menu
    for e in soya.process_event():
      if e[0]==sdlconst.KEYDOWN and e[3]!=0:
        stateMachine.state='menu'


class MainMenuIdler(MenuIdler):
  """ Main Menu Idler """

  def start_game_state(self):
    explosion_sound.play()
    stateMachine.state='game'

  def start_lobby_state(self):
    explosion_sound.play()
    stateMachine.state='lobby'
  
  def create_widgets(self):
    MenuIdler.create_widgets(self)

    # all our menu choices
    choices=[ widget.Choice('Start Game',self.start_game_state),
              widget.Choice('Lobby Test',self.start_lobby_state),
              widget.Choice('Exit',lambda: sys.exit()),
            ]
    
    self.choicelist=widget.ChoiceList(soya.root_widget,choices)
        
    explosion_sound.play()

  def resize(self):
    MenuIdler.resize(self)

    self.choicelist.top=150
    # fit the height of the list to exactly match the amount of items in the list
    self.choicelist.height=len(self.choicelist.choices)*(widget.default_font.height+10)
    self.choicelist.width=soya.root_widget.width
   
  def begin_round(self):
    MenuIdler.begin_round(self)
    
    # pass all events to the choicelist
    for e in soya.process_event():
      self.choicelist.process_event(e)


class SimpleInput(widget.ChoiceList):
  """ A simple bodge to fake a text input """

  class ChoiceInput(widget.ChoiceInput):
    """ A modified version of ChoiceInput to change the output formatting and to catch
    enter key presses"""

    def get_label(self):
      # make some sort of prompt and cursor
      return ">%s_" % self.value

    def key_down(self,key_id,mods):
      # if the key is enter we want to call our owners on_enter function
      # otherwise just let soya.ChoiceInput deal with it 
      if key_id==sdlconst.K_RETURN:
        self.parent.on_enter()
      elif key_id in [sdlconst.K_DELETE,sdlconst.K_BACKSPACE,sdlconst.K_CLEAR]:
        print "backspace"
        self.value=self.value[:-1]
      elif key_id!=0:
        # make sure the character is considered printable. 
        # is there a better way than this?
        if chr(key_id) in string.printable:
          self.value+=chr(key_id)
      else: print key_id,mods

  def process_event(self,event):
    # we must subclass this to make use of the unicode data in the event

    if (event[0] == soya.sdlconst.KEYDOWN):
      self.input.key_down(event[3],event[2])      

    """
    # not really needed but here for reference from the orginal
    # soya.ChoiceList.process_event

    elif (event[0] == soya.sdlconst.MOUSEMOTION):
      self.mouse_move(event[1], event[2])
    elif (event[0] == soya.sdlconst.MOUSEBUTTONDOWN):
      self.choices[self.selected].mouse_click(event[1])
    elif (event[0] == soya.sdlconst.JOYAXISMOTION):
      if event[1] == 0:
        if event[2] < 0:
          self.key_down(soya.sdlconst.K_LEFT, 0)
        elif event[2] > 0:
          self.key_down(soya.sdlconst.K_RIGHT, 0)
      elif event[1] == 1:
        if event[2] < 0:
          self.key_down(soya.sdlconst.K_UP, 0)
        elif event[2] > 0:
          self.key_down(soya.sdlconst.K_DOWN, 0)
    elif (event[0] == soya.sdlconst.JOYBUTTONDOWN):
      if event[1] // 2 == event[1] / 2.0:
        self.key_down(soya.sdlconst.K_RETURN, 0)
      else:
        self.key_down(soya.sdlconst.K_LEFT, 0)
     """

  # The following will be used as property-handlers for self.value
  def _get_value(self):
    return self.input.value

  def _set_value(self, value):
    self.input.value=value
   
  # create a property to make this class seem more like a single control
  value=property(_get_value, _set_value)

  def __init__(self,parent,value='',enter_func=None):
    # our modified soya.ChoiceInput
    self.input=self.ChoiceInput()
    # give the choice a handle back to here so we can call on_enter
    self.input.parent=self

    self.value=value
    self.enter_func=enter_func
    
    widget.ChoiceList.__init__(self,parent,[self.input],align=0)

    self.height=(widget.default_font.height+10)

  def on_enter(self):
    """ called whenever enter is pressed """
    if self.enter_func!=None:
      self.enter_func(self.value)


class LobbyIdler(MenuIdler):
  """ Idler for the networking Lobby """

  def create_widgets(self):
    MenuIdler.create_widgets(self)
  
    # create a message to display
    message="""This is a lobby test using the default soya widgets.

Commands
---------------------------------
\\exit to return to the main menu.
\\start to start a new game 

"""
    
    # this is where output will go. ie stdout
    self.text=widget.Label(soya.root_widget,message,align=0)

    # this is our "edit box". ie stdin
    self.input=SimpleInput(soya.root_widget,enter_func=self.send)

  def resize(self):
    MenuIdler.resize(self)

    # fill the main body of the screen
    self.text.top=100
    self.text.left=30
    self.text.width=soya.root_widget.width-60
    self.text.height=soya.root_widget.height-100

    # calculate how many lines we should display 
    self.show_lines=self.text.height/(widget.default_font.height+5)

    # position at the bottom of the screen
    self.input.top=soya.root_widget.height-50
    self.input.left=30
    self.input.width=soya.root_widget.width-60
   
  def send(self, message):
    """ this happens when the user presses enter. this would probably 
    be used to send a command or chat to a server
    """

    # get all the lines as an array from our main text wiget
    text=self.text.get_text().split("\n")
    # add the text from the input widget
    text.append(message)

    # trim off extra lines so it fits the available space
    if len(text)>self.show_lines:
      text=text[-self.show_lines:]

    # set the text of the ouput widget
    self.text.set_text("\n".join(text))

    # check if the input was a command 
    if self.input.value[:1]=='\\':
      command =self.input.value[1:].lower()
      if command=='exit':
        stateMachine.state='menu'
      elif command=='start':
        stateMachine.state='game'
    
    # clear the inputs value ready for the next user input 
    self.input.value=''

  def begin_round(self):
    MenuIdler.begin_round(self)
    
    # just send all events to the input 
    for e in soya.process_event():
      self.input.process_event(e)
       
 
if __name__=='__main__':
  soya.init(width=800,height=600,title="Balazar Bomber")
  
  #soya.init_audio()
  mixer.init();  

  # play our music file on loop forever :D
  #music=soya.MusicFile(os.path.join(SOUNDS,'test.mod'))
  #music.play(-1)
  music=mixer.Music(os.path.join(SOUNDS,'test.mod'))
  music.play()

  # we load this for later
  #explosion_sound=soya.AudioFile(os.path.join(SOUNDS,'explosion.wav'))
  #bonus_sound=soya.AudioFile(os.path.join(SOUNDS,'arcade.wav'))
  explosion_sound=mixer.Sample(os.path.join(SOUNDS,'explosion.wav'))
  bonus_sound=mixer.Sample(os.path.join(SOUNDS,'arcade.wav'))

  # turn on unicode key events for better text input
  soya.set_use_unicode(True)
  
  # the global state machine object
  stateMachine=StateMachine()
  
  # all our application states
  stateMachine['intro']=IntroIdler
  stateMachine['menu']=MainMenuIdler
  stateMachine['lobby']=LobbyIdler
  stateMachine['game']=GameIdler

  # run the first state
  stateMachine.state='intro'
