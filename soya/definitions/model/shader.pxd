# -*- indent-tabs-mode: t -*-

cdef class _ARBShaderProgram(_CObj):
	cdef readonly GLuint shader_type
	cdef readonly GLuint _prog_id
	cdef readonly object code
	cdef public object _filename
	cdef void _activate(self)
	cdef void _inactivate(self)
	cdef void _set_env_parameter(self, int index, float v0, float v1, float v2, float v3)
	cdef void _set_local_parameter(self, int index, float v0, float v1, float v2, float v3)
