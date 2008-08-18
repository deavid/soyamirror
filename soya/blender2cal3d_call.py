# -*- indent-tabs-mode: t -*-

# Soya 3D
# Copyright (C) 2006 Jean-Baptiste LAMY -- jiba@tuxfamily.org
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
import Blender

__file__ = sys.argv[sys.argv.index("-P") + 1]

sys.path.append(os.path.dirname(__file__))

import cal3d_export

cal3d_export.blendercal.bcconf.EXPORTGL    = True
cal3d_export.blendercal.bcconf.SUBMESHMODE = "object"
cal3d_export.blendercal.bcconf.XMLINDENT   = 2
cal3d_export.blendercal.bcconf.FILENAME    = sys.argv[-2]

ADDITIONAL_CFG = ""
MATERIAL_MAP = {}

def parse_args(args):
	global ADDITIONAL_CFG
	
	for arg in args:
		if "=" in arg:
			attr, val = arg.split("=")
			attr = attr.lower()
			try: val = int(val)
			except:
				try: val = float(val)
				except: pass
				
		if   attr.startswith("material_"): # A material map
			#self.materials_map[attr[9:]] = val
			MATERIAL_MAP[attr[len("material_"):]] = val
			print MATERIAL_MAP
			
		elif attr.startswith("lod"):
			cal3d_export.blendercal.bcconf.LOD = val
			
		elif attr == "config_text": # Config text
			print >> sys.stderr, "(reading config text %s)" % val
			parse_buffer(val)
			
		elif attr == "config_file": # Config file
			print >> sys.stderr, "(reading config file %s)" % val
			parse_args(open(var).read().split("\n"))
			
		elif attr == "scale":
			cal3d_export.blendercal.bcconf.SCALE = val
			
		else:
			ADDITIONAL_CFG += arg + "\n"
			
def parse_buffer(name):
	try: args = Blender.Text.get(name).asLines()
	except: pass
	else: parse_args(args)
	
parse_buffer("soya_params")
if sys.argv[-1] != "-": parse_buffer(sys.argv[-1])

cal3d_export.Cal3DExport(cal3d_export.blendercal.bcconf.FILENAME)

if ADDITIONAL_CFG:
	open(cal3d_export.blendercal.bcconf.FILENAME, "a").write("\n" + ADDITIONAL_CFG)
	
if MATERIAL_MAP:
	import glob
	for filename in glob.glob(os.path.join(os.path.dirname(cal3d_export.blendercal.bcconf.FILENAME), "*.xrf")):
		material = old_material = open(filename).read()
		for old, new in MATERIAL_MAP.items():
			material = material.replace(old, new)
		if old_material != material:
			open(filename, "w").write(material)
			
Blender.Quit()


