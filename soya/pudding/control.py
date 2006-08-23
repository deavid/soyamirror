# -*- indent-tabs-mode: t -*-

""" most basic widget for pudding """

__revision__ = '$Revision: 1.2 $'

__doc_classes__ = [ 'SimpleLabel', 
										'Label', 
										'PrePostLabel', 
										'Input', 
										'Panel', 
										'Button', 
										'Console', 
										'Image',
										'Logo',
										]

__doc_functions__ = []

import string

from soya.pudding           import ConstantError, EXPAND_BOTH, EXPAND_HORIZ, ANCHOR_ALL, ANCHOR_RIGHT, ANCHOR_BOTTOM, CLIP_NONE, CLIP_LEFT, CLIP_RIGHT
from soya.pudding.core      import Base, Control, TestControl, InputControl, _TestInputControl, TestContainer
from soya.pudding.container import VerticalContainer
from soya.pudding.core      import LateBindingProperty

import soya
from soya.opengl import *
from soya import sdlconst as sdl


class Box(Control, InputControl):
	""" A simple graphical box that responds to user events, usefull for 
	and descending other controls"""

	def __get_background_color__(self):
		return self._background_color

	def __set_background_color__(self, color):
		self._background_color = color
	
	def __get_border_color__(self):
		return self._border_color

	def __set_border_color__(self, color):
		self._border_color = color

	def __get_border_width__(self):
		return self._border_width

	def __set_border_width__(self, width):
		self._border_width = width

	background_color  = LateBindingProperty('__get_background_color__', 
															'__set_background_color__', 
															doc = "background color of the box")

	border_color      = LateBindingProperty('__get_border_color__',
															'__set_border_color__', 
															doc = "border color of the box")

	border_width      = LateBindingProperty('__get_border_width__', 
															'__set_border_width__', 
															doc = "border width")

	def __init__(self, parent=None, **kwargs):
		self._background_color = None
		self._border_color = None
		self._border_width = None

		Control.__init__(self, parent, **kwargs)
		InputControl.__init__(self)

	def process_event(self, event):
		""" use the InputControl class to process events """
		return InputControl.process_event(self, event)

	def render_self(self):
		""" render the box with current settings """

		soya.pudding.STYLE.draw_bordered_box(self.width, self.height, 
				background = self.background_color, border = self.border_color, 
				border_width = self.border_width)


class TestBox(TestControl, _TestInputControl):
	klass = Box


