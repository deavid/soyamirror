# -*- indent-tabs-mode: t -*-
# -*- coding: utf-8 -*-

# Soya 3D
# Copyright (C) 2007 Jean-Baptiste LAMY -- jiba@tuxfamily.org
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
import soya, soya.sdlconst as sdlconst, soya.opengl as opengl

soya.set_use_unicode(1)

class Style(object):
	def __init__(self):
		self.table_row_pad = 5
		self.table_col_pad = 5
		#self.font = soya.Font(os.path.join(soya.DATADIR, "FreeSans.ttf"), 25, 30)
		#self.font = soya.Font(os.path.join(soya.DATADIR, "FreeSans.ttf"), 30, 30)
		self.font = soya.Font(os.path.join(soya.DATADIR, "FreeSans.ttf"), 20, 20)
		self.font.filename = "DEFAULT_FONT"
		self._char_height = None
		
		self.materials = [
			soya.Material(),
			soya.Material(),
			soya.Material(),
			soya.Material(),
			soya.Material(),
			]
# 		self.materials[0].diffuse = (0.3, 0.3, 0.3, 0.8) # Base
# 		self.materials[1].diffuse = (0.0, 0.6, 0.0, 1.0) # Selected
# 		self.materials[2].diffuse = (0.0, 0.6, 0.0, 1.0) # Window title
# 		self.materials[3].diffuse = (0.0, 0.8, 0.0, 1.0) # Selected window title
# 		self.line_colors = [
# 			(1.0, 1.0, 1.0, 0.8), # Base
# 			(1.0, 1.0, 1.0, 1.0), # Selected
# 			(1.0, 1.0, 1.0, 1.0), # Window title
# 			(1.0, 1.0, 1.0, 1.0), # Selected window title
# 			]
# 		self.line_width     = 2
		
		self.materials[0].diffuse = (0.8, 0.0, 0.0, 1.0) # Base
		self.materials[1].diffuse = (1.0, 0.2, 0.2, 1.0) # Selected
		self.materials[2].diffuse = (0.8, 0.0, 0.0, 1.0) # Window title
		self.materials[3].diffuse = (1.0, 0.0, 0.0, 1.0) # Selected window title
		self.materials[4].diffuse = (1.0, 1.0, 1.0, 0.9) # Window background
		self.corner_colors = [
			(0.0, 0.0, 0.0, 1.0), # Base
			(0.0, 0.0, 0.0, 1.0), # Selected
			(0.0, 0.0, 0.0, 1.0), # Window title
			(0.0, 0.0, 0.0, 1.0), # Selected window title
			(0.5, 0.5, 0.5, 0.5), # Window background
			]
		self.line_colors = [
			(0.0, 0.0, 0.0, 1.0), # Base
			(0.0, 0.0, 0.0, 1.0), # Selected
			(0.0, 0.0, 0.0, 1.0), # Window title
			(0.0, 0.0, 0.0, 1.0), # Selected window title
			(0.0, 0.0, 0.0, 1.0), # Window background
			]
		self.text_colors = [
			(0.0, 0.0, 0.0, 1.0), # Base
			(0.0, 0.2, 0.0, 1.0), # Selected
			(1.0, 1.0, 1.0, 1.0), # Window title
			]
		self.line_width = 1
		
		
		self.materials[0].diffuse = (1.0, 0.9, 0.4, 1.0) # Base
		self.materials[1].diffuse = (1.0, 1.0, 0.7, 1.0) # Selected
		self.materials[2].diffuse = (1.0, 0.9, 0.4, 1.0) # Window title
		self.materials[3].diffuse = (1.0, 1.0, 0.5, 1.0) # Selected window title
		
		self.materials[2].diffuse = (1.0, 0.7, 0.2, 1.0) # Window title
		self.materials[3].diffuse = (1.0, 0.9, 0.4, 1.0) # Selected window title
		self.materials[4].diffuse = (1.0, 1.0, 1.0, 0.9) # Window background
		b  = (0.9, 0.6, 0.0, 1.0)
		b2 = (0.9, 0.5, 0.0, 1.0)
		self.corner_colors = [
			b, # Base
			b, # Selected
			b2, # Window title
			b2, # Selected window title
			(1.0, 0.9, 0.4, 0.9), # Window background
			]
		self.line_colors = [
			b, # Base
			b, # Selected
			b2, # Window title
			b2, # Selected window title
			b, # Window background
			]
		self.text_colors = [
			(0.0, 0.0, 0.0, 1.0), # Base
			(0.0, 0.2, 0.0, 1.0), # Selected
			(0.7, 0.4, 0.0, 1.0), # Window title
			]
		self.line_width = 2
		
	def get_char_height(self):
		return self.font.get_print_size("m")[1]
	
	def rectangle(self, x1, y1, x2, y2, material_index = 0):
		self.materials[material_index].activate()
		if self.materials[material_index].is_alpha(): opengl.glEnable(opengl.GL_BLEND)
