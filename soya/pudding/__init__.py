# -*- indent-tabs-mode: t -*-

"""
Main pudding module

"""

__revision__ = "$Revision: 1.1 $"
__version__  = "0.1-0"

import soya
import soya.widget

from soya.pudding.style import Style

STYLE = None

# constants #

# there may well be a better way to do these

CLIP_NONE   = 0
CLIP_LEFT   = 2
CLIP_RIGHT  = 4
CLIP_TOP    = 8
CLIP_BOTTOM = 16

EXPAND_NONE   = 0
EXPAND_HORIZ  = 2
EXPAND_VERT   = 4
EXPAND_BOTH   = EXPAND_HORIZ | EXPAND_VERT
CENTER_HORIZ  = 8
CENTER_VERT   = 16
CENTER_BOTH   = CENTER_HORIZ | CENTER_VERT
ALIGN_LEFT    = 32
ALIGN_RIGHT   = 64
ALIGN_TOP     = 128
ALIGN_BOTTOM  = 256

TOP_LEFT = ALIGN_LEFT | ALIGN_TOP
TOP_RIGHT = ALIGN_RIGHT | ALIGN_TOP
BOTTOM_LEFT = ALIGN_LEFT | ALIGN_BOTTOM
BOTTOM_RIGHT = ALIGN_RIGHT | ALIGN_BOTTOM

CORNERS = [TOP_LEFT, TOP_RIGHT, BOTTOM_LEFT, BOTTOM_RIGHT]

ANCHOR_LEFT   = 2
ANCHOR_TOP    = 4
ANCHOR_RIGHT  = 8
ANCHOR_BOTTOM = 16

ANCHOR_TOP_LEFT = ANCHOR_TOP | ANCHOR_LEFT
ANCHOR_TOP_RIGHT = ANCHOR_TOP | ANCHOR_RIGHT
ANCHOR_BOTTOM_LEFT = ANCHOR_BOTTOM | ANCHOR_LEFT
ANCHOR_BOTTOM_RIGHT = ANCHOR_BOTTOM | ANCHOR_RIGHT

ANCHOR_ALL    =  ANCHOR_LEFT | ANCHOR_TOP | ANCHOR_RIGHT | ANCHOR_BOTTOM 


def init(style = None):
	""" Intialise \\module{soya.pudding}. \\var{style} should be a subclass of 
	\\class{soya.pudding.style.Style} 
	"""

	global STYLE

	print "* Soya Pudding * Version: %s" % __version__
	
	STYLE = style or Style()

	# lets just turn this on whatever
	# using text inputs without unicode is really painfull unless you care about
	# using A-Z 
	soya.set_use_unicode(1)


def process_event(events=None):
	""" This gets the event list from soya and filters it for any events handled 
	by widgets. It returns an array with the events that have not been used. 
	If you use the \class{soya.pudding.main_loop.MainLoop} then this function is called in 
	\\method{main_loop.begin_round} and the events unprocessed put in 
	\\var{main_loop.events.} 
	"""
	if events is None:
		events = soya.MAIN_LOOP.raw_events

	unused_events = []

	for event in events: 
		if not soya.root_widget.process_event(event):
			unused_events.append(event)

	return unused_events 


class PuddingError(Exception):
	""" A \\module{soya.pudding} exception """

	def __init__(self, msg):
		Exception.__init__(self)
		self.msg = msg

	def __str__(self):
		print "[soya.pudding] %s" % self.msg


class ConstantError(PuddingError):
	""" Error using a \\module{soya.pudding} constant """
	pass


from soya.pudding import core, container, control, main_loop

