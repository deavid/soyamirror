#! /usr/bin/env python
# -*- indent-tabs-mode: t -*-

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
from StringIO import StringIO
from os.path import exists


# Modify the following if needed :
USE_OPENAL = 1     # use OpenAL
#USE_OPENAL = 0

# Modify the following if needed :
UNIVERSAL_BINARY = True #try to build a UB if possible


INCDIR = [
	#"ode-0.5/include",
	"/usr/include",
	"/usr/local/include",
	"/usr/X11R6/include",
	"/usr/X11/include",
	"/usr/include/freetype2",
	"/usr/X11/include/freetype2",
	"/usr/local/include/freetype2",
	"/usr/include/cal3d",
	"/usr/local/include/cal3d",
	"/sw/include", # For Mac OS X "fink"
	"/opt/local/include",# For Mac OS X "darwin port"
	"/opt/local/include/freetype2", # For Mac OS X "darwin port"
	#"/System/Library/Frameworks/OpenAL.framework/Headers/",
	]
LIBDIR = [
	#"ode-0.5/lib",
	"/usr/lib",
	"/usr/local/lib",
	"/opt/local/lib", # For Mac OS X "darwin port"
	"/usr/X11R6/lib",
	"/usr/X11/lib",
	"/sw/lib/", # For Mac OS X
	#"/System/Library/Frameworks/OpenAL.framework/"
	]
	
COMPILE_ARGS = [
	"-w",  # with GCC ; disable (Pyrex-dependant) warning
	"-fsigned-char", # On Mac, char are unsigned by default, contrary to Linux or Windows.
	]


import os, os.path, sys, glob, distutils.core, distutils.sysconfig
from distutils.core import setup, Extension

from tempfile import NamedTemporaryFile


def framework_exist(framework_name): #Os X related stuff. test if a .Framework are present or not.
	tmp = NamedTemporaryFile()
	ret = os.system("ld -framework %s -o %s -r 2> /dev/null"%(framework_name,tmp.name))
	return not ret


BUILDING = ("build" in sys.argv[1:]) and not ("--help" in sys.argv[1:])
INSTALLING = ("install" in sys.argv[1:]) and not ("--help" in sys.argv[1:])
SDISTING = ("sdist" in sys.argv[1:]) and not ("--help" in sys.argv[1:])

MACOSX_DEPLOYMENT_TARGET  = os.getenv('MACOSX_DEPLOYMENT_TARGET')
try:
	from Pyrex.Distutils import build_ext
	USE_PYREX = 1
except ImportError:
	USE_PYREX = 0
	print "No Pyrex found"

# Only enable Pyrex compilation for SVN sources
if not os.path.exists(os.path.join(os.path.dirname(__file__), ".svn")):
	print "None repository source, pyrex disabled"
	USE_PYREX = 0

if USE_PYREX: print "Pyrex compilation enabled!"
else:          print "Pyrex compilation disabled."
	
# env hack as pyrex change this variable
if MACOSX_DEPLOYMENT_TARGET is None:
	os.environ.pop('MACOSX_DEPLOYMENT_TARGET',None)
else:
	os.environ['MACOSX_DEPLOYMENT_TARGET'] = MACOSX_DEPLOYMENT_TARGET

HERE = os.path.dirname(sys.argv[0])
#ODE_DIR = os.path.join(HERE, "ode-0.5")
DEFINES = []
endian = sys.byteorder
if endian == "big":
	DEFINES.append(("SOYA_BIG_ENDIAN", endian))

#from config import *

if sys.platform[:3] == "win":
	LIBS = ["m", "glew32", "SDL", "SDL_mixer", "freetype", "cal3d", "stdc++", "ode"]
else:
	LIBS = ["m", "GLEW", "SDL", "freetype", "cal3d", "stdc++","ode"]
	FRAMEWORKS=[]

SOYA_PYREX_SOURCES  = ["_soya.pyx", "matrix.c", "chunk.c"]
SOYA_C_SOURCES      = ["_soya.c"  , "matrix.c", "chunk.c"]


print "BUILDING", BUILDING
# Generate config.pxd and config.pyx

