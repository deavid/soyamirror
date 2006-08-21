# -*- indent-tabs-mode: t -*-

# Soya
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

"""soya.cerealizer

Import this module to make Soya's objects cerealizable.
"""

import sys
import cerealizer
import soya, soya.cursor, soya.laser, soya.ray, soya.spc_material, soya.label3d
_soya = sys.modules["soya._soya"]


class SavedInAPathHandler(cerealizer.ObjHandler):
	def collect(self, obj, dumper):
		if (not soya._SAVING is obj) and obj._filename: # self is saved in another file, save filename only
			return cerealizer.Handler.collect(self, obj, dumper)
		else: return cerealizer.ObjHandler.collect(self, obj, dumper)
		
	def dump_obj(self, obj, dumper, s):
		cerealizer.ObjHandler.dump_obj(self, obj, dumper, s)
		if (not soya._SAVING is obj) and obj._filename: # self is saved in another file, save filename only
			dumper.dump_ref(obj._filename, s)
		else: dumper.dump_ref("", s)
		
	def dump_data(self, obj, dumper, s):
		if (not soya._SAVING is obj) and obj._filename: # self is saved in another file, save filename only
			return cerealizer.Handler.dump_data(self, obj, dumper, s)
		else: cerealizer.ObjHandler.dump_data(self, obj, dumper, s)
		
	def undump_obj(self, dumper, s):
		filename = dumper.undump_ref(s)
		if filename: return self.Class._reffed(filename)
		return cerealizer.ObjHandler.undump_obj(self, dumper, s)
	
	def undump_data(self, obj, dumper, s):
		if not getattr(obj, "_filename", 0): # else, has been get'ed
			cerealizer.ObjHandler.undump_data(self, obj, dumper, s)

cerealizer.register_class(soya.Vertex)
cerealizer.register_class(soya.World, SavedInAPathHandler(soya.World))
cerealizer.register_class(soya.NoBackgroundAtmosphere)
cerealizer.register_class(soya.FixTraveling)
cerealizer.register_class(soya.SimpleModel, SavedInAPathHandler(soya.SimpleModel))
cerealizer.register_class(soya.Material, SavedInAPathHandler(soya.Material))
cerealizer.register_class(soya.CylinderSprite)
cerealizer.register_class(soya.Light)
cerealizer.register_class(soya.TravelingCamera)
cerealizer.register_class(soya.CoordSystState)
cerealizer.register_class(soya.CoordSystSpeed)
cerealizer.register_class(soya.Vector)
cerealizer.register_class(soya.Point)
cerealizer.register_class(soya.Image, SavedInAPathHandler(soya.Image))
cerealizer.register_class(soya.CellShadingModel, SavedInAPathHandler(soya.CellShadingModel))
cerealizer.register_class(soya._soya._AnimatedModelData)
cerealizer.register_class(soya.Model, SavedInAPathHandler(soya.Model))
cerealizer.register_class(soya.SkyAtmosphere)
cerealizer.register_class(soya.Portal)
cerealizer.register_class(soya.Terrain)
cerealizer.register_class(soya.Face)
cerealizer.register_class(soya.Atmosphere)
cerealizer.register_class(soya.TreeModel, SavedInAPathHandler(soya.TreeModel))
cerealizer.register_class(soya.SolidModel, SavedInAPathHandler(soya.SolidModel))
cerealizer.register_class(soya.Particles)
cerealizer.register_class(soya.Sprite)
cerealizer.register_class(soya.Bonus)
cerealizer.register_class(soya.AnimatedModel, SavedInAPathHandler(soya.AnimatedModel))
#cerealizer.register_class(soya.Cal3dBody)
cerealizer.register_class(soya.Body)
#cerealizer.register_class(soya.SavedInAPath)
cerealizer.register_class(soya.ThirdPersonTraveling)
cerealizer.register_class(soya.cursor.Cursor)
cerealizer.register_class(soya.label3d.Label3D)
cerealizer.register_class(soya.laser.Laser)
cerealizer.register_class(soya.ray.Ray)
cerealizer.register_class(soya.ray.HalfRay)
cerealizer.register_class(soya.spc_material.ZoomingMaterial, SavedInAPathHandler(soya.spc_material.ZoomingMaterial))
cerealizer.register_class(soya.spc_material.MovingMaterial, SavedInAPathHandler(soya.spc_material.MovingMaterial))
cerealizer.register_class(soya.spc_material.RotatingMaterial, SavedInAPathHandler(soya.spc_material.RotatingMaterial))
cerealizer.register_class(soya.Font, SavedInAPathHandler(soya.Font))

