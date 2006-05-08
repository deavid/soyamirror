import sys, os, os.path
import soya
from math import sqrt
from random import random, shuffle

from bbomber import Level
from bbomber import SoftBox



# Inits Soya
soya.init()


# Define data path (=where to find models, textures, ...)
HERE = os.path.dirname(sys.argv[0])
soya.path.append(os.path.join(HERE, "data"))


class Intro:
    def create_level(self):
        level = Level()
        level_static = soya.World(level)
        
        
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
        atmosphere.fog_end   = 50.0
        atmosphere.fog_color = atmosphere.bg_color = (0.2, 0.5, 0.7, 1.0)
        atmosphere.skyplane  = 1
        atmosphere.sky_color = (1.5, 1.0, 0.8, 1.0)
          
        # Set the atmosphere to the level
        level.atmosphere = atmosphere
          
        # Save the level as "./worlds/level_demo.data" (remember, levels are subclasses of worlds)
        level_static.filename = level.name = "intro_bbomber_static"
        level_static.save()
        level.filename = level.name = "intro_bbomber"
        level.save()
          
            
class Level1:    
    def create_level(self, name):
      """This function creates and saves the game skeleton demo level."""
      
      # Create a level object
      level = Level()
      size_y=8
      size_x=10
      # Separates static and non static parts
      # This will speed up network games, since only the non static part will be
      # sent on the network
      level_static = soya.World(level)
      
      # Load 3 materials (= textures) for files ./materials{grass|ground|snow}.data
    
      ground = soya.Material.get("block2")
    
      
      # Creates a landscape, from the heighmap "./images/map.png"
      # The landscape is in the static part (=level_static), because it won't change along the game.
      land = soya.Land(level_static)
      land.y =0.0
      land.from_image(soya.Image.get("floor.png"))
      
      # Sets how high is the landscape
      land.multiply_height(-0.0)
      
      # These values are trade of between quality and speed
      land.map_size = 8
      land.scale_factor = 1.5
      land.texture_factor = 1.0
      
      # Set the texture on the landscape, according to the height
      # (i.e. height 0.0 to 15.0 are textured with grass, ...)
    
      land.set_material_layer(ground, 0.0,  25.0)
    
      # squares where the player starts
      # Note that this is stored in physical, not abstract, coordinates.
      always_clear=[(-1,-1),(-2,-1),(0,-1),(-1,-2),(-1,0)]
      cube = soya.Shape.get("cube")
          
      # r and c represent the cube positions in the grid,
      # while x and y represent the physical coordinates in the world.
      # Note the simple formula: r = x + self.size_x , c = y + self.size_y
      border_row, border_col = 2*size_x - 2, 2*size_y - 2
      for r, x in enumerate(range(-size_x,size_x-1)):
          for c, y in enumerate(range(-size_y,size_y-1)):
            bx = x +128
            by = y +128        
            if (r % 2 == 0 and c % 2 == 0) or \
               (r == 0 or c == 0 or r == border_row  or c == border_col ):
              # This is a wall block
              block = soya.Volume(level_static, cube)
              block.scale(1.0, 1.0, 1.0)
              block.set_xyz(bx, 0.5, by) 
            elif random() < 0.8 and not (x, y) in always_clear:
              # A soft block
              block = SoftBox()
              level.add_mobile(block)
              block.scale(1.0, 1.0,1.0)
              block.set_xyz(bx, 0.5, by)
            
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
      atmosphere.fog_end   = 50.0
      atmosphere.fog_color = atmosphere.bg_color = (0.2, 0.5, 0.7, 1.0)
      atmosphere.skyplane  = 1
      atmosphere.sky_color = (1.5, 1.0, 0.8, 1.0)
      
      # Set the atmosphere to the level
      level.atmosphere = atmosphere
      
      # Save the level as "./worlds/level_demo.data" (remember, levels are subclasses of worlds)
      level_static.filename = level.name = name+"_bbomber_static"
      level_static.save()
      level.filename = level.name = name+"_bbomber"
      level.save()
      

# Now we just display the level


thelevel = Intro()
print "creating the intro level"
thelevel.create_level()
thelevel = Level1()
print "creating level1"
thelevel.create_level('level1')
print "creating level2"
thelevel.create_level('level2')
