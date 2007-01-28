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

#ctypedef struct CListHandle:
#	CListHandle* next
#	void*				 data

#ctypedef struct CList:
#	CListHandle* begin
#	CListHandle* end

cdef CList* handle_recycler
cdef int    nb_used_hanles
cdef int    old_nb_used_hanles

# Init the list system
cdef void clist_init():
	global handle_recycler
	global nb_used_hanles
	global old_nb_used_hanles
	# pre alloc some handles here ?
	nb_used_hanles = 0
	old_nb_used_hanles = 0
	handle_recycler = get_clist()

# Dealloc the list system
cdef void clist_dealloc():
	global handle_recycler
	cdef CListHandle* the_handle
	the_handle = _clist_pop_handle(handle_recycler)
	while the_handle:
		free(the_handle)
	free(handle_recycler)

# Free progressivly the unused handles
cdef void clist_manage_recycler():
	global handle_recycler
	global nb_used_hanles
	global old_nb_used_hanles
	cdef CListHandle* the_handle
	if nb_used_hanles < old_nb_used_hanles:
		the_handle = _clist_pop_handle(handle_recycler)
		if the_handle: free(the_handle)
	old_nb_used_hanles = nb_used_hanles
	nb_used_hanles     = 0

# Return a list handle
cdef CListHandle* _get_clist_handle():
	global handle_recycler
	global nb_used_hanles
	cdef CListHandle* new_handle
	new_handle = _clist_pop_handle(handle_recycler)
	if new_handle == NULL:
		new_handle = <CListHandle*> malloc(sizeof(CListHandle))
	nb_used_hanles = nb_used_hanles + 1
	return new_handle

# Drop a list handle
cdef void _drop_clist_handle(CListHandle* the_handle):
	global handle_recycler
	_clist_add_handle(handle_recycler, the_handle)

# Add an handle at the end of a list
cdef void _clist_add_handle(CList* the_list, CListHandle* the_handle):
	if the_list.begin == NULL:
		the_list.begin  = the_handle
		the_list.end    = the_handle
	else:
		the_list.end.next = the_handle
		the_list.end      = the_handle
	the_handle.next = NULL

# Return the first handle of a list and remove it from the list
cdef CListHandle* _clist_pop_handle(CList* the_list):
	cdef CListHandle* the_handle
	the_handle = the_list.begin
	if the_handle == NULL:
		return NULL
	if the_list.begin == the_list.end:
		the_list.begin = NULL
		the_list.end   = NULL
	else:
		the_list.begin = the_handle.next
	return the_handle

# Return a new list
cdef CList* get_clist():
	cdef CList* new_list
	new_list       = <CList*> malloc(sizeof(CList))
	new_list.begin = NULL
	new_list.end   = NULL
	return new_list

# Drop a list
cdef void drop_clist(CList* the_list):
	clist_flush(the_list)
	free(the_list)

# Add an item at the end of a list
cdef void clist_add(CList* the_list, void* data):
	cdef CListHandle* handle
	handle = _get_clist_handle()
	handle.data = data
	_clist_add_handle(the_list, handle)

# Put the contant of a list into an other list, the first list is left empty
cdef clist_transfer(CList* src, CList* dest):
	if src.begin  == NULL:
		return
	if dest.begin == NULL: dest.begin    = src.begin
	else:                  dest.end.next = src.begin
	dest.end  = src.end
	src.begin = NULL
	src.end   = NULL

# Empty a list
cdef clist_flush (CList* the_list):
	global handle_recycler
	clist_transfer(the_list, handle_recycler)

# Find the first occurence of data in the list and return the corresponding handle or NULL if not found
cdef CListHandle* clist_find(CList* the_list, void* data):
	cdef CListHandle* handle
	
	handle = the_list.begin
	while handle != NULL:
		if handle.data == data: break
		handle = handle.next
	else:
		return NULL
	return handle
