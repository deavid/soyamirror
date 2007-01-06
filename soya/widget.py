# -*- indent-tabs-mode: t -*-

# Soya 3D
# Copyright (C) 2001-2002 Jean-Baptiste LAMY -- jiba@tuxfamily.org
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

import os, os.path
import soya, soya.sdlconst
from soya.opengl import *


WIDGET_RESIZE_MAXIMIZE = ('maximize', )


default_font = soya.Font(os.path.join(soya.DATADIR, "FreeSans.ttf"), 25, 30)
default_font.filename = "DEFAULT_FONT"

# for font_filename in (
#   # FreeFont
#   "/usr/share/fonts/freefont/FreeSans.ttf", # Mandrake
#   "/usr/share/fonts/truetype/freefont/FreeSans.ttf", # Debian
#   os.path.join(os.environ.get("WINDIR", ""), "Fonts", "FreeSans.ttf"), # Windows
#   os.path.join(soya.DATADIR, "FreeSans.ttf"), # soya's DATADIR
#   os.path.join(os.getcwd(), "data", "fonts", "FreeSans.ttf"), # working directory
	
#   # Bluehigh
#   "/usr/share/fonts/ttf/western/Bluehigh.ttf", # Mandrake
	
#   # Vera
#   "/usr/share/fonts/ttf/vera/Vera.ttf", # Mandrake
#   "/usr/share/fonts/truetype/ttf-bitstream-vera/Vera.ttf", # Debian
#   "/usr/share/fonts/ttf-bitstream-vera/Vera.ttf", # Gentoo
#   "/usr/share/fonts/TTF/Vera.ttf", # Gentoo
#   os.path.join(os.environ.get("WINDIR", ""), "Fonts", "Vera.ttf"), # Windows
#   os.path.join(soya.DATADIR, "Vera.ttf"), # soya's DATADIR
#   os.path.join(os.getcwd(), "data", "fonts", "Vera.ttf"), # working directory
#   ):
#   if os.path.exists(font_filename):
#     default_font = soya.Font(font_filename, 25, 30)
#     break
# else:
#   print "Soya * WARNING : no font file found !!!! *"
#   print "Soya * Please do the following :"
#   print "Soya *   search a file called 'FreeSans.ttf' on your computer,"
#   print "Soya *   and send the location of this file and your OS name"
#   print "Soya *   to soya@oomadness.tuxfamily.org"
#   print "Soya * Thanks !"
#   default_font = None

# ----------------------------------------

class Widget(object):
	def __init__(self, master = None, resize_style = None):
		# these attributes are named (left,top) and not (x,y) to avoid confusion with
		# the (x,y,z) attributes of 3D objects
		self.left = 0
		self.top  = 0
		self.width  = 0
		self.height = 0
		self._resize_style = resize_style
		# this attribute is not called parent for avoiding confusion with 3D objects parent
		# attribute and also because Camera is a 3D object and a Widget
		if master: master.add(self)
		else: self.master = None
		
	def get_resize_style(self): return self._resize_style
	def set_resize_style(self, resize_style):
		self._resize_style = resize_style
		if self.master: self.resize(self.master.left, self.master.top, self.master.width, self.master.height)
	resize_style = property(get_resize_style, set_resize_style)
	
	def resize(self, parent_left, parent_top, parent_width, parent_height):
		# this method can be rewritten for each widget instance or you can use the standard
		# resize style statement
		if self.resize_style:
			for e in self.resize_style:
				if type(e) == str:
					if   e == 'maximize':
						self.left   = parent_left
						self.top    = parent_top
						self.width  = parent_width
						self.height = parent_height
					elif e == 'parent left':
						self.left = parent_left
					elif e == 'parent top':
						self.top  = parent_top
					elif e == 'maximize width':
						self.width = parent_width - self.left + parent_left
					elif e == 'maximize height':
						self.height = parent_height - self.top + parent_top
					elif e == 'center x':
						self.left = int((parent_width - self.width) * 0.5)
					elif e == 'center y':
						self.top = int((parent_height - self.height) * 0.5)
				else:
					if   e[0] == 'percent left':
						self.left = parent_left + int(parent_width * e[1])
					elif e[0] == 'percent top':
						self.top = parent_top + int(parent_height * e[1])
					elif e[0] == 'percent width':
						self.width = int(parent_width * e[1])
					elif e[0] == 'percent height':
						self.height = int(parent_height * e[1])
					elif e[0] == 'margin left':
						self.left  += e[1]
						self.width -= e[1]
					elif e[0] == 'margin top':
						self.top    += e[1]
						self.height -= e[1]
					elif e[0] == 'margin right':
						self.width -= e[1]
					elif e[0] == 'margin bottom':
						self.height -= e[1]
					elif e[0] == 'max width':
						if self.width > e[1]: self.width = e[1]
					elif e[0] == 'max height':
						if self.height > e[1]: self.height = e[1]
					elif e[0] == 'keep ratio':
						# ratio is width / height
						if self.height * e[1] < self.width:
							self.width = int(self.height * e[1])
						else:
							self.height = int(self.width / e[1])
			
	def widget_begin_round(self): pass
	def widget_advance_time(self, proportion): pass
	def widget_end_round(self): pass
	
	
