from soya.testlib import SoyaTestCase, TestCase, unittest_main
from soya.sdlconst import *
from soya import coalesce_motion_event

DOWN_LEFT =  (KEYDOWN, K_LEFT, None) # add a valid modifier
DOWN_A =  (KEYDOWN, K_a, None) # add a valid modifier

MOUSE_MOTION_1   =  (MOUSEMOTION, 43, -35, 23, -20, 0)
MOUSE_MOTION_1_C   =  (MOUSEMOTION, 43, -35, 23, -20)
MOUSE_MOTION_2   =  (MOUSEMOTION, 50, -30,  7,   5, 0)
MOUSE_MOTION_2_C =  (MOUSEMOTION, 50, -30, 30, -15)
MOUSE_MOTION_3   =  (MOUSEMOTION, 45, -25, -5,   5, 0)
MOUSE_MOTION_3_C =  (MOUSEMOTION, 45, -25, 25, -10)

class CoalesceTC(TestCase):

	def _assert_unaltered(self, input):
		# XXX I don't check non alteration I may need to copy
		self._assert_in_out(input, input)

	def _assert_in_out(self, input, expected):
		output = coalesce_motion_event(input)
		self.assertEquals(output, expected)

	def test_empty(self):
		"""test that coalesce_motion_event don't alter empty list"""
		self._assert_unaltered( [] )

	def test_keydown_single(self):
		"""test that coalesce_motion_event don't alter list with a single
		keydown event"""
		self._assert_unaltered( [DOWN_LEFT] )

	def test_keydown_double(self):
		"""test that coalesce_motion_event don't alter list with two
		keydown events"""
		self._assert_unaltered( [DOWN_LEFT, DOWN_A] )

	def test_mouse_single(self):
		"""test that coalesce_motion_event don't alter list with a single
		mouse motion event"""
		self._assert_in_out( [MOUSE_MOTION_1], [MOUSE_MOTION_1_C] )

	def test_mouse_double(self):
		"""test that coalesce_motion_event don't alter list with two
		mouse motion event"""
		input =  [MOUSE_MOTION_1, MOUSE_MOTION_2]
		expected = [MOUSE_MOTION_2_C]
		self._assert_in_out(input, expected)

	def test_mouse_triple_interlaced(self):
		"""test that coalesce_motion_event don't alter list with three
		mouse motion event interlaced with KEYDOWN event"""
		input =  [MOUSE_MOTION_1, DOWN_A, MOUSE_MOTION_2, DOWN_A, DOWN_LEFT,
		          MOUSE_MOTION_3]
		expected = [DOWN_A, DOWN_A, DOWN_LEFT, MOUSE_MOTION_3_C]
		self._assert_in_out(input, expected)





class EventsTC(SoyaTestCase):

	def test_queue_event(self):
		self.main_loop.queue_event(DOWN_LEFT)
		self.run_soya_rounds()
		self.assertTrue(DOWN_LEFT in self.main_loop.raw_events)
		self.assertTrue(DOWN_LEFT in self.main_loop.events)

	def test_no_coalesced(self):
		input_ev = [DOWN_LEFT, MOUSE_MOTION_1, DOWN_A]
		expected = [DOWN_LEFT, DOWN_A, MOUSE_MOTION_1_C]
		for event in input_ev:
			self.main_loop.queue_event(event)
		self.run_soya_rounds()
		self.assertEquals(self.main_loop.raw_events, input_ev)
		self.assertEquals(self.main_loop.events, expected)

	def test_coalesced(self):
		expected_raw = [DOWN_LEFT, DOWN_A, MOUSE_MOTION_1, MOUSE_MOTION_2]
		expected = [DOWN_LEFT, DOWN_A, MOUSE_MOTION_2_C]
		for event in expected_raw:
			self.main_loop.queue_event(event)
		self.run_soya_rounds()
		self.assertEquals(self.main_loop.raw_events, expected_raw)
		self.assertEquals(self.main_loop.events, expected)


if __name__ == '__main__':
	unittest_main()
