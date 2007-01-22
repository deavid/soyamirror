# TOFU
# Copyright (C) 2005-2007 Jean-Baptiste LAMY
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

import sys, os, os.path, struct, random
import soya, soya.tofu as tofu, cerealizer, soya.cerealizer4soya, soya.sdlconst as sdlconst, soya.widget, soya.label3d

soya.path.append(os.path.join(os.path.dirname(sys.argv[0]), "data"))

tofu.SAVED_GAME_DIR = "/tmp/tofu_demo"

mode = sys.argv[1][2:]
tofu.set_side(mode)


class PlayerID(tofu.PlayerID):
  def __init__(self, filename, password):
    tofu.PlayerID.__init__(self, filename, password)

tofu.LOAD_PLAYER_ID = PlayerID.loads


class Player(tofu.Player):
  def __init__(self, player_id):
    tofu.Player.__init__(self, player_id)
    
    level = tofu.Level.get("demo")
    
    mobile = Mobile()
    mobile.set_xyz(108.0, -6.0, 107.0)
    label = soya.label3d.Label3D(mobile, player_id.filename)
    label.y = 3
    label.lit = 0
    label.auto_flip = 1
    mobile.level = level
    self.add_mobile(mobile)

    
tofu.CREATE_PLAYER = Player

class MainLoop(tofu.MainLoop):
  def begin_round(self):
    self.events = soya.process_event()
    tofu.MainLoop.begin_round(self)
    
    
class Level(tofu.Level):
  def __init__(self):
    tofu.Level.__init__(self)
    

def create_demo_level():
  level = Level()
  level.static_part = static_part = soya.World(level)
  
  terrain = soya.Terrain(static_part)
  terrain.from_image(soya.Image.get("map.png"))
  terrain.multiply_height(50.0)
  terrain.scale_factor = 1.5
  terrain.texture_factor = 1.0
  terrain.y = -35.0
  terrain.set_material_layer(soya.Material.get("grass" ),  0.0,  15.0)
  terrain.set_material_layer(soya.Material.get("ground"), 15.0,  25.0)
  terrain.set_material_layer(soya.Material.get("snow"  ), 25.0,  50.0)
  
  house1 = soya.Body(static_part, soya.Model.get("ferme"))
  house1.set_xyz(125.0, -7.2, 91.0)
  
  house2 = soya.Body(static_part, soya.Model.get("ferme"))
  house2.set_xyz(108.0, -11.25, 100.0)
  house2.rotate_y(100.0)
  
  sun = soya.Light(static_part)
  sun.directional = 1
  sun.diffuse = (1.0, 0.8, 0.4, 1.0)
  sun.rotate_x(-45.0)
  
  level.atmosphere = soya.SkyAtmosphere()
  level.atmosphere.ambient = (0.3, 0.3, 0.4, 1.0)
  level.atmosphere.fog = 1
  level.atmosphere.fog_type  = 0
  level.atmosphere.fog_start = 40.0
  level.atmosphere.fog_end   = 50.0
  level.atmosphere.fog_color = level.atmosphere.bg_color = (0.2, 0.5, 0.7, 1.0)
  level.atmosphere.skyplane  = 1
  level.atmosphere.sky_color = (1.5, 1.0, 0.8, 1.0)
  
  #level.bot = Bot()
  #level.add_mobile(level.bot)
  #level.bot.set_xyz(128.0, 6.0, 107.0)
  
  static_part.filename = "demo_static_part"; static_part.save()
  level      .filename = "demo"            ; level      .save()
  
  level.discard()


ACTION_MOVE_FORWARD  = "^"
ACTION_STOP_MOVING   = "-"
ACTION_MOVE_BACKWARD = "v"
ACTION_TURN_LEFT     = "<"
ACTION_STOP_TURNING  = "|"
ACTION_TURN_RIGHT    = ">"
ACTION_JUMP          = "J"

CONTROL_KEYS = [
  [sdlconst.K_UP, sdlconst.K_DOWN, sdlconst.K_LEFT, sdlconst.K_RIGHT, sdlconst.K_LSHIFT], # Local player #1
  [sdlconst.K_e, sdlconst.K_x, sdlconst.K_s, sdlconst.K_d, sdlconst.K_z],                 # Local player #2
  [sdlconst.K_y, sdlconst.K_b, sdlconst.K_g, sdlconst.K_h, sdlconst.K_t],                 # Local player #3
  ]

