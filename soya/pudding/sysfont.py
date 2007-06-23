# -*- indent-tabs-mode: t -*-

##  pygame - Python Game Library
##  Copyright (C) 2000-2003  Pete Shinners
##
##  This library is free software; you can redistribute it and/or
##  modify it under the terms of the GNU Library General Public
##  License as published by the Free Software Foundation; either
##  version 2 of the License, or (at your option) any later version.
##
##  This library is distributed in the hope that it will be useful,
##  but WITHOUT ANY WARRANTY; without even the implied warranty of
##  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
##  Library General Public License for more details.
##
##  You should have received a copy of the GNU Library General Public
##  License along with this library; if not, write to the Free
##  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
##
##  Pete Shinners
##  pete@shinners.org

"sysfont, used in the font module to find system fonts"

# modified for use with pudding by dunkfordyce ( dunk@dunkfordyce.co.uk )

__revision__ = '$Revision: 1.3 $'

import os, sys

class FontNotFoundError(IOError):
	pass

def _simplename(name):
	""" create simple version of the font name """
	for char in '_ -':
		name = name.replace(char, '')
	name = name.lower()
	name = name.replace('-', '')
	name = name.replace("'", '')
	return name


def _addfont(name, bold, italic, font, fontdict):
	""" insert a font and style into the font dictionary """
	if not fontdict.has_key(name):
		fontdict[name] = {}
	fontdict[name][bold, italic] = font


def initsysfonts_win32():
	""" read the fonts on windows """
	import _winreg
	fonts = {}
	mods = 'demibold', 'narrow', 'light', 'unicode', 'bt', 'mt'
	fontdir = os.path.join(os.environ['WINDIR'], "Fonts")

	#this is a list of registry keys containing information
	#about fonts installed on the system.
	keys = []

	#find valid registry keys containing font information.
	possible_keys = [
		r"SOFTWARE\Microsoft\Windows\CurrentVersion\Fonts",
		r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts"
		]

	for key_name in possible_keys:
		try:
			key = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, key_name)
			keys.append(key)
		except WindowsError:
			pass

	for key in keys:
		fontdict = {}
		for i in range(_winreg.QueryInfoKey(key)[1]):
			try: 
				name, font, t = _winreg.EnumValue(key, i)
			except EnvironmentError: 
				break

			font = str(font)
			if font[-4:].lower() != ".ttf":
				continue
			if os.sep not in font:
				font = os.path.join(fontdir, font)

			if name[-10:] == '(TrueType)':
				name = name[:-11]
			name = name.lower().split()

			bold = italic = 0
			for mod in mods:
				if mod in name:
					name.remove(mod)
			if 'bold' in name:
				name.remove('bold')
				bold = 1
			if 'italic' in name:
				name.remove('italic')
				italic = 1
			name = ''.join(name)

			_addfont(name, bold, italic, font, fonts)
	return fonts


def initsysfonts_darwin():
	 """ read of the fonts on osx """

	 paths = ['/Library/Fonts',
				'~/Library/Fonts',
				'/Local/Library/Fonts',
				'/Network/Library/Fonts',
				'/System/Library/Fonts/',]
	 fonts = {}
	 for p in paths:
		 d = os.path.expanduser(p)
		 if os.path.isdir(d):
			 os.path.walk(d, _fontwalk_darwin, fonts)
	 return fonts

def _fontwalk_darwin(fonts, path, files):
	 """ walk the path directory trees """
	 for font in files:
		 if font[-4:].lower() != '.ttf':
			 continue
		 name = font[:-4].lower()
		 font = os.path.join( path, font )
		 bold = 0
		 italic = 0
		 _addfont(name, bold, italic, font, fonts)




def read_unix_fontscache(dir, file, fonts):
	""" read the fonts from a unix 'fonts.cache-1' file """
	file = open(os.path.join(dir, file))
	for line in file.readlines():
		try:
			font, num, vals = line.split(' ', 2)
		except ValueError:
			continue
		font = font.replace('"', '')
		if font[-4:].lower() != '.ttf':
			continue
		font = os.path.join(dir, font)
		vals = vals.split(':')
		name = _simplename(vals[0][1:])
		bold = vals[1].find('Bold') >= 0
		italic = vals[1].find('Italic') >= 0
		_addfont(name, bold, italic, font, fonts)


def read_unix_fontsdir(dir, file, fonts):
	""" read the fonts from a unix 'fonts.dot' file """
	file = open(os.path.join(dir, file))
	numfonts = int(file.readline())
	for line in file.readlines():
		font, descr = (line.split(' ', 1) + ['', ''])[:2]
		if font[-4:].lower() != ".ttf":
			continue
		font = os.path.join(dir, font)
		descr = descr.split('-', 13)
		name = _simplename(descr[2])
		bold = (descr[3] == 'bold')
		italic = (descr[4] == 'i')
		_addfont(name, bold, italic, font, fonts)


def _fontwalk(fonts, path, files):
	""" walk the path directory trees """
	if 'fonts.scale' in files:
		read_unix_fontsdir(path, 'fonts.scale', fonts)
	elif 'fonts.dir' in files:
		read_unix_fontsdir(path, 'fonts.dir', fonts)
	elif 'fonts.cache-1' in files:
		read_unix_fontscache(path, 'fonts.cache-1', fonts)