# ----------------------------------------

class Group(Widget):
	def __init__(self, master = None):
		self.children = []
		Widget.__init__(self, master, WIDGET_RESIZE_MAXIMIZE)
		self.visible = 1
	def render(self):
		if self.visible:
			for widget in self.children:
				widget.render()
	def resize(self, parent_left, parent_top, parent_width, parent_height):
		Widget.resize(self, parent_left, parent_top, parent_width, parent_height)
		for widget in self.children: widget.resize(parent_left, parent_top, parent_width, parent_height)
	def add(self, widget):
		self.children.append(widget)
		widget.master = self
		widget.resize(self.left, self.top, self.width, self.height)
	def insert(self, index, widget):
		self.children.insert(index, widget)
		widget.master = self
		widget.resize(self.left, self.top, self.width, self.height)
	def remove(self, widget):
		self.children.remove(widget)
		widget.master = None
	def widget_begin_round(self):
		for widget in self.children: widget.widget_begin_round()
	def widget_advance_time(self, proportion):
		for widget in self.children: widget.widget_advance_time(proportion)
	def widget_end_round(self):
		for widget in self.children: widget.widget_end_round()
			
class Clearer(Widget):
	def __init__(self, master = None, color = soya.BLACK):
		Widget.__init__(self)
		self.color = color
		if master: master.add(self)
	def render(self):
		glClearColor(self.color[0], self.color[1], self.color[2], self.color[3])


# ----------------------------------------

# class Label(Widget):
#   def __init__(self, master = None, text = "", align = 0, color = (1.0, 1.0, 1.0, 1.0), font = default_font):
#     self.text  = text
#     self.color = color
#     self.font  = font
#     # align: 0 left, 1 center
#     self.align  = align
#     Widget.__init__(self, master)
#   def render(self):
#     if self.text:
#       soya.DEFAULT_MATERIAL.activate()
#       glColor4f(*self.color)
#       self.font.draw_area(self.text, self.left, self.top, 0.0, self.width, self.height, self.align)

class Label(Widget):
	def get_font (self): return self._font
	def set_font (self, x): self._font  = x; self._changed = -2
	def get_color(self): return self._color
	def set_color(self, x): self._color = x; self._changed = -2
	def get_text (self): return self._text
	def set_text (self, x): self._text  = x; self._changed = -2
	def get_align(self): return self._align
	def set_align(self, x): self._align = x; self._changed = -2
	font  = property(get_font , set_font )
	color = property(get_color, set_color)
	text  = property(get_text , set_text )
	align = property(get_align, set_align)
	
	def resize(self, parent_left, parent_top, parent_width, parent_height):
		self._changed = -2
		Widget.resize(self, parent_left, parent_top, parent_width, parent_height)
		
	def __init__(self, master = None, text = "", align = 0, color = (1.0, 1.0, 1.0, 1.0), font = None, resize_style = None):
		self._text         = text
		self._color        = color
		self._font         = font or default_font
		self._align        = align # align: 0 left, 1 center
		self._changed      = -2
		self._display_list = soya.DisplayList()
		Widget.__init__(self, master, resize_style)
		
	def build_display_list(self):
		"""Label.build_display_list()

Really renders the text.

If you override this method, DO NOT SET self.text or self._set here !!!
It might call glyph tessellation that would be included in the display list !"""
		glColor4f(*self._color)
		self._font.draw_area(self._text, self.left, self.top, 0.0, self.width, self.height, self._align)
		
	def render(self):
		soya.DEFAULT_MATERIAL.activate()
		if self._changed != self._font._pixels_height:
			self._font.create_glyphs(self._text)
			
			glNewList(self._display_list.id, GL_COMPILE_AND_EXECUTE)
			self.build_display_list()
			glEndList()
			self._changed = self._font._pixels_height
		else:
			glCallList(self._display_list.id)
			


