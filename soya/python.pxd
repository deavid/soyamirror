# -*- indent-tabs-mode: t -*-

# Soya 3D
# Copyright (C) 2003 Jean-Baptiste LAMY -- jiba@tuxfamily.org
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

cdef extern from "Python.h":
	char*  PyString_AS_STRING(object string)
	object PyString_FromString(char* raw)
	object PyString_FromStringAndSize(char* raw, int length)
	object PyTuple_GET_ITEM(object, int)
	double PyFloat_AS_DOUBLE(object)
	
	void   PyErr_CheckSignals()
	
	int    len "PyObject_Length" (object o) except -1

