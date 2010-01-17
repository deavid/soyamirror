# -*- indent-tabs-mode: t -*-

import sys, os

import soya

# tutorial at a fetus stade


soya.init("first ODE test",width=1024,height=768)

soya.path.append(os.path.join(os.path.dirname(sys.argv[0]), "data"))

#predefined mass generating function
#SphericalMass
#BoxedMass
#CylindricalMass
#CappedCylindricalMass(



# create a world
scene = soya.World()
m = soya.Mass()
### The Mass parameter :
# - mass
#    A float corresponding to the total mass of the Mass object.
m.mass = 50
print 'Mass:', m.mass
# - c
#    The center of gravity position in the Body frame.
#    Take care it's a three floats tuple (x,y,z) NOT a soya.Vector
m.c = (0,5.4,-9)
print 'Center of Gravity:', m.c
# - I
#   The Inertia Tensor of the Mass object (3-tuple 3-tuples floats)
# it a read only attribute
# ((a,b,c),
#  (b,d,e),
#  (c,e,f))

#m.I = (
#	(1.,0 , 0),
#	(0 ,1., 0),
#	(0 ,0 ,1.))
m.set_parameters(m.mass, 0,0,0, 511, 522, 533, 512, 513, 523)
print 'Inertia Tensor:', m.I
# By default a Mass is created with this property :
#    Mass: 0.0
#    Center of Gravity: (0.0, 0.0, 0.0)
#    Inertia Tensor: ((0, 0, 0), (0, 0, 0), (0, 0, 0))



b = soya.Body(scene,mass=m)
# WARNING when a mass is assigned to a body it's value are
# are copied into the body and not cleanly referenced. so:
assert b.mass is not m
# and
assert b.mass == m
m.mass+=3
assert b.mass < m

# load a model
head_model = soya.Model.get("caterpillar_head")
# instanciate two Body
heads = [ soya.Body(scene,head_model) for i in xrange(2)]
# adding two mass
for head in heads:
    head.mass = soya.SphericalMass()
# Setting the gravity of the scene
scene.gravity = soya.Vector(scene,0,-9.8,0)
#Set whether the body is influenced by the world's gravity
#or not. If body.gravity_mode is True it is, otherwise it isn't.
#(default to True)
heads[0].gravity_mode = False
heads[1].gravity_mode = True
#place the head
heads[0].x=-3
heads[0].x= 3

#light and camera stuff
light = soya.Light(scene)
light.set_xyz(30, 5, -30)

camera = soya.Camera(scene)
camera.z = 25

soya.set_root_widget(camera)
ml = soya.MainLoop(scene)
ml.main_loop()