# class FPSLabel(Widget):
#   """FPSLabel

# A label that shows the FPS.
# It works ONLY with soya.main_loop !!!"""
	
#   def resize(self, parent_left, parent_top, parent_width, parent_height):
#     self.x = parent_left + parent_width  - 120
#     self.y = parent_top  + parent_height - 37
		
#   def render(self):
#     soya.DEFAULT_MATERIAL.activate()
#     glColor4f(1.0, 1.0, 1.0, 1.0)
#     if soya.MAIN_LOOP:
#       default_font.draw("%.1f FPS" % soya.MAIN_LOOP.fps, self.x, self.y)
#     else:
#       default_font.draw("No main_loop", self.x, self.y)

class FPSLabel(Label):
	"""FPSLabel

A label that shows the FPS.
It works ONLY with soya.main_loop !!!"""
	def __init__(self, master = None):
		Label.__init__(self, master)
		self.fps = -1.0
		
	def resize(self, parent_left, parent_top, parent_width, parent_height):
		self.width, self.height = self.font.get_print_size("30.0 FPS")
		self.width  += 10
		self.height +=  5
		self.left   = parent_left + parent_width  - self.width
		self.top    = parent_top  + parent_height - self.height
		self._changed = -2
		
	def widget_begin_round(self):
		if soya.MAIN_LOOP:
			if self.fps != soya.MAIN_LOOP.fps:
				self.fps  = soya.MAIN_LOOP.fps
				self.text = "%.1f FPS" % self.fps
		else:
			if self.fps != -2.0:
				self.fps  = -2.0
				self.text = "No main_loop"
				
				
class Image(Widget):
	def __init__(self, master = None, material = None, color = soya.WHITE, resize_style = None):
		# mode 0 : normal
		# mode 1 : texcoords follow the height and width of the widget
		self.tex_mode   = 0
		self.material   = material or soya.DEFAULT_MATERIAL
		self.tex_top    = 0.0
		self.tex_left   = 0.0
		self.tex_bottom = 1.0
		self.tex_right  = 1.0
		self.color      = color
		self.rotz        = 0.0
		Widget.__init__(self, master, resize_style)
		
	def render(self):
		self.material.activate()
		if self.material.is_alpha() or (self.color[3] < 1.0): glEnable(GL_BLEND)
		glColor4f   (*self.color)
		glPushMatrix()
		
		hw = self.width  / 2
		hh = self.height / 2

		glTranslatef(float(self.left + hw), float(self.top + hh), 0.0)
		if self.rotz: glRotatef   (self.rotz, 0.0, 0.0, 1.0)
		
		glBegin     (GL_QUADS)
		glTexCoord2f(self.tex_left, self.tex_top)
		glVertex2i  (-hw, -hh)
		glTexCoord2f(self.tex_left, self.tex_bottom)
		glVertex2i  (-hw, -hh + self.height)
		glTexCoord2f(self.tex_right, self.tex_bottom)
		glVertex2i  (-hw + self.width, -hh + self.height)
		glTexCoord2f(self.tex_right, self.tex_top)
		glVertex2i  (-hw + self.width, -hh)
		glEnd()
		soya.DEFAULT_MATERIAL.activate()
		glPopMatrix()
		if self.material.is_alpha() or (self.color[3] < 1.0): glDisable(GL_BLEND)
		
	def resize(self, parent_left, parent_top, parent_width, parent_height):
		Widget.resize(self, parent_left, parent_top, parent_width, parent_height)
		if self.tex_mode == 1:
			self.tex_right  = float(self.width ) / self.material.texture.width  + self.tex_left
			self.tex_bottom = float(self.height) / self.material.texture.height + self.tex_top




# ----------------------------------------

