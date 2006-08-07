# TOFU
# Copyright (C) 2005-2006 Jean-Baptiste LAMY
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

import sys, os, os.path, struct
import soya, tofu_udp, cerealizer, soya.cerealizer4soya, soya.sdlconst as sdlconst, soya.widget, soya.label3d

HERE = os.path.dirname(sys.argv[0])
soya.path.append(os.path.join(HERE, "data"))
soya.AUTO_EXPORTERS_ENABLED = 0

mode = sys.argv[1][2:]
tofu_udp.set_side(mode)


class Player(tofu_udp.Player):
  def __init__(self, filename, password, opt_data = ""):
    tofu_udp.Player.__init__(self, filename, password, opt_data)
    
    level = tofu_udp.Level.get("demo")
    
    mobile = Mobile()
    mobile.set_xyz(108.0, -6.0, 107.0)
    label = soya.label3d.Label3D(mobile, filename)
    label.y = 3
    label.lit = 0
    label.auto_flip = 1
    level.add_mobile(mobile)
    self.add_mobile(mobile)

    
tofu_udp.CREATE_PLAYER = Player


class Level(tofu_udp.Level):
  def __init__(self):
    tofu_udp.Level.__init__(self)

def create_demo_level():
  level = Level()
  level.static_part = static_part = soya.World(level)
  
#   terrain = soya.Terrain(static_part)
#   terrain.from_image(soya.Image.get("map.png"))
#   terrain.multiply_height(50.0)
#   terrain.scale_factor = 1.5
#   terrain.texture_factor = 1.0
#   terrain.y = -35.0
#   terrain.set_material_layer(soya.Material.get("grass" ),  0.0,  15.0)
#   terrain.set_material_layer(soya.Material.get("ground"), 15.0,  25.0)
#   terrain.set_material_layer(soya.Material.get("snow"  ), 25.0,  50.0)

#   house1 = soya.Body(static_part, soya.Model.get("ferme"))
#   house1.set_xyz(125.0, -7.2, 91.0)

#   house2 = soya.Body(static_part, soya.Model.get("ferme"))
#   house2.set_xyz(108.0, -11.25, 100.0)
#   house2.rotate_y(100.0)

#   sun = soya.Light(static_part)
#   sun.directional = 1
#   sun.diffuse = (1.0, 0.8, 0.4, 1.0)
#   sun.rotate_x(-45.0)

#   level.atmosphere = soya.SkyAtmosphere()
#   level.atmosphere.ambient = (0.3, 0.3, 0.4, 1.0)
#   level.atmosphere.fog = 1
#   level.atmosphere.fog_type  = 0
#   level.atmosphere.fog_start = 40.0
#   level.atmosphere.fog_end   = 50.0
#   level.atmosphere.fog_color = level.atmosphere.bg_color = (0.2, 0.5, 0.7, 1.0)
#   level.atmosphere.skyplane  = 1
#   level.atmosphere.sky_color = (1.5, 1.0, 0.8, 1.0)

  #level.bot = Bot()
  #level.add_mobile(level.bot)
  #level.bot.set_xyz(128.0, 6.0, 107.0)
  
#  static_part.filename = "demo_static_part"#; static_part.save()
  level      .filename = "demo"            ; level      .save()
  level.discard()

  level = None
  import gc
  gc.collect()
  gc.collect()
  gc.collect()
  gc.collect()
  print gc.garbage

ACTION_MOVE_FORWARD  = "^"
ACTION_STOP_MOVING   = "-"
ACTION_MOVE_BACKWARD = "v"
ACTION_TURN_LEFT     = "<"
ACTION_STOP_TURNING  = "|"
ACTION_TURN_RIGHT    = ">"
ACTION_JUMP          = "J"

class Mobile(tofu_udp.InterpolatedAnimatedMobile):
  def __init__(self):
    tofu_udp.InterpolatedAnimatedMobile.__init__(self)
    
    self.model          = soya.AnimatedModel.get("balazar")
    self.solid          = 0
    self.radius         = 0.8
    self.radius_y       = 1.0
    
    self.left   = soya.Vector(self, -1.0,  0.0,  0.0)
    self.right  = soya.Vector(self,  1.0,  0.0,  0.0)
    self.down   = soya.Vector(self,  0.0, -1.0,  0.0)
    self.up     = soya.Vector(self,  0.0,  1.0,  0.0)
    self.front  = soya.Vector(self,  0.0,  0.0, -1.0)
    self.back   = soya.Vector(self,  0.0,  0.0,  1.0)
    
    self.counter = 0
    
  def generate_action(self):
    for event in soya.process_event():
      if   event[0] == sdlconst.KEYDOWN:
        if   (event[1] == sdlconst.K_q) or (event[1] == sdlconst.K_ESCAPE): soya.MAIN_LOOP.stop()
        elif event[1] == sdlconst.K_UP:     self.send_action(ACTION_MOVE_FORWARD)
        elif event[1] == sdlconst.K_DOWN:   self.send_action(ACTION_MOVE_BACKWARD)
        elif event[1] == sdlconst.K_LEFT:   self.send_action(ACTION_TURN_LEFT)
        elif event[1] == sdlconst.K_RIGHT:  self.send_action(ACTION_TURN_RIGHT)
        elif event[1] == sdlconst.K_LSHIFT: self.send_action(ACTION_JUMP)
        
      elif event[0] == sdlconst.KEYUP:
        if   event[1] == sdlconst.K_UP:    self.send_action(ACTION_STOP_MOVING)
        elif event[1] == sdlconst.K_DOWN:  self.send_action(ACTION_STOP_MOVING)
        elif event[1] == sdlconst.K_LEFT:  self.send_action(ACTION_STOP_TURNING)
        elif event[1] == sdlconst.K_RIGHT: self.send_action(ACTION_STOP_TURNING)
        
