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
import soya, tofu_udp, cerealizer, soya.cerealizer4soya, soya.sdlconst as sdlconst, soya.widget

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
    mobile.x += 2 * len(level.mobiles)
    level.add_mobile(mobile)
    self.add_mobile(mobile)
    
tofu_udp.CREATE_PLAYER = Player


class Level(tofu_udp.Level):
  def __init__(self):
    tofu_udp.Level.__init__(self)
    
    self.terrain = soya.Terrain(self)
    self.terrain.from_image(soya.Image.get("map.png"))
    self.terrain.multiply_height(50.0)
    self.terrain.scale_factor = 1.5
    self.terrain.texture_factor = 1.0
    self.terrain.y = -35.0
    self.terrain.set_material_layer(soya.Material.get("grass" ),  0.0,  15.0)
    self.terrain.set_material_layer(soya.Material.get("ground"), 15.0,  25.0)
    self.terrain.set_material_layer(soya.Material.get("snow"  ), 25.0,  50.0)
    
    self.house1 = soya.Body(self, soya.Model.get("ferme"))
    self.house1.set_xyz(125.0, -7.2, 91.0)
    
    self.house2 = soya.Body(self, soya.Model.get("ferme"))
    self.house2.set_xyz(108.0, -11.25, 100.0)
    self.house2.rotate_y(100.0)
    
    self.sun = soya.Light(self)
    self.sun.directional = 1
    self.sun.diffuse = (1.0, 0.8, 0.4, 1.0)
    self.sun.rotate_x(-45.0)
    
    self.atmosphere = soya.SkyAtmosphere()
    self.atmosphere.ambient = (0.3, 0.3, 0.4, 1.0)
    self.atmosphere.fog = 1
    self.atmosphere.fog_type  = 0
    self.atmosphere.fog_start = 40.0
    self.atmosphere.fog_end   = 50.0
    self.atmosphere.fog_color = self.atmosphere.bg_color = (0.2, 0.5, 0.7, 1.0)
    self.atmosphere.skyplane  = 1
    self.atmosphere.sky_color = (1.5, 1.0, 0.8, 1.0)
    

ACTION_MOVE_FORWARD  = "^"
ACTION_STOP_MOVING   = "-"
ACTION_MOVE_BACKWARD = "v"
ACTION_TURN_LEFT     = "<"
ACTION_STOP_TURNING  = "|"
ACTION_TURN_RIGHT    = ">"
ACTION_JUMP          = "J"

class Action(tofu_udp.Action):
  def __init__(self, mobile, action, round = None):
    tofu_udp.Action.__init__(self, mobile, round)
    self.action = action
    
  def dumps(self): return self.mobile_uid + self.action + struct.pack("!q", self.round)
  
tofu_udp.LOAD_ACTION = lambda s: Action(tofu_udp.Unique.undumpsuid(s[:4]), s[4], struct.unpack("!q", s[5:])[0])

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
    
  def compute_action(self):
    for event in soya.process_event():
      if   event[0] == sdlconst.KEYDOWN:
        if   (event[1] == sdlconst.K_q) or (event[1] == sdlconst.K_ESCAPE): soya.MAIN_LOOP.stop()
        elif event[1] == sdlconst.K_UP:     self.plan_action(Action(self, ACTION_MOVE_FORWARD))
        elif event[1] == sdlconst.K_DOWN:   self.plan_action(Action(self, ACTION_MOVE_BACKWARD))
        elif event[1] == sdlconst.K_LEFT:   self.plan_action(Action(self, ACTION_TURN_LEFT))
        elif event[1] == sdlconst.K_RIGHT:  self.plan_action(Action(self, ACTION_TURN_RIGHT))
        elif event[1] == sdlconst.K_LSHIFT: self.plan_action(Action(self, ACTION_JUMP))
        
      elif event[0] == sdlconst.KEYUP:
        if   event[1] == sdlconst.K_UP:    self.plan_action(Action(self, ACTION_STOP_MOVING))
        elif event[1] == sdlconst.K_DOWN:  self.plan_action(Action(self, ACTION_STOP_MOVING))
        elif event[1] == sdlconst.K_LEFT:  self.plan_action(Action(self, ACTION_STOP_TURNING))
        elif event[1] == sdlconst.K_RIGHT: self.plan_action(Action(self, ACTION_STOP_TURNING))
        
  def do_action(self, action):
    #print action.action
    animation = ""
    if   action.action == ACTION_MOVE_FORWARD : self.speed.z = -0.35; animation = "marche"
    elif action.action == ACTION_STOP_MOVING  : self.speed.z =  0.0 ; animation = "attente"
    elif action.action == ACTION_MOVE_BACKWARD: self.speed.z =  0.2 ; animation = "recule"
    
    elif action.action == ACTION_TURN_LEFT:
      self.speed.rotate_lateral( 5.0)
      if self.speed.z == 0.0: animation = "tourneG"
      
    elif action.action == ACTION_STOP_TURNING :
      self.speed.reset_orientation_scaling()
      if self.speed.z == 0.0: animation = "attente"
      
    elif action.action == ACTION_TURN_RIGHT:
      self.speed.rotate_lateral(-5.0)
      if self.speed.z == 0.0: animation = "tourneD"
      
    elif action.action == ACTION_JUMP:
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
    
    
cerealizer.register(Action)
cerealizer.register(Mobile)
cerealizer.register(Level , soya.cerealizer4soya.SavedInAPathHandler(Level ))
cerealizer.register(Player, soya.cerealizer4soya.SavedInAPathHandler(Player))

if   mode == "server":
  #LEVEL = Level()
  #LEVEL.filename = "demo"
  #LEVEL.save()
  pass
  
elif mode == "client":
  soya.init("Soya & Tofu demo", 640, 480)
  tofu_udp.LOGIN    = sys.argv[2]
  tofu_udp.PASSWORD = "test"
  if len(sys.argv) >= 4: tofu_udp.HOST = sys.argv[3]
  
elif mode == "single":
  #LEVEL = Level()
  #LEVEL.filename = "demo"
  #LEVEL.save()
  
  soya.init("Soya & Tofu demo", 640, 480)
  tofu_udp.LOGIN = sys.argv[2]
  tofu_udp.PASSWORD = "test"

main_loop = tofu_udp.MainLoop(soya.World())
main_loop.main_loop()

