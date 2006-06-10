# -*- indent-tabs-mode: t -*-

# Soya 3D
# Copyright (C) 2001-2002 Jean-Baptiste LAMY
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

import os, atexit, cPickle as pickle, soya, soya.editor, editobj, editobj.main, editobj.treewidget as treewidget
from Tkinter import *

class Config(object):
	def __init__(self):
		self.path = os.environ["HOME"]
		
	def apply(self):
		soya.path = [self.path]
		
	def save(self, file = None):
		file = file or open(CONFIG_FILE, "w")
		pickle.dump(self, file)
		
CONFIG_FILE = os.path.join(os.environ["HOME"], ".soya_editor")


if os.path.exists(CONFIG_FILE):
	try:
		CONFIG = pickle.load(open(CONFIG_FILE))
		CONFIG.apply()
	except:
		import sys
		sys.excepthook(*sys.exc_info())
		print "Bugged config file (%s) -- I create a new one !" % CONFIG_FILE
		CONFIG = Config()
		CONFIG.save()
		CONFIG.apply()
		
else:
	print "No config file -- I create a new one !"
	
	CONFIG = Config()
	CONFIG.save()
	CONFIG.apply()
	

atexit.register(CONFIG.save)


class App(Toplevel):
	def __init__(self, extra_classes = ()):
		# Get, or create if needed, the root Tk.
		try:
			from Tkinter import _default_root
			tkroot = _default_root
		except ImportError: pass
		if not tkroot:
			tkroot = Tk(className = "Soya Editor")
			tkroot.withdraw()
			
		menubar = Menu(tkroot)
		file_menu = Menu(menubar, tearoff = 1)
		file_menu.add_command(label = "New Material...", command = self.new_material)
		file_menu.add_command(label = "New World..."   , command = self.new_world)
		for clazz in extra_classes:
			file_menu.add_command(label = "New %s..." % clazz.__name__, command = lambda clazz = clazz: editobj.edit(clazz()))
			
		file_menu.add_separator()
		file_menu.add_command(label = "Load..."        , command = self.load)
		file_menu.add_command(label = "Quit"           , command = self.quit)
		menubar.add_cascade(label = "File", menu = file_menu)
		
		Toplevel.__init__(self, tkroot, menu = menubar)
		
		self.edit_config = editobj.main.EditPropertyFrame(self)
		self.edit_config.edit(CONFIG)
		self.edit_config.pack(fill = BOTH)
		
		Button(self, text = "Apply", command = self.validate).pack()
		
		self.wm_protocol("WM_DELETE_WINDOW", self.quit)
		
	def validate(self, event = None):
		self.focus_set()
		CONFIG.apply()
		
	def new_material(self, event = None):
		editobj.edit(soya.Material())
		
	def new_world(self, event = None):
		editobj.edit(soya.World())
		
	def load(self, event = None):
		import tkFileDialog
		s = tkFileDialog.askopenfilename()
		if s:
			obj = pickle.load(open(s, "rb"))
			editobj.edit(obj)
		
	def quit(self, event = None):
		import sys
		sys.exit()
