# -*- indent-tabs-mode: t -*-

""" 
Core objects for \module{soya.pudding}

"""

__revision__ = '$Revision: 1.1 $'

__doc_classes__ = ['Base', 'Control', 'InputControl', 'RootWidget']
__doc_functions__ = []

import soya
from soya.opengl import *
import soya.sdlconst as sdl

import traceback

import unittest

import sys

#import soya.pudding as pudding
from soya.pudding import PuddingError, ANCHOR_LEFT, ANCHOR_TOP, ANCHOR_RIGHT, ANCHOR_BOTTOM

if sys.version_info < (2,4):
	def sorted(iterable, cmp=None, key=None, reverse=False):
		"return a sorted copy of its input"
		seq = list(iterable)
		if reverse:
				seq.reverse()        # preserve stability
		if key is not None:
				seq = [(key(elem), i, elem) for i, elem in enumerate(seq)]
		seq.sort(cmp)
		if key is not None:
				seq = [elem for (key, i, elem) in seq]
		if reverse:
				seq.reverse()
		return seq


class LateBindingProperty(object):
	""" http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/408713 """

	def __init__(self, getname=None, setname=None, delname=None,
							 doc=None):
		self.getname = getname
		self.setname = setname
		self.delname = delname
		self.__doc__ = doc

	def __get__(self, obj, default = None):
		if obj is None:
			return self
		if self.getname is None:
			raise AttributeError('unreadable attribute')
		try:
			fget = getattr(obj, self.getname)
		except TypeError:
			raise TypeError("you have passed %s instead of a string" % self.getname)
		except AttributeError:
			raise TypeError('%s object does not have a %s method' %
												(type(obj).__name__, self.getname))
		return fget()

	def __set__(self, obj, value):
		if self.setname is None:
			raise AttributeError("can't set attribute")
		try:
			fset = getattr(obj, self.setname)
		except AttributeError:
			raise TypeError('%s object does not have a %s method' %
												(type(obj).__name__, self.setname))
		fset(value)

	def __delete__(self, obj):
		if self.delname is None:
			raise AttributeError("can't delete attribute")
		try:
			fdel = getattr(obj, self.delname)
		except AttributeError:
			raise TypeError('%s object does not have a %s method' %
												(type(obj).__name__, self.delname))
		fdel()


class Base(object):
	""" The base class for all widgets. Note a Base control doesnt render 
	anything to the screen or it does it in a fashion where position and size 
	are not relevant. For graphical controls subclass \class{soya.pudding.Control}
	instead 
	"""

	def __get_child__(self):
		return self._child

	def __set_child__(self, child):
		if child == self:
			raise AttributeError('child cannot be self!')
			
		self._child = child
		if self._child.parent != self:
			self._child.parent = self

		self.on_set_child(child)
	
	def __get_parent__(self):
		return self._parent

	def __set_parent__(self, parent):
		if parent != None and not issubclass(parent.__class__, Base):
			raise PuddingError('parent is not a subclass of soya.pudding.Base!')
			
		self._parent = parent

	child     = LateBindingProperty('__get_child__', '__set_child__', 
											doc = "child object")
	parent    = LateBindingProperty('__get_parent__', '__set_parent__', 
											doc = "parent object")
	
	def __init__(self, parent=None, **kwargs):
		self._parent = parent
		
		self._child = None

		if self.parent:
			if issubclass( self.parent.__class__, Container):
				self.parent.add_child(self)
			else:
				self.parent.child = self

		for arg,value in kwargs.iteritems():
			if hasattr(self, arg):
				setattr(self, arg, value)
			else:
				raise AttributeError('%s has no attribute %s, ejector seat triggered'
														 % (self, arg))

		self.on_init()
	
	def process_event(self, event):
		""" process one event. returning False means that the event has not been
		handled and should be passed on to other widgets. returning True means
		that the event has been handled and the event should no longer be 
		propogated """

		if self._child: 
			return self._child.process_event(event)

		return False

	def begin_round(self):
		""" soya begin_round event """
		if self.child:
			self.child.begin_round()

	def advance_time(self, proportion):
		""" soya advance_time event """
		if self.child:
			self.child.advance_time(proportion)

	def end_round(self):
		""" soya.end_round event """
		if self.child:
			self.child.end_round()

	def on_init(self):
		""" event occurs at the end of initialisation for user processing """
		pass

	def on_set_child(self, child):
		""" event triggered when the child attribute is set """
		pass