class Mobile(tofu.SpeedInterpolatedMobile, tofu.AnimatedMobile, tofu.RaypickCollidedMobileWithGravity):
  def __init__(self):
    super(Mobile, self).__init__()
    
    self.model        = soya.AnimatedModel.get("balazar")
    self.control_keys = CONTROL_KEYS[0]
    
  def generate_actions(self):
    for event in soya.MAIN_LOOP.events:
      if   event[0] == sdlconst.KEYDOWN:
        if   (event[1] == sdlconst.K_q) or (event[1] == sdlconst.K_ESCAPE): soya.MAIN_LOOP.stop()
        elif event[1] == self.control_keys[0]: self.send_action(ACTION_MOVE_FORWARD)
        elif event[1] == self.control_keys[1]: self.send_action(ACTION_MOVE_BACKWARD)
        elif event[1] == self.control_keys[2]: self.send_action(ACTION_TURN_LEFT)
        elif event[1] == self.control_keys[3]: self.send_action(ACTION_TURN_RIGHT)
        elif event[1] == self.control_keys[4]: self.send_action(ACTION_JUMP)

      elif event[0] == sdlconst.KEYUP:
        if   event[1] == self.control_keys[0]: self.send_action(ACTION_STOP_MOVING)
        elif event[1] == self.control_keys[1]: self.send_action(ACTION_STOP_MOVING)
        elif event[1] == self.control_keys[2]: self.send_action(ACTION_STOP_TURNING)
        elif event[1] == self.control_keys[3]: self.send_action(ACTION_STOP_TURNING)
        
  def do_action(self, action):
    animation = ""
    if   action == ACTION_MOVE_FORWARD : self.speed.z = -0.35; animation = "marche"
    elif action == ACTION_STOP_MOVING  : self.speed.z =  0.0 ; animation = "attente"
    elif action == ACTION_MOVE_BACKWARD: self.speed.z =  0.2 ; animation = "recule"
    
    elif action == ACTION_TURN_LEFT:
      self.speed.rotate_lateral( 5.0)
      if self.speed.z == 0.0: animation = "tourneG"
      
    elif action == ACTION_STOP_TURNING :
      self.speed.reset_orientation_scaling()
      if self.speed.z == 0.0: animation = "attente"
      
    elif action == ACTION_TURN_RIGHT:
      self.speed.rotate_lateral(-5.0)
      if self.speed.z == 0.0: animation = "tourneD"
      
    elif action == ACTION_JUMP:
      if self.speed.y == 0.0: self.speed.y = 0.6
      
    if self.speed.y: animation = "chute"
    if animation: self.set_animation(animation)
    
    self.set_current_state_importance(2)
    
  def do_physics(self):
    super(Mobile, self).do_physics()
    
    if    self.speed.y <  0.0: self.set_animation("chute")
    elif (self.speed.y == 0.0) and (self.current_animation == "chute"):
      if   self.speed.z < 0.0: self.set_animation("marche")
      elif self.speed.z > 0.0: self.set_animation("recule")
      else:                    self.set_animation("attente")
      
  def control_owned(self):
    super(Mobile, self).control_owned()

    local_mobiles = [mobile for mobile in self.level.mobiles if mobile.local]
    
    self.control_keys = CONTROL_KEYS[min(len(local_mobiles), len(CONTROL_KEYS)) - 1]

    if len(local_mobiles) == 1:
      soya.MAIN_LOOP.camera = soya.TravelingCamera(soya.MAIN_LOOP.scenes[0])
      soya.MAIN_LOOP.camera.back = 70.0
      group = soya.widget.Group()
      group.add(soya.MAIN_LOOP.camera)
      soya.widget.FPSLabel(group)
      soya.set_root_widget(group)

      traveling = soya.ThirdPersonTraveling(self)
      traveling.distance = 5.0
      soya.MAIN_LOOP.camera.add_traveling(traveling)
      soya.MAIN_LOOP.camera.zap()
      
  def control_lost(self):
    super(Mobile, self).control_lost()

    if self.control_keys == CONTROL_KEYS[0]:
      soya.MAIN_LOOP.camera.parent.remove(soya.MAIN_LOOP.camera)
      soya.MAIN_LOOP.camera = None
      soya.set_root_widget(None)
      

cerealizer.register(Mobile)
cerealizer.register(Level , soya.cerealizer4soya.SavedInAPathHandler(Level ))
cerealizer.register(Player, soya.cerealizer4soya.SavedInAPathHandler(Player))

if (mode == "server") or (mode == "single"): create_demo_level()
if (mode == "client") or (mode == "single"): soya.init("Soya & Tofu demo", 640, 480)
  
if (mode == "single"): logins = sys.argv[2:]
  
if (mode == "client"):
  tofu.HOST = sys.argv[2]
  logins = sys.argv[3:]

if (mode == "client") or (mode == "single"):
  tofu.PLAYER_IDS = [PlayerID(login, "test") for login in logins]
  
main_loop = MainLoop()



main_loop.main_loop()

# while 1:
#   main_loop = soya.MainLoop()
  
#   import gc, weakref, memtrack
#   print soya.MAIN_LOOP
#   soya.MAIN_LOOP = None
#   soya.IDLER     = None
#   print gc.collect()
#   print gc.collect()
#   print gc.collect()
#   print gc.garbage
  
#   nb = 0
#   level = None
#   for i in gc.get_objects():
#     #if isinstance(i, soya.Terrain): print "!!!", i
#     if isinstance(i, soya._CObj):
#       print "!!!", i
#       nb += 1
#     if isinstance(i, soya.TravelingCamera):
#       level = weakref.ref(i)
#     #if isinstance(i, Player): print "!!!", i
#   print nb, len(gc.get_objects())
#   print
#   #memtrack.track(level())
#   #memtrack.reverse_track(level())
  
#   import time, random
#   time.sleep(random.random())
#   main_loop = MainLoop(soya.World())
#   main_loop.main_loop()

