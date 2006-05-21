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
USE_ODE = True     # use ODE
#USE_ODE = False

INCDIR = [
  "ode-0.5/include",
  "/usr/include",
  "/usr/local/include",
  "/usr/X11R6/include",
  "/usr/include/freetype2",
  "/usr/local/include/freetype2",
  "/usr/include/cal3d",
  "/usr/local/include/cal3d",
  "/sw/include", # For Mac OS X
  "/home/cubicool/local/include"
  ]
LIBDIR = [
  "ode-0.5/lib",
  "/usr/lib",
  "/usr/local/lib",
  "/usr/X11R6/lib",
  "/sw/lib/", # For Mac OS X
  "/home/cubicool/local/lib"
  ]


import os, os.path, sys, glob, distutils.core, distutils.sysconfig
from distutils.core import setup, Extension

try:
  from Pyrex.Distutils import build_ext
  HAVE_PYREX = 1
except:
  HAVE_PYREX = 0

HERE = os.path.dirname(sys.argv[0])
ODE_DIR = os.path.join(HERE, "ode-0.5")

endian = sys.byteorder
if endian == "big":
  DEFINES = [("SOYA_BIG_ENDIAN", endian)]
else:
  DEFINES = []

from config import *

if sys.platform[:3] == "win":
  LIBS = ["m", "glew32", "SDL", "SDL_mixer", "freetype", "cal3d", "stdc++"]
else:
  #LIBS = ["m", "GLEW", "GL", "GLU", "SDL", "SDL_mixer", "freetype", "cal3d", "stdc++"]
  LIBS = ["m", "GLEW", "SDL", "freetype", "cal3d", "stdc++"]

SOYA_PYREX_SOURCES  = ["_soya.pyx", "matrix.c", "chunk.c" ]
SOYA_C_SOURCES      = ["_soya.c"  , "matrix.c", "chunk.c" ]

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
    
    
if USE_ODE:
  if "build" in sys.argv:
    if "--dont-build-ode" in sys.argv: sys.argv.remove("--dont-build-ode")
    elif os.path.exists(os.path.join(ODE_DIR, "lib", "libode.a")):
      # XXX Works only for Linux / Unix
      print "ODE and OPCODE have already been compiled; if you want to recompile them do:  cd %s ; make clean" % ODE_DIR
    else:
      print "Building ODE and OPCODE from %s" % ODE_DIR
      do("cd %s ; make clean" % ODE_DIR)
      do("cd %s ; make configure" % ODE_DIR)
      do("cd %s ; make" % ODE_DIR)
      print "ODE and OPCODE built successfully !"
      
  elif "sdist" in sys.argv:
    # Clean ODE, to remove configuration files and binaries
    do("cd %s ; make clean" % ODE_DIR)
  
  
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
              extra_compile_args = ["-w"], # with GCC ; disable (Pyrex-dependant) warning
              ),
    Extension("soya.opengl",   ["opengl.pyx"],
              include_dirs=INCDIR, library_dirs=LIBDIR,
              libraries=LIBS, define_macros=DEFINES,
              extra_compile_args = ["-w"], # with GCC ; disable (Pyrex-dependant) warning
              ),
    Extension("soya.sdlconst", ["sdlconst.pyx"],
              include_dirs=INCDIR, library_dirs=LIBDIR,
              libraries=LIBS, define_macros=DEFINES,
              extra_compile_args = ["-w"], # with GCC ; disable (Pyrex-dependant) warning
              ),
    ],
    "cmdclass" : {
        'build_ext'   : build_ext,            # Pyrex magic stuff
        'install_data': install_data_twisted, # Put data with the lib
        },
    }

  if USE_ODE:
      KARGS["ext_modules"].append(
          Extension("soya._ode", ["_ode.pyx", "matrix.c"],
              include_dirs=INCDIR, library_dirs=LIBDIR,
              libraries=LIBS + ["ode","stdc++"], define_macros=DEFINES,
              extra_compile_args = ["-w", "-O0"], # with GCC ; disable (Pyrex-dependant) warning
      ))
  
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
              extra_compile_args = ["-w"], # with GCC ; disable (Pyrex-dependant) warning
              ),
    Extension("soya.opengl",   ["opengl.c"],
              include_dirs=INCDIR, library_dirs=LIBDIR,
              libraries=LIBS, define_macros=DEFINES,
              extra_compile_args = ["-w"], # with GCC ; disable (Pyrex-dependant) warning
              ),
    Extension("soya.sdlconst", ["sdlconst.c"],
              include_dirs=INCDIR, library_dirs=LIBDIR,
              libraries=LIBS, define_macros=DEFINES,
              extra_compile_args = ["-w"], # with GCC ; disable (Pyrex-dependant) warning
              )
    ],
    "cmdclass" : {
        'install_data': install_data_twisted, # Put data with the lib
        },
    }

  if USE_ODE:
      KARGS["ext_modules"].append(
          Extension("soya._ode", ["_ode.c", "matrix.c"],
              include_dirs=INCDIR, library_dirs=LIBDIR,
              libraries=LIBS + ["ode","stdc++"], define_macros=DEFINES,
              extra_compile_args = ["-w", "-O0"], # with GCC ; disable (Pyrex-dependant) warning
      ))
  

setup(
  name         = "Soya",
  version      = "0.10.5rc1",
  license      = "GPL",
  description  = "A practical high-level object-oriented 3D engine for Python.",
  long_description  = """A practical high-level object-oriented 3D engine for Python.
Soya is designed with game in mind. It includes heightmaps, particles systems, animation support,...""",
  keywords     = "3D engine openGL python",
  author       = "Jiba (LAMY Jean-Baptiste), Blam (LAMY Bertrand), LunacyMaze (GHISLAIN Mary)",
  author_email = "jiba@tuxfamily.org",
  url          = "http://gna.org/projects/soya/",
  classifiers  = [
  "Topic :: Multimedia :: Graphics :: 3D Rendering",
  "Topic :: Software Development :: Libraries :: Python Modules",
  "Programming Language :: Python",
  "Intended Audience :: Developers",
  "Development Status :: 5 - Production/Stable",
  "License :: OSI Approved :: GNU General Public License (GPL)",
  ],
  
  scripts      = ["soya_editor"],
  package_dir  = {"soya" : ""},
  packages     = ["soya", "soya.editor", "soya.pudding", "soya.pudding.ext", "soya.pudding.styles"],
  
  data_files   = [(os.path.join("soya", "data"),
                   [os.path.join("data", file) for file in os.listdir("data") if (file != "CVS") and (file != ".arch-ids") and (file != ".svn")]
                   )],
  **KARGS)

