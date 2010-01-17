import soya
from soya import Body, Camera, Material
from soya.cube import Cube
from soya.testlib import SoyaTestCase, TestCase, unittest_main

class ScreenShotTC(SoyaTestCase):

	def setup_scene(self):
		super(ScreenShotTC, self).setup_scene()

		red  = Material()
		red.diffuse = (1.0, 0.0, 0.0, 1.0)
		blue = Material()
		blue.diffuse = (0.0, 0.0, 1.0, 1.0)

		red_cube_model = Cube(material=red).to_model()
		blue_cube_model = Cube(material=blue).to_model()

		self.red_cube = Body(self.scene, red_cube_model)
		self.blue_cube  = Body(self.scene, blue_cube_model)

		self.blue_camera = Camera(self.scene)
		self.red_camera  = Camera(self.scene)

		self.blue_cube.set_xyz(-5, 0 , 0)
		self.blue_camera.set_xyz(-5, 0 , 1.1)
		self.blue_camera.look_at(self.blue_cube)

		self.red_cube.set_xyz( 5, 0 , 0)
		self.red_camera.set_xyz( 5, 0, 1.1)
		self.red_camera.look_at(self.red_cube)

		self.light.set_xyz(0., 0., 20.)

	def test_render_front(self):
		soya.set_root_widget(self.blue_camera)
		soya.render()
		screenshot = soya.screenshot()
		self.assertEquals(screenshot.getpixel((0,0)), (0, 0, 255))

		soya.set_root_widget(self.red_camera)
		soya.render()
		screenshot = soya.screenshot()
		self.assertEquals(screenshot.getpixel((0,0)),(255, 0, 0))

	def test_render_back_read(self):
		"""Test that rendering made without switching back buffer are accessible with screenshot"""
		# Screenshot in front buffer
		soya.set_root_widget(self.blue_camera)
		soya.render()
		screenshot = soya.screenshot()
		self.assertEquals(screenshot.getpixel((0,0)),(0, 0, 255))

		# Screenshot in back buffer
		soya.set_root_widget(self.red_camera)
		soya.render(False)
		screenshot = soya.screenshot(use_back_buffer=True)
		self.assertEquals(screenshot.getpixel((0,0)),(255, 0, 0))

	def test_render_does_not_alter(self):
		"""Test that rendering in the back buffer doesn't alter the front one."""
		# Screenshot in front buffer
		soya.set_root_widget(self.blue_camera)
		soya.render()

		# Screenshot in back buffer
		soya.set_root_widget(self.red_camera)
		soya.render(False)

		# Front buffer didn't changed
		screenshot = soya.screenshot()
		self.assertEquals(screenshot.getpixel((0,0)),(0, 0, 255))

		# Everything still work fine
		soya.set_root_widget(self.blue_camera)
		soya.render()
		screenshot = soya.screenshot()
		self.assertEquals(screenshot.getpixel((0,0)),(0, 0, 255))


if __name__ == '__main__':
    unittest_main()
