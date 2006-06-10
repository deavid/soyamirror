# -*- indent-tabs-mode: t -*-

""" containers for pudding """

from soya.pudding      import EXPAND_VERT, EXPAND_HORIZ, CENTER_HORIZ, CENTER_VERT
from soya.pudding.core import Container, TestContainer

__revision__ = "$Revision: 1.1 $"

__doc_classes__ = [ 'VerticalContainer', 
										'HorizontalContainer',
										]

__doc_functions__ = []

# we should be able to merge these two classes but i cant think how atm

class VerticalContainer(Container):
	""" class to resize all children in a column"""

	def on_resize(self):
		""" resize all children into a column """

		self.do_anchoring()
		
		unchangable = 0 
		unchangable_count = 0
	
		for y, child in enumerate(self.children):
			if not child._container_flags & EXPAND_VERT:
				unchangable += child.height
				unchangable_count += 1

		try:
			height = (self.height - unchangable) / (len(self.children) - \
																										unchangable_count)

		except ZeroDivisionError:
			# this happens if none of the children are resizable
			height = 0

		y = 0

		for child in self.children:
			child.top = y 
			child.left = 0

			if not  child._container_flags & EXPAND_HORIZ and \
							child._container_flags & CENTER_HORIZ:
				child.left = (self.width / 2) - (child.width / 2)

			elif child._container_flags & EXPAND_HORIZ:
				child.width = self.width
				
			if child._container_flags & EXPAND_VERT:
				child.height = height

			y += child.height + self._padding

			child.on_resize()

class TestVerticalContainer(TestContainer):
	klass = VerticalContainer


class HorizontalContainer(Container):
	""" class to resize all children in a row"""

	def on_resize(self):
		""" resize all children into a row """

		self.do_anchoring()

		unchangable = 0 
		unchangable_count = 0
	
		for x, child in enumerate(self.children):
			if not child._container_flags & EXPAND_HORIZ:
				unchangable += child.width
				unchangable_count += 1
			
		try:
			width = (self.width - unchangable) / (len(self.children) - \
																									unchangable_count)
		except ZeroDivisionError:
			# this happens if none of the children are resizable
			width = 0

		x = 0

		for child in self.children:
			child.top = 0 
			child.left = x

			if not  child._container_flags & EXPAND_VERT and \
							child._container_flags & CENTER_VERT:
				child.top = (self.height / 2) - (child.height / 2)
				
			elif child._container_flags & EXPAND_VERT:
				child.height = self.height
				
			if child._container_flags & EXPAND_HORIZ:
				child.width = width

			x += child.width + self._padding

			child.on_resize()

class TestHorizontalContainer(TestContainer):
	klass = HorizontalContainer

