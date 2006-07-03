# -*- indent-tabs-mode: t -*-


from soya._ode import *
import soya._ode as _ode
import soya

class World(_ode._World, soya.World):
		pass

_ode.World = World

class Body(_ode._Body, soya.World):
		pass

_ode.Body = Body

class Terrain(_ode._Terrain):
		pass

_ode.Terrain = Terrain

class GeomModel(_ode._GeomModel):
		pass

_ode.GeomModel = GeomModel

class GeomTerrain(_ode._GeomTerrain):
		pass

_ode.GeomTerrain = GeomTerrain


