# -*- indent-tabs-mode: t -*-

"""
SVG Elements:

Most information can be found looking at the ElementManager class

"""

__revision__ = '$Revision: 1.1 $'

import os, sys

import soya.pudding as pudding
import soya.pudding.core
import soya.pudding.control
import soya.pudding.main_loop

import soya
from soya.opengl import *

try:
	try:
		from elementtree import ElementTree
	except ImportError:
		from xml.etree import ElementTree
except ImportError:
	raise "You need elementtree from http://effbot.org/zone/element-index.htm"

try:
	import cairo
	import cairo.svg
	CAIRO = 1
except ImportError:
	print " * Cairo not found. Automatic SVG generation not available"
	CAIRO = 0

NS_SVG = "http://www.w3.org/2000/svg"

class Element:
	""" part of the whole texture """

	def __init__(self, owner):
		self.owner = owner

		self.name = None
		self.top, self.left, self.width, self.height = 0, 0, 0, 0
		self.ttop, self.tleft, self.twidth, self.theight = 0, 0, 0, 0

	def __str__(self):
		return """<Element %s 
	%s %s %s %s
	%s %s %s %s>""" % ( self.name, 
										self.left, self.top, self.width, self.height,
										self.tleft, self.ttop, self.twidth, self.theight)

	def draw(self, width = -1, height = -1):
		""" draw """
		self.owner.material.activate()    

		if width == -1:
			width = self.width

		if height == -1:
			height = self.height

		if self.owner.material.is_alpha():
			glEnable(GL_BLEND)
		
		glBegin(GL_QUADS)

		glTexCoord2f(self.tleft, self.ttop)
		glVertex2i(0, 0)

		glTexCoord2f(self.tleft, self.ttop + self.theight)
		glVertex2i(0, height)

		glTexCoord2f(self.tleft + self.twidth, self.ttop + self.theight)
		glVertex2i(width, height)

		glTexCoord2f(self.tleft + self.twidth, self.ttop)
		glVertex2i(width, 0)

		glEnd()

		#if self.owner.material.is_alpha():
		#  glDisable(GL_BLEND)
	 
def find_svg(fn):
	""" locate an svg file in the soya path """
	for path in soya.path:
		test_file = os.path.join(path, 'svg', fn)

		if os.path.isfile(test_file):
			return test_file
	
	raise "cannot find %s" % fn

def find_img(fn):
	""" locate an image file in the soya path """
	for path in soya.path:
		test_file = os.path.join(path, 'images', fn)

		if os.path.isfile(test_file):
			return test_file

	return False

class ElementManager:
	""" This class allows you to simply use one texture for many images.

	The SVG document must be designed in layers. One image per layer. To 
	define the boundry of each image you must draw an svg rect inside the 
	layer with no fill or border ( ie style="fill:none; stroke:none;" )

	Each element is named after the id of the layer.

	Each image found will be stored in its own svgelements.Element which 
	contains both the svg coords of the image and the texture coords which 
	will be used for opengl calls.

	ElementImage is a simple image widget designed to show one image element

	This has only been tested with Inkscape (http://inkscape.org) saving to 
	plain SVG altho it should work with any standard SVG writer 
	
	pycairo (http://cairographics.org/) can be used to automatically render
	svg.

	"""

	boundry_prefix = 'boundry_'

	def __init__(self, img, svg):
		self.svg_file = find_svg(svg)

		if CAIRO:
			imfn = find_img(img)

			if not os.path.isfile(imfn) or \
					os.path.getmtime(self.svg_file) > os.path.getmtime(imfn):

				print "[svgelements] converting svg to png..."

				svg = cairo.svg.Context()
				svg.parse(self.svg_file)
				width, height = svg.size
				surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
				ctx = cairo.Context(surface)
				svg.render(ctx)
				surface.write_to_png(imfn)

		self.material = soya.Material(soya.Image.get(img))

		self.svg = ElementTree.parse(self.svg_file)

		self.size = float(self.svg.getroot().get('width'))

	def __getitem__(self, name):
		return self.elements[name]

	def is_boundry(self, element):
		""" returns true if the element is a boundry """
		name = element.get('id')
		if name.startswith(self.boundry_prefix): 
			return element.get('id')[len(self.boundry_prefix):]

		return False

	def find_elements(self):
		""" find all the elements in the svg file """
		elements = self.svg.getroot().getchildren()
		
		self.elements = {}
	 
		for element in elements:
			name = self.is_boundry(element)

			if not name:
				continue
			
			new_el = Element(self)

			new_el.name = name

			new_el.left    = float(element.get('x')) - 1
			new_el.top     = float(element.get('y')) - 1
			new_el.width   = float(element.get('width')) + 2
			new_el.height  = float(element.get('height')) + 2

			new_el.tleft   = new_el.left / self.size
			new_el.ttop    = new_el.top / self.size
			new_el.twidth  = new_el.width / self.size
			new_el.theight = new_el.height / self.size

			print new_el

			self.elements[new_el.name] = new_el

class ElementImage(pudding.core.Control):
	""" simple image control based on svgelements """

	def __init__(self, parent=None, manager=None, image=None, autosize=True,
							 **kwargs):

		pudding.core.Control.__init__(self, parent, **kwargs)

		self.manager = manager
		self.image_name = image

		self.autosize = autosize

		if self.autosize:
			self.on_resize()

	def on_resize(self):
		""" resize """
		if self.autosize:
			self.width = int(self.manager[self.image_name].width)
			self.height = int(self.manager[self.image_name].height)

		pudding.core.Control.on_resize(self)
	
	def render_self(self):
		""" render """
		self.manager[self.image_name].draw(self.width, self.height)
		
