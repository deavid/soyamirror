# -*- indent-tabs-mode: t -*-
#
# Mass class Definition.

cdef class _Mass:
	"""Mass parameters of a rigid body.

	This class stores mass parameters of a rigid body which can be
	accessed through the following attributes:

	 - mass: The total mass of the body (float)
	 - c:    The center of gravity position in body frame (3-tuple of floats)
	 - I:    The 3x3 inertia tensor in body frame (3-tuple of 3-tuples)

	This class wraps the dMass structure from the C API.

	@ivar mass: The total mass of the body
	@ivar c: The center of gravity position in body frame (cx, cy, cz)
	@ivar I: The 3x3 inertia tensor in body frame ((I11, I12, I13), (I12, I22, I23), (I13, I23, I33))
	@type mass: float
	@type c: 3-tuple of floats
	@type I: 3-tuple of 3-tuples of floats 
	"""
	cdef dMass _mass
	
	cdef __getcstate__(self)
	cdef __setcstate__(self,cstate)
