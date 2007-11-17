# -*- indent-tabs-mode: t -*-
# -*- coding: utf-8 -*-

# Soya 3D
# Copyright (C) 2007 Jean-Baptiste LAMY -- jiba@tuxfamily.org
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

from soya.gui.style import Style
from soya.gui.widgets import *

set_style(Style())

soya.set_use_unicode(1)




			
if __name__ == "__main__":
	soya.init(width = 640, height = 480)

	import soya.widget

	class Root(soya.widget.Widget):
		def __init__(self, widget):
			soya.widget.Widget.__init__(self)
			
			self.widget = widget
			self.widget.resize(0, 0, 640, 480)
			
		def render(self): self.widget.render()
		
	class MainLoop(soya.MainLoop):
		def __init__(self, *worlds):
			soya.MainLoop.__init__(self, *worlds)
			self.events = []
			
		def begin_round(self):
			soya.root_widget.widget.begin_round()
			self.events = soya.process_event()
			soya.root_widget.widget.process_event(self.events)
			soya.MainLoop.begin_round(self)
			
		def advance_time(self, proportion):
			soya.root_widget.widget.advance_time(proportion)
			soya.MainLoop.advance_time(self, proportion)
			
			
	
	black = soya.Material()
	black.diffuse = (0.0, 0.0, 0.0, 1.0)
	
	red = soya.Material()
	red.diffuse = (1.0, 0.0, 0.0, 1.0)
	
	blue = soya.Material()
	blue.diffuse = (0.0, 0.0, 1.0, 1.0)
	
	layer = Layer(None)
	backg = Image(layer, black)
	
# 	table = Table(layer, 2, 5)
	
# 	#l11 = Label(table, u"Jib")
# 	l11 = Layer(table)
# 	l11i = Image(l11, red)
# 	l11l = Label(l11, u"Jib g")
	
# 	#l12 = Label(table, u"20")
# 	l12 = Layer(table)
# 	l12i = Image(l12, blue)
# 	l12l = Label(l12, u"20")

# 	l21 = Label(table, u"Blamffffffffff")
# 	l22 = Layer(table)
# 	l22i = Image(l22, blue)
# 	l22c = CheckBox(l22, u"bla", 0)
	
# 	#l31 = Label(table, u"Marmoute")
# 	l31 = VScrollBar(table, 0.0, 3.0, 1.0, 1.0)
# 	#l32 = Label(table, "18")
# 	l32 = CheckBox(table, u"bla", 1)
	
# 	#l41 = VScrollBar(table, 0.0, 3.0, 1.0, 0.0)
# 	l41 = Button(table, u"Dac")
	
# 	l42  = ScrollPane(table)
# 	l42c = Label(l42, u"Un texte très long très long très long très long très long")
	
# 	l51 = Button(table, u"Dac")
	
# 	#l21.extra_width  = 1.0
	
# 	#l12l.extra_height = 1.0
# 	l21.extra_height = 1.0
# 	#l31.extra_height = 1.0
	
	window = Window(layer)
	wl = Label(window, u"Jiba X")
	
	window = Window(layer)
	sc  = ScrollPane(window)
	#Label(sc, u"Un texte très long très long très long très long très long !!!!")
	Text(sc, u"""Bla bla
Un texte très long très long
Un texte très long très long
Un texte très long très long
Un texte très long très long
Un texte très long très long  Un texte très long très long Un texte très long très long
UUn texte très long très long
Un texte très long très long
n texte très long très long

oezoe
poer,jvfpr
reprpvgeo,jvê
oidvjroi

Jiba""")

	
	window = Window(layer)
	table = Table(window, 2, 5)
	table.row_pad = 20
	Label(table, u"Fullscreen")
	CheckBox(table, u"bla bla", 1)
	Label(table, u"Quality")
	HScrollBar(table, 0, 9, 1, 1, 1)
	Label(table, u"Information")
	Text(ScrollPane(table), u"This is a small demo of a new widget module for the Soya 3D engine.\nIt features flying windows, scrolling panes, and the usual set of widgets :\n * Label\n * Image\n * Input\n * Button\n * CheckBox\n * ScrollBar\n * ...\nAnd it's only the third widget module for soya ;-)")
	Label(table, u"Name")
	Input(table, u"Jiba")
	#table.skip_case()
	CancelButton(table)
	ValidateButton(table)
	
	window = Window(layer, u"List demo")
	table = VTable(window, 2)
	table.row_pad = table.col_pad = 20
	
	Label(table, u"vertical list\nin a scroll pane")
	l = VList(ScrollPane(table))
	Label(l, u"Baby").extra_width = 1.0
	Label(l, u"Beginner")
	Label(l, u"Very easy")
	Label(l, u"Easy")
	Label(l, u"Hard gamer")
	Label(l, u"Nighmare")
	Label(l, u"Impossible")
	Label(l, u"God")
	Label(l, u"Jiba :-)")
	
	Label(table, u"vertical list\nwith 2 columns")
	l = VList(table, 2)
	ProgressBar(l, 0.2)
	Label(l, u"Beginner")
	ProgressBar(l, 0.5)
	Label(l, u"Hard gamer")
	ProgressBar(l, 0.8)
	Label(l, u"Nighmare")
	
	Label(table, u"horizontal list")
	l = HList(table)
	Label(l, u"Beginner")
	Label(l, u"Hard gamer")
	Label(l, u"Nighmare")
	
	window = Window(layer, u"Camera demo")
	scene = soya.World()
	#scene.atmosphere = soya.NoBackgroundAtmosphere()
	print scene.atmosphere
	#scene.atmosphere = soya.Atmosphere()
	light = soya.Light(scene)
	light.set_xyz(0.5, 0.0, 2.0)
	camera = soya.Camera(scene)
	camera.z = 2.0
	camera.partial = 1
	import soya.cube
	cube = soya.cube.Cube(scene, red)
	cube.advance_time = lambda proportion: cube.rotate_lateral(proportion)
	CameraViewport(window, camera)
	
	
	root = Root(layer)
	soya.set_root_widget(root)
	
	MainLoop(scene).main_loop()
