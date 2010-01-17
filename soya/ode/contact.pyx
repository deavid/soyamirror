# -*- indent-tabs-mode: t -*-

############################## Contact ################################

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
		

		def __cinit__(self, *args, **kw):
				self._contact.surface.mode = ContactBounce
				self._contact.surface.mu   = dInfinity
				self._contact.surface.bounce = 0
		def __init__(self,bounce=0, mu=dInfinity,
		             _World ode_root=None):
			self._contact.surface.bounce = bounce
			self._contact.surface.mu = mu
			self_ode_root = ode_root
				
		def __getitem__(self,index):
			if index ==0:
				if self._contact.geom.g1 == NULL:
					return None
				else:
					return <object>dGeomGetData(self._contact.geom.g1)
			if index ==1:
				if self._contact.geom.g2 == NULL:
					return None
				else:
					return <object>dGeomGetData(self._contact.geom.g2)
			else:
				raise IndexError("(%i) Only two body are stored into a Contact"%index)
		def __setitem__(self,index,_Geom geom):
			cdef dGeomID gid
			if geom is None:
				gid = NULL
			else:
				gid = geom._OdeGeomID
			if index ==0:
				self._contact.geom.g1 = gid
			elif index ==1:
				self._contact.geom.g2 = gid
			else:
				raise IndexError("(%i) Only two body may be stored into a Contact"%index)
		
		def erase_Geom1(self):
			self._contact.geom.g1 = NULL
			
		def erase_Geom2(self):
			self._contact.geom.g2 = NULL
			
				
		def __contains__(self,_Geom geom):
			return geom._OdeGeomID == self._contact.geom.g1 or geom._OdeGeomID ==self._contact.geom.g2
		def __iter__(self):
			return iter((self[0],self[1]))

			
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
				return Point(self._ode_root,self._contact.geom.pos[0], self._contact.geom.pos[1], 
					self._contact.geom.pos[2])

			def __set__(self,_Point pos):
				cdef float p[3]
				pos._into(self._ode_root,p)
				self._contact.geom.pos[0] = p[0]
				self._contact.geom.pos[1] = p[1]
				self._contact.geom.pos[2] = p[2]

		property normal:
			"""The normal of the contact geom"""
			def __get__(self):
				return Vector(self._ode_root,self._contact.geom.normal[0], self._contact.geom.normal[1],
						self._contact.geom.normal[2])

			def __set__(self, _Vector normal):
				cdef float n[3]
				normal._into(self._ode_root,n)
				self._contact.geom.normal[0] = n[0]
				self._contact.geom.normal[1] = n[1]
				self._contact.geom.normal[2] = n[2]

		property depth:
				"""The depth of the contact point"""
				def __get__(self):
						return self._contact.geom.depth

				def __set__(self, depth):
						self._contact.geom.depth = depth

cdef class ContactJoint(_Joint):
		"""Contact joint.

		Constructor::
		
			ContactJoint(world, jointgroup, contact)
		"""

		#def __new__(self, _World world not None, jointgroup, Contact contact, *args, **kw):
		#		cdef JointGroup jg
		#		cdef dJointGroupID jgid
		#		jgid=NULL
		#		if jointgroup!=None:
		#				jg=jointgroup
		#				jgid=jg.gid
		#		self.jid = dJointCreateContact(world._wid, jgid, &contact._contact)
		def __init__(self,Contact contact,_JointGroup group= None,bounce=None):
			cdef _Body body1
			cdef _Body body2
			cdef _World world
			cdef dJointGroupID gid
			world = None
			if contact[0] is None:
				body1 = None
			else:
				body1 = contact[0].body
				world = body1.ode_parent
			if contact[1] is None:
				if world is None:
					raise RuntimeError("can't build a ContactJoin with no body")
				body2 = None
			else:
				body2 = contact[1].body
				if world is None:
					world = body2.ode_parent
			if group is not None:
				group._addjoint(self)
				gid = group._OdeGroupJoinID
			else:
				gid = NULL
			self._OdeJointID = dJointCreateContact(world._OdeWorldID, gid, &contact._contact)
			self.attach(body1, body2)
			self._contact = contact
			
	#cdef       _getParam(self, int param):
	#	return dJointGet
	#cdef dReal _setParam(self, int param,dReal value):
