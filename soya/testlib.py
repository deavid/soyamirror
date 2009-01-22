from unittest import TestCase, main as unittest_main

import soya


class SoyaTestCase(TestCase):

	pre_build = True

	def setUp(self):
		soya.init("Soya Test", width=640, height=480, quiet=True)
		if self.pre_build:
			self.setup_scene()

	def setup_scene(self):
		self.scene = scene = soya.World()
		self.light = soya.Light(scene)
		self.camera = soya.Camera(scene)
		soya.set_root_widget(self.camera)
		self.main_loop = soya.MainLoop(scene)
		self.run_soya_rounds() # XXX dismiss init events (a big mouse one)

	def run_soya_rounds(self, nb_round=1):
		for time in xrange(nb_round):
			self.main_loop.begin_round() ;
			self.main_loop.advance_time(1.0) ;
			self.main_loop.end_round();

	def tearDown(self):
		soya.quit()