class TestBase(unittest.TestCase):
	""" tes class for base """
	klass = Base

	def setUp(self):
		self.parent = Base

	# we use test1Create to force this test to run first
	def test1Create(self):
		""" testing creation """
		base = self.klass()

	def testChild(self):
		""" testing as child """
		base = self.parent()
		child = self.klass(base)

	def testBeginRound(self):
		""" testing begin round function """
		self.klass().begin_round()

	def testEndRound(self):
		""" testing end round function """
		self.klass().end_round()

	def testAdvanceTime(self):
		""" testing advance_time function """
		self.klass().advance_time(0.1)

class Control(Base):
	""" The main graphical base class for all widgets."""

	def __get_left__(self):
		return self._left

	def __set_left__(self, left):
		self._left = left

	def __get_top__(self):
		return self._top

	def __set_top__(self, top):
		self._top = top

	def __get_width__(self):
		return self._width

	def __set_width__(self, width):
		self._width = width

	def __get_height__(self):
		return self._height

	def __set_height__(self, height):
		self._height = height
	
	def __get_right__(self):
		return self.parent.width - self._left - self._width

	# not sure which imlpementation is correct..
	#def __set_right__(self, val):
	#  self._left = self.parent.width - self._width - val

	def __set_right__(self, val):
		self._width = self.parent.width - self._left - val

	def __get_bottom__(self):
		return self.parent.height - self._top - self._height

	# not sure which imlpementation is correct..
	#def __set_bottom__(self, val):
	#  self._top = self.parent.height - self._width - val

	def __set_bottom__(self, val):
		self._height = self.parent.height - self._top - val

	def __get_screen_left__(self):
		return self._screen_left

	def __get_screen_top__(self):
		return self._screen_top

	def __get_screen_right__(self):
		return self._screen_left + self._width

	def __get_screen_bottom__(self):
		return self._screen_top + self._height

	def __get_visible__(self):
		return self._visible

	def __set_visible__(self, visible):
		if visible:
			self._visible = True
			self.on_show()
		else:
			self._visible = False
			self.on_hide()

	def __get_anchors__(self):
		return self._anchors

	def __set_anchors__(self, anchors):
		self._anchors = anchors

		self._anchor_left = self._left
		self._anchor_right = self.right
		self._anchor_top = self._top
		self._anchor_bottom = self.bottom


	left = LateBindingProperty('__get_left__', '__set_left__',
									doc = """distance from the left edge of 
									the screen to the left edge of the control""")
									
	top = LateBindingProperty('__get_top__', '__set_top__',
									doc = """distrance from the top edge of 
									the screen to the top edge of the control""")
									
	right = LateBindingProperty('__get_right__', '__set_right__', 
									doc = """distance from the right edge of 
									the screen to the right edge of the control""")
									
	bottom = LateBindingProperty('__get_bottom__', '__set_bottom__',
									doc = """distance from the bottom edge of 
									the screen to the bottom edge of the control""")

	width = LateBindingProperty('__get_width__', '__set_width__',
									doc = "width of the control")

	height = LateBindingProperty('__get_height__', '__set_height__',
									doc = "height of the control")

	screen_left   = LateBindingProperty('__get_screen_left__')
	screen_top    = LateBindingProperty('__get_screen_top__')
	screen_right  = LateBindingProperty('__get_screen_right__')
	screen_bottom = LateBindingProperty('__get_screen_bottom__')

	visible = LateBindingProperty('__get_visible__', '__set_visible__', 
									doc = "is the object visible")

	anchors = LateBindingProperty('__get_anchors__', '__set_anchors__')
 
	####### end of properties
	
	def __init__(self, parent=None, left=0, top=0, width=0, height=0, **kwargs):
		self._width = width
		self._height = height

		self._left = left
		self._top = top

		self._anchor_left = 0
		self._anchor_top = 0
		self._anchor_right = 0
		self._anchor_bottom = 0

		self._screen_left = left
		self._screen_top = top

		self._visible = True
		self._needs_update = True

		self._anchors = 0

		self.z_index = 0
	
		Base.__init__(self, parent, **kwargs)

	def process_event(self, event):
		""" process one event. returning False means that the event has not been
		handled and should be passed on to other widgets. returning True means
		that the event has been handled and the event should no longer be 
		propogated. """
		
		if not self._visible:
			return False

		if self._child: 
			return self._child.process_event(event)

		return False

	def start_render(self):
		""" sets up opengl state"""
		glPushMatrix()

		self._screen_left = self.left + self.parent._screen_left
		self._screen_top = self.top + self.parent._screen_top

		glTranslatef( self.left, self.top, 0.)

	def end_render(self):
		""" shuts down opengl state"""
		glPopMatrix()

	def render_self(self):
		""" renders the current object. ie dont render the children, render self """
		pass

	def render(self):
		""" render the whole object. setup and take down opengl, render self and 
		render all children """

		if self._visible:
			self.start_render()
			self.render_self()
			if self.child:
				self.child.render()
			self.end_render()

	def resize(self, left, top, width, height):
		""" set the position and size of the control """

		self._left = left
		self._top = top
		self._width = width
		self._height = height

		self.on_resize()

	def do_anchoring(self):
		""" move the control based on anchor flags """

		if self._anchors & ANCHOR_LEFT:
			self._left = self._anchor_left
		
		if self._anchors & ANCHOR_TOP:
			self._top = self._anchor_top

		if self._anchors & ANCHOR_RIGHT:
			if self._anchors & ANCHOR_LEFT:
				self.right = self._anchor_right
			else:
				self._left = self.parent.width - self._width - self._anchor_right

		if self._anchors & ANCHOR_BOTTOM:
			if self._anchors & ANCHOR_TOP:
				self.bottom = self._anchor_bottom
			else:
				self._top = self.parent.height - self._height - self._anchor_bottom

	def set_pos_bottom_right(self, right = None, bottom = None):
		""" whereas using .right and .bottom effect the width and height of the 
		control this will effect the left and the top """

		if right != None:
			self._left = self.parent.width - self._width - right

		if bottom != None:
			self._top = self.parent.height - self._height - bottom
	 
	def on_resize(self):
		""" event when the control is resized """

		self.do_anchoring()
	 
		if self.child:
			self.child.on_resize()

	def on_show(self):
		""" event when the control is made visible """
		pass

	def on_hide(self):
		""" event when the control is made invisible """
		pass


