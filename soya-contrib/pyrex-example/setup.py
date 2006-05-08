#! /usr/bin/env python

import os.path, sys, glob, distutils.core, distutils.sysconfig
from distutils.core import setup, Extension

# im presuming this is in soya-contrib.
# adjust this to point to your soya source

PATH_TO_SOYA=os.path.join('..','..','soya')

INCDIR = [
  "/usr/include",
  "/usr/local/include",
  "/usr/X11R6/include",
  "/usr/include/freetype2",
  "/usr/local/include/freetype2",
  # if you dont use soya's ode
  #"/usr/include/ode",
  #"/usr/local/include/ode",
  # if you use soya's ode
  os.path.join(PATH_TO_SOYA,"ode"),
  "/sw/include", # For Mac OS X
  PATH_TO_SOYA,
  ]

# we dont need any libs so we dont define any
# put the paths to your libs here 
LIBDIR = [
  #"/usr/lib",
  #"/usr/local/lib",
  #"/usr/X11R6/lib",
  #"/sw/lib/", # For Mac OS X
  ]

# put any include paths for pyrex here
PYREX_INCDIR = [
  PATH_TO_SOYA,
  os.path.join(PATH_TO_SOYA,'definitions'),
  ]

endian = sys.byteorder
if endian == "big":
  DEFINES = [("SOYA_BIG_ENDIAN", endian)]
else:
  DEFINES = []

# it might be nice to use a config file called config.py to set user settings/overrides
#from config import *

# i dont think we need any of this 
# altho should we link to _soya.so ?
if sys.platform[:3] == "win":
  LIBS = ["m", "opengl32", "glu32", "SDL", "freetype", "cal3d", "stdc++"]
else:
  LIBS = ["m", "GL", "GLU", "SDL", "freetype", "cal3d", "stdc++"]

#LIBS=[]

# list of all the pyrex files to run pyrexc on 
SOYA_PYREX_SOURCES  = ["test.pyx"]
# list of all files to compile with the c compiler
SOYA_C_SOURCES      = ["test.c"]

import distutils.command.build_ext
import Pyrex.Compiler.Main

from Pyrex.Compiler.Errors import PyrexError
from distutils.dep_util import newer
import os
import sys

def replace_suffix(path, new_suffix):
    return os.path.splitext(path)[0] + new_suffix

# this custom class allows us to include directories in pyrex's search path
class build_ext(distutils.command.build_ext.build_ext):

  description = ("compile Pyrex scripts, then build C/C++ extensions "
                 "(compile/link to build directory)")

  def finalize_options(self):
      distutils.command.build_ext.build_ext.finalize_options(self)

  def swig_sources(self, sources):
      if not self.extensions:
          return
      
      pyx_sources = [source for source in sources
                     if source.endswith('.pyx')]
      other_sources = [source for source in sources
                       if not source.endswith('.pyx')]
      c_sources = []

      for pyx in pyx_sources:
          # should I raise an exception if it doesn't exist?
          if os.path.exists(pyx):
              source = pyx
              target = replace_suffix(source, '.c')
              c_sources.append(target)
              if newer(source, target) or self.force:
                  self.pyrex_compile(source)
      return c_sources + other_sources

  def pyrex_compile(self, source):
      options = Pyrex.Compiler.Main.CompilationOptions(
          show_version=0,
          use_listing_file=0,
          errors_to_stderr=1,
          include_path=self.get_pxd_include_paths(),
          c_only=1,
          obj_only=1,
          output_file=None)
      
      result = Pyrex.Compiler.Main.compile(source, options)
      if result.num_errors <> 0:
          sys.exit(1)

  def get_pxd_include_paths(self):
      """Override this to return a list of include paths for pyrex.
      """
      return PYREX_INCDIR


# from the distultis documentation:
"""
If the foo extension belongs in the root package, the setup script for this could be

from distutils.core import setup
setup(name = "foobar", version = "1.0",
  ext_modules = [Extension("foo", ["foo.c"])])

If the extension actually belongs in a package, say foopkg, then

With exactly the same source tree layout, this extension can be put in the foopkg 
package simply by changing the name of the extension:

from distutils.core import setup
setup(name = "foobar", version = "1.0",
  ext_modules = [Extension("foopkg.foo", ["foo.c"])])

"""


KARGS = {
  "ext_modules" : [
  Extension("test", SOYA_PYREX_SOURCES,
            include_dirs=INCDIR, library_dirs=LIBDIR,
            libraries=LIBS, define_macros=DEFINES,
            extra_compile_args = ["-w"], # with GCC ; disable (Pyrex-dependant) warning
            ),
  ],
  "cmdclass" : {
      'build_ext'   : build_ext,            # Pyrex magic stuff
      },
  }

setup(
  name         = "test",
  version      = "0.0.1",
  #license      = "GPL",
  #description  = "a description of your module",
  #keywords     = "test module replace with keywords",
  #author       = "names and nicks of authors",
  #author_email = "main_author@email.com",
  #url          = "http://www.myproject.org",
  #classifiers  = [
  #"Topic :: Multimedia :: Graphics :: 3D Rendering",
  #"Topic :: Software Development :: Libraries :: Python Modules",
  #"Programming Language :: Python",
  #"Intended Audience :: Developers",
  #"Development Status :: 5 - Production/Stable",
  #"License :: OSI Approved :: GNU General Public License (GPL)",
  #],
  
  package_dir  = {"test" : "."},
  
  **KARGS)

