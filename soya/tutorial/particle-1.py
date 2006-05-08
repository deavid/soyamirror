# Soya 3D tutorial
# Copyright (C) 2001-2004 Jean-Baptiste LAMY
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

# This shows how to use soya's particles.

# Imports and inits Soya (see lesson basic-1.py).

import sys, os, os.path, soya

from random import random
from math import sqrt
from soya import sdlconst
from soya import particle

soya.init()
soya.path.append(os.path.join(os.path.dirname(sys.argv[0]), "data"))

# Creates the scene.

scene = soya.World()

# Create a particle system

# particles are just like any other object in soya. you must 
# still add them to the scene and they have the same methods available.
# all particles also support a material for the sprite which you can 
# pass to the constructor or set as a property later.
# particle systems have nb_particles to specifiy how many particles
# will be generated, in conjunction with this there is the 
# auto_generate_particle property which determines wether new particles
# should be created when old ones die or not.

# comment/uncomment the different sections to try the different systems

# here we use the built in FireWork system. auto_generate_particle is 
# on by default so this will continue forever
fountain = particle.FlagFirework(scene, nb_particles=4, nb_sub_particles=10)

# this is slightly more dull
# you will notice that this doesnt automatically set auto_generate_particle
#smoke=particle.Smoke(scene)

# here we use the same smoke particle system but set auto_generate_particle
# so that it continues
#smoke=particle.Smoke(scene)
#smoke.auto_generate_particle=1

# its also possible to create your own particle systems
# i dont think you can beat looking at the source file model/particle.pyx
# for understanding how to do this 
class MyParticleSystem(particle.Smoke):
  def __init__(self,parent):
    particle.Particles.__init__(self,parent,nb_max_particles=50)
    self.set_colors((1.0, 1.0, 1.0, 1.0), (1.0, 0.0, 0.0,0.5),(1.0,1.0,0.,0.5),(0.5,0.5,0.5,0.5),(0.,0.,0.,0.5))
    self.set_sizes ((0.19, 0.19), (0.35, 0.35))
    self.auto_generate_particle=1

  def generate(self, index):
    sx = (random()- 0.5) * .2
    sy = (random())
    sz = (random() - 0.5) * .2
    l = (0.2 * (1.0 + random())) / sqrt(sx * sx + sy * sy + sz * sz) * 0.5
    self.set_particle(index, random()*.5, sx * l, sy * l, sz * l, 0.,0.,0.)

#particles=MyParticleSystem(scene)

# Creates a light.

light = soya.Light(scene)
light.set_xyz(0.5, 0.0, 2.0)

# Creates a camera.

camera = soya.Camera(scene)
camera.z = 10.0
soya.set_root_widget(camera)

# make an idler that stops on any keystroke
class Idler(soya.Idler):
  def begin_round(self):
    soya.Idler.begin_round(self)

    # wait for any keystoke to quit
    for e in soya.process_event():
      if e[0]==sdlconst.KEYDOWN and e[1]!=0:
        self.stop()        

Idler(scene).idle()


