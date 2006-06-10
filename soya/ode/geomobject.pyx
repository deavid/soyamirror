# -*- indent-tabs-mode: t -*-

# Each geom object has to insert itself into the global dictionary
# _geom_c2py_lut (key:address - value:Python object).
# This lookup table is used in the near callback to translate the C
# pointers into corresponding Python wrapper objects.
#
# Additionally, each geom object must have a method _id() that returns
# the ODE geom id. This is used during collision detection.
# 
# ##########################
# # Obsolete:
# #
# # Each geom object has to register itself at its space as the
# # space keeps a dictionary that's used as lookup table to translate
# # C pointers into Python objects (this is used in the near callback).

# Forward declarations
cdef class SpaceBase(GeomObject)

# Geom base class
cdef class GeomObject(_soya.CoordSyst):
		"""This is the abstract base class for all geom objects.
		"""
		
		# The id of the geom object as returned by dCreateXxxx()
		cdef dGeomID gid
		#cdef dGeomID tid # The transform geom
		# The space in which the geom was placed (or None). This reference
		# is kept so that the space won't be destroyed while there are still
		# geoms around that might use it. 
		cdef SpaceBase space
		# The body that the geom was attached to (or None).
		cdef _Body _body

		cdef _World world

		def __new__(self, _soya.CoordSyst parent=None, SpaceBase space=None, *args, **kw):
				cdef dSpaceID sid
				cdef _soya.CoordSyst p

				if space is None:
						sid = NULL
				else:
						sid = space.sid

				self.gid = NULL
				#self.tid = NULL
				self.space = space
				self._body = None
				#self.attribs = {}

				p = parent
				while p is not None:
						if isinstance(p, _Body):
								self._body = p
								break
						if isinstance(p, _World):
								self.world = p
								break
						p = p._parent

				if self.world is None:
						while p is not None:
								if isinstance(p, _World):
										self.world = p
										break
								p = p._parent

		def __init__(self, _soya.CoordSyst parent=None, SpaceBase space=None, *args, **kw):
				dGeomSetData(self.gid, <void *>self)
				_soya.CoordSyst.__init__(self, parent)
				if space is not None:
						# Don't call add because we're already in the space
						space.geoms.append(self)

		#def _create(self, space, *a, **kw):
		#    raise NotImplementedError, "Cannot use GeomObject directly"

		cdef float _point_depth(self, float x, float y, float z):
				raise NotImplementedError, "Cannot use GeomObject directly"

		def point_depth(self, pos):
				return self._point_depth(pos[0], pos[1], pos[2])

		def __dealloc__(self):
				print "dealloc", self
				if self.gid is not NULL:
						dGeomDestroy(self.gid)
						self.gid = NULL

		def placeable(self):
				"""placeable() -> bool

				Returns True if the geom object is a placeable geom.

				This method has to be overwritten in derived methods.
				"""
				return False

		property body:
				def __get__(self):
						return self._body or environment

		def begin_round(self):
				"""Need to update the ODE state every round"""
				self._invalidate()

		cdef void _invalidate(self):
				"""Update the geom's matrix after invalidating the root and inverted
				root matrices. We do this here because all movement methods must
				call this."""

				cdef dMatrix3 R
				cdef GLfloat m[19]

				_soya.CoordSyst._invalidate(self)
				if self.placeable():
						#if self._body is not None:
						#    _soya.multiply_matrix(m, self._root_matrix(), self._body._inverted_root_matrix())
						#else:    
						#    _soya.multiply_matrix(m, self._root_matrix(), self.world._inverted_root_matrix())

						_soya.multiply_matrix(m, self._root_matrix(), self.world._inverted_root_matrix())

						R[0] = m[0]
						R[1] = m[4]
						R[2] = m[8]
						R[3] = 0.0
						R[4] = m[1]
						R[5] = m[5]
						R[6] = m[9]
						R[7] = 0.0
						R[8] = m[2]
						R[9] = m[6]
						R[10] = m[10]
						R[11] = 0.0

						# Overriding the movement methods would be faster due to the fact
						# that we wouldn't have to copy the rotation matrix as well
						dGeomSetPosition(self.gid, m[12], m[13], m[14])
						dGeomSetRotation(self.gid, R)

		def getAABB(self):
				"""getAABB() -> 6-tuple

				Return an axis aligned bounding box that surrounds the geom.
				The return value is a 6-tuple (minx, maxx, miny, maxy, minz, maxz).
				"""
				cdef dReal aabb[6]
				
				dGeomGetAABB(self.gid, aabb)
				return (aabb[0], aabb[1], aabb[2], aabb[3], aabb[4], aabb[5])

		def isSpace(self):
				"""isSpace() -> bool

				Return 1 if the given geom is a space, or 0 if not."""
				return dGeomIsSpace(self.gid)

		def getSpace(self):
				"""getSpace() -> Space

				Return the space that the given geometry is contained in,
				or return None if it is not contained in any space."""        
				return self.space

		def setCollideBits(self, bits):
				"""setCollideBits(bits)

				Set the "collide" bitfields for this geom.

				@param bits: Collide bit field
				@type bits: int
				"""
				dGeomSetCollideBits(self.gid, bits)
				
		def setCategoryBits(self, bits):
				"""setCategoryBits(bits)

				Set the "category" bitfields for this geom.

				@param bits: Category bit field
				@type bits: int
				"""
				dGeomSetCategoryBits(self.gid, bits)

		def getCollideBits(self):
				"""getCollideBits() -> int

				Return the "collide" bitfields for this geom.
				"""
				return dGeomGetCollideBits(self.gid)

		def getCategoryBits(self):
				"""getCategoryBits() -> int

				Return the "category" bitfields for this geom.
				"""
				return dGeomGetCategoryBits(self.gid)
		
		property enabled:
				def __set__(self, flag):
						if flag:
								dGeomEnable(self.gid)
						else:
								dGeomDisable(self.gid)

				def __get__(self):
						return dGeomIsEnabled(self.gid)


