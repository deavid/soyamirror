# -*- indent-tabs-mode: t -*-
#
# Join class Definition.

# author:
#	edited by Marmoute - Pierre-Yves David - marmoute@nekeme.net

cdef class _JointGroup:
	cdef dJointGroupID _OdeGroupJoinID
	# A list of Python joints that were added to the group
	cdef object jointlist
	
Joint = None
cdef class _Joint:
	"""Base class for all joint classes."""

		
	# Joint id as returned by dJointCreateXxx()
	cdef dJointID _OdeJointID
	# A reference to the world so that the world won't be destroyed while
	# there are still joints using it.
	cdef object world
	# The feedback buffer
	cdef dJointFeedback* feedback

	cdef _Body _body1
	cdef _Body _body2
	
	cdef _destroy(self)
	cdef void _destroyed(self)
	cdef void _setParam(self, int param, dReal value)
	cdef dReal _getParam(self, int param)
	
	cdef __getcstate__(self)
	cdef void __setcstate__(self,cstate)
