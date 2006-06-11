# -*- indent-tabs-mode: t -*-

# Copyright 2006 Reto Spoerri

""" list controls for pudding """

__revision__ = '$Revision: 0.1 $'

import soya

import soya.pudding as pudding
import soya.pudding.core
import soya.pudding.control
import soya.pudding.container

class HighlightText( soya.pudding.control.Label ):
	def __init__( self, parent, text ):
		soya.pudding.control.Label.__init__( self, parent, text )

	def highlight( self, enabled ):
		if enabled:
			self.color = ( 1.00, 1.00, 1.00, 1.00 )
		else:
			self.color = ( 0.5, 0.5, 0.5, 1.00 )

def limit( number, maxSize, minSize ):
	return max( minSize, min( maxSize, number ) )

class ListBox( pudding.core.Control, pudding.core.InputControl):
	""" Simple List.

	Value may be set with mouse scroll wheel or by clicking in the list.
	If the top object is selected the list is scrolled up,
	selecting the last object in the list scrolls it down.
	"""

	def __get_value__(self):
		return self._value

	def __set_value__(self, val):
		self._value = val

		if self.value < self.min: 
			self.value = self. min
		elif self.value > self.max:
			self.value = self.max 

		self.on_set_value()

	value = property(__get_value__, __set_value__)

	def __init__(self, parent, object_list, max_objects = 0, width = 0, height = 0, font = None, **kwargs):
		''' create a list of strings, max_objects define number of lines in the list to show strings
		the object_list is a list of strings to be shown in the list, to be mouse-wheel selectable
		the width and size has to be defined on init
		'''

		font = font or soya.pudding.STYLE.default_font
		self.text_height = font.get_print_size('X')[1]
		self.max_objects = max_objects or len(object_list)
		height = height or (self.text_height * self.max_objects + 10)
		width  = width  or (max([font.get_print_size(i)[0] for i in object_list]) + 3)
		
		pudding.core.Control.__init__(self, parent, width = width, height = height, **kwargs)
		pudding.core.InputControl.__init__(self)
		
		
		self.container_box = soya.pudding.control.Box( parent, height=height, width=width )
		self.container_box.z_index = -1
		self.container = soya.pudding.container.VerticalContainer( parent, height=height, width=width )
		self.object_list = object_list

		self.list_text = list()
		for i in xrange( self.max_objects ):
			self.list_text.append( HighlightText( self.container, "" ) )
			self.list_text[-1].font = font

		self.start_object = 0
		self.active_object = 0

		self.update()

	def update( self ):
		# update visible list on screen
		i = self.start_object
		for c in self.list_text:
			if i < len(self.object_list):
				c.visible = True
				c.label = self.object_list[i]
				if i == self.active_object:
					c.highlight( True )
				else:
					c.highlight( False )
				i += 1
			else:
				c.visible = False
				c.label = ''

	def on_mouse_down(self, x, y, button):
		if button == 4:
			# scoll button up
			self.active_object -= 1
			if self.active_object < 0:
				self.active_object = 0
		elif button == 5:
			# scroll button down
			self.active_object += 1
		elif button == 1:
			# select with mouse
			obj = int((y/self.text_height) + self.start_object)
			self.active_object = obj

		# active object max not be bigger then amout of objects and smaller then 0
		self.active_object = limit( self.active_object, len( self.object_list ) - 1, 0 )
		# move visible part of list depending on active Object
		self.start_object = limit( self.start_object, self.active_object - 1, self.active_object - ( self.max_objects - 2 ) )
		# limit start_object from 0 to length of strings - showedStrings
		self.start_object = limit( self.start_object, len( self.object_list ) - self.max_objects, 0 )
		# bugfix for list length 1
		if self.max_objects == 1:
			self.start_object = self.active_object
		self.update()

		return True

	def get_selected_item_number( self ):
		return self.active_object

	def get_selected_item_name( self ):
		return self.object_list[ self.active_object ]

	def clear_all_items( self ):
		self.object_list = []

	def add_item( self, itemName ):
		self.object_list.append( itemName )
		self.update()

	def remove_item( self, itemName ):
		self.object_list.remove( itemName )
		self.update()

	def set_list_lenght( self, length ):
		self.max_objects = length

	def process_event(self, event):
		return pudding.core.InputControl.process_event(self, event)

	def on_set_value(self):
		pass

