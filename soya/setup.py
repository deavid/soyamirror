# -*- indent-tabs-mode: t -*-

#! /usr/bin/env python

# Soya 3D
# Copyright (C) 2001-2002 Jean-Baptiste LAMY -- jiba@tuxfamily
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


# Modify the following if needed :
USE_OPENAL = 1     # use OpenAL
#USE_OPENAL = 0

	

INCDIR = [
	#"ode-0.5/include",
	"/usr/include",
	"/usr/local/include",
	"/usr/X11R6/include",
	"/usr/include/freetype2",
	"/usr/local/include/freetype2",
	"/usr/include/cal3d",
	"/usr/local/include/cal3d",
	"/sw/include", # For Mac OS X "fink"
	"/opt/local/include", # For Mac OS X "darwin port"
	#"/System/Library/Frameworks/OpenAL.framework/Headers/",
	]
LIBDIR = [
	#"ode-0.5/lib",
	"/usr/lib",
	"/usr/local/lib",
	"/opt/local/lib", # For Mac OS X "darwin port"
	"/usr/X11R6/lib",
	"/sw/lib/", # For Mac OS X
	#"/System/Library/Frameworks/OpenAL.framework/"
	]
	
COMPILE_ARGS = [
	"-w",  # with GCC ; disable (Pyrex-dependant) warning
	"-fsigned-char", # On Mac, char are unsigned by default, contrary to Linux or Windows.
	]


import os, os.path, sys, glob, distutils.core, distutils.sysconfig
from distutils.core import setup, Extension

BUILDING = ("build" in sys.argv[1:]) and not ("--help" in sys.argv[1:])
SDISTING = ("sdist" in sys.argv[1:]) and not ("--help" in sys.argv[1:])


try:
	from Pyrex.Distutils import build_ext
	HAVE_PYREX = 1
except:
	HAVE_PYREX = 0

HERE = os.path.dirname(sys.argv[0])
#ODE_DIR = os.path.join(HERE, "ode-0.5")
DEFINES = []
endian = sys.byteorder
if endian == "big":
	DEFINES.append(("SOYA_BIG_ENDIAN", endian))

#from config import *

if sys.platform[:3] == "win":
	LIBS = ["m", "glew32", "SDL", "SDL_mixer", "freetype", "cal3d", "stdc++","ode"]
else:
	#LIBS = ["m", "GLEW", "GL", "GLU", "SDL", "SDL_mixer", "freetype", "cal3d", "stdc++"]
	LIBS = ["m", "GLEW", "SDL", "freetype", "cal3d", "stdc++","ode"]

SOYA_PYREX_SOURCES  = ["_soya.pyx", "matrix.c", "chunk.c" ]
SOYA_C_SOURCES      = ["_soya.c"  , "matrix.c", "chunk.c" ]


print "BUILDING", BUILDING
# Generate config.pxd and config.pyx
if BUILDING:
	CONFIG_PXD_FILE = open(os.path.join(HERE,"config.pxd"), "w", 0)
	CONFIG_PXD_FILE.write("""# Machine-generated file, DO NOT EDIT!

""")
	CONFIG_PYX_FILE = open(os.path.join(HERE,"config.pyx"), "w", 0)
	CONFIG_PYX_FILE.write("""# Machine-generated file, DO NOT EDIT!

""")
	if USE_OPENAL:
		print "Sound support (with OpenAL) enabled..."

		CONFIG_PXD_FILE.write("""include "sound/al.pxd"\n""")
		CONFIG_PYX_FILE.write("""include "sound/sound.pyx"\n""")
	else:
		print "Sound support (with OpenAL) disabled..."
		CONFIG_PYX_FILE.write("""include "sound/nosound.pyx"\n""")

if USE_OPENAL:
	if sys.platform == 'darwin':# and os.path.exists("/System/Library/Frameworks/OpenAL.framework/"):
		#COMPILE_ARGS.append("-framework OpenAL")
		#print "using Tiger OpenAl.framework"
		DEFINES.append(('SOYA_MACOSX',1))
	LIBS.append("openal")
		