class SimpleLabel(Control):
	""" A simple, unresponsive label widget """
	MAXLEN = 2000

	def __get_label__(self):
		return self._text

	def __set_label__(self, label):
		self._text = label
		self.update()

		self.on_set_label()

	def __get_font__(self):
		return self._font

	def __set_font__(self, font):
		self._font = font
	
	def __get_color__(self):
		return self._color

	def __set_color__(self, color):
		self._color = color

	def __get_autosize__(self):
		return self._autosize

	def __set_autosize__(self, autosize):
		if autosize:
			self._autosize = True
		else:
			self._autosize = False

	def __get_clip__(self):
		return self._clip

	def __set_clip__(self, clip):
		if clip not in [CLIP_LEFT, CLIP_RIGHT]:
			raise ConstantError(
										'clip must be soya.pudding.CLIP_LEFT or soya.pudding.CLIP_RIGHT')

		self._clip = clip

	def __get_wrap__(self):
		return self._wrap

	def __set_wrap__(self, wrap):
		self._wrap = wrap

	color = LateBindingProperty('__get_color__', 
															'__set_color__', 
															doc = "color of the text")

	label = LateBindingProperty('__get_label__', 
															'__set_label__', 
															doc = "text displayed")
	
	font =  LateBindingProperty('__get_font__', 
															'__set_font__' , 
															doc = "font used for rendering")
	 
	autosize = LateBindingProperty( '__get_autosize__', 
																	'__set_autosize__',
												doc = """should the label automatically adjust its size 
														to accomodate all the text""")

	clip =  LateBindingProperty('__get_clip__', 
															'__set_clip__', 
												doc = """if there is too much text do we clip the left 
												or right. must be soya.pudding.core.[soya.pudding.CLIP_LEFT | 
												soya.pudding.CLIP_RIGHT]""")

	wrap = LateBindingProperty('__get_wrap__', '__set_wrap__')
		
	## end of properties
	
	def __init__(self, parent=None, label='', **kwargs):
		self._autosize = kwargs.get('autosize', True)
		self._wrap = False
		self._color = (1., 1., 1., 1.)
		self._font = soya.pudding.STYLE.default_font
		self._clip = CLIP_LEFT
		
		Control.__init__(self, parent, **kwargs)

		self.display_list = glGenLists(1)
		
		self._text = label
		self._display_text = ''

		self.update()

	def render_self(self):
		""" draw the text with the current settings """

		soya.DEFAULT_MATERIAL.activate()
		glColor4f(*self._color)
		glDisable(GL_CULL_FACE)

		if self.needs_update:
			self._font.create_glyphs(self._display_text)

			glNewList(self.display_list, GL_COMPILE_AND_EXECUTE)

			self._font.draw(self._display_text, 0., 0., 0.)

			glEndList()

			self.needs_update = False
		else:
			glCallList(self.display_list)

		glDisable(GL_CULL_FACE)

	def set_display_text(self, text):
		""" get the text we should actually display. usefull if you want to add a
		constant string or perform some processing before the string gets 
		wrapped or clipped or whatever """

		self._display_text = text

	def update(self):
		""" refresh settings based on clip and autoresize etc """

		if len(self._text) > SimpleLabel.MAXLEN:
			self._text = self._text[-SimpleLabel.MAXLEN:]
		
		self.needs_update = True
		
		self.set_display_text( self._text )

		if self._wrap:
			max_width, height, self._display_text = \
						self._font.wordwrap(self._display_text, self._width)

			if self._autosize:
				self.height = height

			self.text_width = max_width
			self.text_height = min(self.height, height)

			if height > self.height:
				lines_to_many = (height - self._height) / self._font.height
				self._display_text = "\n".join( 
										self._display_text.split('\n')[int(lines_to_many):]
										)
 
		elif self._autosize:
			self._width, self._height = \
						self._font.get_print_size(self._display_text)

			self.text_width, self.text_height = self._width, self._height
 
		elif self._clip != CLIP_NONE:
			width, height = self._font.get_print_size(self._display_text)
 
			while width > self.width:
				if self._clip == CLIP_LEFT:
					self._display_text = self._display_text[1:]
				else:
					self._display_text = self._display_text[:-1]
 
				width, height = self._font.get_print_size(self._display_text)
 
			self.text_width, self.text_height = width, height
	 
	def on_resize(self):
		""" update position with anchoring and apply wrapping/clipping """
		self.do_anchoring()
		self.update()
	
	def on_set_label(self):
		""" event triggered when the label is changed """
		pass

class TestSimpleLabel(TestControl):
	klass = SimpleLabel

	def testSetLabel(self):
		""" testing setting label """
		self.getControl().label = 'something'


class Label(SimpleLabel, InputControl):
	""" Label with events. Created using SimpleLabel and InputControl with 
	multiple inheritance """

	def __init__(self, parent=None, label='', **kwargs):

		SimpleLabel.__init__(self, parent, label, **kwargs)

		InputControl.__init__(self)

	def process_event(self, event):
		""" let InputControl class deal with events """
		return InputControl.process_event(self, event)

class TestLabel(TestSimpleLabel, _TestInputControl):
	klass = Label