class TestControl(TestBase):
	""" test class for control """
	klass = Control

	def setUp(self):
		TestBase.setUp(self)

		self.parent = RootWidget

	def getControl(self):
		try:
			return self.klass(self.parent(), left = 10, top = 10, width = 100, height = 100)
		except TypeError, inst:
			raise TypeError('%s.__init__ got unexpected keyword argument %s' %
												(self.klass.__name__, inst)) 

	def testEvent(self):
		""" testing sending event """
		self.getControl().process_event([sdl.MOUSEMOTION, 0, 0, 0, 0]), True

	def testRender(self):
		""" testing calling render """
		self.getControl().render()

	def testOnResize(self):
		""" testing calling on_resize """
		self.getControl().on_resize()

	def testOnShow(self):
		""" testing calling on_show """
		self.getControl().on_show()

	def testOnHide(self):
		""" testing calling on_hide """
		self.getControl().on_hide()

	def testLTWHAttr(self):
		""" testing setting left/top/width/height """
		self.left = 10
		self.top = 10
		self.width = 10
		self.height = 10
		
	def testBeginRound(self):
		""" testing calling begin_round """
		self.getControl().begin_round()

	def testEndRound(self):
		""" testing calling end_round """
		self.getControl().end_round()

	def testAdvanceTime(self):
		""" testing calling advance_time """
		self.getControl().advance_time(0.1)


