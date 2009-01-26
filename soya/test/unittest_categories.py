from soya import Body, GeomSphere, Vector
from soya.testlib import SoyaTestCase, unittest_main

class Witness(Body):
	
	def __init__(self, *args, **kargs):
		Body.__init__(self, *args, **kargs)
		self.collide_trace = []
		GeomSphere(self)

	def hit(self, other, contacts):
		for contact in contacts:
			self.collide_trace.append(other)

class ODECategoriesTC(SoyaTestCase):

	def setup_scene(self):
		super(ODECategoriesTC, self).setup_scene()
		self.witness_1 = Witness(self.scene)
		self.witness_2 = Witness(self.scene)

	def test_collide_standard(self):
		self.run_soya_rounds()
		self.assertTrue(self.witness_1.collide_trace)
		self.assertTrue(self.witness_2.collide_trace)

	def test_collide_bit_null(self):
		self.witness_1.geom.collide_bits = 0
		self.witness_2.geom.collide_bits = 0
		self.run_soya_rounds()
		self.assertEquals(self.witness_1.collide_trace, [])
		self.assertEquals(self.witness_2.collide_trace, [])

	def test_category_bit_null(self):
		self.witness_1.geom.category_bits = 0
		self.witness_2.geom.category_bits = 0
		self.run_soya_rounds()
		self.assertEquals(self.witness_1.collide_trace, [])
		self.assertEquals(self.witness_2.collide_trace, [])

	def test_collide_incompatible(self):
		self.witness_1.geom.collide_bits  = 1
		self.witness_2.geom.collide_bits  = 2
		self.witness_1.geom.category_bits = 1
		self.witness_2.geom.category_bits = 2
		self.run_soya_rounds()
		self.assertEquals(self.witness_1.collide_trace, [])
		self.assertEquals(self.witness_2.collide_trace, [])

	def test_collide_compatible_equals(self):
		self.witness_1.geom.collide_bits  = 2
		self.witness_2.geom.collide_bits  = 0
		self.witness_1.geom.category_bits = 0
		self.witness_2.geom.category_bits = 2
		self.run_soya_rounds()
		self.assertNotEquals(self.witness_1.collide_trace, [])
		self.assertNotEquals(self.witness_2.collide_trace, [])

	def test_collide_compatible_equals(self):
		self.witness_1.geom.collide_bits  = 2
		self.witness_2.geom.collide_bits  = 0
		self.witness_1.geom.category_bits = 0
		self.witness_2.geom.category_bits = 2
		self.run_soya_rounds()
		self.assertNotEquals(self.witness_1.collide_trace, [])
		self.assertNotEquals(self.witness_2.collide_trace, [])

	def test_collide_compatible_overlay(self):
		self.witness_1.geom.collide_bits  = 0
		self.witness_2.geom.collide_bits  = 6
		self.witness_1.geom.category_bits = 12
		self.witness_2.geom.category_bits = 0
		self.run_soya_rounds()
		self.assertNotEquals(self.witness_1.collide_trace, [])
		self.assertNotEquals(self.witness_2.collide_trace, [])

	def test_collide_compatible_wide(self):
		self.witness_1.geom.collide_bits  = ~1
		self.witness_2.geom.collide_bits  = ~1
		self.witness_1.geom.category_bits = 2
		self.witness_2.geom.category_bits = 2
		self.run_soya_rounds()
		self.assertNotEquals(self.witness_1.collide_trace, [])
		self.assertNotEquals(self.witness_2.collide_trace, [])

if __name__ == '__main__':
	unittest_main()
