# -*- indent-tabs-mode: t -*-

# Soya 3D
# Copyright (C) 2004 Jean-Baptiste LAMY -- jiba@tuxfamily.org
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

cdef class _Particles(CoordSyst):
	cdef _Material _material
	cdef CoordSyst _particle_coordsyst
	cdef int       _nb_particles, _nb_max_particles, _particle_size # range from 11 to 20 float
	cdef float*    _particles # life, max_life, position, speed, acceleration, [color], [size], [direction]
														# life, max_life, x/y/z, u/v/w, a/b/c, [r/g/b/a], [w/h], [m/n/o]
	cdef float     _delta_time
	cdef int       _nb_colors, _nb_sizes
	cdef float*    _fading_colors, *_sizes # fading colors and size gain
	cdef int       _nb_creatable_particles, _max_particles_per_round
	
	cdef __getcstate__(self)
	cdef void __setcstate__(self, object cstate)
	cdef void _reinit(self)
	cdef void _advance(self, float proportion)
	cdef void _batch(self, CoordSyst coordsyst)
	cdef void _render(self, CoordSyst coordsyst)
	cdef void _compute_alpha(self)
	cdef void _get_fading_color(self, float life, float max_life, float* returned_color)
	cdef void _get_size(self, float life, float max_life, float* returned_size)
	cdef float* _generate(self, int index, float life)


#cdef class Fountain(_Particles):


cdef class Smoke(_Particles):
	cdef float  _life_base
	cdef object _life_function
	cdef float  _speed_factor
	cdef float  _acceleration
#cdef class FlagSubFire(_Particles)


cdef class FlagFirework(_Particles):
	cdef _Particles _subgenerator
	cdef int        _nb_sub_particles
		