if BUILDING:
	CONFIG_PXD_PATH = os.path.join(HERE,"config.pxd")
	CONFIG_PYX_PATH = os.path.join(HERE,"config.pyx")
	CONFIG_PXD_FILE = StringIO()
	CONFIG_PYX_FILE = StringIO()
	CONFIG_PXD_FILE.write("""# Machine-generated file, DO NOT EDIT!\n\n""")
	CONFIG_PYX_FILE.write("""# Machine-generated file, DO NOT EDIT!\n\n""")

	if USE_OPENAL:
		print "Sound support (with OpenAL) enabled..."

		CONFIG_PXD_FILE.write("""include "sound/al.pxd"\n""")
		CONFIG_PYX_FILE.write("""include "sound/sound.pyx"\n""")
	else:
		print "Sound support (with OpenAL) disabled..."
		CONFIG_PYX_FILE.write("""include "sound/nosound.pyx"\n""")
	if exists(CONFIG_PXD_PATH) and exists(CONFIG_PYX_PATH):
		config_pxd_orig = open(CONFIG_PXD_PATH).read()
		config_pyx_orig = open(CONFIG_PYX_PATH).read()
		write = config_pxd_orig != CONFIG_PXD_FILE.getvalue() or \
		        config_pyx_orig != CONFIG_PYX_FILE.getvalue()
	else:
		write = True
	
	if write:
		print "\twriting new sound configuration"
		config_pxd_orig = open(CONFIG_PXD_PATH,'w',0).write(CONFIG_PXD_FILE.getvalue())
		config_pyx_orig = open(CONFIG_PYX_PATH,'w',0).write(CONFIG_PYX_FILE.getvalue())


	
elif INSTALLING:
		auto_files = ("config.pxd", "config.pyx")
		missing_files = []
		for f in auto_files:
			if not os.path.exists(os.path.join(HERE,f)):
				missing_files.append(f)
		if missing_files:
			if len(missing_files)>1:
				s = ", ".join(missing_files[:-1])+" and "+missing_files[-1] + " have"
			else :
				s = missing_files[0]+ " has"
			print >> sys.stderr, s ,"not been generated please run 'setup.py build'"
			sys.exit(2)

if USE_OPENAL:
	#print "OpenAl exist :",framework_exist('OpenAL')
	if "darwin" in sys.platform and framework_exist('OpenAL'):
		print "using OpenAl.Framework"
		FRAMEWORKS.append('OpenAL')
		DEFINES.append(('SOYA_MACOSX',1))
	else:
		LIBS.append("openal")


if "darwin" in sys.platform:
	kernel_version = os.uname()[2] # 8.4.3
	major_version = int(kernel_version.split('.')[0])
	if UNIVERSAL_BINARY and major_version >=8 :
		os.environ['CFLAGS'] = "-arch ppc -arch i386 "+ os.environ.get('CFLAGS','')
		#try to use framework if present.
	else:
		os.environ['ARCHFLAGS'] = ' '
	to_be_remove_lib =[]
	print "Looking for available framework to use instead of a UNIX library"
	for lib in LIBS:
		if framework_exist(lib):
			to_be_remove_lib.append(lib)
			FRAMEWORKS.append(lib)
			print "%-64sfound" % ("%s.framework" % lib)
		else:
			print "%-60snot found" % ("%s.framework" % lib)
	for lib in to_be_remove_lib:
		LIBS.remove(lib)
	for framework in FRAMEWORKS:
		DEFINES.append(('HAS_FRAMEWORK_%s'%framework.upper(),1))
		#os.environ['CFLAGS']= ('-DHAS_FRAMEWORK_%s '%framework.upper()) + os.environ.get('CFLAGS','')
		os.environ['CFLAGS']= ('-framework %s '%framework) + os.environ.get('CFLAGS','')
	os.environ['LDFLAGS']= '-Wl,-dylib_file,/System/Library/Frameworks/OpenGL.framework/Versions/A/Libraries/libGL.dylib:/System/Library/Frameworks/OpenGL.framework/Versions/A/Libraries/libGL.dylib '+os.environ.get('LDFLAGS','')

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
		
		
	
	
if USE_PYREX:
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
	version      = "0.14",
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
	packages     = ["soya", "soya.gui", "soya.editor", "soya.pudding", "soya.pudding.ext", "soya.pudding.styles", "soya.blendercal", "soya.tofu"],
	
	data_files   = [(os.path.join("soya", "data"),
									 [os.path.join("data", file) for file in os.listdir("data") if (file != "CVS") and (file != ".arch-ids") and (file != ".svn")]
									 )],
	**KARGS)