# Taken from Twisted ; thanks to Christopher Armstrong :
#   make sure data files are installed in twisted package
#   this is evil.
import distutils.command.install_data
class install_data_twisted(distutils.command.install_data.install_data):
	def finalize_options(self):
		self.set_undefined_options('install', ('install_lib', 'install_dir'))
		distutils.command.install_data.install_data.finalize_options(self)


def do(command):
	print command
	r = os.system(command)
	if r:
		print "Failed !"
		sys.exit(1)
		
		
	
	
if HAVE_PYREX:
	# make pyrex recompile the soya module if any of the .pyx files have changed
	# should probably recurse directories
	# much nicer than having to use --force
	soya_pyx_mtime=os.path.getmtime('_soya.pyx')
	for f in glob.glob('*.pyx'):
		if os.path.getmtime(f)>soya_pyx_mtime:
			os.utime('_soya.pyx',None)
			break
	
	KARGS = {
		"ext_modules" : [
		Extension("soya._soya", SOYA_PYREX_SOURCES,
							include_dirs=INCDIR, library_dirs=LIBDIR,
							libraries=LIBS, define_macros=DEFINES,
							extra_compile_args = COMPILE_ARGS, 
							),
		Extension("soya.opengl",   ["opengl.pyx"],
							include_dirs=INCDIR, library_dirs=LIBDIR,
							libraries=LIBS, define_macros=DEFINES,
							extra_compile_args = COMPILE_ARGS, 
							),
		Extension("soya.sdlconst", ["sdlconst.pyx"],
							include_dirs=INCDIR, library_dirs=LIBDIR,
							libraries=LIBS, define_macros=DEFINES,
							extra_compile_args = COMPILE_ARGS, 
							),
		],
		"cmdclass" : {
				'build_ext'   : build_ext,            # Pyrex magic stuff
				'install_data': install_data_twisted, # Put data with the lib
				},
		}

	
else:
	print
	print "PYREX NOT FOUND"
	print "Compiling the c file WITHOUT reading any .pyx files"
	print "This is OK as long as you don't modify Soya sources."
	print
	
 
	KARGS = {
		"ext_modules" : [
		Extension("soya._soya", SOYA_C_SOURCES,
							include_dirs=INCDIR, library_dirs=LIBDIR,
							libraries=LIBS, define_macros=DEFINES,
							extra_compile_args = COMPILE_ARGS, 
							),
		Extension("soya.opengl",   ["opengl.c"],
							include_dirs=INCDIR, library_dirs=LIBDIR,
							libraries=LIBS, define_macros=DEFINES,
							extra_compile_args = COMPILE_ARGS, 
							),
		Extension("soya.sdlconst", ["sdlconst.c"],
							include_dirs=INCDIR, library_dirs=LIBDIR,
							libraries=LIBS, define_macros=DEFINES,
							extra_compile_args = COMPILE_ARGS, 
							)
		],
		"cmdclass" : {
				'install_data': install_data_twisted, # Put data with the lib
				},
		}

	

setup(
	name         = "Soya",
	version      = "0.13rc1",
	license      = "GPL",
	description  = "A practical high-level object-oriented 3D engine for Python.",
	long_description  = """A practical high-level object-oriented 3D engine for Python.
Soya is designed with game in mind. It includes heightmaps, particles systems, animation support,...""",
	keywords     = "3D engine openGL python",
	author       = "Jiba (LAMY Jean-Baptiste)",
	author_email = "jiba@tuxfamily.org",
	url          = "http://home.gna.org/oomadness/en/soya/index.html",
	classifiers  = [
  "Topic :: Games/Entertainment",
	"Topic :: Multimedia :: Graphics :: 3D Rendering",
	"Topic :: Software Development :: Libraries :: Python Modules",
	"Programming Language :: Python",
	"Intended Audience :: Developers",
	"Development Status :: 5 - Production/Stable",
	"License :: OSI Approved :: GNU General Public License (GPL)",
	],
	
	scripts      = ["soya_editor"],
	package_dir  = {"soya" : ""},
	packages     = ["soya", "soya.editor", "soya.pudding", "soya.pudding.ext", "soya.pudding.styles", "soya.blendercal"],
	
	data_files   = [(os.path.join("soya", "data"),
									 [os.path.join("data", file) for file in os.listdir("data") if (file != "CVS") and (file != ".arch-ids") and (file != ".svn")]
									 )],
	**KARGS)

