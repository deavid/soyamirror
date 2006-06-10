# -*- indent-tabs-mode: t -*-

""" an interactive python console for pudding """

__revision__ = '$Revision: 1.1 $'

import sys

import soya.pudding as pudding

from code import InteractiveConsole

class PythonConsole(pudding.control.Console):
	""" an interactive python console for pudding """

	def __init__(self, parent=None, lokals=None, **kwargs):
		pudding.control.Console.__init__(self, parent, initial='', **kwargs)

		self.interpreter = InteractiveConsole(lokals)
		self.interpreter.write = self.write

		self.stdout = sys.stdout
		sys.stdout = self

	def on_return(self):
		""" run the command if its complete """
		self.input_buffer.append(self.input.value)

		self.write(">>> %s\n" % self.input.value)
		self.interpreter.push(self.input.value)

		self.input.clear()

	def write(self, string):
		""" write method to pretend to be a file like object """
		self.output.label += "%s" % string
		print >>self.stdout, string
		
class TestPythonConsole(pudding.control.TestConsole):
	klass = PythonConsole

	def testPython(self):
		""" testing console python """
		console = self.getControl()
		console.interpreter.push('print dir()')
