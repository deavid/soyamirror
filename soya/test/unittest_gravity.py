import os, sys
import soya
from soya import Vector
soya.path.append(os.path.join(os.path.dirname(__file__), "data"))
from unittest import TestCase, main as unittest_main
soya.init("gravity test case",width=1024,height=768)

class GravityTestCase(TestCase):

	def setUp(self):
		self.scene = scene = soya.World()
		scene.gravity = soya.Vector(scene,0,-9.8,0)

		light = soya.Light(scene)
		light.set_xyz(15, 15, -15)
		camera = soya.Camera(scene)
		camera.set_xyz(0, 0,-10)
		camera.look_at(soya.Point(scene, 0, 0, 0))
		soya.set_root_widget(camera)
		self.main_loop = soya.MainLoop(scene)


	def spend_time(self, time):
		for time in xrange(time):
			self.main_loop.begin_round() ;
			self.main_loop.advance_time(1.0) ;
			self.main_loop.end_round();

	def test_body(self):

		body = soya.Body(self.scene, soya.Model.get("caterpillar"))
		body.set_xyz( 5, 0,  0)
		body.mass = soya.SphericalMass(1,1)

		self.spend_time(10)

		self.assert_(body.y < 0)
		self.assertEquals(body.x, 5)
		self.assertEquals(body.z, 0)

	def test_world(self):
		world = soya.World(self.scene, soya.Model.get("caterpillar_head"))
		world.set_xyz(-5, 0, 0)
		world.mass = soya.SphericalMass(1,1)

		self.spend_time(10)

		self.assert_(world.y < 0)
		self.assertEquals(world.x, -5)
		self.assertEquals(world.z,  0)

if __name__ == '__main__':
	unittest_main()
