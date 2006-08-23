# -*- indent-tabs-mode: t -*-
# Callback function for the dSpaceCollide() call in the Space.collide() method
# The data parameter is a tuple (Python-Callback, Arguments).
# The function calls a Python callback function with 3 arguments:
# def callback(UserArg, Geom1, Geom2)
# Geom1 and Geom2 are instances of GeomXyz classes.

cdef void collide_callback(void* data, dGeomID o1, dGeomID o2):
	#cdef Space space

    #if (dGeomGetBody(o1)==dGeomGetBody(o2)):
    #    return
	cdef void *gv1, *gv2
	cdef _JointGroup contact_group
	cdef _PlaceableGeom geom
	cdef _Body body
	cdef _World world
	#print "collide_callback called"
	space = <object>data
	if dGeomIsSpace(o1) or dGeomIsSpace(o2):
		dSpaceCollide2(o1, o2, data, collide_callback)
	else:
		gv1 = dGeomGetData(o1)
		g1  = <object>gv1
		gv2 = dGeomGetData(o2)
		g2  = <object>gv2
		contacts = collide(g1, g2)
		if len(contacts):
			geom = g1
			body = geom.body
			world = body.ode_parent
			contact_group = world._contact_group
			if hasattr(g1.body,'hit'):
				g1.body.hit(g2.body,contacts)
			if hasattr(g2.body,'hit'):
				g2.body.hit(g1.body,contacts)
			if not (g1.body is None or g2.body is None):
				if not (g1.body.pushable or g2.body.pushable):
					return
				elif not g1.body.pushable:
					for contact in contacts:
						contact[0]=None
				elif not g2.body.pushable:
					for contact in contacts:
						contact[1]=None
				
			for contact in contacts:
				#print "bouh"
				joint = ContactJoint(contact,contact_group)
				#print "bi"
			



def collide(_Geom geom1, _Geom geom2, int max_contacts=8):
	"""Generate contact information for two objects.

	Given two geometry objects that potentially touch (geom1 and geom2),
	generate contact information for them. Internally, this just calls
	the correct class-specific collision functions for geom1 and geom2.

	[flags specifies how contacts should be generated if the objects
	touch. Currently the lower 16 bits of flags specifies the maximum
	number of contact points to generate. If this number is zero, this
	function just pretends that it is one - in other words you can not
	ask for zero contacts. All other bits in flags must be zero. In
	the future the other bits may be used to select other contact
	generation strategies.]

	If the objects touch, this returns a list of Contact objects,
	otherwise it returns an empty list.
	"""
	
	cdef dContactGeom c[150]
	cdef int i, n
	cdef Contact cont
	
	if max_contacts < 1 or max_contacts > 150:
			raise ValueError, "max_contacts must be between 1 and 150"
	
	n = dCollide(geom1._OdeGeomID, geom2._OdeGeomID, max_contacts, c, sizeof(dContactGeom))
	res = []
	body = geom1.body
	if body is None:
		body = geom2.body
	root = body.ode_parent
	if n:
		bounce = (geom1._bounce+geom2._bounce)/2.
	for i from 0 <= i < n:
			cont = Contact(bounce=bounce,ode_root=root)
			cont._contact.geom = c[i]
			res.append(cont)

	# Set collision flag on trimeshes when they're colliding with one
	# another so that they don't update their last transformations
	# This could probably be done more genericly in a collision notification
	# method.
	#if n and isinstance(geom1, _TriMesh) and isinstance(geom2, _TriMesh):
	#		(<_TriMesh>geom1)._colliding = 1
	#		(<_TriMesh>geom2)._colliding = 1

	return res

cdef int collide_edge(GLfloat *A, GLfloat *B,
			 GLfloat *AB, GLfloat *normalA,
			 GLfloat *normalB,
			 dGeomID o1, dGeomID o2, int max_contacts, 
			 int flags, dContactGeom *contact):
		"""Check for collision with one triangle edge. Uses a normal
		that's halfway between the precomputed normals of the vertices
		that make up the edge."""
		cdef dGeomID _land_ray   # Reusable ray geom #XXX misplaced


		cdef int n, num_contacts, nA, nB
		cdef dContactGeom contactA, contactB
		cdef _Geom other
		_land_ray = dCreateRay(NULL, 1.0)#XXX misplaced

		# First, do one direction
		dGeomRaySetLength(_land_ray, point_distance_to(A, B))
		dGeomRaySet(_land_ray, A[0], A[1], A[2], AB[0], AB[1], AB[2])
		nA = dCollide(_land_ray, o2, flags, &contactA, sizeof(dContactGeom))
	

		# Then the other
		dGeomRaySet(_land_ray, B[0], B[1], B[2], -AB[0], -AB[1], -AB[2])
		nB = dCollide(_land_ray, o2, flags, &contactB, sizeof(dContactGeom))
		dGeomDestroy(_land_ray)
		
		if nA and nB:
				contact.pos[0] = (contactA.pos[0] + contactB.pos[0]) / 2.0
				contact.pos[1] = (contactA.pos[1] + contactB.pos[1]) / 2.0
				contact.pos[2] = (contactA.pos[2] + contactB.pos[2]) / 2.0

				# D
				contact.normal[0] = (normalA[0] + normalB[0]) / 2.0
				contact.normal[1] = (normalA[1] + normalB[1]) / 2.0
				contact.normal[2] = (normalA[2] + normalB[2]) / 2.0

				# Get the depth of the contact point in the colliding geom
				other = <_Geom>dGeomGetData(o2)
				contact.depth = other._point_depth(contact.pos[0], contact.pos[1], 
																					 contact.pos[2])
				contact.g1 = o1
				contact.g2 = o2

				return 1

		return 0
