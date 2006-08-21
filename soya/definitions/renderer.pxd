# -*- indent-tabs-mode: t -*-

# Soya 3D
# Copyright (C) 2003-2004 Jean-Baptiste LAMY -- jiba@tuxfamily.org
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

# XXX does not allows None/NULL as a valid context, use a default context instead

cdef class Context:
	cdef             lights
	cdef _Atmosphere atmosphere
	cdef _Portal     portal
	
		
cdef class Renderer:
	cdef int       engine_option
	cdef int       state
	cdef _World    root_object
	cdef _Camera   current_camera
	cdef _Material current_material
	
	cdef Frustum*  root_frustum
	cdef Chunk*    frustums
	cdef CoordSyst current_coordsyst
	
	# contexts
	cdef Context current_context
	cdef contexts
	cdef int nb_contexts
	cdef int max_contexts
	cdef _Atmosphere root_atmosphere # root atmosphere (the one to clear the screen with)
	
	# list of collected objects to render
	cdef Chunk* opaque
	cdef Chunk* secondpass
	cdef Chunk* alpha
	cdef Chunk* specials  # objects that are rendered after the shadows (= not shadowed)
	
	cdef top_lights # contain top level activated lights
	cdef worlds_made  # list of world whose context has been made (used by portals to determine if a world must be batched or not)
	cdef portals  # a list of encountered portals to clear_part the atmosphere before any other rendering and to draw fog at the end
	
	# mesh renderer
	cdef Chunk* data
	cdef Chunk* used_opaque_packs, *used_secondpass_packs, *used_alpha_packs
	cdef float** colors
	
	# screen
	cdef SDL_Surface* screen
	cdef int screen_width, screen_height
	
	cdef float delta_time
	
	cdef Frustum* _frustum(self, CoordSyst coordsyst)
	cdef Context _context(self)
	cdef void _activate_context_over(self, Context old, Context new)
	cdef void _reset(self)
	cdef void _batch(self, Chunk* list, obj, CoordSyst coordsyst, int data)
	cdef void _render(self)
	cdef void _render_list(self, Chunk* list)
	cdef void _clear_screen(self, float* color)
	cdef void _render_shadows(self)


cdef class _DisplayList(_CObj)

