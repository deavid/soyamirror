
from soya._ode import *
import soya._ode as _ode
import soya

class World(_ode._World, soya.World):
    pass

_ode.World = World

class Body(_ode._Body, soya.World):
    pass

_ode.Body = Body

class Land(_ode._Land):
    pass

_ode.Land = Land

class GeomShape(_ode._GeomShape):
    pass

_ode.GeomShape = GeomShape

class GeomLand(_ode._GeomLand):
    pass

_ode.GeomLand = GeomLand