# 		opengl.glBegin   (opengl.GL_QUADS)
# 		opengl.glTexCoord2f(0.0, 0.0); opengl.glVertex2i(x1, y1)
# 		opengl.glTexCoord2f(0.0, 1.0); opengl.glVertex2i(x1, y2)
# 		opengl.glColor4f(*self.corner_colors[material_index])
# 		opengl.glTexCoord2f(1.0, 1.0); opengl.glVertex2i(x2, y2)
# 		opengl.glColor4f(*self.materials[material_index].diffuse)
# 		opengl.glTexCoord2f(1.0, 0.0); opengl.glVertex2i(x2, y1)
# 		opengl.glEnd()
		if self.corner_colors[material_index]:
			if  (x2 - x1) // 2 < y2 - y1:
				opengl.glBegin   (opengl.GL_QUADS)
				opengl.glVertex2i(x1, y1)
				opengl.glVertex2i(x1, y2)
				opengl.glVertex2i(x2, y2 - (x2 - x1) // 2)
				opengl.glVertex2i(x2, y1)
				opengl.glEnd()
				opengl.glBegin   (opengl.GL_TRIANGLES)
				opengl.glVertex2i(x2, y2 - (x2 - x1) // 2)
				opengl.glVertex2i(x1, y2)
				opengl.glColor4f(*self.corner_colors[material_index])
				opengl.glVertex2i(x2, y2)
				opengl.glEnd()
			else:
				opengl.glBegin   (opengl.GL_QUADS)
				opengl.glVertex2i(x1, y1)
				opengl.glVertex2i(x1, y2)
				opengl.glVertex2i(x2 - 2 * (y2 - y1), y2)
				opengl.glVertex2i(x2, y1)
				opengl.glEnd()
				opengl.glBegin   (opengl.GL_TRIANGLES)
				opengl.glVertex2i(x2, y1)
				opengl.glVertex2i(x2 - 2 * (y2 - y1), y2)
				opengl.glColor4f(*self.corner_colors[material_index])
				opengl.glVertex2i(x2, y2)
				opengl.glEnd()
		else:
			opengl.glBegin   (opengl.GL_QUADS)
			opengl.glTexCoord2f(0.0, 0.0); opengl.glVertex2i(x1, y1)
			opengl.glTexCoord2f(0.0, 1.0); opengl.glVertex2i(x1, y2)
			opengl.glTexCoord2f(1.0, 1.0); opengl.glVertex2i(x2, y2)
			opengl.glTexCoord2f(1.0, 0.0); opengl.glVertex2i(x2, y1)
			opengl.glEnd()
		soya.DEFAULT_MATERIAL.activate()
		if self.line_width and self.line_colors[material_index][3]:
			opengl.glColor4f(*self.line_colors[material_index])
			opengl.glLineWidth(self.line_width)
			opengl.glBegin   (opengl.GL_LINE_LOOP)
			opengl.glVertex2i(x1, y1)
			opengl.glVertex2i(x1, y2)
			opengl.glVertex2i(x2, y2)
			opengl.glVertex2i(x2, y1)
			opengl.glEnd()
			opengl.glLineWidth(1.0)
		
	def triangle(self, side, x1, y1, x2, y2, material_index = 0):
		self.materials[material_index].activate()
		if self.materials[material_index].is_alpha(): opengl.glEnable(opengl.GL_BLEND)
		opengl.glBegin   (opengl.GL_TRIANGLES)
		if   side == 0:
			opengl.glTexCoord2f(0.0, 0.5); opengl.glVertex2i(x1, (y1 + y2) // 2)
			opengl.glTexCoord2f(1.0, 1.0); opengl.glVertex2i(x2, y2)
			opengl.glTexCoord2f(1.0, 0.0); opengl.glVertex2i(x2, y1)
		elif side == 1:
			opengl.glTexCoord2f(1.0, 0.5); opengl.glVertex2i(x2, (y1 + y2) // 2)
			opengl.glTexCoord2f(0.0, 0.0); opengl.glVertex2i(x1, y1)
			opengl.glTexCoord2f(0.0, 1.0); opengl.glVertex2i(x1, y2)
		elif side == 2:
			opengl.glTexCoord2f(0.5, 0.0); opengl.glVertex2i((x1 + x2) // 2, y1)
			opengl.glTexCoord2f(0.0, 1.0); opengl.glVertex2i(x1, y2)
			opengl.glTexCoord2f(1.0, 1.0); opengl.glVertex2i(x2, y2)
		elif side == 3:
			opengl.glTexCoord2f(0.5, 1.0); opengl.glVertex2i((x1 + x2) // 2, y2)
			opengl.glTexCoord2f(1.0, 0.0); opengl.glVertex2i(x2, y1)
			opengl.glTexCoord2f(0.0, 0.0); opengl.glVertex2i(x1, y1)
		opengl.glEnd()
		soya.DEFAULT_MATERIAL.activate()
		if self.line_width and self.line_colors[material_index][3]:
			opengl.glColor4f(*self.line_colors[material_index])
			opengl.glLineWidth(self.line_width)
			opengl.glBegin   (opengl.GL_LINE_LOOP)
			if   side == 0:
				opengl.glVertex2i(x1, (y1 + y2) // 2)
				opengl.glVertex2i(x2, y1)
				opengl.glVertex2i(x2, y2)
			elif side == 1:
				opengl.glVertex2i(x2, (y1 + y2) // 2)
				opengl.glVertex2i(x1, y1)
				opengl.glVertex2i(x1, y2)
			elif side == 2:
				opengl.glVertex2i((x1 + x2) // 2, y1)
				opengl.glVertex2i(x1, y2)
				opengl.glVertex2i(x2, y2)
			elif side == 3:
				opengl.glVertex2i((x1 + x2) // 2, y2)
				opengl.glVertex2i(x1, y1)
				opengl.glVertex2i(x2, y1)
			opengl.glEnd()
			opengl.glLineWidth(1.0)
		
		

STYLE = Style()

HIGHLIGHT_WIDGET     = None
MOUSE_GRABBER_WIDGET = None
FOCUSED_WIDGET       = None

class CalcSizeRestart(Exception): pass

class Widget(object):
	def __init__(self, parent = None):
		self.x      = 0
		self.y      = 0
		self.width  = 0
		self.height = 0
		
		self.extra_width  = 0.0
		self.extra_height = 0.0
		
		self.min_width    = 0
		self.min_height   = 0
		
		self.ideal_width  = 0
		self.ideal_height = 0
		
		if parent: parent.add(self)
		else: self.parent = None
		
	def added_into(self, parent):
		self.parent = parent

	def get_window(self):
		ancestor = self.parent
		while ancestor:
			if isinstance(ancestor, Window): return ancestor
			ancestor = ancestor.parent
			
	def resize(self, x, y, width, height):
		self.reset_size()
		while 1:
			try:
				self.calc_ideal_size()
				self.allocate(x, y, width, height)
			except CalcSizeRestart: continue
			break
		
	def reset_size(self): pass
	
	def calc_ideal_size(self): pass
	
	def allocate(self, x, y, width, height):
		if self.extra_width == -1:
			self.width = min(width, self.ideal_width)
			self.x     = x + (width - self.width) // 2
		else:
			self.width  = width
			self.x      = x
		
		if self.extra_height == -1:
			self.height = min(height, self.ideal_height)
			self.y      = y + (height - self.height) // 2
		else:
			self.height = height
			self.y      = y
			
	def move(self, x, y): self.allocate(x, y, self.width, self.height)
	
	def render(self): pass
	
	def process_event(self, events):
		for event in events:
			if   event[0] == sdlconst.MOUSEMOTION:
				if MOUSE_GRABBER_WIDGET: MOUSE_GRABBER_WIDGET.on_mouse_move    (*event[1:])
				else:                    self                .on_mouse_move    (*event[1:])
			elif event[0] == sdlconst.MOUSEBUTTONDOWN:
				if MOUSE_GRABBER_WIDGET: MOUSE_GRABBER_WIDGET.on_mouse_pressed (*event[1:])
				else:                    self                .on_mouse_pressed (*event[1:])
			elif event[0] == sdlconst.MOUSEBUTTONUP  :
				if MOUSE_GRABBER_WIDGET: MOUSE_GRABBER_WIDGET.on_mouse_released(*event[1:])
				else:                    self                .on_mouse_released(*event[1:])
			elif event[0] == sdlconst.KEYDOWN:
				widget = FOCUSED_WIDGET
				while widget:
					if widget.on_key_pressed(event[1], event[3], event[2]): break
					widget = widget.parent
			elif event[0] == sdlconst.KEYUP:
				widget = FOCUSED_WIDGET
				while widget:
					if widget.on_key_released(event[1], event[2]): break
					widget = widget.parent
			elif event[0] == sdlconst.JOYBUTTONDOWN:
				widget = FOCUSED_WIDGET
				while widget:
					if widget.on_joy_pressed(event[1]): break
					widget = widget.parent
				else:
					if   event[1] == 0: self.process_event([(sdlconst.KEYDOWN, sdlconst.K_RETURN, 0, 0)])
					elif event[1] == 1: self.process_event([(sdlconst.KEYDOWN, sdlconst.K_ESCAPE, 0, 0)])
			elif event[0] == sdlconst.JOYBUTTONUP:
				widget = FOCUSED_WIDGET
				while widget:
					if widget.on_joy_released(event[1]): break
					widget = widget.parent
				else:
					if   event[1] == 0: self.process_event([(sdlconst.KEYUP, sdlconst.K_RETURN, 0)])
					elif event[1] == 1: self.process_event([(sdlconst.KEYUP, sdlconst.K_ESCAPE, 0)])
			elif event[0] == sdlconst.JOYAXISMOTION:
				widget = FOCUSED_WIDGET
				while widget:
					if widget.on_joy_moved(event[1], event[2]): break
					widget = widget.parent
				else:
					if   event[1] == 0:
						if   event[2] < -1000: self.process_event([(sdlconst.KEYDOWN, sdlconst.K_LEFT , 0, 0), (sdlconst.KEYUP, sdlconst.K_LEFT , 0)])
						elif event[2] >  1000: self.process_event([(sdlconst.KEYDOWN, sdlconst.K_RIGHT, 0, 0), (sdlconst.KEYUP, sdlconst.K_RIGHT, 0)])
					if   event[1] == 1:
						if   event[2] < -1000: self.process_event([(sdlconst.KEYDOWN, sdlconst.K_UP   , 0, 0), (sdlconst.KEYUP, sdlconst.K_UP   , 0)])
						elif event[2] >  1000: self.process_event([(sdlconst.KEYDOWN, sdlconst.K_DOWN , 0, 0), (sdlconst.KEYUP, sdlconst.K_DOWN , 0)])
						
	def set_grab_mouse(self, grab):
		global MOUSE_GRABBER_WIDGET
		if   grab and not MOUSE_GRABBER_WIDGET:             MOUSE_GRABBER_WIDGET = self
		elif (not grab) and (MOUSE_GRABBER_WIDGET is self): MOUSE_GRABBER_WIDGET = None
		
	def on_mouse_pressed (self, button, x, y): pass
		
	def on_mouse_released(self, button, x, y): pass
	
	def on_mouse_move(self, x, y, x_relative, y_relative, state):
		global HIGHLIGHT_WIDGET
		if HIGHLIGHT_WIDGET:
			HIGHLIGHT_WIDGET.set_highlight(0)
			HIGHLIGHT_WIDGET = None
		
	def on_key_pressed (self, key, unicode_key, mods): pass
	def on_key_released(self, key, mods): pass
	
	def on_joy_moved   (self, axis, value): pass
	def on_joy_pressed (self, button): pass
	def on_joy_released(self, button): pass
	
	def begin_round(self): pass
	def advance_time(self, proportion): pass

class HighlightableWidget(Widget):
	def __init__(self):
		self.highlight = 0
	def on_highlight (self, highlight): pass
	def set_highlight(self, highlight):
		global HIGHLIGHT_WIDGET
		if highlight:
			if HIGHLIGHT_WIDGET is not self:
				if HIGHLIGHT_WIDGET: HIGHLIGHT_WIDGET.set_highlight(0)
				HIGHLIGHT_WIDGET = self
				self.highlight = 1
				self.on_highlight(1)
		else:
			if HIGHLIGHT_WIDGET is self:
				HIGHLIGHT_WIDGET = None
				self.highlight = 0
				self.on_highlight(0)
		return 1
	
	def on_mouse_move(self, x, y, x_relative, y_relative, state):
		self.set_highlight(1)
		return 1
	
class FocusableWidget(Widget):
	def __init__(self):
		self.focus = 0
	def on_focus (self, focus): pass
	def set_focus(self, focus, from_side = -1):
		global FOCUSED_WIDGET
		if focus:
			if FOCUSED_WIDGET is not self:
				if FOCUSED_WIDGET: FOCUSED_WIDGET.set_focus(0)
				FOCUSED_WIDGET = self
				
				window = self.get_window()
				if window: window.last_focused_widget = self
				
				self.focus = 1
				self.on_focus(1)
		else:
			if FOCUSED_WIDGET is self:
				FOCUSED_WIDGET = None
				self.focus = 0
				self.on_focus(0)
		return 1
		
	def on_mouse_pressed(self, button, x, y):
		self.set_focus(1)
		return 1
		

class Group(Widget):
	def __init__(self, parent):
		Widget.__init__(self, parent)
		self.widgets = []
		self.visible = 1
		
	def recursive(self, l = None):
		if not l: l = []
		for widget in self.widgets:
			if widget:
				l.append(widget)
				if isinstance(widget, Group): widget.recursive(l)
		return l
	
	def add(self, widget):
		self.widgets.append(widget)
		widget.added_into(self)
		
	def remove(self, widget):
		self.widgets.remove(widget)
		widget.added_into(None)
		
	def reset_size(self):
		for widget in self.widgets: widget.reset_size()
		
	def render(self):
		if self.visible:
			for widget in self.widgets:
				if widget: widget.render()
			
	def begin_round(self):
		if self.visible:
			for widget in self.widgets:
				if widget: widget.begin_round()
			
	def advance_time(self, proportion):
		if self.visible:
			for widget in self.widgets:
				if widget: widget.advance_time(proportion)
	
	def move(self, x, y):
		dx = x - self.x
		dy = y - self.y
		self.x = x
		self.y = y
		for widget in self.widgets:
			if widget: widget.move(widget.x + dx, widget.y + dy)
			
	def __repr__(self): return """<%s widgets=[%s]>""" % (self.__class__.__name__, ", ".join([repr(widget) for widget in self.widgets]))


class Layer(Group):
	def set_on_top(self, widget):
		if not widget is self.widgets[-1]:
			self.widgets.remove(widget)
			self.widgets.append(widget)
			
	def calc_ideal_size(self):
		for widget in self.widgets:
			widget.calc_ideal_size()

		self.ideal_width  = max([widget.ideal_width  for widget in self.widgets])
		self.ideal_height = max([widget.ideal_height for widget in self.widgets])
		self.min_width    = max([widget.min_width    for widget in self.widgets])
		self.min_height   = max([widget.min_height   for widget in self.widgets])
		self.extra_width  = max([widget.extra_width  for widget in self.widgets])
		self.extra_height = max([widget.extra_height for widget in self.widgets])
		
	def allocate(self, x, y, width, height):
		Group.allocate(self, x, y, width, height)
		
		for widget in self.widgets:
			widget.allocate(x, y, width, height)
			
	def on_mouse_pressed(self, button, x, y):
		for widget in self.widgets[::-1]:
			if (widget.x <= x <= widget.x + widget.width) and (widget.y <= y <= widget.y + widget.height):
				if widget.on_mouse_pressed(button, x, y): return 1
			
	def on_mouse_released(self, button, x, y):
		for widget in self.widgets[::-1]:
			if (widget.x <= x <= widget.x + widget.width) and (widget.y <= y <= widget.y + widget.height):
				if widget.on_mouse_released(button, x, y): return 1
			
	def on_mouse_move(self, x, y, x_relative, y_relative, state):
		for widget in self.widgets[::-1]:
			if (widget.x <= x <= widget.x + widget.width) and (widget.y <= y <= widget.y + widget.height):
				if widget.on_mouse_move(x, y, x_relative, y_relative, state): return 1
			
			
class Table(Group):
	def __init__(self, parent, nb_col = 1, nb_row = 1):
		Group.__init__(self, parent)
		
		self.nb_col      = nb_col
		self.nb_row      = nb_row
		self.col_pad     = STYLE.table_col_pad
		self.row_pad     = STYLE.table_row_pad
		self._col_pads   = 0
		self._row_pads   = 0
		self.border_pad  = 0
		self._next_index = 0
		self.widgets     = [None] * (nb_col * nb_row)

	def skip_case(self, nb = 1):
		self._next_index += nb
		
	def add(self, widget):
		self.widgets[self._next_index] = widget
		self._next_index += 1
		widget.added_into(self)
		
	def set_widget_at(self, widget, col = None, row = None):
		index = col + row * self.nb_col
		if self.widgets[index]: self.remove(self.widgets[index])
		self.widgets[index] = widget
		widget.added_into(self)
		
	def remove(self, widget):
		self.widgets[self.widgets.index(widget)] = None
		widget.added_into(None)
		
	def get_cols(self):
		return [filter(None, [self.widgets[i + j * self.nb_col] for j in range(self.nb_row)]) for i in range(self.nb_col)]
	
	def get_rows(self):
		return [filter(None, self.widgets[i * self.nb_col : (i + 1) * self.nb_col]) for i in range(self.nb_row)]
	
	def get_extra_width(self):
		return max([widget.get_extra_width() for widget in self.widgets])
		
	def reset_size(self):
		for widget in self.widgets:
			if widget: widget.reset_size()
		
	def calc_ideal_size(self, calc_min = 1):
		for widget in self.widgets:
			if widget: widget.calc_ideal_size()
			
		cols = self.get_cols()
		rows = self.get_rows()
		
		self.ideal_col_widths  = [max([0] + [widget.ideal_width  for widget in col]) for col in cols]
		self.ideal_row_heights = [max([0] + [widget.ideal_height for widget in row]) for row in rows]
		self.min_col_widths    = [max([0] + [widget.min_width    for widget in col]) for col in cols]
		self.min_row_heights   = [max([0] + [widget.min_height   for widget in row]) for row in rows]
		self.extra_col_widths  = [max([-1] + [max(widget.extra_width , 0.0) for widget in col]) for col in cols]
		self.extra_row_heights = [max([-1] + [max(widget.extra_height, 0.0) for widget in row]) for row in rows]
		
		self._col_pads = sum([self.col_pad for width  in self.ideal_col_widths  if width  > 0])
		self._row_pads = sum([self.row_pad for height in self.ideal_row_heights if height > 0])
		if self.border_pad:
			self._col_pads += self.col_pad
			self._row_pads += self.row_pad
		else:
			self._col_pads -= self.col_pad
			self._row_pads -= self.row_pad
			
		self.ideal_width  = self._col_pads + sum(self.ideal_col_widths)
		self.ideal_height = self._row_pads + sum(self.ideal_row_heights)
		if calc_min:
			self.min_width  = self._col_pads + sum(self.min_col_widths)
			self.min_height = self._row_pads + sum(self.min_row_heights)

		self.extra_width  = sum(self.extra_col_widths)
		self.extra_height = sum(self.extra_row_heights)
		
	def allocate(self, x, y, width, height):
		Group.allocate(self, x, y, width, height)
		
		extra = width - self.ideal_width
		if  (extra == 0) or ((extra > 0) and (self.extra_width == 0)):
			self.col_widths = [int(self.ideal_col_widths[i]) for i in range(self.nb_col)]
		elif extra > 0:
			self.col_widths = [int(self.ideal_col_widths[i] + extra * (self.extra_col_widths[i] / self.extra_width)) for i in range(self.nb_col)]
		else:
			available = width - self._col_pads
			required  = sum(self.min_col_widths)
			ideal     = sum(self.ideal_col_widths)
			if ideal == required:
				factor = float(available) / required
				self.col_widths = [int(self.min_col_widths[i] * factor) for i in range(self.nb_col)]
			else:
				factor = float(available - required) / (ideal - required)
				self.col_widths = [int(self.min_col_widths[i] + (self.ideal_col_widths[i] - self.min_col_widths[i]) * factor) for i in range(self.nb_col)]
			
		extra = height - self.ideal_height
		if  (extra == 0) or ((extra > 0) and (self.extra_height == 0)):
			self.row_heights = [int(self.ideal_row_heights[i]) for i in range(self.nb_row)]
		elif extra > 0:
			self.row_heights = [int(self.ideal_row_heights[i] + extra * (self.extra_row_heights[i] / self.extra_height)) for i in range(self.nb_row)]
		else:
			available = height - self._row_pads
			required  = sum(self.min_row_heights)
			ideal     = sum(self.ideal_row_heights)
			if ideal == required:
				factor = float(available) / required
				self.row_heights = [int(self.min_row_heights[i] * factor) for i in range(self.nb_row)]
			else:
				factor = float(available - required) / (ideal - required)
				self.row_heights = [int(self.min_row_heights[i] + (self.ideal_row_heights[i] - self.min_row_heights[i]) * factor) for i in range(self.nb_row)]
				
		wx = x
		if self.border_pad: wx += self.row_pad
		for col in range(self.nb_col):
			wy = y
			if self.border_pad: wy += self.col_pad
			for row in range(self.nb_row):
				widget = self.widgets[col + row * self.nb_col]
				if widget:
					widget.allocate(wx, wy, self.col_widths[col], self.row_heights[row])
				wy += self.row_heights[row] + self.row_pad
			wx += self.col_widths[col] + self.col_pad
			
	def widget_at(self, x, y):
		if (x < 0) or (y < 0): return None
		
		wx = self.x
		if self.border_pad: wx += self.col_pad
		for col in range(self.nb_col):
			wx += self.col_widths[col]
			if x <= wx: break
			wx += self.col_pad
			if x <= wx: return None
		else: return None
		
		wy = self.y
		if self.border_pad: wy += self.row_pad
		for row in range(self.nb_row):
			wy += self.row_heights[row]
			if y <= wy: break
			wy += self.row_pad
			if y <= wy: return None
		else: return None
		
		widget = self.widgets[col + row * self.nb_col]
		if widget and (widget.x <= x <= widget.x + widget.width) and (widget.y <= y <= widget.y + widget.height):
			return widget
		
	def on_mouse_pressed(self, button, x, y):
		widget = self.widget_at(x, y)
		if widget and widget.on_mouse_pressed(button, x, y): return 1
		return super(Table, self).on_mouse_pressed(button, x, y)
		
	def on_mouse_released(self, button, x, y):
		widget = self.widget_at(x, y)
		if widget and widget.on_mouse_released(button, x, y): return 1
		return super(Table, self).on_mouse_released(button, x, y)
		
	def on_mouse_move(self, x, y, x_relative, y_relative, state):
		widget = self.widget_at(x, y)
		if widget and widget.on_mouse_move(x, y, x_relative, y_relative, state): return 1
		return super(Table, self).on_mouse_move(x, y, x_relative, y_relative, state)

	def set_focus(self, focus, from_side = -1):
		if from_side == -1: widgets = self.widgets
		else:               widgets = self.widgets[::-1]
		for widget in widgets:
			if widget and (isinstance(widget, FocusableWidget) or isinstance(widget, Group)) and widget.set_focus(focus, from_side): return 1
			
	def on_key_pressed (self, key, unicode_key, mods):
		if key in _MOVING_KEYS:
			widget = FOCUSED_WIDGET
			while widget and (widget.parent is not self): widget = widget.parent
			i = self.widgets.index(widget)
			col = i %  self.nb_col
			row = i // self.nb_col
			
			if   key == sdlconst.K_UP:
				while row > 0:
					row -= 1
					widget = self.widgets[col + row * self.nb_col]
					if widget and (isinstance(widget, FocusableWidget) or isinstance(widget, Group)) and widget.set_focus(1,  1): return 1
					
			elif key == sdlconst.K_DOWN:
				while row < self.nb_row - 1:
					row += 1
					widget = self.widgets[col + row * self.nb_col]
					if widget and (isinstance(widget, FocusableWidget) or isinstance(widget, Group)) and widget.set_focus(1, -1): return 1
					
			elif (key == sdlconst.K_LEFT) or ((key == sdlconst.K_TAB) and (mods & sdlconst.MOD_LSHIFT)):
				while col > 0:
					col -= 1
					widget = self.widgets[col + row * self.nb_col]
					if widget and (isinstance(widget, FocusableWidget) or isinstance(widget, Group)) and widget.set_focus(1,  1): return 1
					
			elif (key == sdlconst.K_RIGHT) or (key == sdlconst.K_TAB):
				while col < self.nb_col - 1:
					col += 1
					widget = self.widgets[col + row * self.nb_col]
					if widget and (isinstance(widget, FocusableWidget) or isinstance(widget, Group)) and widget.set_focus(1, -1): return 1
					
	def insert_row(self, index):
		for i in range(index * self.nb_col, (index + 1) * self.nb_col): self.widgets.insert(i, None)
		self.nb_row += 1
		
	def delete_row(self, index):
		self.nb_row -= 1
		del self.widgets[index * self.nb_col : (index + 1) * self.nb_col]
		
	def insert_col(self, index):
		self.nb_col += 1
		for i in range(self.nb_row): self.widgets.insert(i * self.nb_col + index, None)
		
	def delete_col(self, index):
		self.nb_col -= 1
		for i in range(self.nb_row): del self.widgets[i * self.nb_col + index]
		
_MOVING_KEYS = set([sdlconst.K_LEFT, sdlconst.K_UP, sdlconst.K_RIGHT, sdlconst.K_DOWN, sdlconst.K_TAB])


class HTable(Table):
	def __init__(self, parent, nb_row = 1):
		Table.__init__(self, parent, 0, nb_row)
		
	def add(self, widget, col = None):
		if col is None: col = self.nb_col - 1
		
		if col == -1: i = 0
		else:
			for i in range(col, len(self.widgets), self.nb_col):
				if self.widgets[i] is None:
					self.widgets[i] = widget
					widget.added_into(self)
					return
				
		self.insert_col(self.nb_col)
		self.widgets[self.nb_col - 1] = widget
		widget.added_into(self)
		
	def remove(self, widget):
		i = self.widgets.index(widget)
		self.widgets[i] = None
		widget.added_into(None)
		col = i % self.nb_col
		for i in range(col, len(self.widgets), self.nb_col):
			if self.widgets[i]: break
		else: self.delete_col(col)			
		
class VTable(Table):
	def __init__(self, parent, nb_col = 1):
		Table.__init__(self, parent, nb_col, 0)
		
	def add(self, widget, row = None):
		if row is None: row = self.nb_row - 1

		if row == -1: i = 0
		else:
			for i in range(row * self.nb_col, (row + 1) * self.nb_col):
				if self.widgets[i] is None:
					self.widgets[i] = widget
					widget.added_into(self)
					return
				
		self.insert_row(self.nb_row)
		self.widgets[(self.nb_row - 1) * self.nb_col] = widget
		widget.added_into(self)
		
	def remove(self, widget):
		i = self.widgets.index(widget)
		self.widgets[i] = None
		widget.added_into(None)
		row = i // self.nb_col
		for i in range(row * self.nb_col, (row + 1) * self.nb_col):
			if self.widgets[i]: break
		else: self.delete_row(row)
		

class VList(VTable, HighlightableWidget, FocusableWidget):
	def __init__(self, parent, nb_col = 1):
		HighlightableWidget.__init__(self)
		FocusableWidget    .__init__(self)
		VTable             .__init__(self, parent, nb_col)
		self.value      = 0
		self.border_pad = 1
		
	def add(self, widget, row = None):
		if isinstance(widget, basestring): widget = Label(None, widget)
		VTable.add(self, widget, row)
		
	def render(self):
		if self.value != -1:
			y = self.y + self.row_pad * self.value
			if self.border_pad: y += self.row_pad
			for i in range(self.value): y += self.row_heights[i]
			STYLE.rectangle(self.x + 2, y - 2, self.x + self.width - 2, y + self.row_heights[self.value] + 2, self.highlight or self.focus)
		VTable.render(self)
		
	def set_focus(self, focus, from_side = -1):
		return FocusableWidget.set_focus(self, focus, from_side)
		
	def on_mouse_pressed(self, button, x, y):
		self.set_focus(1)
		widget = self.widget_at(x, y)
		if widget and widget.on_mouse_pressed(button, x, y): pass
		elif button == 1:
			wy = self.y
			if self.border_pad: wy += self.row_pad
			for row in range(self.nb_row):
				wy += self.row_heights[row] + self.row_pad
				if y <= wy:
					self.set_value(row)
					break
			else: self.set_value(-1)
			
	def on_key_pressed (self, key, unicode_key, mods):
		if   key == sdlconst.K_DOWN:
			if self.value < self.nb_row - 1: self.set_value(self.value + 1); return 1
		elif key == sdlconst.K_UP:
			if self.value > 0              : self.set_value(self.value - 1); return 1
			
	def set_value(self, value):
		if value != self.value:
			self.value = value
			self.on_value_changed()
			
	def on_value_changed(self): pass
	
class HList(HTable, HighlightableWidget, FocusableWidget):
	def __init__(self, parent, nb_row = 1):
		HighlightableWidget.__init__(self)
		FocusableWidget    .__init__(self)
		HTable             .__init__(self, parent, nb_row)
		self.value      = 0
		self.border_pad = 1
		
	def add(self, widget, col = None):
		if isinstance(widget, basestring): widget = Label(None, widget)
		HTable.add(self, widget, col)
		
	def render(self):
		if self.value != -1:
			x = self.x + self.col_pad * self.value
			if self.border_pad: x += self.col_pad
			for i in range(self.value): x += self.col_widths[i]
			STYLE.rectangle(x - 2, self.y + 2, x + self.col_widths[self.value] + 2, self.y + self.height - 2, self.highlight or self.focus)
		HTable.render(self)
		
	def set_focus(self, focus, from_side = -1):
		return FocusableWidget.set_focus(self, focus, from_side)
		
	def on_mouse_pressed(self, button, x, y):
		self.set_focus(1)
		widget = self.widget_at(x, y)
		if widget and widget.on_mouse_pressed(button, x, y): pass
		elif button == 1:
			wx = self.x
			if self.border_pad: wx += self.col_pad
			for col in range(self.nb_col):
				wx += self.col_widths[col] + self.col_pad
				if x <= wx:
					self.set_value(col)
					break
			else: self.set_value(-1)
			
	def on_key_pressed (self, key, unicode_key, mods):
		if   key == sdlconst.K_RIGHT:
			if self.value < self.nb_col - 1: self.set_value(self.value + 1); return 1
		elif key == sdlconst.K_LEFT:
			if self.value > 0              : self.set_value(self.value - 1); return 1
			
	def set_value(self, value):
		if value != self.value:
			self.value = value
			self.on_value_changed()
			
	def on_value_changed(self): pass
	
	
class Image(Widget):
	def __init__(self, parent = None, material = None):
		self.material = material
		self.tex_x1 = 0.0
		self.tex_y1 = 0.0
		self.tex_x2 = 1.0
		self.tex_y2 = 1.0
		Widget.__init__(self, parent)
		
	def render(self):
		if self.material:
			self.material.activate()
			if self.material.is_alpha(): opengl.glEnable(opengl.GL_BLEND)
			opengl.glBegin     (opengl.GL_QUADS)
			opengl.glTexCoord2f(self.tex_x1, self.tex_y1); opengl.glVertex2i(self.x             , self.y)
			opengl.glTexCoord2f(self.tex_x1, self.tex_y2); opengl.glVertex2i(self.x             , self.y + self.height)
			opengl.glTexCoord2f(self.tex_x2, self.tex_y2); opengl.glVertex2i(self.x + self.width, self.y + self.height)
			opengl.glTexCoord2f(self.tex_x2, self.tex_y1); opengl.glVertex2i(self.x + self.width, self.y)
			opengl.glEnd()
			soya.DEFAULT_MATERIAL.activate()
			if self.material.is_alpha(): opengl.glDisable(opengl.GL_BLEND)


class Label(Widget):
	def __init__(self, parent = None, text = u"", color = None, font = None):
		self.color         = color or STYLE.text_colors[0]
		self.text          = text
		self._font         = font or STYLE.font
		self._changed      = -2
		self._display_list = soya.DisplayList()
		Widget.__init__(self, parent)
		self.extra_height = -1
		
	def __repr__(self): return """<%s text="%s">""" % (self.__class__.__name__, self._text.encode("latin"))
	
	def get_font (self): return self._font
	def set_font (self, x): self._font  = x; self._changed = -2
	def get_text (self): return self._text
	def set_text (self, x): self._text  = x; self._changed = -2
	font  = property(get_font, set_font)
	text  = property(get_text, set_text)
	
	def calc_ideal_size(self):
		text_size = self._font.get_print_size(self._text)
		self.ideal_width  = int(text_size[0])
		self.ideal_height = int(text_size[1])
		self.min_width  = self.ideal_width
		self.min_height = self.ideal_height
		
	def allocate(self, x, y, width, height):
		if (width != self.width) or (height != self.height): self._changed = -2
		Widget.allocate(self, x, y, width, height)
		
	def build_display_list(self):
		"""Label.build_display_list()

Really renders the text.

If you override this method, DO NOT SET self.text or self._text here !!!
It might call glyph tessellation that would be included in the display list !"""
		#self._font.draw_area(self._text, self.x, self.y, 0.0, self.width, self.height, 0)
		self._font.draw(self._text, 0.0, 0.0)
		
	def render(self):
		soya.DEFAULT_MATERIAL.activate()
		opengl.glColor4f(*self.color)
		opengl.glPushMatrix()
		opengl.glTranslatef(self.x, self.y, 0.0)
		if self._changed != self._font._pixels_height:
			self._font.create_glyphs(self._text)
			
			opengl.glNewList(self._display_list.id, opengl.GL_COMPILE_AND_EXECUTE)
			self.build_display_list()
			opengl.glEndList()
			self._changed = self._font._pixels_height
		else:
			opengl.glCallList(self._display_list.id)
		opengl.glPopMatrix()
		
class Text(Widget):
	def __init__(self, parent = None, text = u"", color = None, font = None):
		self.color         = color or STYLE.text_colors[0]
		self.text          = text
		self._font         = font or STYLE.font
		self._changed      = -2
		self._display_list = soya.DisplayList()
		Widget.__init__(self, parent)
		self.min_width  = 300
		self._wrap_at_width = 1000000.0
		
	def __repr__(self): return """<%s text="%s">""" % (self.__class__.__name__, self._text.encode("latin"))
	
	def get_font (self): return self._font
	def set_font (self, x): self._font  = x; self._changed = -2
	def get_text (self): return self._text
	def set_text (self, x): self._text  = x; self._changed = -2
	font  = property(get_font, set_font)
	text  = property(get_text, set_text)

	def reset_size(self):
		self._wrap_at_width = 1000000.0
		
	def calc_ideal_size(self):
		max_line_width, total_height, wrapped_text = self._font.wordwrap(self._text, self._wrap_at_width)
		self.ideal_width  = int(max_line_width)
		self.ideal_height = int(total_height)
		self.min_height   = self.ideal_height
		
	def allocate(self, x, y, width, height):
		max_line_width, total_height, wrapped_text = self._font.wordwrap(self._text, width)
		if (height < total_height) and (width < self._wrap_at_width):
			self._wrap_at_width = width
			print "text wraps => restart calc_size !"
			raise CalcSizeRestart

		if (width != self.width) or (height != self.height): self._changed = -2
		Widget.allocate(self, x, y, width, height)
		
	def move(self, x, y):
		self.x = x
		self.y = y
		
	def build_display_list(self):
		self._font.draw_area(self._text, 0.0, 0.0, 0.0, self.width, self.height, 0)
		
	def render(self):
		soya.DEFAULT_MATERIAL.activate()
		opengl.glColor4f(*self.color)
		opengl.glPushMatrix()
		opengl.glTranslatef(self.x, self.y, 0.0)
		if self._changed != self._font._pixels_height:
			self._font.create_glyphs(self._text)
			
			opengl.glNewList(self._display_list.id, opengl.GL_COMPILE_AND_EXECUTE)
			self.build_display_list()
			opengl.glEndList()
			self._changed = self._font._pixels_height
		else:
			opengl.glCallList(self._display_list.id)
		opengl.glPopMatrix()


class Button(Label, HighlightableWidget, FocusableWidget):
	def __init__(self, parent = None, text = u"", color = None, font = None):
		HighlightableWidget.__init__(self)
		FocusableWidget    .__init__(self)
		Label.__init__(self, parent, text, color, font)
		
	def calc_ideal_size(self):
		Label.calc_ideal_size(self)
		self.ideal_width  += 6
		self.ideal_height += 6
		self.min_width    += 6
		self.min_height   += 4
		
	def build_display_list(self):
		self._font.draw(self._text, (self.width - self.ideal_width) // 2, 3.0)
		
	def render(self):
		STYLE.rectangle(self.x, self.y, self.x + self.width, self.y + self.height, self.highlight or self.focus)
		Label.render(self)
		
	def on_clicked(self):
		print "Button clicked !"
	
	def on_mouse_released(self, button, x, y):
		if button == 1: self.on_clicked()
		return 1
	
	def on_key_pressed (self, key, unicode_key, mods):
		if (key == sdlconst.K_SPACE) or (key == sdlconst.K_RETURN) or (key == sdlconst.K_KP_ENTER):
			self.on_clicked()
			return 1
		
	def on_highlight(self, highlight):
		HighlightableWidget.on_highlight(self, highlight)
		if highlight: self.color = STYLE.text_colors[1]
		else:         self.color = STYLE.text_colors[0]

class CancelButton(Button):
	def __init__(self, parent = None, text = u"Cancel", color = None, font = None):
		Button.__init__(self, parent, text, color, font)
		
	def on_clicked(self): self.get_window().close()
	
class ValidateButton(Button):
	def __init__(self, parent = None, text = u"Ok", color = None, font = None):
		Button.__init__(self, parent, text, color, font)

	
class Input(Label, HighlightableWidget, FocusableWidget):
	def __init__(self, parent = None, text = u"", color = None, font = None):
		self.cursor_pos = len(text)
		HighlightableWidget.__init__(self)
		FocusableWidget    .__init__(self)
		Label.__init__(self, parent, text, color, font)
		
	def calc_ideal_size(self):
		Label.calc_ideal_size(self)
		self.ideal_width  += 6
		self.ideal_height += 6
		self.min_width    += 6
		self.min_height   += 5
		
	def build_display_list(self):
		self._font.draw(self._text, 3.0, 3.0)
		
	def render(self):
		STYLE.rectangle(self.x, self.y, self.x + self.width, self.y + self.height, self.highlight or self.focus)
		Label.render(self)
		if self.highlight or self.focus:
			cursor_x = self.x + 3 + int(self._font.get_print_size(self._text[:self.cursor_pos])[0])
			opengl.glColor4f(*STYLE.text_colors[self.highlight])
			opengl.glBegin(opengl.GL_LINES)
			opengl.glVertex2i(cursor_x, self.y + 3)
			opengl.glVertex2i(cursor_x, self.y + self.height - 3)
			opengl.glEnd()
			
	def on_text_changed(self): pass
	def on_key_pressed (self, key, unicode_key, mods):
		if   key == sdlconst.K_LEFT  : self.cursor_pos = max(self.cursor_pos - 1, 0)              ; return 1
		elif key == sdlconst.K_RIGHT : self.cursor_pos = min(self.cursor_pos + 1, len(self._text)); return 1
		elif key == sdlconst.K_HOME  : self.cursor_pos = 0                                        ; return 1
		elif key == sdlconst.K_END   : self.cursor_pos = len(self._text)                          ; return 1
		elif key == sdlconst.K_DELETE:
			self.text = self._text[:self.cursor_pos] + self._text[self.cursor_pos + 1:]
			self.on_text_changed()
			return 1
		elif key == sdlconst.K_BACKSPACE:
			self.text = self._text[:self.cursor_pos - 1] + self._text[self.cursor_pos:]
			self.cursor_pos = max(self.cursor_pos - 1, 0)
			self.on_text_changed()
			return 1
		elif key == sdlconst.K_TAB   : return 0 # Not a valid character, but has a valid unicode!
		elif key == sdlconst.K_ESCAPE: return 0 # Not a valid character, but has a valid unicode!
		elif(key == sdlconst.K_RETURN) or (key == sdlconst.K_KP_ENTER): return 0 # Not a valid character, but has a valid unicode!
		elif unicode_key:
			self.text = self._text[:self.cursor_pos] + unichr(unicode_key) + self._text[self.cursor_pos:]
			self.cursor_pos += 1
			self.on_text_changed()
			return 1
		
	def on_mouse_pressed(self, button, x, y):
		super(Input, self).on_mouse_pressed(button, x, y)
		x -= self.x + 3.0
		i = 0
		for char in self._text:
			char_width = self._font.get_print_size(char)[0]
			if x < char_width // 2: self.cursor_pos = i; break
			i += 1
			x -= char_width
			if x < 0              : self.cursor_pos = i; break
		self.cursor_pos = i
		return 1
	
	def on_mouse_released(self, button, x, y): return 1 # Make the widget "opaque" : don't give the event to another one
	
	def on_highlight(self, highlight):
		if highlight: self.color = STYLE.text_colors[1]
		else:         self.color = STYLE.text_colors[0]
		
		
class CheckBox(Label, HighlightableWidget, FocusableWidget):
	base_color_index = 0
	def __init__(self, parent = None, text = u"", value = 0, color = None, font = None):
		self.value     = value
		self.focus     = 0
		HighlightableWidget.__init__(self)
		FocusableWidget    .__init__(self)
		Label.__init__(self, parent, text, color, font)
		
		self.check_size = int(STYLE.get_char_height() * 0.9)
		
	def calc_ideal_size(self):
		text_size = self._font.get_print_size(self._text)
		self.text_width  = int(text_size[0])
		self.text_height = int(text_size[1])
		if self._text: self.ideal_width  = int(self.text_width + self.check_size * 1.1)
		else:          self.ideal_width  = self.check_size
		self.ideal_height = max(self.text_height, self.check_size)
		self.min_width  = self.ideal_width
		self.min_height = self.ideal_height
		
	def build_display_list(self):
		self._font.draw(self._text, self.check_size * 1.1, 0.0)
		
	def render(self):
		Label.render(self)
		x1 = self.x
		y1 = self.y
		x2 = x1 + self.check_size
		y2 = y1 + self.check_size
		STYLE.rectangle(x1, y1, x2, y2, self.base_color_index + (self.highlight or self.focus))
		if self.value:
			opengl.glLineWidth(2.0)
			opengl.glColor4f(*STYLE.line_colors[self.base_color_index + (self.highlight or self.focus)])
			opengl.glBegin   (opengl.GL_LINES)
			opengl.glVertex2i(x1, y1)
			opengl.glVertex2i(x2, y2)
			opengl.glVertex2i(x2, y1)
			opengl.glVertex2i(x1, y2)
			opengl.glEnd()
			opengl.glLineWidth(1.0)
			
	def on_mouse_released(self, button, x, y):
		if button == 1:
			self.set_value(not self.value)
			
	def on_key_pressed (self, key, unicode_key, mods):
		if (key == sdlconst.K_SPACE) or (key == sdlconst.K_RETURN) or (key == sdlconst.K_KP_ENTER):
			self.set_value(not self.value)
			return 1
		
	def set_value(self, value):
		self.value = value
		self.on_value_changed()
		
	def on_value_changed(self): pass
	
	def on_highlight(self, highlight):
		if highlight: self.color = STYLE.text_colors[1]
		else:         self.color = STYLE.text_colors[0]
	
		
class WindowCloseButton(CheckBox):
	base_color_index = 2
	def set_value(self, value):
		CheckBox.set_value(self, value)
		if not value: self.parent.parent.close()
		
class Window(Table, HighlightableWidget):
	def __init__(self, parent = None, title = u"Window", closable = 1):
		HighlightableWidget.__init__(self)
		Table.__init__(self, parent, 1, 2)
		self.border_pad = 1
		if isinstance(title, Widget): title_widget = title; self.add(title)
		else:                         title_widget = Label(None, title, color = STYLE.text_colors[2]); title_widget.extra_width = 1.0
		if closable:
			title_bar = Table(self, 2, 1)
			title_bar.col_pad = 15
			title_bar.add(title_widget)
			self.close_button = WindowCloseButton(title_bar, u"", 1)
		else: self.add(title_widget)
		self.max_width_percent   = 0.8
		self.max_height_percent  = 0.8
		self.last_focused_widget = None
		
	def on_key_pressed (self, key, unicode_key, mods):
		if    key == sdlconst.K_ESCAPE:
			self.close()
			return 1
		elif (key == sdlconst.K_SPACE) or (key == sdlconst.K_RETURN) or (key == sdlconst.K_KP_ENTER):
			for widget in self.recursive():
				if isinstance(widget, ValidateButton):
					widget.on_clicked()
					return 1
				
	def close(self):
		if self.parent:
			parent = self.parent
			self.parent.remove(self)
			self.on_closed()
			if FOCUSED_WIDGET.get_window() is self:
				widget = parent.widgets[-1]
				if   isinstance(widget, Window):
					if widget.last_focused_widget: widget.last_focused_widget.set_focus(1)
				elif isinstance(widget, FocusableWidget) or isinstance(widget, Table):
					widget.set_focus(1)
					
	def on_closed(self): pass
	
	def calc_ideal_size(self):
		Table.calc_ideal_size(self)
		self.ideal_width  += 2 * self.border_pad
		self.ideal_height += 2 * self.border_pad
		self.min_width    += 2 * self.border_pad
		self.min_height   += 2 * self.border_pad
		self.extra_width  = -1
		self.extra_height = -1
		
	def allocate(self, x, y, width, height):
		w_width  = min(width , self.ideal_width , int(self.max_width_percent  * self.parent.width ))
		w_height = min(height, self.ideal_height, int(self.max_height_percent * self.parent.height))
		
		if   x < self.parent.x                                   : x = self.parent.x
		elif x > self.parent.x + self.parent.width  - self.width : x = self.parent.x + self.parent.width  - self.width
		if   y < self.parent.y                                   : y = self.parent.y
		elif y > self.parent.y + self.parent.height - self.height: y = self.parent.y + self.parent.height - self.height
		
		Table.allocate(self, x, y, w_width, w_height)
		
		if self.last_focused_widget is None:
			if isinstance(self.widgets[1], Group): widgets = self.widgets[1].recursive()
			else:                                  widgets = [self.widgets[1]]
			for widget in widgets:
				if isinstance(widget, FocusableWidget):
					widget.set_focus(1)
					break
			else:
				self.close_button.set_focus(1)
				
	def move(self, x, y):
		if   x < self.parent.x                                   : x = self.parent.x
		elif x > self.parent.x + self.parent.width  - self.width : x = self.parent.x + self.parent.width  - self.width
		if   y < self.parent.y                                   : y = self.parent.y
		elif y > self.parent.y + self.parent.height - self.height: y = self.parent.y + self.parent.height - self.height
		Table.move(self, x, y)
		
	def render(self):
		if self.visible:
			title_y = self.y + self.widgets[0].height + int(1.3 * self.row_pad)
			STYLE.rectangle(self.x, self.y, self.x + self.width, self.y + self.height, 4)
			STYLE.rectangle(self.x, self.y, self.x + self.width, title_y, 2 + self.highlight)
			Group.render(self)
			
	def on_mouse_pressed(self, button, x, y):
		if isinstance(self.parent, Layer):
			self.parent.set_on_top(self)
			if   self.last_focused_widget: self.last_focused_widget.set_focus(1)
			elif FOCUSED_WIDGET: FOCUSED_WIDGET.set_focus(0)
			
		if not self is MOUSE_GRABBER_WIDGET:
			r = Table.on_mouse_pressed(self, button, x, y)
			if r: return r
			
		if (button == 1) and (y < self.y + self.widgets[0].height + int(1.3 * self.row_pad)):
			self.set_grab_mouse(1)
		return 1
	
	def on_mouse_released(self, button, x, y):
		if not self is MOUSE_GRABBER_WIDGET:
			r = Table.on_mouse_released(self, button, x, y)
			if r: return r
			
		if button == 1: self.set_grab_mouse(0)
		
		return 1
	
	def on_mouse_move(self, x, y, x_relative, y_relative, state):
		if not self is MOUSE_GRABBER_WIDGET:
			widget = self.widget_at(x, y)
			if widget and widget.on_mouse_move(x, y, x_relative, y_relative, state): return 1
			
		if y <= self.y + self.widgets[0].height + int(1.3 * self.row_pad):
			HighlightableWidget.on_mouse_move(self, x, y, x_relative, y_relative, state)
			
		if state == 1:
			self.move(self.x + x_relative, self.y + y_relative)
		return 1
	
		

class ScrollBar(HighlightableWidget, FocusableWidget):
	def __init__(self, parent = None, min = 0, max = 100, value = None, page_size = 0.0, step_size = 1.0):
		self.min   = min
		self.max   = max
		if value is None: self.value = min
		else:             self.value = value
		self.page_size      = page_size
		self.step_size      = step_size
		self.bar_size       = int(0.9 * STYLE.get_char_height())
		self.highlight_part = 0
		self.changing       = 0.0
		self.changing_round = 0
		HighlightableWidget.__init__(self)
		FocusableWidget    .__init__(self)
		Widget             .__init__(self, parent)
		
	def __repr__(self): return """<%s min=%s max=%s value=%s page_size=%s>""" % (self.__class__.__name__, self.min, self.max, self.value, self.page_size)
	
	def set_value(self, value):
		if   value < self.min                 : self.value = self.min
		elif value > self.max - self.page_size: self.value = self.max - self.page_size
		else:                                   self.value = value
		self.update_bar()
		self.on_value_changed()

	def on_value_changed(self): pass
		
	def set_range(self, min, max, value, page_size, step_size):
		self.min       = min
		self.max       = max
		self.page_size = page_size
		self.step_size = step_size
		self.set_value(value)
		
	def allocate(self, x, y, width, height):
		Widget.allocate(self, x, y, width, height)
		self.update_bar()
		
	def on_highlight(self, highlight):
		if not highlight:
			self.highlight_part = 0
			
	def on_mouse_released(self, button, x, y):
		self.set_grab_mouse(0)
		self.changing = 0.0

	def begin_round(self):
		if self.changing:
			self.changing_round += 1
			if self.changing_round == 4:
				self.set_value(self.value + self.changing)
				self.changing_round = 0
				
	def on_key_released(self, key, mods): self.changing = 0.0
	
			
class HScrollBar(ScrollBar):
	def __init__(self, parent = None, min = 0, max = 100, value = None, page_size = 0.0, step_size = 1.0):
		ScrollBar.__init__(self, parent, min, max, value, page_size)
		self.ideal_width  = self.bar_size * 6
		self.ideal_height = self.bar_size
		self.min_width    = self.bar_size * 4
		self.min_height   = self.bar_size
		self.extra_width  = 1.0
		self.extra_height = -1

	def update_bar(self):
		self.page_width = int((self.width - 2 * self.bar_size) * self.page_size / (self.max - self.min))
		if self.page_width < self.bar_size:
			self.additional_page_width = self.bar_size - self.page_width
			self.page_x = int(self.x + self.bar_size + (self.width - 2 * self.bar_size - self.additional_page_width) * self.value / (self.max - self.min))
			self.page_width = self.bar_size
		else:
			self.additional_page_width = 0
			self.page_x = int(self.x + self.bar_size + (self.width - 2 * self.bar_size) * self.value / (self.max - self.min))
			
	def render(self):
		STYLE.triangle(0, self.x, self.y, self.x + self.bar_size - 2, self.y + self.bar_size, self.highlight_part == 1)
		STYLE.triangle(1, self.x + self.width - self.bar_size + 2, self.y, self.x + self.width, self.y + self.bar_size, self.highlight_part == 4)
		STYLE.rectangle(self.page_x, self.y, self.page_x + self.page_width, self.y + self.bar_size, (self.highlight_part == 2) or self.focus)
		
	def set_value_pixel(self, x):
		self.set_value(self.min + float(x - (self.page_width) / 2.0 - self.x - self.bar_size) / (self.width - 2 * self.bar_size - self.additional_page_width) * (self.max - self.min))
		
	def on_mouse_move(self, x, y, x_relative, y_relative, state):
		HighlightableWidget.on_mouse_move(self, x, y, x_relative, y_relative, state)
		if   x < self.x + self.bar_size                     : self.highlight_part = 1
		elif x > self.x + self.width - self.bar_size        : self.highlight_part = 4
		else:                                                 self.highlight_part = 2
		if  (state == 1) and not self.changing:
			if self.x + self.bar_size < x < self.x + self.width - self.bar_size:
				self.set_value_pixel(self.page_x + (self.page_width) / 2.0 + x_relative)
				
		elif state == 2:
			if self.x + self.bar_size < x < self.x + self.width - self.bar_size: self.set_value_pixel(x)
		return 1
	
	def on_mouse_pressed(self, button, x, y):
		ScrollBar.on_mouse_pressed(self, button, x, y)
		self.changing_round = 0
		if   button == 1:
			if   x < self.x + self.bar_size                     : self.changing = -self.step_size
			elif x > self.x + self.width - self.bar_size        : self.changing =  self.step_size
			elif x < self.page_x                                : self.changing = -max(self.page_size, self.step_size)
			elif x > self.page_x + self.page_width              : self.changing =  max(self.page_size, self.step_size)
			self.set_value(self.value + self.changing)
			self.set_grab_mouse(1)
		elif button == 2:
			if self.x + self.bar_size < x < self.x + self.width - self.bar_size:
				self.set_value_pixel(x)
				self.set_grab_mouse(1)
		return 1
	
	def on_key_pressed(self, key, unicode_key, mods):
		if   key == sdlconst.K_LEFT :
			if self.value == self.min: return 0
			self.changing_round = -10
			self.changing = -self.step_size
			self.set_value(self.value + self.changing)
			return 1
		elif key == sdlconst.K_RIGHT:
			if self.value + self.page_size == self.max: return 0
			self.changing_round = -10
			self.changing =  self.step_size
			self.set_value(self.value + self.changing)
			return 1
			
	
class VScrollBar(ScrollBar):
	def __init__(self, parent = None, min = 0, max = 100, value = None, page_size = 0.0, step_size = 1.0):
		ScrollBar.__init__(self, parent, min, max, value, page_size)
		self.ideal_width  = self.bar_size
		self.ideal_height = self.bar_size * 4
		self.min_width    = self.bar_size
		self.min_height   = self.bar_size * 3
		self.extra_width  = -1
		self.extra_height = 1.0
		
	def update_bar(self):
		self.page_height = int((self.height - 2 * self.bar_size) * self.page_size / (self.max - self.min))
		if self.page_height < self.bar_size:
			self.additional_page_height = self.bar_size - self.page_height
			self.page_y = int(self.y + self.bar_size + (self.height - 2 * self.bar_size - self.additional_page_height) * self.value / (self.max - self.min))
			self.page_height = self.bar_size
		else:
			self.additional_page_height = 0
			self.page_y = int(self.y + self.bar_size + (self.height - 2 * self.bar_size) * self.value / (self.max - self.min))
			
	def render(self):
		STYLE.triangle(2, self.x, self.y, self.x + self.bar_size, self.y + self.bar_size - 2, self.highlight_part == 1)
		STYLE.triangle(3, self.x, self.y + self.height - self.bar_size + 2, self.x + self.bar_size, self.y + self.height, self.highlight_part == 4)
		STYLE.rectangle(self.x, self.page_y, self.x + self.bar_size, self.page_y + self.page_height, (self.highlight_part == 2 or self.focus))
		
	def set_value_pixel(self, y):
		self.set_value(self.min + float(y - self.page_height / 2.0 - self.y - self.bar_size) / (self.height - 2 * self.bar_size - self.additional_page_height) * (self.max - self.min))
		
	def on_mouse_move(self, x, y, x_relative, y_relative, state):
		HighlightableWidget.on_mouse_move(self, x, y, x_relative, y_relative, state)
		if   y < self.y + self.bar_size                      : self.highlight_part = 1
		elif y > self.y + self.height - self.bar_size        : self.highlight_part = 4
		else:                                                  self.highlight_part = 2
		if  (state == 1) and not self.changing:
			if self.y + self.bar_size < y < self.y + self.height - self.bar_size:
				self.set_value_pixel(self.page_y + self.page_height / 2.0 + y_relative)
				
		elif state == 2:
			if self.y + self.bar_size < y < self.y + self.height - self.bar_size: self.set_value_pixel(y)
		return 1
	
	def on_mouse_pressed(self, button, x, y):
		ScrollBar.on_mouse_pressed(self, button, x, y)
		self.changing_round = 0
		if   button == 1:
			if   y < self.y + self.bar_size              : self.changing = -self.step_size
			elif y > self.y + self.height - self.bar_size: self.changing =  self.step_size
			elif y < self.page_y                         : self.changing = -max(self.page_size, self.step_size)
			elif y > self.page_y + self.page_height      : self.changing =  max(self.page_size, self.step_size)
			self.set_value(self.value + self.changing)
			self.set_grab_mouse(1)
		elif button == 2:
			if self.y + self.bar_size < y < self.y + self.height - self.bar_size:
				self.set_value_pixel(y)
				self.set_grab_mouse(1)
		elif button == 4: self.set_value(self.value - self.step_size)
		elif button == 5: self.set_value(self.value + self.step_size)
		return 1
	
	def on_key_pressed(self, key, unicode_key, mods):
		if   key == sdlconst.K_UP  :
			if self.value == self.min: return 0
			self.changing_round = -10
			self.changing = -self.step_size
			self.set_value(self.value + self.changing)
			return 1
		elif key == sdlconst.K_DOWN:
			if self.value + self.page_size == self.max: return 0
			self.changing_round = -10
			self.changing =  self.step_size
			self.set_value(self.value + self.changing)
			return 1
		
		
class _ScrollPaneHScrollBar(HScrollBar):
	def on_value_changed(self):
		self.parent.update_viewport()
		
class _ScrollPaneVScrollBar(VScrollBar):
	def on_value_changed(self):
		self.parent.update_viewport()
		
class ScrollPane(Table):
	def __init__(self, parent = None):
		Table.__init__(self, parent, 2, 2)
		self.hscroll = _ScrollPaneHScrollBar()
		self.vscroll = _ScrollPaneVScrollBar()
		self.hscroll.calc_ideal_size()
		self.vscroll.calc_ideal_size()
		self.min_width  = 200
		self.min_height = 200
		self.scroll_x0 = 0
		self.scroll_y0 = 0
		
	def reset_size(self):
		Table.reset_size(self)
		if self.hscroll.parent:
			self.widgets[2] = None
			self.hscroll.added_into(None)
		
		if self.vscroll.parent:
			self.widgets[1] = None
			self.vscroll.added_into(None)
			
	def calc_ideal_size(self):
		min_width  = self.min_width
		min_height = self.min_height
		
		Table.calc_ideal_size(self, calc_min = 1)
		if self.border_pad: nb_pad = 3
		else:               nb_pad = 1

		self.inner_min_width  = self.min_width
		self.inner_min_height = self.min_height
		self.min_width  = min_width
		self.min_height = min_height
		
		self.min_col_widths [0] = self.min_width  - self.col_pad * nb_pad - self.vscroll.min_width
		self.min_row_heights[0] = self.min_height - self.row_pad * nb_pad - self.hscroll.min_height
		
	def allocate(self, x, y, width, height):
		if (self.hscroll.parent is None) and (width  < self.inner_min_width ):
			self.set_widget_at(self.hscroll, 0, 1)
			raise CalcSizeRestart
		if (self.vscroll.parent is None) and (height < self.inner_min_height):
			self.set_widget_at(self.vscroll, 1, 0)
			raise CalcSizeRestart
		
		Table.allocate(self, x, y, width, height)
		
		self.scroll_x0 = self.widgets[0].x
		self.scroll_y0 = self.widgets[0].y
		if self.hscroll.parent: self.hscroll.set_range(0, max(self.widgets[0].min_width , self.col_widths [0]), self.hscroll.value, self.col_widths [0], 50.0)
		else:                   self.hscroll.value = 0.0; self.hscroll.page_size = self.col_widths [0]; self.hscroll.max = max(self.widgets[0].min_width , self.col_widths [0])
		if self.vscroll.parent: self.vscroll.set_range(0, max(self.widgets[0].min_height, self.row_heights[0]), self.vscroll.value, self.row_heights[0], 50.0)
		else:                   self.vscroll.value = 0.0; self.vscroll.page_size = self.row_heights[0]; self.vscroll.max = max(self.widgets[0].min_height, self.row_heights[0])
		
		self.widgets[0].allocate(
			int(self.scroll_x0 - self.hscroll.value),
			int(self.scroll_y0 - self.vscroll.value),
			max(self.widgets[0].min_width , self.col_widths [0]),
			max(self.widgets[0].min_height, self.row_heights[0]),
			)
		
	def move(self, x, y):
		self.scroll_x0 += x - self.x
		self.scroll_y0 += y - self.y
		Table.move(self, x, y)
		
	def update_viewport(self):
		self.widgets[0].move(
			int(self.scroll_x0 - self.hscroll.value),
			int(self.scroll_y0 - self.vscroll.value),
			)
		
	def render(self):
		if self.visible:
			opengl.glMatrixMode(opengl.GL_PROJECTION)
			opengl.glPushAttrib(opengl.GL_VIEWPORT)
			opengl.glPushMatrix()
			opengl.glLoadIdentity()
			
			opengl.glViewport(self.scroll_x0,
												soya.get_screen_height() - (self.scroll_y0 + self.vscroll.page_size),
												self.hscroll.page_size,
												self.vscroll.page_size)
			
			opengl.glOrtho(self.scroll_x0,
										 self.scroll_x0 + self.hscroll.page_size,
										 self.scroll_y0 + self.vscroll.page_size,
										 self.scroll_y0, -1.0, 1.0)
			
# 			soya.DEFAULT_MATERIAL.activate()
# 			opengl.glColor4f(0.0, 1.0, 1.0, 1.0)
# 			opengl.glBegin(opengl.GL_QUADS)
# 			opengl.glVertex2i(0, 1000)
# 			opengl.glVertex2i(1000, 1000)
# 			opengl.glVertex2i(1000, 0)
# 			opengl.glVertex2i(0, 0)
# 			opengl.glEnd()
			
			self.widgets[0].render()

			opengl.glPopMatrix()
			opengl.glPopAttrib()
			opengl.glMatrixMode(opengl.GL_MODELVIEW)
			
			for widget in self.widgets[1:]:
				if widget: widget.render()
				
	def on_mouse_pressed(self, button, x, y):
		r = Table.on_mouse_pressed(self, button, x, y)
		if r: return r
		
		if self.vscroll.parent:
			if   button == 4: self.vscroll.set_value(self.vscroll.value - self.vscroll.step_size); return 1
			elif button == 5: self.vscroll.set_value(self.vscroll.value + self.vscroll.step_size); return 1
		

class ProgressBar(Widget):
	def __init__(self, parent = None, value = 0.0):
		self.value = value
		Widget.__init__(self, parent)
		self.extra_width = 1.0
		self.min_height  = self.ideal_height = int(STYLE.get_char_height())
		self.min_width   = int(3 * STYLE.get_char_height())
		self.ideal_width = int(5 * STYLE.get_char_height())

	def render(self):
		STYLE.rectangle(self.x, self.y, self.x + int(self.value * self.width), self.y + self.height)


class CameraViewport(Widget):
	def __init__(self, parent, camera = None):
		Widget.__init__(self, parent)
		self.camera = camera
		self.extra_width  = 1.0
		self.extra_height = 1.0
		self.ideal_width  = 320
		self.ideal_height = 200

	def set_camera(self, camera):
		self.camera = camera
		if self.camera: self.camera.resize(self.x, self.y, self.width, self.height)
		
	def allocate(self, x, y, width, height):
		Widget.allocate(self, x, y, width, height)
		if self.camera:
			self.camera.resize(self.x, self.y, self.width, self.height)
			
	def render(self):
		if self.camera:
			self.camera.render()
			
			
if __name__ == "__main__":
	soya.init(width = 640, height = 480)

	import soya.widget

	class Root(soya.widget.Widget):
		def __init__(self, widget):
			soya.widget.Widget.__init__(self)
			
			self.widget = widget
			self.widget.resize(0, 0, 640, 480)
			
		def render(self): self.widget.render()
		
	class MainLoop(soya.MainLoop):
		def __init__(self, *worlds):
			soya.MainLoop.__init__(self, *worlds)
			self.events = []
			
		def begin_round(self):
			soya.root_widget.widget.begin_round()
			self.events = soya.process_event()
			soya.root_widget.widget.process_event(self.events)
			soya.MainLoop.begin_round(self)
			
		def advance_time(self, proportion):
			soya.root_widget.widget.advance_time(proportion)
			soya.MainLoop.advance_time(self, proportion)
			
			
	
	black = soya.Material()
	black.diffuse = (0.0, 0.0, 0.0, 1.0)
	
	red = soya.Material()
	red.diffuse = (1.0, 0.0, 0.0, 1.0)
	
	blue = soya.Material()
	blue.diffuse = (0.0, 0.0, 1.0, 1.0)
	
	layer = Layer(None)
	backg = Image(layer, black)
	
# 	table = Table(layer, 2, 5)
	
# 	#l11 = Label(table, u"Jib")
# 	l11 = Layer(table)
# 	l11i = Image(l11, red)
# 	l11l = Label(l11, u"Jib g")
	
# 	#l12 = Label(table, u"20")
# 	l12 = Layer(table)
# 	l12i = Image(l12, blue)
# 	l12l = Label(l12, u"20")

# 	l21 = Label(table, u"Blamffffffffff")
# 	l22 = Layer(table)
# 	l22i = Image(l22, blue)
# 	l22c = CheckBox(l22, u"bla", 0)
	
# 	#l31 = Label(table, u"Marmoute")
# 	l31 = VScrollBar(table, 0.0, 3.0, 1.0, 1.0)
# 	#l32 = Label(table, "18")
# 	l32 = CheckBox(table, u"bla", 1)
	
# 	#l41 = VScrollBar(table, 0.0, 3.0, 1.0, 0.0)
# 	l41 = Button(table, u"Dac")
	
# 	l42  = ScrollPane(table)
# 	l42c = Label(l42, u"Un texte très long très long très long très long très long")
	
# 	l51 = Button(table, u"Dac")
	
# 	#l21.extra_width  = 1.0
	
# 	#l12l.extra_height = 1.0
# 	l21.extra_height = 1.0
# 	#l31.extra_height = 1.0
	
	window = Window(layer)
	wl = Label(window, u"Jiba X")
	
	window = Window(layer)
	sc  = ScrollPane(window)
	#Label(sc, u"Un texte très long très long très long très long très long !!!!")
	Text(sc, u"""Bla bla
Un texte très long très long
Un texte très long très long
Un texte très long très long
Un texte très long très long
Un texte très long très long  Un texte très long très long Un texte très long très long
UUn texte très long très long
Un texte très long très long
n texte très long très long

oezoe
poer,jvfpr
reprpvgeo,jvê
oidvjroi

Jiba""")

	
	window = Window(layer)
	table = Table(window, 2, 5)
	table.row_pad = 20
	Label(table, u"Fullscreen")
	CheckBox(table, u"bla bla", 1)
	Label(table, u"Quality")
	HScrollBar(table, 0, 9, 1, 1, 1)
	Label(table, u"Information")
	Text(ScrollPane(table), u"This is a small demo of a new widget module for the Soya 3D engine.\nIt features flying windows, scrolling panes, and the usual set of widgets :\n * Label\n * Image\n * Input\n * Button\n * CheckBox\n * ScrollBar\n * ...\nAnd it's only the third widget module for soya ;-)")
	Label(table, u"Name")
	Input(table, u"Jiba")
	#table.skip_case()
	CancelButton(table)
	ValidateButton(table)
	
	window = Window(layer, u"List demo")
	table = VTable(window, 2)
	table.row_pad = table.col_pad = 20
	
	Label(table, u"vertical list\nin a scroll pane")
	l = VList(ScrollPane(table))
	Label(l, u"Baby").extra_width = 1.0
	Label(l, u"Beginner")
	Label(l, u"Very easy")
	Label(l, u"Easy")
	Label(l, u"Hard gamer")
	Label(l, u"Nighmare")
	Label(l, u"Impossible")
	Label(l, u"God")
	Label(l, u"Jiba :-)")
	
	Label(table, u"vertical list\nwith 2 columns")
	l = VList(table, 2)
	ProgressBar(l, 0.2)
	Label(l, u"Beginner")
	ProgressBar(l, 0.5)
	Label(l, u"Hard gamer")
	ProgressBar(l, 0.8)
	Label(l, u"Nighmare")
	
	Label(table, u"horizontal list")
	l = HList(table)
	Label(l, u"Beginner")
	Label(l, u"Hard gamer")
	Label(l, u"Nighmare")
	
	window = Window(layer, u"Camera demo")
	scene = soya.World()
	#scene.atmosphere = soya.NoBackgroundAtmosphere()
	print scene.atmosphere
	scene.atmosphere = soya.Atmosphere()
	light = soya.Light(scene)
	light.set_xyz(0.5, 0.0, 2.0)
	camera = soya.Camera(scene)
	camera.z = 2.0
	camera.partial = 1
	import soya.cube
	cube = soya.cube.Cube(scene, red)
	cube.advance_time = lambda proportion: cube.rotate_lateral(proportion)
	CameraViewport(window, camera)
	
	
	root = Root(layer)
	soya.set_root_widget(root)
	
	MainLoop(scene).main_loop()
