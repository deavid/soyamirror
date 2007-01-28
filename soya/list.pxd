# -*- indent-tabs-mode: t -*-

# Souvarine souvarine@aliasrobotique.org
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

cdef struct _CListHandle:
	_CListHandle* next
	void*				 data

ctypedef _CListHandle CListHandle

cdef struct _CList:
	_CListHandle* begin
	_CListHandle* end

ctypedef _CList CList

#cdef public void          clist_init           ()
#cdef public void          clist_dealloc        ()
#cdef public void          clist_manage_recycler()
#cdef public CListHandle* _get_clist_handle     ()
#cdef public void         _drop_clist_handle    (CListHandle* the_handle)
#cdef public void         _clist_add_handle     (CList* the_list, CListHandle* the_handle)
#cdef public CListHandle* _clist_pop_handle     (CList* the_list)
#cdef public CList*        get_clist            ()
#cdef public void          drop_clist           ()
#cdef public void          clist_add            (CList* the_list, void* data)
#cdef public void          clist_transfer       (CList* src, CList* dest)
#cdef public void          clist_flush          (CList* the_list)
#cdef public CListHandle*  clist_find           (CList* the_list, void* data)
