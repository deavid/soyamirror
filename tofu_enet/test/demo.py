
import sys, os, os.path

import soya, tofu_enet, cerealizer, soya.cerealizer4soya, soya.sdlconst as sdlconst


mode = sys.argv[1]

HERE = os.path.dirname(sys.argv[0])

soya.path.append(os.path.join(HERE, "data"))

tofu_enet.set_mode(mode)


class Player(tofu_enet.Player):
  def __init__(self, filename, password, opt_data = ""):
    tofu_enet.Player.__init__(self, filename, password, opt_data)
    
    mobile = Mobile()
    mobile.set_xyz(108.0, -8.0, 107.0)
    mobile.x += 2 * len(LEVEL.mobiles)
    LEVEL.add_mobile(mobile)
    self.add_mobile(mobile)
    self.save()
    
    
tofu_enet.CREATE_PLAYER = Player

class Level(tofu_enet.Level):
  def __init__(self):
    tofu_enet.Level.__init__(self)
    
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

class Action(tofu_enet.Action):
  def __init__(self, mobile, action):
    tofu_enet.Action.__init__(self, mobile)
    self.action = action
    


class Mobile(tofu_enet.Mobile):
  def __init__(self):
    tofu_enet.Mobile.__init__(self)
    
    self.model          = soya.AnimatedModel.get("balazar")
    self.solid          = 0
    self.speed          = soya.Vector(self)
    self.rotation_speed = 0.0
    
  def compute_action(self):
		for event in soya.process_event():
			if   event[0] == sdlconst.KEYDOWN:
				if   (event[1] == sdlconst.K_q) or (event[1] == sdlconst.K_ESCAPE): soya.MAIN_LOOP.stop()
				elif event[1] == sdlconst.K_UP:    self.plan_action(Action(self, ACTION_MOVE_FORWARD))
				elif event[1] == sdlconst.K_DOWN:  self.plan_action(Action(self, ACTION_MOVE_BACKWARD))
				elif event[1] == sdlconst.K_LEFT:  self.plan_action(Action(self, ACTION_TURN_LEFT))
				elif event[1] == sdlconst.K_RIGHT: self.plan_action(Action(self, ACTION_TURN_RIGHT))
				
			elif event[0] == sdlconst.KEYUP:
				if   event[1] == sdlconst.K_UP:    self.plan_action(Action(self, ACTION_STOP_MOVING))
				elif event[1] == sdlconst.K_DOWN:  self.plan_action(Action(self, ACTION_STOP_MOVING))
				elif event[1] == sdlconst.K_LEFT:  self.plan_action(Action(self, ACTION_STOP_TURNING))
				elif event[1] == sdlconst.K_RIGHT: self.plan_action(Action(self, ACTION_STOP_TURNING))
        
  def do_action(self, action):
    print action.action
    if   action.action == ACTION_MOVE_FORWARD : self.speed.z = -0.35
    elif action.action == ACTION_STOP_MOVING  : self.speed.z =  0.0
    elif action.action == ACTION_MOVE_BACKWARD: self.speed.z =  0.2
    elif action.action == ACTION_TURN_LEFT    : self.rotation_speed =  5.0
    elif action.action == ACTION_STOP_TURNING : self.rotation_speed =  0.0
    elif action.action == ACTION_TURN_RIGHT   : self.rotation_speed = -5.0
    
  def advance_time(self, proportion):
    tofu_enet.Mobile.advance_time(self, proportion)
    self.add_mul_vector(proportion, self.speed)
    self.rotate_y(proportion * self.rotation_speed)
    
  def control_owned(self):
    tofu_enet.Mobile.control_owned(self)
    
    if not getattr(soya.MAIN_LOOP, "camera", None):
      soya.MAIN_LOOP.camera = soya.TravelingCamera(soya.MAIN_LOOP.scenes[0])
      soya.MAIN_LOOP.camera.back = 70.0
      soya.set_root_widget(soya.MAIN_LOOP.camera)
      
    traveling = soya.ThirdPersonTraveling(self)
    traveling.distance = 5.0
    soya.MAIN_LOOP.camera.add_traveling(traveling)
    soya.MAIN_LOOP.camera.zap()
    
    
    
cerealizer.register(Action)
cerealizer.register(Mobile)
cerealizer.register(Level , soya.cerealizer4soya.SavedInAPathHandler(Level ))
cerealizer.register(Player, soya.cerealizer4soya.SavedInAPathHandler(Player))


if   mode == "server":
  try: os.mkdir("/tmp/tofu_data")
  except: pass
  try: os.mkdir("/tmp/tofu_data/players")
  except: pass
  try: os.mkdir("/tmp/tofu_data/levels")
  except: pass
  
  soya.path.insert(0, "/tmp/tofu_data")
  
  LEVEL = Level()
  LEVEL.filename = "demo"
  LEVEL.save()
  
elif mode == "client":
  soya.init("Soya & Tofu demo", 320, 240)
  tofu_enet.HOST = "127.0.0.1"
  tofu_enet.LOGIN = sys.argv[2]
  

main_loop = tofu_enet.MainLoop(soya.World())
main_loop.main_loop()

