# -*- indent-tabs-mode: t -*-

""" a simple replacement main_loop for soya """

__revision__ = '$Revision: 1.1 $'

__doc_classes__ = [ 'MainLoop' ] 

__doc_functions__ = []

import soya
from soya.pudding import process_event

import unittest

class MainLoop(soya.MainLoop):
	""" Simple replacement for the soya.MainLoop that calls soya.pudding.process_event
	in begin_round and places all unhandled events into main_loop.events.
	
	"""

	def __init__(self, *scenes):
		soya.MainLoop.__init__(self, *scenes)


	def begin_round(self):
		""" call soya.pudding.process event and put all events in self.events so the 
		"game" can handle other events """

		soya.MainLoop.begin_round(self)
		process_event(self.raw_events)

	def main_loop(self):
		""" resize all widgets and start the main_loop """
		soya.root_widget.on_resize()

		return soya.MainLoop.main_loop(self)

class TestMainLoop(unittest.TestCase):
	def testCreate(self):
		main_loop = MainLoop()
