# -*- indent-tabs-mode: t -*-

# Soya 3D tutorial
# Copyright (C) 2001-2002 Jean-Baptiste LAMY
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


# character-animation-2: Mixing Cal3D and Soya : Balazar with a sword

# In this lesson, we add a sword in the right hand of Balazar, the sorcerer of the
# previous lesson.
# The sword is a Soya object, wich is added inside the Cal3D character, and moves along
# with it!


# Imports and inits Soya.

import sys, os, os.path, soya, soya.widget as widget

soya.init()
soya.path.append(os.path.join(os.path.dirname(sys.argv[0]), "data"))

# Creates the scene.

scene = soya.World()

# Loads the sorcerer model.

sorcerer_model = soya.AnimatedModel.get("balazar")

# Creates the sorcerer.
# We need the sorcerer to be a World, in order to add other objects in it (= the sword).
# The Cal3D body is now added in the sorcerer world.

sorcerer = soya.World(scene)
sorcerer.rotate_y(-120.0)
#sorcerer_body = soya.Cal3dBody(sorcerer, sorcerer_model)
#sorcerer_body = soya.Body(sorcerer, sorcerer_model)
#sorcerer_body.animate_blend_cycle("marche")
sorcerer.model = sorcerer_model
sorcerer.animate_blend_cycle("marche")

# Creates a right hand world in the sorcerer, and attach it to the bone called 'mainD'
# (French abbrev for 'right hand').

right_hand = soya.World(sorcerer)
#sorcerer_body.attach_to_bone(right_hand, "mainD")
sorcerer.attach_to_bone(right_hand, "mainD")

# Creates a right_hand_item Body, with a sword model, inside the right hand.

#sword = soya.World()
#soya.Face(sword, [soya.Vertex(sword, 0.0, 0.0, 0.0), soya.Vertex(sword, 0.0, 1.0, 0.0), soya.Vertex(sword, 1.0, 0.0, 0.0)])
#epee = soya.Body(scene, sword.to_model())

right_hand_item = soya.Body(right_hand)
right_hand_item = soya.Body(right_hand, soya.Model.get("sword"))
right_hand_item.rotate_z(180.0)
right_hand_item.set_xyz(0.05, 0.1, 0.0)

# By using right_hand_item.set_model(...), you can easily replace the sword with an axe
# or a gun !
# Use Soya system coordinate conversion facilities for collision detection
# (e.g. Point(right_hand_item, 0.0, 0.0, -3.0) is the end of the sword)

camera = soya.Camera(scene)
camera.set_xyz(0.0, 1.5, 3.0)

soya.set_root_widget(widget.Group())
soya.root_widget.add(camera)
soya.root_widget.add(widget.FPSLabel())

soya.Light(scene).set_xyz(5.0, 5.0, 8.0)

soya.MainLoop(scene).main_loop()
