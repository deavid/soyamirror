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
			#print "collide_callback called (two obj collide %s, %s) and %d contacts found" % (repr(g1.body),repr(g2.body),len(contacts))
			
			if hasattr(g1.body,'ode_parent'):
				world = g1.body.ode_parent
			else:
				world = g2.body.ode_parent
				
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
						contact.erase_Geom1()
				elif not g2.body.pushable:
					for contact in contacts:
						contact.erase_Geom2()
				
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
	
	cdef long nb_contact
	if max_contacts < 1 or max_contacts > 150:
			raise ValueError, "max_contacts must be between 1 and 150"
	# WTH is n ?
	nb_contact = dCollide(geom1._OdeGeomID, geom2._OdeGeomID,
	                      max_contacts, c, sizeof(dContactGeom))
	res = []
	body = geom1.body
	if body is None:
		body = geom2.body
	root = body.ode_parent
	if nb_contact:
		bounce = (geom1._bounce + geom2._bounce)/2.
		grip = (geom1._grip * geom2._grip)
	for i from 0 <= i < nb_contact:
		cont = Contact(bounce=bounce,mu=grip, ode_root=root)
		cont._contact.geom = c[i]
		res.append(cont)

	# Set collision flag on trimeshes when they're colliding with one
	# another so that they don't update their last transformations
	# This could probably be done more genericly in a collision notification
	# method.
	#if n and isinstance(geom1, _TriMesh) and isinstance(geom2, _TriMesh):
	#	(<_TriMesh>geom1)._colliding = 1
	#	(<_TriMesh>geom2)._colliding = 1

	return res

#U#cdef int collide_edge(GLfloat *A, GLfloat *B,
#U#			 GLfloat *AB, GLfloat *normalA,
#U#			 GLfloat *normalB,
#U#			 dGeomID o1, dGeomID o2, int max_contacts, 
#U#			 int flags, dContactGeom *contact):
#U#		"""Check for collision with one triangle edge. Uses a normal
#U#		that's halfway between the precomputed normals of the vertices
#U#		that make up the edge."""
#U#		cdef dGeomID _land_ray   # Reusable ray geom #XXX misplaced
#U#
#U#
#U#		cdef int n, num_contacts, nA, nB
#U#		cdef dContactGeom contactA, contactB
#U#		cdef _Geom other
#U#		cdef void* tmp_ptr
#U#		_land_ray = dCreateRay(NULL, 1.0)#XXX misplaced
#U#
#U#		# First, do one direction
#U#		dGeomRaySetLength(_land_ray, point_distance_to(A, B))
#U#		dGeomRaySet(_land_ray, A[0], A[1], A[2], AB[0], AB[1], AB[2])
#U#		nA = dCollide(_land_ray, o2, flags, &contactA, sizeof(dContactGeom))
#U#	
#U#
#U#		# Then the other
#U#		dGeomRaySet(_land_ray, B[0], B[1], B[2], -AB[0], -AB[1], -AB[2])
#U#		nB = dCollide(_land_ray, o2, flags, &contactB, sizeof(dContactGeom))
#U#		dGeomDestroy(_land_ray)
#U#		
#U#		if nA and nB:
#U#				contact.pos[0] = (contactA.pos[0] + contactB.pos[0]) / 2.0
#U#				contact.pos[1] = (contactA.pos[1] + contactB.pos[1]) / 2.0
#U#				contact.pos[2] = (contactA.pos[2] + contactB.pos[2]) / 2.0
#U#
#U#				# D
#U#				contact.normal[0] = (normalA[0] + normalB[0]) / 2.0
#U#				contact.normal[1] = (normalA[1] + normalB[1]) / 2.0
#U#				contact.normal[2] = (normalA[2] + normalB[2]) / 2.0
#U#
#U#				# Get the depth of the contact point in the colliding geom
#U#				tmp_ptr = dGeomGetData(o2)
#U#				other = <_Geom>tmp_ptr
#U#				contact.depth = other._point_depth(contact.pos[0], contact.pos[1], 
#U#																					 contact.pos[2])
#U#				contact.g1 = o1
#U#				contact.g2 = o2
#U#
#U#				return 1
#U#
#U#		return 0
