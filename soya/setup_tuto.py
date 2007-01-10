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

import os.path, sys, re

HERE    = os.path.dirname(sys.argv[0])

VERSION = re.findall(r'version\s*=\s*"(.*?)"', open(os.path.join(HERE, "setup.py")).read())[0]

# if "sdist" in sys.argv:
#   c = """cd %s; tar -cvjf ~/dist/SoyaTutorial-%s.tar.bz2 tutorial""" % (HERE, VERSION)
#   print c
#   os.system(c)

import os.path, sys, glob, distutils.core, distutils.sysconfig
from distutils.core import setup

sys.argv.extend(["--template", "MANIFEST_tuto.in", "--manifest", "MANIFEST_tuto"])

setup(
	name         = "SoyaTutorial",
	version      = "0.13rc2",
	license      = "GPL",
	description  = "Tutorial for Soya, a practical high-level object-oriented 3D engine for Python.",
	long_description  = """Tutorial for Soya, a practical high-level object-oriented 3D engine for Python.
Soya is designed with game in mind. It includes heightmaps, particles systems, animation support,...""",
	keywords     = "3D engine openGL python",
	author       = "Jiba (LAMY Jean-Baptiste), Blam (LAMY Bertrand), LunacyMaze (GHISLAIN Mary)",
	author_email = "jiba@tuxfamily.org",
	url          = "http://home.gna.org/oomadness/en/soya/index.html",
	classifiers  = [
	"Topic :: Multimedia :: Graphics :: 3D Rendering",
	"Topic :: Software Development :: Libraries :: Python Modules",
	"Programming Language :: Python",
	"Intended Audience :: Developers",
	"Development Status :: 5 - Production/Stable",
	"License :: OSI Approved :: GNU General Public License (GPL)",
	],
	
	data_files   = [
	("tutorial", ["tutorial",]),
	],
	
	)