#     if not "jiba" in tofu_udp.LOGIN:
#       import random
#       if random.random() < 0.02: self.plan_action(Action(self, ACTION_MOVE_FORWARD))
#       if random.random() < 0.02: self.plan_action(Action(self, ACTION_MOVE_BACKWARD))
#       if random.random() < 0.02: self.plan_action(Action(self, ACTION_STOP_MOVING))
#       if random.random() < 0.02: self.plan_action(Action(self, ACTION_TURN_LEFT))
#       if random.random() < 0.02: self.plan_action(Action(self, ACTION_TURN_RIGHT))
#       if random.random() < 0.02: self.plan_action(Action(self, ACTION_STOP_TURNING))
#       if random.random() < 0.02: self.plan_action(Action(self, ACTION_JUMP))
      
#       import random
#       if random.random() < 0.01: soya.MAIN_LOOP.stop()
        
  def load_action(self, s): return Action(self, s)
  
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
    tofu_udp.InterpolatedAnimatedMobile.do_physics(self)
    
    center = soya.Point(self.next_state, 0.0, self.radius_y, 0.0)
    context = self.level.RaypickContext(center, max(self.radius, 0.1 + self.radius_y))
    
    r = context.raypick(center, self.down, 0.1 + self.radius_y, 1, 1)
    if r:
      ground, ground_normal = r
      ground.convert_to(self.level)
      self.next_state.y = ground.y
      if self.speed.y < 0.0: self.speed.y = 0.0
      
      if self.current_animation == "chute":
        if   self.speed.z < 0.0: self.set_animation("marche")
        elif self.speed.z > 0.0: self.set_animation("recule")
        else:                    self.set_animation("attente")
     
    else:
      self.speed.y = max(self.speed.y - 0.03, -0.5)
      if self.current_animation != "chute": self.set_animation("chute")
        
    for vec in (self.left, self.right, self.front, self.back, self.up):
      r = context.raypick(center, vec, self.radius, 1, 1)
      if r:
        collision, wall_normal = r
        hypo = vec.length() * self.radius - center.distance_to(collision)
        correction = wall_normal * hypo
        
        self.next_state += correction
        center          += correction
        
    self.set_current_state_importance(1)
    
  def control_owned(self):
    tofu_udp.InterpolatedAnimatedMobile.control_owned(self)
    
    if not getattr(soya.MAIN_LOOP, "camera", None):
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
    

class Bot(Mobile):
  def __init__(self):
    Mobile.__init__(self)
    self.counter = 0
    
  def generate_action(self):
    self.counter += 1
    if   self.counter == 35: self.plan_action(Action(self, ACTION_MOVE_FORWARD))
    elif self.counter == 55: self.plan_action(Action(self, ACTION_MOVE_BACKWARD)); self.counter = 0
    

cerealizer.register(Mobile)
cerealizer.register(Bot)
cerealizer.register(Level , soya.cerealizer4soya.SavedInAPathHandler(Level ))
cerealizer.register(Player, soya.cerealizer4soya.SavedInAPathHandler(Player))

if   mode == "server":
  create_demo_level()
  
elif mode == "client":
  soya.init("Soya & Tofu demo", 640, 480)
  tofu_udp.LOGIN    = sys.argv[2]
  tofu_udp.PASSWORD = "test"
  if len(sys.argv) >= 4: tofu_udp.HOST = sys.argv[3]
  
elif mode == "single":
  create_demo_level()
  
  soya.init("Soya & Tofu demo", 640, 480)
  tofu_udp.LOGIN = sys.argv[2]
  tofu_udp.PASSWORD = "test"


main_loop = tofu_udp.MainLoop(soya.World())
main_loop.main_loop()

# while 1:
#   import time, random
#   time.sleep(random.random())
#   main_loop = tofu_udp.MainLoop(soya.World())
#   main_loop.main_loop()