class BannerElement:
	
	def __init__(self, text = "", color = (1.0, 1.0, 1.0, 1.0), font = None):
		self.text = text
		self.color = color
		self.font = font or default_font

	def compute_size(self, width = None):
		if width == None:
			t = self.font.get_print_size(self.text)
		else:
			t = self.font.wordwrap(self.text, width)
		self.width  = t[0]
		self.height = t[1]


class Banner(Widget):

	def __init__(self, master = None, elements = []):
		self.valid = 0
		self.set_elements(elements)
		Widget.__init__(self, master, WIDGET_RESIZE_MAXIMIZE)
		self.loop = 1
		self.total = 0
		self.speed = 4.0
		self.visible = 1

	def set_elements(self, elements, separator = None):
		if separator:
			for e in elements:
				self.elements.append(separator)
				self.elements.append(e)
		else:
			self.elements = elements
		self.init()

	def add_elements_from_strings(self, strings = [], attribs = {}, separator = None):
		try:    color = attribs['color']
		except: color = (1.0, 1.0, 1.0, 1.0)
		try:    font  = attribs['font']
		except: font  = default_font
		if type(separator) == str:
			separator = BannerElement(separator, color, font)
		for s in strings:
			if separator: self.elements.append(separator)
			self.elements.append(BannerElement(s, color, font))
		self.init()
			
	def add_elements_from_tuples(self, tuples = [], key_attribs = {}, value_attribs = {}, separator = None):
		try:    k_color = key_attribs['color']
		except: k_color = (1.0, 1.0, 1.0, 1.0)
		try:    k_font  = key_attribs['font']
		except: k_font  = default_font
		try:    v_color = value_attribs['color']
		except: v_color = (1.0, 1.0, 1.0, 1.0)
		try:    v_font  = value_attribs['font']
		except: v_font  = default_font
		if type(separator) == str:
			separator = BannerElement(separator, v_color, v_font)
		for t in tuples:
			if separator: self.elements.append(separator)
			self.elements.append(BannerElement(t[0], k_color, k_font))
			self.elements.append(BannerElement(t[1], v_color, v_font))
		self.init()
		
	def widget_advance_time(self, proportion):
		self._position += proportion * self.speed
		self.position = int(self._position)
		if self.position >= self.total:
			if self.loop:
				self._position -= self.total
#        self.position -= self.total
			else:
				if self.master: self.master.remove(self)


class HorizontalBanner(Banner):

	def __init__(self, master = None, elements = []):
		Banner.__init__(self, master, elements)
		self.position = - self.width
		self._position = self.position
		self.top = 0
		self.height = 0

	def init(self):
		for e in self.elements:
			e.compute_size()
			if e.font.height > self.height: self.height = e.font.height
			self.total += e.width
			
	def render(self):
		if self.visible:
			n = 0
			i = 0
			while (i < len(self.elements)):
				e = self.elements[i]
				n += e.width
				if n >= self.position:
					# element e is after position
					glColor4f(*e.color)
					e.font.draw(e.text, n - e.width - self.position, self.top)
					while (n - self.position < self.width):
						i += 1
						if i >= len(self.elements):
							if self.loop:
								i = 0
							else:
								break
						e = self.elements[i]
						glColor4f(*e.color)
						e.font.draw(e.text, n - self.position, self.top)
						n += e.width
					break
				i += 1
			glColor4f(1.0, 1.0, 1.0, 1.0)
			self.valid = 1

	def resize(self, parent_left, parent_top, parent_width, parent_height):
		Widget.resize(self, parent_left, parent_top, parent_width, parent_height)
		if self.valid == 0:
			self.position = - self.width
			self._position = -self.width