class Container(Control):
	""" Base class for child containers. Some child containers can handle clever
	resizing ( see soya.pudding.container ).
	
	The child attribute for containers is not used. 
	"""

	def __get_children__(self):
		return self._children

	def __set_children__(self, children):
		self._children = children

	def __get_padding__(self):
		return self._padding
	
	def __set_padding__(self, padding):
		self._padding = padding
	
	children  = LateBindingProperty('__get_children__', 
																	'__set_children__', 
																	doc = "children of the container")
	padding   = LateBindingProperty('__get_padding__', 
																	'__set_padding__', 
																	doc = "padding around child widgets")
	
	def __init__(self, parent=None, **kwargs):
		self._children = []
		self._padding = 0

		Control.__init__(self, parent, **kwargs)

	def apply(self, function, *args):
		""" utility function to call the same function for all children 
		with the same arguments """

		for child in self.children:
			getattr(child, function)(*args)

	def render_self(self):
		""" calls the render function of all children """

		# uncomment this to see where the sizers are really going
		#pudding.STYLE.draw_bordered_box(self.width, self.height, 
		#    background = (1.0, 0., 0., 1. ), border = (1.0,1.,1.,1.))

		for child in sorted(self.children, key=lambda child: child.z_index):
			child.render()

	def add_child(self, child, flags = 0):
		""" add a child to the container. The childs parent attribute will be 
		updated.
		control as it wants. valid flags are in soya.pudding.__init__.py. 

		"""

		"""
		examples:
		
		\\begin{verbatim}
			# create a label that is allowed to resize with the container
			my_container.add_child( soya.pudding.control.Label(None, 'some text'), 
															soya.pudding.EXPAND_BOTH)

			# create a label that is allowed to resize with the container but 
			# only horizontally
			my_container.add_child( soya.pudding.control.Label(None, 'some text'), 
															soya.pudding.EXPAND_HORIZ)

			# create a button that is not allowed to resize but sits in the middle 
			# of its space
			my_container.add_child( soya.pudding.control.Button(None, 'some text', 
																							width = 50, height = 20), 
															soya.pudding.CENTER_BOTH)

		\\end{verbatim}
		"""
			

		self.children.append(child)
		
		# add a property to the child for storing flags 
		# i get the feeling this is evil but the only other thing i can think to do 
		# is to create another list off container to store the child flags 
		child._container_flags = flags
		
		child.parent = self

		return child

	def get_child_index(self, child):
		""" return the index of child in children """
		for index, test_child in enumerate(self.children):
			if test_child == child:
				return index
		
	def get_child_options(self, child):
		""" get options set for the child """
		index = self.get_child_index(child)

		return self.children[index]._container_flags

	def set_child_options(self, child, flags = 0):
		""" set options for the child """

		index = self.get_child_index(child)

		self._children[index]._container_flags = flags

	def process_event(self, event):
		""" try passing the event to all children. 
		Returns True if one of the children handled the event """

		if not self._visible:
			return False

		for child in self.children:
			if child.process_event(event):
				return True

		return False

	def on_resize(self):
		""" Update anchors and then tell all children to resize themselves """

		self.do_anchoring()

		for child in self.children:
			child.on_resize()

	def begin_round(self):
		""" soya begin_round event """
		self.apply('begin_round')

	def advance_time(self, proportion):
		""" soya advance_time event """
		self.apply('advance_time', proportion)

	def end_round(self):
		""" soya.end_round event """
		self.apply('end_round')


class TestContainer(TestControl):
	klass = Container


