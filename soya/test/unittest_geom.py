import os, sys
import soya
from soya import Vector
soya.path.append(os.path.join(os.path.dirname(__file__), "data"))
from unittest import TestCase, main as unittest_main
soya.init("geom test case",width=1024,height=768)

class GeomTestCase(TestCase):

	def setUp(self):
		self.scene = scene = soya.World()

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

	def test_remove_geom(self):
		"""Proper remove of a Geom from it's body"""

		body = soya.Body(self.scene, soya.Model.get("caterpillar"))
		body.set_xyz( 5, 0,  0)
		body.mass = soya.SphericalMass(1,1)
		geom = body.geom = soya.GeomSphere(radius=1)

		self.assertTrue(geom.body is body)

		self.spend_time(10)

		body.geom = None

		self.assertTrue(geom.body is None)

	def test_remove_body_from_worl(self):
		"""Proper remove of a Geom from the parent space when the body is removed from it"""

		body = soya.Body(self.scene, soya.Model.get("caterpillar"))
		body.set_xyz( 5, 0,  0)
		body.mass = soya.SphericalMass(1,1)
		geom = body.geom = soya.GeomSphere(radius=1)

		self.assertTrue(geom.space is self.scene.space)
		self.assertTrue(geom in self.scene.space)

		self.spend_time(10)

		self.scene.remove(body)

		self.assertTrue(geom.space is None)
		self.assertTrue(geom not in self.scene.space)


if __name__ == '__main__':
	unittest_main()
