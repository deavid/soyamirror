# -*- indent-tabs-mode: t -*-

cdef class _TriMesh(GeomObject)

# SpaceBase
cdef class SpaceBase(GeomObject):
		"""Space class (container for geometry objects).

		A Space object is a container for geometry objects which are used
		to do collision detection.
		The space does high level collision culling, which means that it
		can identify which pairs of geometry objects are potentially
		touching.

		This Space class can be used for both, a SimpleSpace and a HashSpace
		(see ODE documentation).

		 >>> space = Space(type=0)   # Create a SimpleSpace
		 >>> space = Space(type=1)   # Create a HashSpace
		"""

		# The id of the space. Actually this is a copy of the value in self.gid
		# (as the Space is derived from GeomObject) which can be used without
		# casting whenever a *space* id is required.
		cdef dSpaceID sid
		cdef readonly geoms

		# The world this space belongs to, for the default collision callback
		#cdef _World world

#    # Group for contact joints generated by this space
#    cdef JointGroup contactgroup
#    
		def __new__(self, *args, **kw):
#        self.contactgroup = JointGroup()
				self.geoms = []

		def __init__(self, _soya._World parent=None, SpaceBase space=None):
				#GeomObject.__init__(self, parent, space)
				self.world = parent
				
				self._create(space)

				dGeomSetData(self.gid, <void *>self)

#        if self.world is not None:
#            self.world.add_space(self)

		def __dealloc__(self):
				if self.gid != NULL:
						dSpaceDestroy(self.sid)
						self.sid = NULL
						self.gid = NULL

#    def _id(self):
#        cdef long id
#        id = <long>self.sid
#        return id

		def add(self, GeomObject geom):
				"""add(geom)

				Add a geom to a space. This does nothing if the geom is
				already in the space.

				@param geom: Geom object to add
				@type geom: GeomObject
				"""
				
				self.geoms.append(geom)
				dSpaceAdd(self.sid, geom.gid)

		def remove(self, GeomObject geom):
				"""remove(geom)

				Remove a geom from a space.

				@param geom: Geom object to remove
				@type geom: GeomObject
				"""

				self.geoms.remove(geom)
				dSpaceRemove(self.sid, geom.gid)

		def set_last_transformations(self):
				"""Set the last transformation for each TriMesh geom in the space.
				This must be called before the geoms are moved but after the 
				previous collisions."""

				cdef GeomObject geom
				cdef _TriMesh trimesh

				for geom in self.geoms:
						if isinstance(geom, _TriMesh):
								trimesh = <_TriMesh>geom
								trimesh._set_last_transformation()

		def query(self, GeomObject geom):
				"""query(geom) -> bool

				Return True if the given geom is in the space.

				@param geom: Geom object to check
				@type geom: GeomObject
				"""
				return dSpaceQuery(self.sid, geom.gid)

		def getNumGeoms(self):
				"""getNumGeoms() -> int

				Return the number of geoms contained within the space.
				"""
				return dSpaceGetNumGeoms(self.sid)

		def getGeom(self, int idx):
				"""getGeom(idx) -> GeomObject

				Return the geom with the given index contained within the space.

				@param idx: Geom index (0,1,...,getNumGeoms()-1)
				@type idx: int
				"""
				cdef dGeomID gid
				cdef void *data

				# Check the index
				if idx<0 or idx>=dSpaceGetNumGeoms(self.sid):
						raise IndexError, "geom index out of range"

				gid = dSpaceGetGeom(self.sid, idx)
				#if <long>gid not in _geom_c2py_lut:
				#    raise RuntimeError, "geom id cannot be translated to a Python object"

				#return _geom_c2py_lut[<long>gid]
				data = dGeomGetData(gid)
				return <object>data

#    def near_callback(self, g1, g2):
#        """Called for each pair of geoms that might be intersecting.
#        Meant to be overridden in subclasses"""
#        
#        cdef Contact c
#        cdef Joint j
#
#        for c in collide(g1, g2):
#            j = ContactJoint(self.world, self.contactgroup, c)
#            j.attach(g1.body, g2.body)

		def placeable(self):
				return False

		def collide(self, callback):
				"""Do collision detection.

				Call a callback function one or more times, for all
				potentially intersecting objects in the space. The callback
				function takes 3 arguments:

				def NearCallback(arg, geom1, geom2):

				The arg parameter is just passed on to the callback function.
				Its meaning is user defined. The geom1 and geom2 arguments are
				the geometry objects that may be near each other. The callback
				function can call the function collide() (not the Space
				method) on geom1 and geom2, perhaps first determining
				whether to collide them at all based on other information.
				"""
				
#        # Empty out our contact group
#        self.contactgroup.empty()
				
				dSpaceCollide(self.sid, <void*>callback, collide_callback)
				

# Callback function for the dSpaceCollide() call in the Space.collide() method
# The data parameter is a tuple (Python-Callback, Arguments).
# The function calls a Python callback function with 3 arguments:
# def callback(UserArg, Geom1, Geom2)
# Geom1 and Geom2 are instances of GeomXyz classes.
cdef void collide_callback(void* data, dGeomID o1, dGeomID o2):
		#cdef Space space

