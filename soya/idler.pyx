# -*- indent-tabs-mode: t -*-

# Soya 3D
# Copyright (C) 2001-2004 Jean-Baptiste LAMY -- jiba@tuxfamily.org
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

import weakref

IDLER = None
BEFORE_RENDER = []

IDLEING_ITEMS = weakref.WeakKeyDictionary()

cdef class Idler:
	"""Idler

A main loop, with FPS regulation.

Interesting attributes:

 - fps (read only): the frame rate (number of frame per second, a usefull speed indicator).

 - running (read only): true if the Idler is idling (=running).

 - next_round_tasks: a list of callable (taking no arg) that will be called once, just
	 after the beginning of the next round.

 - scenes: the scenes associated to this idler.

 - round_duration: The duration of a round. Round is the idler's time unit. The idler calls
	 successively begin_round(), advance_time() (possibly several times) and end_round(); it
	 is granted that ALL rounds correspond to a period of duration ROUND_DURATION (though
	 the different period may not be regularly spread over time).
	 Default is 0.030.

 - min_frame_duration: minimum duration for a frame. This attribute can be used to limit
	 the maximum FPS to save CPU time; e.g. FPS higher than 30-40 is usually useless.
	 Default is 0.020, which limits FPS to 40 in theory and to about 33 in practice
	 (I don't know why there is a difference between theory and practice !).
"""
	
	# for time computation, double precision is needed
	
	#cdef                 _next_round_tasks, _return_value
	#cdef                 _scenes
	#cdef public   double round_duration, min_frame_duration
	#cdef readonly double fps
	#cdef public   int    running
	#cdef public   int    will_render
	#cdef double          _time, _time_since_last_round
	
	property scenes:
		def __get__(self):
			return self._scenes
			
	property next_round_tasks:
		def __get__(self):
			return self._next_round_tasks
		
	property return_value:
		def __get__(self):
			return self._return_value
		
	def __init__(self, *scenes):
		"""Idler(scene1, scene2,...) -> Idler

Creates a new idler for scenes SCENE1, SCENE2,...."""
		self._next_round_tasks  = []
		self.fps                = 0.0
		self.running            = 0
		self._scenes            = list(scenes)
		self.round_duration     = 0.030
		self.min_frame_duration = 0.020
		self.will_render        = 0
		
		import soya
		soya.IDLER = self
		
	def start(self):
		"""Idler.start()

Starts idling with a new thread (see Idler.idle() if you don't want to create a new thread)."""
		import thread
		thread.start_new_thread(self.idle, ())
		
	def stop(self, value = None):
		"""Idler.stop(VALUE = None)

Stops idling. The stopping may not occur immediately, but at the end of the next iteration.
Idler.stop() causes Idler.idle() to returns ; VALUE is the (optionnal) value that Idler.idle() will return."""
		self.running       = 0
		self._return_value = value
		
	def reset(self):
		import time
		self._time = time.time()
		
	def idle(self):
		"""Idler.idle()

Starts idling with the current thread. This method never finishes, until you call Idler.stop()."""
		import time
		
		# for time computation, double precision is needed
		cdef double last_fps_computation_time, current, delta, spent_time
		cdef int    nb_frame
		self.running = 1
		self._time = last_fps_computation_time = time.time()
		self._time_since_last_round = 0.0
		
		self.begin_round()
		
		while self.running == 1:
			nb_frame = 0
			while (self.running == 1) and (nb_frame < 80):
				nb_frame = nb_frame + 1
				
				while 1: # Sleep until at least MIN_FRAME_DURATION second has passed since the last frame
					current = time.time()
					delta   = current - self._time
					if delta > self.min_frame_duration: break
					time.sleep(self.min_frame_duration - delta)
					
				self._time = current
				
				while self._time_since_last_round + delta > self.round_duration: # Start a new frame
					spent_time = self.round_duration - self._time_since_last_round
					
					self.advance_time(spent_time / self.round_duration) # Complete the previous round
					self.end_round()                                    # Ends the previous round
					self.begin_round()                                  # Prepare the following round
					
					if self._next_round_tasks:
						for task in self._next_round_tasks: task()
						self._next_round_tasks = []
						
					delta = delta - spent_time
					self._time_since_last_round = 0
					
				self.will_render = 1
				self.advance_time(delta / self.round_duration) # start the current round
				self.will_render = 0
				self._time_since_last_round = self._time_since_last_round + delta
				
				self.render()
				
			current = time.time()
			self.fps = nb_frame / (current - last_fps_computation_time)
			last_fps_computation_time = current

		return self._return_value
	
	def begin_round(self):
		"""Idler.begin_round()

Called by Idler.idle when a new round begins; default implementation delegates to Idler.scene.begin_round."""
		cdef _World scene
		for item in IDLEING_ITEMS: item.begin_round()
		for scene in self._scenes: scene.begin_round()
		if root_widget: root_widget.widget_begin_round()
		
	def end_round(self):
		"""Idler.end_round()

Called by Idler.idle when a round is finished; default implementation delegates to Idler.scene.end_round."""
		cdef _World scene
		for item in IDLEING_ITEMS: item.end_round()
		for scene in self._scenes: scene.end_round()
		if root_widget: root_widget.widget_end_round()
		
		PyErr_CheckSignals()
		
	def advance_time(self, float proportion):
		"""Idler.advance_time(proportion)

Called by Idler.idle when a piece of a round has occured; default implementation delegates to Idler.scene.advance_time.
PROPORTION is the proportion of the current round's time that has passed (1.0 for an entire round)."""
		cdef _World scene
		for item in IDLEING_ITEMS: item.advance_time(proportion)
		for scene in self._scenes: scene.advance_time(proportion)
		if root_widget: root_widget.widget_advance_time(proportion)
		
	def render(self):
		"""Idler.render()

Called by Idler.idle when rendering is needed; default implementation calls soya.render."""
		for i in BEFORE_RENDER: i()
		render()
		
		
