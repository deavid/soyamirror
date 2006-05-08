#! /usr/bin/python -O

import sys, os, os.path
import soya
import soya.widget as widget

soya.init()

import pudding
import pudding.core
import pudding.control
import pudding.idler
import pudding.ext.fpslabel

pudding.init()

from SoyaModelling.explorer import PuddingExplorerIdler

HERE = os.path.dirname(sys.argv[0])
soya.path.append('/home/dunk/cvs/soya/tutorial/data/')

doc = """

ExplorerIdler Test
------------------

  * use aswd keys to move around 
  * use middle click and mouse move to look around 
  * cntrl + midlle click and mouse move to "zoom" blender style
  * ESC to quit

  Its quite easy to extend this class to use for level editors and such

  have fun 

"""

print doc

class Level(soya.World):
  pass

def create_level():
  """This function creates and saves the game skeleton demo level."""
  
  # Create a level object
  level = Level()
  
  # Separates static and non static parts
  # This will speed up network games, since only the non static part will be
  # sent on the network
  level_static = soya.World(level)
  
  # Load 3 materials (= textures) for files ./materials{grass|ground|snow}.data
  grass  = soya.Material.get("grass")
  ground = soya.Material.get("ground")
  snow   = soya.Material.get("snow")
  
  # Creates a landscape, from the heighmap "./images/map.png"
  # The landscape is in the static part (=level_static), because it won't change along the game.
  land = soya.Land(level_static)
  land.y = -35.0
  land.from_image(soya.Image.get("map.png"))
  
  # Sets how high is the landscape
  land.multiply_height(50.0)
  
  # These values are trade of between quality and speed
  land.map_size = 8
  land.scale_factor = 1.5
  land.texture_factor = 1.0
  
  # Set the texture on the landscape, according to the height
  # (i.e. height 0.0 to 15.0 are textured with grass, ...)
  land.set_material_layer(grass,   0.0,  15.0)
  land.set_material_layer(ground, 15.0,  25.0)
  land.set_material_layer(snow,   25.0,  50.0)
  
  # Creates a light in the level, similar to a sun (=a directional light)
  sun = soya.Light(level_static)
  sun.directional = 1
  sun.diffuse = (1.0, 0.8, 0.4, 1.0)
  sun.rotate_vertical(-45.0)
  
  # Creates a sky atmosphere, with fog
  atmosphere = soya.SkyAtmosphere()
  atmosphere.ambient = (0.3, 0.3, 0.4, 1.0)
  atmosphere.fog = 1
  atmosphere.fog_type  = 0
  atmosphere.fog_start = 40.0
  atmosphere.fog_end   = 200.0
  atmosphere.fog_color = atmosphere.bg_color = (0.2, 0.5, 0.7, 1.0)
  atmosphere.skyplane  = 1
  atmosphere.sky_color = (1.5, 1.0, 0.8, 1.0)
  
  # Set the atmosphere to the level
  level.atmosphere = atmosphere
  
  # Save the level as "./worlds/level_demo.data" (remember, levels are subclasses of worlds)
  level_static.filename = level.name = "level_demo_static"
  level_static.save()
  level.filename = level.name = "level_demo"
  level.save()
  
if __name__ == '__main__':
  create_level()

  # Create the scene (a world with no parent)
  scene = soya.World()

  # Loads the level, and put it in the scene
  level = soya.World.get("level_demo")
  scene.add(level)

  # Creates a camera in the scene
  camera = soya.Camera(scene)
  camera.back = level.atmosphere.fog_end
  camera.look_at(soya.Point(level, 100, 0, 100))

  # Creates a widget group, containing the camera and a label showing the FPS.
  soya.set_root_widget(pudding.core.RootWidget())
  soya.root_widget.add_child(camera)

  #soya.render(); soya.screenshot().resize((320, 240)).save(os.path.join(os.path.dirname(sys.argv[0]), "results", os.path.basename(sys.argv[0])[:-3] + ".jpeg"))

  # Creates and run an "idler" (=an object that manage time and regulate FPS)
  # By default, FPS is locked at 40.
  PuddingExplorerIdler(camera, scene).idle()