class VerticalBanner(Banner):

	def __init__(self, master = None, elements = []):
		Banner.__init__(self, master, elements)
		self.position = - self.height
		self._position = self.position
		self.alpha_zone = 150
		self.center_text = 1
		
	def init(self):
		self.total = 0
		for e in self.elements:
			e.compute_size(self.width)
			self.total += e.height
			
	def render(self):

		def render_element(e, y):

			def color_for_y(y, color):
				return (e.color[0], e.color[1], e.color[2], )
			
			if self.alpha_zone == 0:
				glColor4f(*e.color)
				e.font.draw_area(e.text, self.left, y, 0.0, self.width, self.height, self.center_text)
			else:
				if y < self.alpha_zone + self.top:
					glColor4f(e.color[0], e.color[1], e.color[2], float(y - self.top) / self.alpha_zone)
				elif y > self.top + self.height - self.alpha_zone - e.height:
					glColor4f(e.color[0], e.color[1], e.color[2], float(self.height - y - e.height + self.top) / self.alpha_zone)
				else:
					glColor4f(*e.color)
				e.font.draw_area(e.text, self.left, y, 0.0, self.width, self.height, self.center_text)

		if self.visible:
			n = self.top
			i = 0
			while (i < len(self.elements)):
				e = self.elements[i]
				o = n - self.position
				n += e.height
				if n >= self.position:
					# element e is after position
					render_element(e, o)
					while (n - self.position < self.height + self.top):
						i += 1
						if i >= len(self.elements):
							if self.loop:
								i = 0
							else:
								break
						e = self.elements[i]
						render_element(e, n - self.position)
						n += e.height
					break
				i += 1
			glColor4f(1.0, 1.0, 1.0, 1.0)
			self.valid = 1

	def resize(self, parent_left, parent_top, parent_width, parent_height):
		Widget.resize(self, parent_left, parent_top, parent_width, parent_height)
		if self.valid == 0:
			self.position = - self.height
			self._position = - self.height
		self.init()


# ----------------------------------------

class Choice:

	def __init__(self, label = '', action = None, value = None, range = None, incr = None):
		self.label  = label
		self.action = action
		self.value  = value
		self.range  = range
		self.incr   = incr

	def get_label(self):
		if (self.value != None): return '%s - %s' % (self.label, self.value)
		else:                    return self.label

	def increment(self):
		if (self.incr):
			self.value = self.value + self.incr
			if (self.range):
				if (self.value < self.range[0]): self.value = self.range[0]
				if (self.value > self.range[1]): self.value = self.range[1]
		else:
			nb = len(self.range)
			i = 0
			while (i < nb):
				if (self.range[i] == self.value):
					i = i + 1
					if (i >= nb): i = 0
					self.value = self.range[i]
					break
				i = i + 1

	def decrement(self):
		if (self.incr):
			self.value = self.value - self.incr
			if (self.range):
				if (self.value < self.range[0]): self.value = self.range[0]
				if (self.value > self.range[1]): self.value = self.range[1]
		else:
			nb = len(self.range)
			i = 0
			while (i < nb):
				if (self.range[i] == self.value):
					i = i - 1
					if (i < 0): i = nb - 1
					self.value = self.range[i]
					break
				i = i + 1    

	def mouse_click(self, button):
		if self.value == None:
			if button == soya.sdlconst.BUTTON_RIGHT or button == soya.sdlconst.BUTTON_LEFT:
				if self.action: self.action()
		else:
			if button == soya.sdlconst.BUTTON_RIGHT or button == soya.sdlconst.BUTTON_WHEELDOWN:
				self.decrement()
			elif button == soya.sdlconst.BUTTON_LEFT or button == soya.sdlconst.BUTTON_WHEELUP:
				self.increment()

	def key_down(self, key_id, mods):
		if self.value == None:
			if (key_id == soya.sdlconst.K_RETURN or key_id == soya.sdlconst.K_KP_ENTER or key_id == soya.sdlconst.K_SPACE):
				if self.action: self.action()
		else:
			if (key_id == soya.sdlconst.K_RIGHT or key_id == soya.sdlconst.K_PLUS or key_id == soya.sdlconst.K_KP_PLUS or key_id == soya.sdlconst.K_RETURN or key_id == soya.sdlconst.K_KP_ENTER or key_id == soya.sdlconst.K_SPACE):
				self.increment()
			elif (key_id == soya.sdlconst.K_LEFT or key_id == soya.sdlconst.K_MINUS or key_id == soya.sdlconst.K_KP_MINUS):
				self.decrement()


