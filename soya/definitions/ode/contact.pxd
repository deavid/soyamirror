cdef class Contact:
	cdef dContact _contact
	cdef _World   _ode_root
cdef class ContactJoint(_Joint):
	cdef Contact _contact
