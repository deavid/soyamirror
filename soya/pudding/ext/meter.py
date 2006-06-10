# -*- indent-tabs-mode: t -*-

""" meter controls for pudding """

__revision__ = '$Revision: 1.1 $'

import soya
from soya.opengl import *

import soya.pudding as pudding
import soya.pudding.core
import soya.pudding.control
import soya.pudding.container

class Meter(pudding.core.Control, pudding.core.InputControl):
	""" Simple Meter/Progress bar type control. 

	Value may be set with mouse scroll wheel or by clicking in the meter.

	To stop user control set <Meter>.user_change = False
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
	
	def __init__(self, parent=None, min=0, max=100, 
										**kwargs):

		pudding.core.Control.__init__(self, parent, **kwargs)
		pudding.core.InputControl.__init__(self)

		self._value = 50
		self.min = min
		self.max = max

		self.color = (0., 0., 1., 1.)
		self.border_color = (0., 0., 0., 1.)

		self.user_change = True

		self.calc_step()

	def calc_step(self):
		self.step = self.width / float(self.max)

	def on_resize(self):
		pudding.core.Control.on_resize(self)

		self.calc_step()

	def render_self(self):
		soya.DEFAULT_MATERIAL.activate()

		glColor4f(*self.color)

		glBegin(GL_QUADS)
		glVertex2i(0, 0)
		glVertex2i(int(self.value * self.step), 0)
		glVertex2i(int(self.value * self.step), self.height)
		glVertex2i(0, self.height)
		glEnd()

		glColor4f(*self.border_color)
		glBegin(GL_LINE_LOOP)
		glVertex2i(0, 0)
		glVertex2i(self.width, 0)
		glVertex2i(self.width, self.height)
		glVertex2i(0, self.height)
		glEnd()

	def process_event(self, event):
		if self.user_change:
			return pudding.core.InputControl.process_event(self, event)
		else:
			return False

	def on_mouse_down(self, x, y, button):
		if button == 5:
			self.value -= 1
		elif button == 4:
			self.value += 1

		elif button == 1:
			self.value = int(x)

		return True

	def on_set_value(self):
		pass

class TestMeter(pudding.core.TestControl):
	klass = Meter

class MeterLabel(pudding.container.HorizontalContainer):
	""" Provides a label and meter wrapped in a container """
	def __get_value__(self):
		return self.meter.value

	def __set_value__(self, val):
		self.meter.value = val

	value = property( __get_value__, __set_value__)

	def __init__(self, parent = None, label = '' , **kwargs):
		pudding.container.HorizontalContainer.__init__(self, parent, **kwargs)
		self.padding = 4

		self._create_label(label)

		self.meter = Meter(width = 100, height = 20)
		self.meter.on_set_value = self.update
		self.add_child(self.meter)

		self.update()

	def _create_label(self, label):
		self.label = pudding.control.SimpleLabel(label = label)
		self.label.color = (0, 0, 0, 1)
		self.add_child(self.label, pudding.ALIGN_RIGHT)

	def update(self):
		pass

class TestMeterLabel(TestMeter):
	klass = MeterLabel

class MeterValueLabel(MeterLabel):
	""" Provides a label(with value) and meter wrapped in a container """

	def _create_label(self, label):
		self.label = pudding.control.PrePostLabel(pre = label)
		self.label.color = (0, 0, 0, 1)
		self.add_child(self.label, pudding.ALIGN_RIGHT)

	def update(self):
		self.label.label = str(self.value)

class TestMeterValueLabel(TestMeter):
	klass = MeterValueLabel