class PrePostLabel(SimpleLabel):
	""" A label with static pre/post -fix """

	def __get_pre__(self):
		return self._pre

	def __set_pre__(self, pre):
		self._pre = pre
		self.update()

	def __get_post__(self):
		return self._post

	def __set_post__(self, post):
		self._post = post
		self.update()

	pre   = LateBindingProperty('__get_pre__'  , '__set_pre__')
	post  = LateBindingProperty('__get_post__' , '__set_post__')

	def __init__(self, parent=None, label='', pre='', post='', **kwargs):

		self._pre = pre
		self._post = post

		SimpleLabel.__init__(self, parent, label, **kwargs)

	def set_display_text(self, text):
		""" set the display text with the pre and post strings """
		self._display_text = "%s%s%s" % (self._pre, text, self._post)

class TestPrePostLabel(TestSimpleLabel):
	klass = Label

	def testSetPre(self):
		""" testing setting pre """
		self.getControl().pre = 'something'

	def testSetPost(self):
		""" testing setting post """
		self.getControl().post = 'something'


class Button(Box):
	""" A simple button widget. The label is a child SimpleLabel widget.
	Note the on_click method provided"""

	def __get_label__(self):
		return self.label_control.label

	def __set_label__(self, val):
		self.label_control.label = val

	label = LateBindingProperty('__get_label__', 
															'__set_label__', 
															doc = "label on the button")

	def __init__(self, parent=None, label='button', width=None, height=None,
							 **kwargs):

		self.label_control = SimpleLabel(label=label, autosize = True)

		if width is None:
			width = self.label_control.width + (self.label_control.font.width * 2)

		if height is None:
			height = self.label_control.height + (self.label_control.font.height / 2)
			
		Box.__init__(self, parent, width=width, height=height, **kwargs)

		self.child = self.label_control

	def __repr__(self):
		return "<Button label = %s>" % self.label

	def render_self(self):
		""" render the box with current settings """

		soya.pudding.STYLE.draw_button(self.width, self.height, 
				background = self.background_color, border = self.border_color, 
				border_width = self.border_width)

	def on_resize(self):
		""" use the resize event to move and resize the buttons child label """

		# put the label in the center of oursleves
		self.label_control.update()

		self.label_control.left = \
								(self._width / 2) - (self.label_control.width / 2)
		self.label_control.top  = \
								(self._height / 2) - (self.label_control.font.height / 2)

	def on_mouse_up(self, x, y, button):
		""" use the mouse up event handler to implement the on_click handler """
		if button == 1:
			self.on_click()
			return True

		return False

	def on_click(self):
		""" event triggered when the button is "clicked" either by the mouse or the 
		keyboard """
		
		print "unhandled click %s" % self


class TestButton(TestBox):
	klass = Button

	def testSetLabel(self):
		""" testing setting label """
		self.getControl().label = "something"

	def testOnClick(self):
		""" testing on_click """
		self.getControl().on_click()


class Input(Box):
	""" Simple input box using a child SimpleLabel widget. 
	Note the on_value_changed method """

	def __get_value__(self):
		return self.label.label

	def __set_value__(self, val):
		self.label.label = val

	def __get_cursor__(self):
		return self._cursor

	def __set_cursor__(self, cursor):
		self._cursor = cursor

	def __get_prompt__(self):
		return self.label.pre

	def __set_prompt__(self, prompt):
		self.label.pre = prompt
		
	value = LateBindingProperty('__get_value__', '__set_value__', 
									doc = "the text in the input box")

	cursor = LateBindingProperty('__get_cursor__, __set_cursor__',
									doc = "text used as a cursor. defaults to '_'")

	prompt = LateBindingProperty('__get_prompt__', '__set_prompt__',
									doc = "static text used as a prompt")

	def __init__(self, parent=None, initial='', **kwargs):

		Box.__init__(self, parent, **kwargs)

		# we want a cropped label not a free sized one 
		self.label = PrePostLabel(self, label = initial, post = '',
															autosize = False)

		# make use of anchors to put the input always 2 px away from the edge
		self.label.left = 8
		self.label.top = 2
		self.label.right = 8
		self.label.bottom = 2
		
		self.label.anchors = ANCHOR_ALL

		self._cursor = '_'

	def set_height_to_font(self):
		""" set the height of the input control to the height of the font """

		# why plus 10? urm...
		# the height doest seem to be correct somewhere
		# so this bodge to get it centered
		self.height = self.label.font.height+10

	def clear(self):
		""" clear the value of the input """
		self.value = ''

	def on_key_down(self, key, mods):
		""" process and key strokes and add them to the current value """

		if key == sdl.K_RETURN:
			self.on_return()
		elif key == sdl.K_BACKSPACE:
			self.value = self.value[:-1]
			self.on_value_changed()
		elif key != 0:
			if chr(key) in string.printable:
				self.value += chr(key)
				self.on_value_changed()

		return True

	def on_resize(self):
		""" set the position and size of our child label """

		# put the label in the center of oursleves

		self.label.on_resize()

		self.label.top = (self.height / 2) - (self.label.height / 2)

	def on_focus(self):
		""" append the cursor sybol when focus is gained """
		self.label.post = self._cursor
		self.label.update()

	def on_loose_focus(self):
		""" remove the cursor symbol when the focus is lost """
		self.label.post = ''
		self.label.update()

	def on_value_changed(self):
		""" event triggered when the value is changed by the user """
		pass

	def on_return(self):
		""" event triggered when the return key is pressed """
		pass

