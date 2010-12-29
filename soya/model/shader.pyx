# -*- indent-tabs-mode: t -*-

# Soya 3D
# Copyright (C) 2010 Jean-Baptiste LAMY -- jiba@tuxfamily.org
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

#cdef int SHADER_TYPE_VERTEX, SHADER_TYPE_FRAGMENT
SHADER_TYPE_VERTEX   = GL_VERTEX_PROGRAM_ARB
SHADER_TYPE_FRAGMENT = GL_FRAGMENT_PROGRAM_ARB

cdef class _ARBShaderProgram(_CObj):
	#cdef readonly GLuint _prog_id
	#cdef readonly object code
	def __init__(self, shader_type, code):
		self.shader_type = shader_type
		glGenProgramsARB(1, &self._prog_id)
		if code: self.set_code(code)
    
	def set_code(self, code):
		self.code = code
		glBindProgramARB(self.shader_type, self._prog_id);
		glProgramStringARB(self.shader_type, GL_PROGRAM_FORMAT_ASCII_ARB, len(code), code)
		#glBindProgramARB(self.shader_type, 0);
		
		cdef GLenum error
		cdef GLint pos
		error = glGetError()
		if error == GL_INVALID_OPERATION:
			print "GL_INVALID_OPERATION in shader program"
			
			message = PyString_FromString(<char*> glGetString(GL_PROGRAM_ERROR_STRING_ARB))
			print "  error : %s" % message
			
			glGetIntegerv(GL_PROGRAM_ERROR_POSITION_ARB, &pos)
			print "  at position %s" % pos
			
			raise GLError, "GL_INVALID_OPERATION in shader program"
    
	def __dealloc__(self):
		glDeleteProgramsARB(1, &self._prog_id)
    
	cdef void _activate(self):
		glEnable(self.shader_type)
		glBindProgramARB(self.shader_type, self._prog_id);
    
	cdef void _inactivate(self):
		glDisable(self.shader_type)
		#glBindProgramARB(self.shader_type, 0);
    
	cdef void _set_env_parameter(self, int index, float v0, float v1, float v2, float v3):
		glProgramEnvParameter4fARB(self.shader_type, index, v0, v1, v2, v3);
    
	cdef void _set_local_parameter(self, int index, float v0, float v1, float v2, float v3):
		glProgramLocalParameter4fARB(self.shader_type, index, v0, v1, v2, v3);
    
	def set_env_parameter(self, int index, float v0, float v1 = 0.0, float v2 = 0.0, float v3 = 0.0):
		glProgramEnvParameter4fARB(self.shader_type, index, v0, v1, v2, v3);
    
	def set_local_parameter(self, int index, float v0, float v1 = 0.0, float v2 = 0.0, float v3 = 0.0):
		glProgramLocalParameter4fARB(self.shader_type, index, v0, v1, v2, v3);
    
	def activate(self): self._activate()
	
	def inactivate(self): self._inactivate()
	
	def __call__(self, **kargs):
		return _ShaderDeform(self, **kargs)
