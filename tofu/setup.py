#! /usr/bin/env python

# TOFU
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

distutils.core.setup(name         = "Tofu",
                     version      = "0.4",
                     license      = "GPL",
                     description  = "A practical high-level network game engine",
                     long_description = """Tofu is a practical high-level network game engine,
written in Python and based on Twisted.

It currently support client-server and single player mode;
peer-to-peer mode may be added later.

A small Tk-based demo is included, as well as docstring.""",
                     author       = "Lamy Jean-Baptiste (Jiba)",
                     author_email = "jibalamy@free.fr",
#                     url          = "http://home.gna.org/oomadness/fr/slune/index.html",
                     
                     package_dir  = {"tofu" : ""},
                     packages     = ["tofu"],
                     )
