# -*- indent-tabs-mode: t -*-

""" slicing image control """

__revision__ = '$Revision: 1.1 $'

import soya
import soya.pudding as pudding

def _split_powers(x):
	i = soya.get_max_texture_size()
	while i != 0:
		while i <= x:
			yield i
			x -= i
		i //= 2

class SlicingImage(pudding.core.Container):
	def __init__(self, parent, pil_image, left=0, top=0, **kwargs):
		width, height = pil_image.size
		self.image_width = width
		self.image_height = height

		pudding.core.Container.__init__(self, parent, left=left, top=top,
																		width=width, height=height, **kwargs)

		self._slices_x = list(_split_powers(width))
		self._slices_y = list(_split_powers(height))
		self._visible = False
		self._slices = {}
		x = 0
		for i, w in enumerate(self._slices_x):
			y = 0
			for j, h in enumerate(self._slices_y):
				slice_pil = pil_image.crop(box=(x, y, x + w, y + h))
				slice_material = soya.Material(soya.image_from_pil(slice_pil))
				self._slices[i, j] = pudding.control.Image(parent=self,
																									 material=slice_material)
				y += h
			x += w
		self.on_resize()
		self._visible = True

	def on_resize(self):
		scale_horiz = self.width / self.image_width
		scale_vert = self.height / self.image_height
		x = 0
		for i, w in enumerate(self._slices_x):
			y = 0
			for j, h in enumerate(self._slices_y):
				im = self._slices[i, j]
				im.left = int(x*scale_horiz)
				im.top = int(y*scale_vert)
				im.width = int((x+w)*scale_horiz) - im.left
				im.height = int((y+h)*scale_vert) - im.top
				im._modified = True
				y += h
			x += w

	def __set_width__(self, width):
		self._width = width
		self._modified = True

	def __set_height__(self, height):
		self._height = height
		self._modified = True