cerealizer.register_class(_soya.SimpleModelBuilder)
cerealizer.register_class(_soya.CellShadingModelBuilder)
cerealizer.register_class(_soya.SolidModelBuilder)
cerealizer.register_class(_soya.TreeModelBuilder)
#cerealizer.register_class(_soya.RaypickContext)
#cerealizer.register_class(_soya.CoordSyst)
cerealizer.register_class(_soya.FlagFirework)
cerealizer.register_class(_soya.Fountain)
cerealizer.register_class(_soya.Smoke)
#cerealizer.register_class(_soya.Traveling)
#cerealizer.register_class(_soya.PythonCoordSyst)
cerealizer.register_class(_soya.FlagSubFire)
#cerealizer.register_class(_soya.Position)
#cerealizer.register_class(_soya.ModelBuilder)
#cerealizer.register_class(_soya._CObj)
cerealizer.register_class(soya.DisplayList)

if hasattr(soya, "Sound"):
	# Has sound / OpenAL support
	cerealizer.register_class(soya.WAVSound, SavedInAPathHandler(soya.WAVSound))
	cerealizer.register_class(soya.OGGVorbisSound, SavedInAPathHandler(soya.OGGVorbisSound))
	cerealizer.register_class(soya.SoundPlayer)
	
# Aliases for backward compatibility
cerealizer.register_alias(soya.Body                   , "soya.Cal3dVolume")
cerealizer.register_alias(soya.Body                   , "soya.Cal3dBody")
cerealizer.register_alias(soya.Body                   , "soya.Volume")
cerealizer.register_alias(soya.Model                  , "soya.Shape")
cerealizer.register_alias(soya.SimpleModel            , "soya.SimpleShape")
cerealizer.register_alias(soya.SolidModel             , "soya.SolidShape")
cerealizer.register_alias(soya.CellShadingModel       , "soya.CellShadingShape")
cerealizer.register_alias(soya.TreeModel              , "soya.TreeShape")
cerealizer.register_alias(soya.AnimatedModel          , "soya.Cal3dShape")
cerealizer.register_alias(soya.Terrain                , "soya.Land")
cerealizer.register_alias(soya.SimpleModelBuilder     , "soya.SimpleShapifier")
cerealizer.register_alias(soya.SimpleModelBuilder     , "_soya.SimpleShapifier")
cerealizer.register_alias(soya.SolidModelBuilder      , "soya.SolidShapifier")
cerealizer.register_alias(soya.SolidModelBuilder      , "_soya.SolidShapifier")
cerealizer.register_alias(soya.CellShadingModelBuilder, "soya.CellShadingShapifier")
cerealizer.register_alias(soya.CellShadingModelBuilder, "_soya.CellShadingShapifier")
cerealizer.register_alias(soya.TreeModelBuilder       , "soya.TreeShapifier")
cerealizer.register_alias(soya.TreeModelBuilder       , "_soya.TreeShapifier")

if __name__ == "__main__": # Testing stuff
	class W(soya.World):
		def __setstate__(self, state):
			print "children", self.children
			print "W.__setstate__", state
			soya.World.__setstate__(self, state)
			print "children", self.children
	cerealizer.register_class(W)
		
	class V(soya.Body):
		def __setstate__(self, state):
			print "V.__setstate__", state
	cerealizer.register_class(V)
	
	w = W()
	#v = soya.Body(w)
	v = V(w)
	
	
	print w.__getstate__()
	
	s = cerealizer.dumps(w)
	print s
	z = cerealizer.loads(s)
	print z
	print
	
	print z.children[0].parent
	
