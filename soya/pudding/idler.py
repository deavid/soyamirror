""" a simple replacement idler for soya """

__revision__ = '$Revision: 1.1 $'

__doc_classes__ = [ 'Idler' ] 

__doc_functions__ = []

import soya
from soya.pudding import process_event

import unittest

class Idler(soya.Idler):
  """ Simple replacement for the soya.Idler that calls soya.pudding.process_event
  in begin_round and places all unhandled events into idler.events.
  
  """

  def __init__(self, *scenes):
    soya.Idler.__init__(self, *scenes)

    self.events = []

  def begin_round(self):
    """ call soya.pudding.process event and put all events in self.events so the 
    "game" can handle other events """

    soya.Idler.begin_round(self)

    self.events = process_event()

  def idle(self):
    """ resize all widgets and start the idler """
    soya.root_widget.on_resize()

    soya.Idler.idle(self)

class TestIdler(unittest.TestCase):
  def testCreate(self):
    idler = Idler()