class ChoiceInput:

	def __init__(self, label = '', value = ''):
		self.label  = label
		self.value  = value
		self.grab   = 0

	def get_label(self):
		if (self.value != None):
			return '%s - %s' % (self.label, self.value)
		else: return self.label

	def mouse_click(self, button): pass

	def key_down(self, key_id, mods):
		if (key_id == soya.sdlconst.K_DELETE or key_id == soya.sdlconst.K_BACKSPACE or key_id == soya.sdlconst.K_CLEAR):
			self.value = self.value[:-1]
		elif (key_id == soya.sdlconst.K_KP0) or (key_id == soya.sdlconst.K_0): self.value += '0'
		elif (key_id == soya.sdlconst.K_KP1) or (key_id == soya.sdlconst.K_1): self.value += '1'
		elif (key_id == soya.sdlconst.K_KP2) or (key_id == soya.sdlconst.K_2): self.value += '2'
		elif (key_id == soya.sdlconst.K_KP3) or (key_id == soya.sdlconst.K_3): self.value += '3'
		elif (key_id == soya.sdlconst.K_KP4) or (key_id == soya.sdlconst.K_4): self.value += '4'
		elif (key_id == soya.sdlconst.K_KP5) or (key_id == soya.sdlconst.K_5): self.value += '5'
		elif (key_id == soya.sdlconst.K_KP6) or (key_id == soya.sdlconst.K_6): self.value += '6'
		elif (key_id == soya.sdlconst.K_KP7) or (key_id == soya.sdlconst.K_7): self.value += '7'
		elif (key_id == soya.sdlconst.K_KP8) or (key_id == soya.sdlconst.K_8): self.value += '8'
		elif (key_id == soya.sdlconst.K_KP9) or (key_id == soya.sdlconst.K_9): self.value += '9'
		elif (key_id == soya.sdlconst.K_KP_PERIOD or key_id == soya.sdlconst.K_PERIOD): self.value += '.'
		else:
			if mods & (soya.sdlconst.MOD_SHIFT | soya.sdlconst.MOD_CAPS):
				if   (key_id >= soya.sdlconst.K_a and key_id <= soya.sdlconst.K_z):
					self.value += chr(key_id - 32)
				elif (key_id == soya.sdlconst.K_SEMICOLON): self.value += '.'
			else:
				if   (key_id >= soya.sdlconst.K_a and key_id <= soya.sdlconst.K_z):
					self.value += chr(key_id)
				elif (key_id >= 0 and key_id < 256):
					self.value += chr(key_id)


class ChoiceList(Widget):

	def __init__(self, master = None, choices = [], font = None, color = (1.0, 0.5, 0.5, 1.0), highlight = (1.0, 1.0, 0.0, 1.0), cancel = None, align=1):
		self.x_percent = 0.0
		self.y_percent = 0.0
		self.w_percent = 1.0
		self.h_percent = 1.0
		Widget.__init__(self, master)
		self.choices = choices
		self.font = font or default_font
		self.color = color
		self.highlight = highlight
		self.selected = 0
		self.visible = 1
		self.align=align
		if master: master.add(self)
		if cancel != None: self.cancel = self.choices[cancel]
		else: self.cancel = None

	def process_event(self, event):
		if (event[0] == soya.sdlconst.KEYDOWN):
			self.key_down(event[1], event[2])
		elif (event[0] == soya.sdlconst.MOUSEMOTION):
			self.mouse_move(event[1], event[2])
		elif (event[0] == soya.sdlconst.MOUSEBUTTONDOWN):
			self.choices[self.selected].mouse_click(event[1])
		elif (event[0] == soya.sdlconst.JOYAXISMOTION):
			if event[1] == 0:
				if event[2] < 0:
					self.key_down(soya.sdlconst.K_LEFT, 0)
				elif event[2] > 0:
					self.key_down(soya.sdlconst.K_RIGHT, 0)
			elif event[1] == 1:
				if event[2] < 0:
					self.key_down(soya.sdlconst.K_UP, 0)
				elif event[2] > 0:
					self.key_down(soya.sdlconst.K_DOWN, 0)
		elif (event[0] == soya.sdlconst.JOYBUTTONDOWN):
			if event[1] // 2 == event[1] / 2.0:
				self.key_down(soya.sdlconst.K_RETURN, 0)
			else:
				self.key_down(soya.sdlconst.K_LEFT, 0)
				
	def key_down(self, key_id, mods):
		if key_id == soya.sdlconst.K_DOWN:
			self.selected = self.selected + 1
			if (self.selected >= len(self.choices)): self.selected = 0
		elif key_id == soya.sdlconst.K_UP:
			self.selected = self.selected - 1
			if (self.selected < 0): self.selected = len(self.choices) - 1
		elif key_id == soya.sdlconst.K_ESCAPE :
			if self.cancel:
				self.cancel.key_down(soya.sdlconst.K_RETURN, mods)
		else: self.choices[self.selected].key_down(key_id, mods)
		
	def mouse_move(self, x, y):
		if (x >= self.left) and (x <= self.left + self.width):
			i = 0
			nb = len(self.choices)
			h1 = int (self.height / nb)
			h2 = int (h1 * 0.5)
			t = int (self.top + h1 * 0.5)
			while (i < nb):
				if (y >= t - h2 and y <= t + h2):
					self.selected = i
					break
				t = t + h1
				i = i + 1
