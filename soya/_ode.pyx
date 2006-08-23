# -*- indent-tabs-mode: t -*-

####################################################################
# Python Open Dynamics Engine Wrapper
#
# Copyright (C) 2003, Matthias Baas (baas@ira.uka.de)
#
# You may distribute under the terms of the BSD license, as
# specified in the files license*.txt.
# -------------------------------------------------------------
# Open Dynamics Engine
# Copyright (c) 2001-2003, Russell L. Smith.
# All rights reserved. 
####################################################################

include "c.pxd"
include "c_opengl.pxd"

cimport _soya

#include "ode/c2py.pxd"

include "ode/declarations.pxd"

# The World should keep a reference to joints/bodies, so that they won't
# be deleted.

# Excplicitly assign the module doc string to __doc__
# (otherwise it won't show up which is probably a "bug" in Pyrex (v0.9.2.1))
__doc__ = """Python Open Dynamics Engine (ODE) wrapper.

This module contains classes and functions that wrap the functionality
of the Open Dynamics Engine (ODE) which can be found at 
http://opende.sourceforge.net.

There are the following classes and functions:

 - World
 - Body
 - JointGroup
 - Contact
 - Space
 - Mass

Joint classes:

 - BallJoint
 - HingeJoint
 - Hinge2Joint
 - SliderJoint
 - UniversalJoint
 - FixedJoint
 - ContactJoint
 - AMotor

Geom classes:

 - GeomSphere
 - GeomBox
 - GeomPlane
 - GeomCCylinder
 - GeomRay
 - GeomTransform
 - GeomTriMesh / TriMeshData

Functions:

 - CloseODE()
 - collide()

"""



######################################################################

# Lookup table for geom objects: C ptr -> Python object
#_geom_c2py_lut = {}

# Mass 
include "ode/mass.pyx"

# Contact
include "ode/contact.pyx"

# World
include "ode/world.pyx"

# Body
include "ode/body.pyx"

# Joint classes
include "ode/joints.pyx"

# Geom base
include "ode/geomobject.pyx"

# Space
include "ode/space.pyx"

# Geom classes
include "ode/geoms.pyx"

# Utility functions for Soya geoms
include "ode/util.pyx"

# Terrain geom for Soya
include "ode/terrain.pyx"

# Model geom using TriMesh
include "ode/model.pyx"

		
def collide(GeomObject geom1, GeomObject geom2, int max_contacts=8):
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

		n = dCollide(geom1.gid, geom2.gid, max_contacts, c, sizeof(dContactGeom))
		res = []
		for i from 0 <= i < n:
				cont = Contact()
				cont._contact.geom = c[i]
				res.append(cont)

		# Set collision flag on trimeshes when they're colliding with one
		# another so that they don't update their last transformations
		# This could probably be done more genericly in a collision notification
		# method.
		if n and isinstance(geom1, _TriMesh) and isinstance(geom2, _TriMesh):
				(<_TriMesh>geom1)._colliding = 1
				(<_TriMesh>geom2)._colliding = 1

		return res

def CloseODE():
		"""CloseODE()

		Deallocate some extra memory used by ODE that can not be deallocated
		using the normal destroy functions.
		"""
		dCloseODE()

######################################################################

environment = _Body(None)
