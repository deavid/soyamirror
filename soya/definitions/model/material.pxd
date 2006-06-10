# -*- indent-tabs-mode: t -*-

cdef class _Material(_CObj):
	cdef int     _option, _nb_packs
	cdef _Image  _texture
	cdef readonly GLuint _id # the OpenGL texture name
	cdef public float shininess
	cdef GLfloat _diffuse[4], _specular[4], _emissive[4]
	cdef public  _filename
	cdef Pack**  _packs # the list of packs which are based on this material

	cdef __getcstate__(self)
	cdef void __setcstate__(self, cstate)
	cdef Pack* _pack(self, int option)
	cdef void _init_texture(self)
	cdef void _build_2D_mipmaps(self, int border)
	cdef void _compute_alpha(self)
	cdef void _activate(self)
	cdef void _inactivate(self)


cdef class _PythonMaterial(_Material):
	cdef void _init_texture(self)
	cdef void _activate(self)
	cdef void _inactivate(self)