class TestInput(TestBox):
	klass = Input

	def testSetValue(self):
		""" testing setting value """
		self.getControl().value = 'something'

	def testSetPrompt(self):
		""" testing setting prompt """
		self.getControl().prompt = 'something'


class Console(VerticalContainer, InputControl):
	""" A simple console style widget """
	def __init__(self, parent=None, initial='', **kwargs):
							
		VerticalContainer.__init__(self, parent, **kwargs)
		InputControl.__init__(self)

		self.output = self.add_child(
										SimpleLabel(label = initial, autosize = False), 
										EXPAND_BOTH)

		self.output.wrap = True

		self.input  = self.add_child( Input(), EXPAND_HORIZ)

		self.input.on_return = self.on_return

		self.input.set_height_to_font()

		self.input_buffer = []
		self.input_buffer_pos = -1
		self.input_buffer_orig = ''

	def process_event(self, event):
		return InputControl.process_event(self, event)

	def on_key_down(self, key, mods):
		""" allow scrolling thru the buffer and do some other 
		mangling so that the whole window receives events"""

		if self.input_buffer and key == sdl.K_UP:
			if self.input_buffer_pos == -1:
				self.input_buffer_orig = self.input.value
			
			self.input_buffer_pos += 1      

			if self.input_buffer_pos >= len(self.input_buffer):
				self.input_buffer_pos = len(self.input_buffer) - 1
				
			self.input.value = self.input_buffer[self.input_buffer_pos]
		
		elif self.input_buffer and key == sdl.K_DOWN:
			self.input_buffer_pos -= 1 
			
			if self.input_buffer_pos < -1:
				self.input_buffer_pos = -1
			elif self.input_buffer_pos == -1:
				self.input.value = self.input_buffer_orig
			else:
				self.input.value = self.input_buffer[self.input_buffer_pos]
		
		elif key == sdl.K_RETURN:
			self.on_return()
		
		elif key < 256:
			self.input.on_key_down(key, mods)

		return True

	def on_resize(self):
		""" update child controls """
		VerticalContainer.on_resize(self)
		
		self.output.update()
		
		self.input.label.update()

	def on_return(self):
		""" send all input to the output and clear the input ready for more """
		value = self.input.value

		self.input_buffer.append( value )

		self.input.clear()

		self.output.label += "%s\n" % value

		return True

	#def process_event(self, event):
	#  """ all events should go straight to our input control """
	#
	#  ret = self.input.process_event(event)
	#  return ret

	def on_focus(self):
		""" automatically give focus to the input when the console gets focus"""
		self.input.focus = True

	def on_loose_focus(self):
		""" automatically give focus to the input when the console gets focus"""
		self.input.focus = False

class TestConsole(TestContainer):
	klass = Console


