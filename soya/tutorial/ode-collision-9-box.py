# -*- indent-tabs-mode: t -*-

# In this tutorial we'll learn how made soya detect collision with ODE
# 
# Our example is to simple head going on eatch other
#
# To enable ODE's collision detection, you only have create a Geom for bodys 
# you want to collide. here we use : "GeomSphere(body,radius)"

import sys, os
import soya
import soya.sphere, soya.cube

#evil hack

soya.init("collision-1-base",width=1024,height=768)
soya.path.append(os.path.join(os.path.dirname(sys.argv[0]), "data"))

# create world
scene = soya.World()
# getting material
ground = soya.Material(soya.Image.get("block2.png"))
metal  = soya.Material(soya.Image.get("metal1.png"))
cube_mat   = soya.Material(soya.Image.get("chaume.png"))
#blue_mat.separate_specular = 1
# creating Model
m_ball = soya.sphere.Sphere(None,metal).shapify()
m_cube = soya.cube.Cube(None, cube_mat,size=3).shapify()
m_ground = soya.cube.Cube(None, ground,size=78).shapify()
#creating Body
ground = soya.Body(scene,m_ground)
ball   = soya.Body(scene,m_ball)
cubes = []
for i in xrange(15):
	cubes.append(soya.Body(scene,m_cube))
## Adding a mass ##
ball_density = 25000
ground.pushable = False
ground.gravity_mode = False
ground.mass     = soya.SphericalMass(1)
ball.mass       =soya.SphericalMass(ball_density)
for cube in cubes:
	cube.mass =soya.BoxedMass(1, 3, 3, 3)
scene.gravity = soya.Vector(scene,0,-9.8,0)
#Adding Geom
ball.bounciness = 1
soya.GeomSphere(ball)
for cube in cubes:
	soya.GeomBox(cube,(3,3,3))
soya.GeomBox(ground,(78,78,78))

	
######
#placing bodys
ground.y-= 39
ball.z   = 10
ball.y   = 0.6
ball.x   = -1

cubes[0].set_xyz(   0,14.0,0)
cubes[1].set_xyz(-1.6, 10.90,0)
cubes[2].set_xyz( 1.6, 10.90,0)
cubes[3].set_xyz(-3.2, 7.80,0)
cubes[4].set_xyz(   0, 7.80,0)
cubes[5].set_xyz( 3.2, 7.80,0)
cubes[6].set_xyz(-4.8, 4.70,0)
cubes[7].set_xyz(-1.6, 4.70,0)
cubes[8].set_xyz( 1.6, 4.70,0)
cubes[9].set_xyz( 4.8, 4.70,0)
cubes[10].set_xyz(-6.4,1.60,0)
cubes[11].set_xyz(-3.2,1.60,0)
cubes[12].set_xyz(   0,1.60,0)
cubes[13].set_xyz( 3.2,1.60,0)
cubes[14].set_xyz( 6.4,1.60,0)



ball.add_force(soya.Vector(scene,ball_density*-50,0,ball_density*-2500))

#placing light over the duel
light = soya.Light(scene)
light.set_xyz(-10, 45,45)
# adding camera
camera = soya.Camera(scene)
camera.set_xyz(13,15,30)
camera.look_at(cubes[4])
camera.back=300
#running soya
soya.set_root_widget(camera)
ml = soya.MainLoop(scene)
ml.main_loop()
