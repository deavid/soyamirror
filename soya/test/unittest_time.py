import soya
from soya import Body, SphericalMass, Vector
from soya.testlib import SoyaTestCase, unittest_main


class ODETimeTC(SoyaTestCase):
	
	def setup_scene(self):
		super(ODETimeTC, self).setup_scene()
		self.body = Body(self.scene)
		self.body.mass = SphericalMass(50)
		self.scene.gravity = soya.Vector(self.scene, 0., -9.8, 0.)

	def test_step_duration(self):
		"""test that test duration are proportional to round duration"""
		body = self.body
		BASE_NUMBER_OF_STEP = 25

		body.set_xyz(0,0,0)
		for i in xrange(BASE_NUMBER_OF_STEP):
			self.run_soya_rounds()
		first_coord = body.y

		self.main_loop.round_duration /= 2
		body.set_xyz(0,0,0)
		body.force = Vector()
		body.linear_velocity = Vector()
		for i in xrange(BASE_NUMBER_OF_STEP * 2):
			self.run_soya_rounds()
		self.assertAlmostEquals(first_coord/body.y, 1, 0)
		self.assertAlmostEquals(first_coord/body.y, 1, 1)
		
	def test_quickstep(self):
		body = self.body
		body.set_xyz(0,0,0)
		for i in xrange(5):
			self.run_soya_rounds()
		first_coord = body.y

		self.scene.use_quickstep = True
		self.assertTrue(self.scene.use_quickstep)
		body.set_xyz(0,0,0)
		body.force = Vector()
		body.linear_velocity = Vector()
		for i in xrange(5):
			self.run_soya_rounds()
		self.assertAlmostEquals(first_coord, body.y)

	def test_slowstep(self):
		body = self.body
		body.set_xyz(0,0,0)
		for i in xrange(5):
			self.run_soya_rounds()
		first_coord = body.y

		self.scene.use_quickstep = False
		self.assertFalse(self.scene.use_quickstep)
		body.set_xyz(0,0,0)
		body.force = Vector()
		body.linear_velocity = Vector()
		for i in xrange(5):
			self.run_soya_rounds()
		self.assertAlmostEquals(first_coord, body.y)

if __name__ == '__main__':
	unittest_main()

# vim : sw=4: tw=4: et!