#			else: self.selected = -1
#		else: self.selected = -1
				
	def render(self):
		if self.visible:
			nb = len (self.choices)
			hi = self.height / nb
			h = int (self.top + hi * 0.5) - 18
			i = 0
			while (i < nb):
				if (i == self.selected):
					glColor4f(*self.highlight)
				else:
					glColor4f(*self.color)
				# Why ? Useless ???
				#glDisable(GL_LIGHTING)
				self.font.draw_area(self.choices[i].get_label(), self.left, h, 0.0, self.width, h + hi, self.align)
				h = h + hi
				i = i + 1


# ----------------------------------------

class Selector(Widget):

	def __init__(self, master = None, choices = [], title = None, font = None, color = (1.0, 0.5, 0.5, 1.0), highlight = (1.0, 1.0, 0.0, 1.0), arrows = None):
		self.x_percent = 0.0
		self.y_percent = 0.0
		self.w_percent = 1.0
		self.h_percent = 1.0
		self.arrow_size = 32
		self.choices = choices
		self.title = title
		self.nb_displayed = 5
		self.font = font or default_font
		self.arrows = arrows
		Widget.__init__(self, master)
		self.selected  = 0
		self.display_from = 0
		self.selected_arrow = 0
		self.color = color
		self.highlight = highlight
		self.visible = 1
		self.enabled = 0
		self.scrolling = 0
		
	def resize(self, parent_left, parent_top, parent_width, parent_height):
		Widget.resize(self, parent_left, parent_top, parent_width, parent_height)
		a = self.height - self.font.height
		if self.arrows: a -= 2 * self.arrow_size
		self.nb_displayed = int(a / self.font.height)
		if not self.nb_displayed & 1: self.nb_displayed -= 1
		if self.arrows:
			self._h = int(self.top + (self.height - self.font.height * (self.nb_displayed + 1) - 2 * self.arrow_size) * 0.5)
		else:
			self._h = int(self.top + (self.height - self.font.height * (self.nb_displayed + 1)) * 0.5)

	def get_choice_at(self, y):
		h = self._h
		if y < h: return -4
		if self.title:
			h += self.font.height
			if (y < h):
				return -1
		h += self.arrow_size
		if (y < h): return -2
		else:
			i = 0
			while(i < self.nb_displayed):
				h += self.font.height
				if (y < h): return self.display_from + i
				i += 1
			h += self.arrow_size
			if (y < h): return -3
		return -4
	
	def scroll_up(self):
		if (self.display_from > 0): self.display_from -= 1
		
	def scroll_down(self):
		if (self.display_from < len(self.choices) - self.nb_displayed): self.display_from += 1
		
	def scroll(self):
		if (self.scrolling > 0):
			if (self.selected + 1 < len(self.choices)): self.selected += 1
			if (self.selected - self.display_from > (self.nb_displayed - 1) * 0.5):
				self.scroll_down()
		elif (self.scrolling < 0):
			if (self.selected > 0): self.selected -= 1
			if (self.selected - self.display_from < (self.nb_displayed - 1) * 0.5):
				self.scroll_up()

	def select(self, index):
		if (index >= 0 and index < len(self.choices)):
			self.selected = index
			self.display_from = int(index - (self.nb_displayed - 1) * 0.5)
			if   (self.display_from < 0): self.display_from = 0
			elif (self.display_from > len(self.choices) - self.nb_displayed): self.display_from = len(self.choices) - self.nb_displayed
			
	def process_event(self, event):
		if (event[0] == soya.sdlconst.KEYDOWN):
			if (event[1] == soya.sdlconst.K_DOWN):
				self.scrolling = 1
