from soya import Body, Vector
from soya.testlib import SoyaTestCase, unittest_main

class ODEVectorTC(SoyaTestCase):
	def setup_scene(self):
		super(ODEVectorTC, self).setup_scene()
		self.body = Body(self.scene)
		self.body.ode = True

	def test_linear_velocity_rest(self):
		vel = self.body.linear_velocity
		vel_coord = (vel.x, vel.y, vel.z)
		self.assertEquals(vel_coord, (0, 0, 0))

	def test_linear_velocity_None(self):
		self.body.add_force(Vector(None, 0.4, 0.7, 0.8))
		self.run_soya_rounds()
		vel = self.body.linear_velocity
		self.assertNotEquals(vel.x, 0)
		self.assertNotEquals(vel.y, 0)
		self.assertNotEquals(vel.z, 0)
		self.body.linear_velocity = None
		vel = self.body.linear_velocity
		self.assertEquals(vel.x, 0)
		self.assertEquals(vel.y, 0)
		self.assertEquals(vel.z, 0)

	def test_angular_velocity_rest(self):
		vel = self.body.angular_velocity
		vel_coord = (vel.x, vel.y, vel.z)
		self.assertEquals(vel_coord, (0, 0, 0))

	def test_angular_velocity_None(self):
		self.body.add_torque(Vector(None, 0.4, 0.7, 0.8))
		self.run_soya_rounds()
		vel = self.body.angular_velocity
		self.assertNotEquals(vel.x, 0)
		self.assertNotEquals(vel.y, 0)
		self.assertNotEquals(vel.z, 0)
		self.body.angular_velocity = None
		vel = self.body.angular_velocity
		self.assertEquals(vel.x, 0)
		self.assertEquals(vel.y, 0)
		self.assertEquals(vel.z, 0)

	def test_torque_rest(self):
		torque = self.body.torque
		self.assertEquals(torque.x, 0)
		self.assertEquals(torque.y, 0)
		self.assertEquals(torque.z, 0)

	def test_torque_None(self):
		self.body.add_torque(Vector(None, +0.5, -25, -78))
		torque = self.body.torque
		self.assertNotEquals(torque.x, 0)
		self.assertNotEquals(torque.y, 0)
		self.assertNotEquals(torque.z, 0)
		self.body.torque = None
		torque = self.body.torque
		self.assertEquals(torque.x, 0)
		self.assertEquals(torque.y, 0)
		self.assertEquals(torque.z, 0)

	def test_force_rest(self):
		force = self.body.force
		self.assertEquals(force.x, 0)
		self.assertEquals(force.y, 0)
		self.assertEquals(force.z, 0)

	def test_force_None(self):
		self.body.add_force(Vector(None, +0.5, -25, -78))
		force = self.body.force
		self.assertNotEquals(force.x, 0)
		self.assertNotEquals(force.y, 0)
		self.assertNotEquals(force.z, 0)
		self.body.force = None
		force = self.body.force
		self.assertEquals(force.x, 0)
		self.assertEquals(force.y, 0)
		self.assertEquals(force.z, 0)

if __name__ == '__main__':
	unittest_main()
