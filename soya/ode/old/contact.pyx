# -*- indent-tabs-mode: t -*-

############################## Contact ################################
cdef class GeomObject(_soya.CoordSyst)

cdef class Contact:
		"""This class represents a contact between two bodies in one point.

		A Contact object stores all the input parameters for a ContactJoint.
		This class wraps the ODE dContact structure which has 3 components::

		 struct dContact {
			 dSurfaceParameters surface;
			 dContactGeom geom;
			 dVector3 fdir1;
		 };    

		This wrapper class provides methods to get and set the items of those
		structures.
		"""
		
		cdef dContact _contact

		def __new__(self, *args, **kw):
				self._contact.surface.mode = ContactBounce
				self._contact.surface.mu   = dInfinity

				self._contact.surface.bounce = 0.1

		property mode:
				def __get__(self):
						return self._contact.surface.mode

				def __set__(self, int m):
						self._contact.surface.mode = m

		property mu:
				def __get__(self):
						return self._contact.surface.mu
		
				def __set__(self, dReal mu):
						self._contact.surface.mu = mu

		property mu2:
				def __get__(self):
						return self._contact.surface.mu2
		
				def __set__(self, dReal mu):
						self._contact.surface.mu2 = mu

		property bounce:
				def __get__(self):
						return self._contact.surface.bounce

				def __set__(self, b):
						self._contact.surface.bounce = b

		property bounce_vel:
				def __get__(self):
						return self._contact.surface.bounce_vel

				def __set__(self, bv):
						self._contact.surface.bounce_vel = bv

		property soft_erp:
				def __get__(self):
						return self._contact.surface.soft_erp

				def __set__(self, erp):
						self._contact.surface.soft_erp = erp

		property soft_cfm:
				def __get__(self):
						return self._contact.surface.soft_cfm

				def __set__(self, cfm):
						self._contact.surface.soft_cfm = cfm

		property motion1:
				def __get__(self):
						return self._contact.surface.motion1

				def __set__(self, m):
						self._contact.surface.motion1 = m

		property motion2:
				def __get__(self):
						return self._contact.surface.motion2

				def __set__(self, m):
						self._contact.surface.motion2 = m

		property slip1:
				def __get__(self):
						return self._contact.surface.slip1

				def __set__(self, s):
						self._contact.surface.slip1 = s

		property slip2:
				def __get__(self):
						return self._contact.surface.slip2

				def __set__(self, s):
						self._contact.surface.slip2 = s

		property pos:
				"""The position of the contact point"""
				def __get__(self):
						return (self._contact.geom.pos[0], self._contact.geom.pos[1], 
										self._contact.geom.pos[2])

				def __set__(self, pos):
						self._contact.geom.pos[0] = pos[0]
						self._contact.geom.pos[1] = pos[1]
						self._contact.geom.pos[2] = pos[2]

		property normal:
				"""The normal of the contact geom"""
				def __get__(self):
						return (self._contact.geom.normal[0], self._contact.geom.normal[1],
										self._contact.geom.normal[2])

				def __set__(self, normal):
						self._contact.geom.normal[0] = normal[0]
						self._contact.geom.normal[1] = normal[1]
						self._contact.geom.normal[2] = normal[2]

		property depth:
				"""The depth of the contact point"""
				def __get__(self):
						return self._contact.geom.depth

				def __set__(self, depth):
						self._contact.geom.depth = depth

		property g1:
				"""The first intersecting geom"""
				def __get__(self):
						return <GeomObject>dGeomGetData(self._contact.geom.g1)

				def __set__(self, GeomObject g1):
						if g1 is None:
								self._contact.geom.g1 = NULL
						else:
								self._contact.geom.g1 = g1.gid

		property g2:
				"""The second intersecting geom"""
				def __get__(self):
						return <GeomObject>dGeomGetData(self._contact.geom.g2)

				def __set__(self, GeomObject g2):
						if g2 is None:
								self._contact.geom.g2 = NULL
						else:
								self._contact.geom.g2 = g2.gid

