cdef class Contact:
	cdef dContact _contact
	cdef _World   _ode_root
cdef class ContactJoint(Joint):
	cdef Contact _contact
