# -*- indent-tabs-mode: t -*-

""" fps label for pudding """

__revision__ = '$Revision: 1.2 $'

import soya

import soya.pudding as pudding
from soya.pudding.core import RootWidget
from soya.pudding.control import SimpleLabel

class FPSLabel(SimpleLabel):
	""" fps label for pudding """

	def __init__(self, parent = None, position = pudding.BOTTOM_RIGHT, 
								margin = 10):

		#assert isinstance(parent, RootWidget)
		assert position in pudding.CORNERS
		
		SimpleLabel.__init__(self, parent, autosize = True)
		
		self.goto_position(position, margin)

		self.fps = -1.

	def goto_position(self, position, margin):
		""" move to a position on the screen """
		# TODO should probably be a property 
		if position == pudding.TOP_LEFT: 
			self.left = margin
			self.top = margin
			self.anchors = pudding.ANCHOR_TOP_LEFT
		elif position == pudding.TOP_RIGHT:
			self.right = margin
			self.top = margin
			self.anchors = pudding.ANCHOR_TOP_RIGHT
		elif position == pudding.BOTTOM_LEFT:
			self.left = margin
			self.bottom = margin
			self.anchors = pudding.ANCHOR_BOTTOM_LEFT
		elif position == pudding.BOTTOM_RIGHT:
			self.right = margin
			self.bottom = margin
			self.anchors = pudding.ANCHOR_BOTTOM_RIGHT

	def begin_round(self):
		""" get the fps from the current main_loop and update if its changed """
		if soya.MAIN_LOOP:
			if self.fps != soya.MAIN_LOOP.fps:
				self.fps = soya.MAIN_LOOP.fps
				self.label = "%.1f FPS" % self.fps
				self.update()
				self.on_resize()
		else:
			self.label = "--- FPS"

class TestFPSLabel(pudding.control.TestSimpleLabel):
	klass = FPSLabel

	def getControl(self):
		return self.klass(self.parent())

	def test1Create(self):
		""" cannot test creation without parent """
		pass