class Panel(Box):
	""" A simple window/panel control with a title. modify the style
	class to change the way this is draw """

	def __get_label__(self):
		return self._label

	def __set_label__(self, label):
		self._label = label

	label = LateBindingProperty('__get_label__', '__set_label__')
		
	def __init__(self, parent = None, label = '', **kwargs):

		Box.__init__(self, parent, **kwargs)
	
		self._label = label

	def render_self(self):
		""" render the box with current settings """

		soya.pudding.STYLE.draw_panel(self.width, self.height, 
					background = self.background_color, border = self.border_color, 
					border_width = self.border_width, label = self._label)

	def process_event(self, event):
		""" default event handling """
		return Base.process_event(self, event)

class TestPanel(TestBox):
	klass = Panel


class Image(Control):
	""" A simple image control """

	def __get_material__(self):
		return self._material

	def __set_material__(self, material):
		self._material = material
		self._modified = 1

	def __set_rotation__(self, rot):
		self._rotation = rot
		self._modified = 1

	def __get_rotation__(self):
		return self._rotation

	def __get_shade__(self):
		return self._shade

	def __set_shade__(self, shade):
		self._shade = shade
		self._modified = 1

	material = LateBindingProperty('__get_material__', '__set_material__')
	rotation = LateBindingProperty('__get_rotation__', '__set_rotation__')
	shade = LateBindingProperty('__get_shade__', '__set_shade__')
	
	def __init__(self, parent=None, material=None, **kwargs):

		self._material = material

		self._tex_top = 0.
		self._tex_left = 0.
		self._tex_right = 1.
		self._tex_bottom = 1.

		self._rotation = 0.
		self._shade = None

		self._display_list = glGenLists(1)
		self._modified = 1

		Control.__init__(self, parent, **kwargs)

	def render_self(self):
		""" render the image to screen """
		
		if self._modified:
			glNewList(self._display_list, GL_COMPILE_AND_EXECUTE)

			if self.material:
				try:
					self._material.activate()
				except AttributeError, inst:
					print "Cant activate material for %s: %s" % (self, inst)
					return 
			else:
				soya.DEFAULT_MATERIAL.activate()

			glPushMatrix()
					 
			half_width = self._width  / 2
			half_height = self._height / 2

			glTranslatef(float(half_width), float(half_height), 0.0)
			if self._rotation: 
				glRotatef(self._rotation, 0.0, 0.0, 1.0)

			glEnable(GL_BLEND)

			glBegin     (GL_QUADS)
			if self._shade:
				glColor4f(*self._shade)
			glTexCoord2f(self._tex_left, self._tex_top)
			glVertex2i  (-half_width, -half_height)
			glTexCoord2f(self._tex_left, self._tex_bottom)
			glVertex2i  (-half_width, -half_height + self.height)
			glTexCoord2f(self._tex_right, self._tex_bottom)
			glVertex2i  (-half_width + self._width, -half_height + self._height)
			glTexCoord2f(self._tex_right, self._tex_top)
			glVertex2i  (-half_width + self._width, -half_height)
			glEnd()
			soya.DEFAULT_MATERIAL.activate()
			glPopMatrix()

			glDisable(GL_BLEND)

			glEndList()
			
			self._modified = 0
		else:
			glCallList(self._display_list)

class TestImage(TestControl):
	klass = Image


class Logo(Image):
	""" Class to display an image in the bottom right corner, usefull for logo's """

	def __init__(self, parent=None, logo_file=None, **kwargs):
		Image.__init__(self, parent, **kwargs)
		
		if logo_file:
			img = soya.Image.get(logo_file)
			self.material = soya.Material(img)
			self.width = img.width
			self.height = img.height
			
		self.set_pos_bottom_right(10, 10)
		
		self.anchors = ANCHOR_RIGHT | ANCHOR_BOTTOM
		
class TestLogo(TestImage):
	klass = Logo

	def getControl(self):
		return self.klass(self.parent())
	
	def test1Create(self):
		pass
		
