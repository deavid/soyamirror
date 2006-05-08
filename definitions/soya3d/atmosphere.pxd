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

cdef class _Atmosphere(_CObj):
  cdef int       _option, _fog_type
  cdef float     _fog_start, _fog_end, _fog_density
  cdef float     _ambient[4], _bg_color[4], _fog_color[4]
  
  cdef __getcstate__(self)
  cdef void __setcstate__(self, object cstate)
  cdef void _clear(self)
  cdef void _draw_bg(self)
  cdef void _render(self)
  cdef float _fog_factor_at(self, float p[3])


cdef class _NoBackgroundAtmosphere(_Atmosphere):
  cdef void _clear(self)
    

cdef class _SkyAtmosphere(_Atmosphere):
  cdef float     _sky_color[4]
  cdef float     _cloud_scale
  cdef _Material _cloud
  cdef           _sky_box
  
  cdef __getcstate__(self)
  cdef void __setcstate__(self, object cstate)
  cdef void _draw_bg(self)
  cdef void _draw_sky_plane(self)
  cdef void _draw_sky_box(self)