def initsysfonts_unix_old():
	""" read the fonts on unix """
	paths = ['/usr/X11R6/lib/X11/fonts', '/usr/share/fonts']
	fonts = {}
	for p in paths:
		if os.path.isdir(p):
			os.path.walk(p, _fontwalk, fonts)
	return fonts

#read the fonts on unix
def initsysfonts_unix():
	fonts = initsysfonts_unix_old()
	
	# we use the fc-list from fontconfig to get a list of fonts.
	
	try:
		# note, we use popen3 for if fc-list isn't there to stop stderr printing.
		flin, flout, flerr = os.popen3('fc-list : file family style')
	except:
		return fonts
	
	try:
		for line in flout:
			try:
				filename, family, style = line.split(':', 2)
				if filename[-4:].lower() in ['.ttf', '.ttc']:
					bold = style.find('Bold') >= 0
					italic = style.find('Italic') >= 0
					oblique = style.find('Oblique') >= 0
					_addfont(_simplename(family), bold, italic or oblique, filename, fonts)
			except:
				# try the next one.
				pass
	except:
		pass
	
	return fonts


def create_aliases():
	""" create alias entries"""

	aliases = (
		('monospace', 'misc-fixed', 'courier', 'couriernew', 'console',
				'fixed', 'mono', 'freemono', 'bitstreamverasansmono',
				'verasansmono', 'monotype', 'lucidaconsole'),
		('sans', 'arial', 'helvetica', 'swiss', 'freesans',
				'bitstreamverasans', 'verasans', 'verdana', 'tahoma'),
		('serif', 'times', 'freeserif', 'bitstreamveraserif', 'roman',
				'timesroman', 'timesnewroman', 'dutch', 'veraserif',
				'georgia'),
		('wingdings', 'wingbats'),
	)
	for set in aliases:
		found = None
		fname = None
		for name in set:
			if Sysfonts.has_key(name):
				found = Sysfonts[name]
				fname = name
				break
		if not found:
			continue
		for name in set:
			if not Sysfonts.has_key(name):
				Sysalias[name] = found


Sysfonts = {}
Sysalias = {}

def initsysfonts():
	""" initialize it all, called once """
	if sys.platform == 'win32':
		fonts = initsysfonts_win32()
	elif sys.platform == 'darwin':
		fonts = initsysfonts_darwin()
	else:
		fonts = initsysfonts_unix()
	Sysfonts.update(fonts)
	create_aliases()
	if not Sysfonts: #dummy so we don't try to reinit
		Sysfonts[None] = None



#the exported functions

def SysFont(name):
	"""pygame.font.SysFont(name, size, bold=False, italic=False) -> Font
		 create a pygame Font from system font resources

		 This will search the system fonts for the given font
		 name. You can also enable bold or italic styles, and
		 the appropriate system font will be selected if available.

		 This will always return a valid Font object, and will
		 fallback on the builtin pygame font if the given font
		 is not found.

		 Name can also be a comma separated list of names, in
		 which case set of names will be searched in order. Pygame
		 uses a small set of common font aliases, if the specific
		 font you ask for is not available, a reasonable alternative
		 may be used.
	"""
	if not Sysfonts:
		initsysfonts()
	
	gotbold = gotitalic = False
	fontname = None
	_name = name
	if name:
		allnames = name
		for name in allnames.split(','):
			name = _simplename(name)
			styles = Sysfonts.get(name)
			if not styles:
				styles = Sysalias.get(name)
			if styles:
				while not fontname:
					plainname = styles.get((False, False))

					#fontname = styles.get((bold, italic))
					#if plainname != fontname:
					#  gotbold = bold
					#  gotitalic = italic
					#elif not fontname:
					#  fontname = plainname

					fontname = plainname
			if fontname: break

	if fontname is None:
		raise FontNotFoundError(_name)
	return fontname


def get_fonts():
	"""pygame.font.get_fonts() -> list
		 get a list of system font names

		 Returns the list of all found system fonts. Note that
		 the names of the fonts will be all lowercase with spaces
		 removed. This is how pygame internally stores the font
		 names for matching.
	"""
	if not Sysfonts:
		initsysfonts()
	return Sysfonts.keys()


def match_font(name, bold=0, italic=0):
	"""pygame.font.match_font(name, bold=0, italic=0) -> name
		 find the filename for the named system font

		 This performs the same font search as the SysFont()
		 function, only it returns the path to the TTF file
		 that would be loaded. The font name can be a comma
		 separated list of font names to try.

		 If no match is found, None is returned.
	"""
	if not Sysfonts:
		initsysfonts()

	fontname = None
	allnames = name
	for name in allnames.split(','):
		name = _simplename(name)
		styles = Sysfonts.get(name)
		if not styles:
			styles = Sysalias.get(name)
		if styles:
			while not fontname:
				fontname = styles.get((bold, italic))
				if italic:
					italic = 0
				elif bold:
					bold = 0
				elif not fontname:
					fontname = styles.values()[0]
		if fontname: break
	return fontname
