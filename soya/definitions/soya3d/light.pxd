# -*- indent-tabs-mode: t -*-

cdef class _Light(CoordSyst):
	cdef public float radius
	cdef float _w, _constant, _linear, _quadratic, _angle, _exponent
	cdef float _colors[16] # ambient + diffuse + specular + shadow colors
	cdef float _data[3] # used by cell-shading and shadow
	cdef readonly int _id
	cdef int _gl_id_enabled
	cdef _static_shadow_displaylists
	
	cdef __getcstate__(self)
	
	cdef void __setcstate__(self, object cstate)
	cdef int _shadow_at(self, float position[3])
	cdef float _spotlight_at(self, float position[3])
	cdef float _attenuation_at(self, float position[3])

	cdef void _static_light_at(self, float* position, float* normal, int shadow, float* result)
	cdef void _cast_into(self, CoordSyst coordsyst)
	cdef void _batch(self, CoordSyst coordsyst)
	cdef void _activate(self)
	cdef void _compute_radius(self)

