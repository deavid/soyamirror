#! /usr/bin/env python
#this is a list of objects that are needed in the game


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

def getScene():
    """ helper function to return current scene object """
    return soya.IDLER.scenes[0]
    
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
  
  def __init__(self,parent, objinfo):
    shape=soya.Shape.get("soft_cube")
    soya.Volume.__init__(self,parent,shape)
    self.randomCreateBonus()
    
    self.objinfo = objinfo
    
    position = self.objinfo['position']
    self.set_xyz(position[0], position[1], position[2])
    
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
  
  def __init__(self,parent, objinfo):
    shape=soya.Shape.get("cube")
    self.objinfo = objinfo
    soya.Volume.__init__(self,parent,shape)

    self.bomb=None
    self.fire=None
    self.fireStrength=0.
    
    self.bonus=None

    position = self.objinfo['position']
    self.set_xyz(position[0], position[1], position[2])
    
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

class Character(soya.World):
  def __init__(self,parent,objinfo):
    soya.World.__init__(self,parent)

    self.createCal3dVolume()

    self.objinfo = objinfo
    
    #self.controller = controller

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
    balazar=soya.Cal3dShape.get(self.objinfo['mesh'])

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
  """     
  def begin_round(self):
    self.begin_action(self.controller.next())
    soya.World.begin_round(self)
    reactor.iterate()
    if clientplayer.state != 'game':
            stateMachine.change_state(clientplayer.state)
            
  

  def advance_time(self, proportion):
    soya.World.advance_time(self, proportion)
    
    self.add_mul_vector(proportion, self.speed)
    self.rotate_lateral(proportion * self.rotation_speed)

  """
class Player(Character):
  def __init__(self, parent, objinfo):
    self.objinfo = objinfo
    
    Character.__init__(self,parent, self.objinfo)

    self.flameStrength = 2
    self.totalBombs = 1
    self.currentBombs=0
    
    position = objinfo['position']
    self.set_xyz(position[0], position[1], position[2])
    
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


