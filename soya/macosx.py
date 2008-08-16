# -*- indent-tabs-mode: t -*-

# Soya 3D
# Copyright (C) 2004 Toni Alatalo -- antont@kyperjokki.fi
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


import objc
from Foundation import NSObject, NSLog, NSBundle, NSDictionary
#from AppKit import NSApplicationDelegate, NSTerminateLater, NSApplication, NSCriticalRequest, NSImage, NSApp, NSMenu, NSMenuItem
from AppKit import NSTerminateLater, NSApplication, NSCriticalRequest, NSImage, NSApp, NSMenu, NSMenuItem
try:
	from AppKit import NSApplicationDelegate
except ImportError:
	NSApplicationDelegate = None

import os, sys

# Make a good guess at the name of the application
if len(sys.argv) > 0:
		MyAppName = os.path.splitext(sys.argv[0])[0]
else:
		MyAppname = 'Soya on Mac'
		
# Need to do this if not running with a nib
def setupAppleMenu():
		appleMenuController = objc.lookUpClass('NSAppleMenuController').alloc().init()
		appleMenu = NSMenu.alloc().initWithTitle_('')
		appleMenuItem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('', None, '')
		appleMenuItem.setSubmenu_(appleMenu)
		NSApp().mainMenu().addItem_(appleMenuItem)
		appleMenuController.controlMenu_(appleMenu)
		NSApp().mainMenu().removeItem_(appleMenuItem)
		
# Need to do this if not running with a nib
def setupWindowMenu():
		windowMenu = NSMenu.alloc().initWithTitle_('Window')
		menuItem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('Minimize', 'performMiniaturize:', 'm')
		windowMenu.addItem_(menuItem)
		del menuItem
		windowMenuItem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('Window', None, '')
		windowMenuItem.setSubmenu_(windowMenu)
		NSApp().mainMenu().addItem_(windowMenuItem)
		NSApp().setWindowsMenu_(windowMenu)

if NSApplicationDelegate is not None:
# Used to cleanly terminate
	class MyAppDelegate(NSObject, NSApplicationDelegate):
			def init(self):
					return self

			def applicationDidFinishLaunching_(self, aNotification):
					pass

			def applicationShouldTerminate_(self, app):
					return NSTerminateLater

# Start it up!
app = NSApplication.sharedApplication()

if NSApplicationDelegate is not None:
	DELEGATE = MyAppDelegate.alloc().init()
	app.setDelegate_(DELEGATE)
if not app.mainMenu():
		mainMenu = NSMenu.alloc().init()
		app.setMainMenu_(mainMenu)
		setupAppleMenu()
		setupWindowMenu()
app.finishLaunching()
app.updateWindows()
app.activateIgnoringOtherApps_(objc.YES)
