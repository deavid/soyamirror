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

import sys, os, os.path
import soya, soya.gui

soya.path.append(os.path.join(os.path.dirname(sys.argv[0]), "data"))

soya.init(width = 640, height = 480)


# Adapter for the new GUI -- this will surely change !!!

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
		self.events = soya.process_event()
		soya.root_widget.widget.process_event(self.events)
		soya.root_widget.widget.begin_round()
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
	



def widget_demo():
	window = soya.gui.Window(root)
	table = soya.gui.VTable(window, 2)
	table.row_pad = 20
	soya.gui.Label(table, u"Fullscreen")
	soya.gui.CheckBox(table, u"bla bla", 1)
	soya.gui.Label(table, u"Quality")
	soya.gui.HScrollBar(table, 0, 9, 1, 1, 1)
	soya.gui.CancelButton(table)
	soya.gui.ValidateButton(table)

def text_demo():
	window = soya.gui.Window(root)
	table = soya.gui.VTable(window)
	table.row_pad = 30
	soya.gui.Label(table, u"Simple label")
	scroll_pane  = soya.gui.ScrollPane(table)
	soya.gui.Text(scroll_pane, u"""Multiline text with automatic breaklines, included inside a scroll pane.

All texts are Unicode, notice the support for accentuated characters: éêëè.

This text is deliberately long and boring, but it is mandatory in order to have a text long enought to get the scroll bar.

I apologize for the lack of interest of this text.

Sorry, Jiba""")
	soya.gui.Input(table, u"A simple one-line text input")
	
def list_demo():
	window = soya.gui.Window(root, u"List demo")
	table = soya.gui.VTable(window, 2)
	table.row_pad = table.col_pad = 20
	
	soya.gui.Label(table, u"vertical list\nin a scroll pane")
	l = soya.gui.VList(soya.gui.ScrollPane(table))
	soya.gui.Label(l, u"Baby").extra_width = 1.0
	soya.gui.Label(l, u"Beginner")
	soya.gui.Label(l, u"Very easy")
	soya.gui.Label(l, u"Easy")
	soya.gui.Label(l, u"Hard gamer")
	soya.gui.Label(l, u"Nighmare")
	soya.gui.Label(l, u"Impossible")
	soya.gui.Label(l, u"God")
	soya.gui.Label(l, u"Jiba :-)")
	
	soya.gui.Label(table, u"vertical list\nwith 2 columns")
	l = soya.gui.VList(table, 2)
	soya.gui.ProgressBar(l, 0.2)
	soya.gui.Label(l, u"Beginner")
	soya.gui.ProgressBar(l, 0.5)
	soya.gui.Label(l, u"Hard gamer")
	soya.gui.ProgressBar(l, 0.8)
	soya.gui.Label(l, u"Nighmare")
	
	soya.gui.Label(table, u"horizontal list")
	l = soya.gui.HList(table)
	soya.gui.Label(l, u"Beginner")
	soya.gui.Label(l, u"Hard gamer")
	soya.gui.Label(l, u"Nighmare")
	
def camera_demo(transparent = 0):
	import soya.cube
	window = soya.gui.Window(root, u"Camera demo")
	scene = soya.World()
	if transparent: scene.atmosphere = soya.NoBackgroundAtmosphere()
	light = soya.Light(scene)
	light.set_xyz(0.5, 0.0, 2.0)
	camera = soya.Camera(scene)
	camera.z = 2.0
	camera.partial = 1
	cube = soya.cube.Cube(scene, red)
	cube.advance_time = lambda proportion: cube.rotate_lateral(proportion)
	soya.gui.CameraViewport(window, camera)
	soya.MAIN_LOOP.scenes.append(scene)

def fps_camera_demo(transparent = 0):
	import soya.cube
	window = soya.gui.Window(root, u"Camera demo")
	layer = soya.gui.Layer(window)
	scene = soya.World()
	if transparent: scene.atmosphere = soya.NoBackgroundAtmosphere()
	light = soya.Light(scene)
	light.set_xyz(0.5, 0.0, 2.0)
	camera = soya.Camera(scene)
	camera.z = 2.0
	camera.partial = 1
	cube = soya.cube.Cube(scene, red)
	cube.advance_time = lambda proportion: cube.rotate_lateral(proportion)
	soya.gui.CameraViewport(layer, camera)
	soya.gui.FPSLabel(layer)
	soya.MAIN_LOOP.scenes.append(scene)


root  = soya.gui.RootLayer(None)
backg = soya.gui.Image(root, black)

window = soya.gui.Window(root, u"Soya GUI demo", closable = 0)
table = soya.gui.VTable(window)
soya.gui.Button(table, u"Widget demo", on_clicked = widget_demo)
soya.gui.Button(table, u"Text demo", on_clicked = text_demo)
soya.gui.Button(table, u"List demo", on_clicked = list_demo)
soya.gui.Button(table, u"Camera demo", on_clicked = lambda: camera_demo(0))
soya.gui.Button(table, u"Transparent camera demo", on_clicked = lambda: camera_demo(1))
soya.gui.Button(table, u"FPS camera demo", on_clicked = lambda: fps_camera_demo(0))
soya.gui.CancelButton(table, u"Quit", on_clicked = sys.exit)


root2 = Root(root)
soya.set_root_widget(root2)
MainLoop().main_loop()