#    if (dGeomGetBody(o1)==dGeomGetBody(o2)):
#        return

		cdef void *g1, *g2
		
		callback = <object>data

		if dGeomIsSpace(o1) or dGeomIsSpace(o2):
				dSpaceCollide2(o1, o2, data, collide_callback)
		else:
				g1 = dGeomGetData(o1)
				g2 = dGeomGetData(o2)
				callback(<object>g1, <object>g2)


# SimpleSpace
cdef class SimpleSpace(SpaceBase):
		"""Simple space.

		This does not do any collision culling - it simply checks every
		possible pair of geoms for intersection, and reports the pairs
		whose AABBs overlap. The time required to do intersection testing
		for n objects is O(n**2). This should not be used for large numbers
		of objects, but it can be the preferred algorithm for a small
		number of objects. This is also useful for debugging potential
		problems with the collision system.
		"""

		def _create(self, SpaceBase space):
				cdef dSpaceID sid

				if space is None:
						sid = NULL
				else:
						sid = space.sid
				
				self.sid = dSimpleSpaceCreate(sid)

				# Copy the ID
				self.gid = <dGeomID>self.sid

				dSpaceSetCleanup(self.sid, 0)

#    def __init__(self, _soya._World parent=None, SpaceBase space=None):
#        pass

# HashSpace
cdef class HashSpace(SpaceBase):
		"""Multi-resolution hash table space.

		This uses an internal data structure that records how each geom
		overlaps cells in one of several three dimensional grids. Each
		grid has cubical cells of side lengths 2**i, where i is an integer
		that ranges from a minimum to a maximum value. The time required
		to do intersection testing for n objects is O(n) (as long as those
		objects are not clustered together too closely), as each object
		can be quickly paired with the objects around it.
		"""

		def _create(self, SpaceBase space):
				cdef dSpaceID sid

				if space is None:
						sid = NULL
				else:
						sid = space.sid

				self.sid = dHashSpaceCreate(sid)

				# Copy the ID
				self.gid = <dGeomID>self.sid

				dSpaceSetCleanup(self.sid, 0)

		def setLevels(self, int minlevel, int maxlevel):
				"""setLevels(minlevel, maxlevel)

				Sets the size of the smallest and largest cell used in the
				hash table. The actual size will be 2^minlevel and 2^maxlevel
				respectively.
				"""
				
				if minlevel>maxlevel:
						raise ValueError, "minlevel (%d) must be less than or equal to maxlevel (%d)"%(minlevel, maxlevel)
						
				dHashSpaceSetLevels(self.sid, minlevel, maxlevel)

		def getLevels(self):
				"""getLevels() -> (minlevel, maxlevel)

				Gets the size of the smallest and largest cell used in the
				hash table. The actual size is 2^minlevel and 2^maxlevel
				respectively.
				"""
				
				cdef int minlevel
				cdef int maxlevel
				dHashSpaceGetLevels(self.sid, &minlevel, &maxlevel)
				return (minlevel, maxlevel)


# QuadTreeSpace
#cdef class QuadTreeSpace(SpaceBase):
#    """Quadtree space.
#
#    This uses a pre-allocated hierarchical grid-based AABB tree to
#    quickly cull collision checks. It's exceptionally quick for large
#    amounts of objects in landscape-shaped worlds. The amount of
#    memory used is 4**depth * 32 bytes.
#
#    Currently getGeom() is not implemented for the quadtree space.
#    """
#
#    def __new__(self, _soya._World parent=None, SpaceBase space=None, center, extents, depth, *args, **kw):
#        cdef dSpaceID parentid
#        cdef dVector3 c
#        cdef dVector3 e
#
#        parentid = NULL
#        if space is not None:
#            parentid = space.sid
#
#        c[0] = center[0]
#        c[1] = center[1]
#        c[2] = center[2]
#        e[0] = extents[0]
#        e[1] = extents[1]
#        e[2] = extents[2]
#        self.sid = dQuadTreeSpaceCreate(parentid, c, e, depth)
#
#        # Copy the ID
#        self.gid = <dGeomID>self.sid
#
#        dSpaceSetCleanup(self.sid, 0)
#        #_geom_c2py_lut[<long>self.sid]=self
#        dGeomSetData(self.gid, <void*>self)
#
#        self.world = world
#        if world is not None:
#            world.add_space(self)
#
##    def __init__(self, center, extents, depth, SpaceBase space=None, _World world=None):
##        pass


#def Space(type=0):
#    """Space factory function.
#
#    Depending on the type argument this function either returns a
#    SimpleSpace (type=0) or a HashSpace (type=1).
#
#    This function is provided to remain compatible with previous
#    versions of PyODE where there was only one Space class.
#    
#     >>> space = Space(type=0)   # Create a SimpleSpace
#     >>> space = Space(type=1)   # Create a HashSpace
#    """
#    if type==0:
#        return SimpleSpace()
#    elif type==1:
#        return HashSpace()
#    else:
#        raise ValueError, "Unknown space type (%d)"%type
#    
