# -*- indent-tabs-mode: t -*-

#! /usr/bin/python -O

# Game Skeleton
# Copyright (C) 2003-2004 Jean-Baptiste LAMY
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

# Soya gaming tutorial, lesson 1
# Create the demo level

# A bunch of import
import sys, os, os.path
import tofu
import soya
import soya.widget as widget

from tofudemo import Level


# Inits Soya
soya.init()

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
	
	# Loads the shape "./shapes/ferme.data"
	# This model has been created in Blender
	house = soya.Shape.get("ferme")

	# Adds 2 houses in the level
	house1 = soya.Volume(level_static, house)
	house1.set_xyz(250.0, -7.2, 182.0)
	
	house2 = soya.Volume(level_static, house)
	house2.set_xyz(216.0, -11.25, 200.0)
	house2.rotate_y(100.0) # degrees
	
	# Creates a light in the level, similar to a sun (=a directional light)
	sun = soya.Light(level_static)
	sun.directional = 1
	sun.diffuse = (1.0, 0.8, 0.4, 1.0)
	sun.rotate_x(-45.0)
	
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
	level_static.filename = level.name = "level_tofudemo_static"
	level_static.save()
	level.filename = level.name = "level_tofudemo"
	level.save()
	

# Now we just display the level



# This function must be called the first time you run game_skel.
# Then, you can comment it, since the level has been saved.
create_level()

# Create the scene (a world with no parent)
scene = soya.World()

# Loads the level, and put it in the scene
level = tofu.Level.get("level_tofudemo")
scene.add(level)

# Creates a camera in the scene
camera = soya.Camera(scene)
camera.set_xyz(222.0, 0.0, 230.0)

# Creates a widget group, containing the camera and a label showing the FPS.
soya.set_root_widget(widget.Group())
soya.root_widget.add(camera)
soya.root_widget.add(widget.FPSLabel())

#soya.render(); soya.screenshot().resize((320, 240)).save(os.path.join(os.path.dirname(sys.argv[0]), "results", os.path.basename(sys.argv[0])[:-3] + ".jpeg"))

# Creates and run an "idler" (=an object that manage time and regulate FPS)
# By default, FPS is locked at 40.
soya.Idler(scene).idle()
