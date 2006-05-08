#! /usr/bin/env python

# Cerealizer
# Copyright (C) 2005 Jean-Baptiste LAMY
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

import os.path, sys, distutils.core

distutils.core.setup(name         = "Cerealizer",
                     version      = "0.1",
                     license      = "GPL",
                     description  = "A secure pickle-like module",
                     long_description = """A secure pickle-like module.
It support basic types (int, string, unicode, tuple, list, dict, set,...),
old and new-style classes (you need to register the class for security), object cycles,
and it can be extended to support C-defined type.""",
                     author       = "Lamy Jean-Baptiste (Jiba)",
                     author_email = "jibalamy@free.fr",
#                     url          = "http://home.gna.org/oomadness/fr/slune/index.html",
                     
                     package_dir  = {"cerealizer" : ""},
                     packages     = ["cerealizer"],
                     )