#        if (self.selected + 1 < len(self.choices)): self.selected += 1
#        if (self.selected - self.display_from > (self.nb_displayed - 1) * 0.5):
#          self.scroll_down()
			elif (event[1] == soya.sdlconst.K_UP):
				self.scrolling = -1
#        if (self.selected > 0): self.selected -= 1
#        if (self.selected - self.display_from < (self.nb_displayed - 1) * 0.5):
#          self.scroll_up()
		elif (event[0] == soya.sdlconst.KEYUP):
			self.scrolling = 0
		elif (event[0] == soya.sdlconst.MOUSEMOTION):
			i = self.get_choice_at(event[2])
			if   (i == -2): self.selected_arrow = 1
			elif (i == -3): self.selected_arrow = 2
			else:           self.selected_arrow = 0
		elif (event[0] == soya.sdlconst.MOUSEBUTTONDOWN):
			if   (event[1] == 4): self.scroll_up()
			elif (event[1] == 5): self.scroll_down()
			else:
				i = self.get_choice_at(event[3])
				if (i >= 0): self.select(i)
				elif (i == -2): self.scroll_up()
				elif (i == -3): self.scroll_down()
		elif (event[0] == soya.sdlconst.JOYAXISMOTION):
			if (event[1] == 1):
				if (event[2] == 0):
					self.scrolling = 0
				elif (event[2] > 0):
					self.scrolling = 1
#          if (self.selected + 1 < len(self.choices)): self.selected += 1
#          if (self.selected - self.display_from > (self.nb_displayed - 1) * 0.5):
#            self.scroll_down()
				elif (event[2] < 0):
					self.scrolling = -1
#          if (self.selected > 0): self.selected -= 1
#          if (self.selected - self.display_from < (self.nb_displayed - 1) * 0.5):
#            self.scroll_up()
		self.scroll()

	def draw_arrow(self, top, yoffset):
		x = int((self.width - self.left - self.arrow_size) * 0.5)
		glTexCoord2f(0.0, yoffset)
		glVertex2f(x, top)
		glTexCoord2f(0.0, yoffset + 0.5)
		glVertex2f(x, top + self.arrow_size)
		glTexCoord2f(1.0, yoffset + 0.5)
		glVertex2f(x + self.arrow_size, top + self.arrow_size)
		glTexCoord2f(1.0, yoffset)
		glVertex2f(x + self.arrow_size, top)
		
	def render(self):
		if self.visible:

			if (self.scrolling > 0):
				self.scrolling += 1
				if (self.scrolling > 8):
					self.scrolling = 1
					self.scroll()
			elif (self.scrolling < 0):
				self.scrolling -= 1
				if (self.scrolling < -8):
					self.scrolling = -1
					self.scroll()

			h = self._h
			if self.title:
				if self.enabled: glColor4f(*self.highlight)
				else:            glColor4f(*self.color)
				self.font.draw_area(self.title, self.left, h, 0.0, self.width, self.font.height, 1)
				h += self.font.height

			if self.arrows:
				self.arrows.activate()
				if self.arrows.is_alpha(): glEnable(GL_BLEND)
				glBegin(GL_QUADS)
				if self.display_from > 0:
					if self.selected_arrow == 1: glColor4f(*self.highlight)
					else:                        glColor4f(*self.color)
					self.draw_arrow(h, 0)
				h += self.arrow_size
				if self.display_from < len(self.choices) - self.nb_displayed:
					if self.selected_arrow == 2: glColor4f(*self.highlight)
					else:                        glColor4f(*self.color)
					self.draw_arrow(h + self.font.height * self.nb_displayed, 0.5)
				glEnd()
				soya.DEFAULT_MATERIAL.activate()
				if self.arrows.is_alpha(): glDisable(GL_BLEND)

			for i in range(self.display_from, self.display_from + min(self.nb_displayed, len(self.choices))):
				if self.selected == i: glColor4f(*self.highlight)
				else:                  glColor4f(*self.color)
				self.font.draw_area(self.choices[i], self.left, h, 0.0, self.width, h + self.font.height, 1)
				h += self.font.height
				