class InputControl: 
	"""  This class should be used with multiple inheritance to create
	some standard events. call InputControl.process_event(self,event)
	from your widgets process_event call.
	
	Note the methods on_mouse*, on_key_*, on_focus and on_loose_focus """

	def __get_focus__(self):
		return self._focus

	def __set_focus__(self, val):
		if val:
			self.on_focus()
		elif self._focus:
			self.on_loose_focus()

		self._focus = val

	focus = LateBindingProperty('__get_focus__', '__set_focus__')

	def __init__(self):
		self._focus = False
			
	def process_event(self, event):
		""" process an individial event and then pass it on the correct event
		handler. if that handler returns True the event is assumed to of been 
		dealt with """

		if not self._visible:
			return False
		
		# if its a mouse event lets see if the cursor is over us
		if event[0] in [sdl.MOUSEMOTION, sdl.MOUSEBUTTONDOWN, sdl.MOUSEBUTTONUP]:
			return self.process_mouse_event(event)
		elif self.focus:
			if event[0] == sdl.KEYDOWN:
				if event[3] != 0:
					return self.on_key_down(event[3], event[2])
				else:
					return self.on_key_down(event[1], event[2])

			elif event[0] == sdl.KEYUP:
				return self.on_key_up(event[1], event[2])

		return False

	def process_mouse_event(self, event):
		""" process a mouse event. focus is set if the mouse is over the widget.
		the event handlers on mouse_* are called from here """

		if event[0] == sdl.MOUSEMOTION:
			x, y = event[1], event[2]
		else:
			x, y = event[2], event[3]


		if x > self.screen_left and x < self.screen_right \
					and y > self.screen_top and y < self.screen_bottom:

			# convert the coords to widget coords not screen coords
			x -= self.screen_left
			y -= self.screen_top

			if not self.focus:
				self.focus = True

			if event[0] == sdl.MOUSEMOTION:
				return self.on_mouse_over(x, y, event[3], event[4], event[5])
			elif event[0] == sdl.MOUSEBUTTONDOWN:
				return self.on_mouse_down(x, y, event[1])
			else:
				return self.on_mouse_up(x, y, event[1])

		else:
			if self._focus:
				self.focus = False

		return False

	def on_mouse_over(self, x, y, dx, dy, buttons):
		""" event triggered when the mouse moves over the control """
		pass

	def on_mouse_down(self, x, y, button):
		""" event triggered when a mouse button is pressed """
		pass

	def on_mouse_up(self, x, y, button):
		""" event triggered when a mouse button is released """
		pass

	def on_key_down(self, key, mods):
		""" event triggered when a key is pressed """
		pass

	def on_key_up(self, key, mods):
		""" event triggered when a key is released """
		pass

	def on_focus(self):
		""" event triggered when the control gets focus """
		pass

	def on_loose_focus(self):
		""" event triggered when the control looses focus """
		pass

class _TestInputControl(unittest.TestCase):
	def testOnMouseOver(self):  
		""" testing calling on_mouse_over """
		self.getControl().on_mouse_over(1, 1, 1, 1, 1)

	def testOnMouseDown(self):
		""" testing calling on_mouse_down """
		self.getControl().on_mouse_down(1, 1, 1)

	def testOnMouseUp(self):
		""" testing calling on_mouse_up """
		self.getControl().on_mouse_up(1, 1, 1)

	def testOnKeyDown(self):
		""" testing calling on_key_down """
		self.getControl().on_key_down(0, 0)

	def testOnKeyUp(self):
		""" testing calling on_key_up """
		self.getControl().on_key_up(0, 0)

	def testOnFocus(self):
		""" testing calling on_focus """
		self.getControl().on_focus()

	def testOnLooseFocus(self):
		""" testing calling on_loose_focus """
		self.getControl().on_loose_focus()


class RootWidget(Container):
	""" The root widget to be used with \module{soya.pudding}.

	If your display looks incorrect try resizing the window. If that corrects 
	the display then you need to call root_widget.on_resize() at some 
	point before the user gets control.

	"""

	def on_init(self):
		""" Declares self.cameras """

		self.cameras = []

	def widget_begin_round(self):
		""" Called at the beginning of every round """
		self.begin_round()
		
	def widget_advance_time(self, proportion):
		""" Called once or more per round """
		self.advance_time(proportion)
	
	def widget_end_round(self):
		""" Called at the end of every round """
		self.end_round()

	def start_render(self):
		""" Load the identity matrix for the root widget """
		# as we're the root we want to make sure we have the starting point
		glPushMatrix()

		self._screen_top = 0
		self._screen_left = 0
		
		glLoadIdentity()

		for camera in self.cameras:
			camera.render()

	def add_child(self, child):
		""" Add a child to the root widget. \class{RootWidget} also accepts cameras
		as children altho these are stored in .cameras """

		# find if something really is subclassed to a camera 
		# isinstance(child, soya.Camera) returns False 
		if isinstance(child, soya._soya._Camera):
			self.cameras.append(child)
		else:
			Container.add_child(self, child)

		return child

	def on_resize(self):
		""" Resize all cameras and children """

		for camera in self.cameras:
			camera.set_viewport(0, 0, self.width, self.height)

		Container.on_resize(self)


class TestRootWidget(unittest.TestCase):
	def test1Create(self):
		""" testing creating """
		r = RootWidget()
