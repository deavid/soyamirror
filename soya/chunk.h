/*
 * Soya 3D
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */

/**********************************************
 * chunk.h
 * Copyright (C) 2001-2002 Bertrand 'blam' LAMY
 **********************************************/

#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <stdarg.h>
#include <float.h>
#include <math.h>

typedef struct {
  void* content;
  int   nb;
  int   max;
} Chunk;

Chunk*    chunk_new         (void);
void      chunk_dealloc     (Chunk*);
int       chunk_check_error (void);
int       chunk_register    (Chunk*, int size);
int       chunk_add         (Chunk*, void*, int size);
int       chunk_add_char    (Chunk*, char);
int       chunk_add_int     (Chunk*, int);
int       chunk_add_float   (Chunk*, float);
int       chunk_add_double  (Chunk*, double);
int       chunk_add_ptr     (Chunk*, void*);
int       chunk_get         (Chunk*, void*, int size);
char      chunk_get_char    (Chunk*);
int       chunk_get_int     (Chunk*);
float     chunk_get_float   (Chunk*);
void*     chunk_get_ptr     (Chunk*);

Chunk*    get_chunk         (void);
void      drop_chunk        (Chunk*);

/* endian-safe version (for file saving). */

int       chunk_add_chars_endian_safe(Chunk*, char*, int);
int       chunk_get_chars_endian_safe(Chunk*, char*, int);

int       chunk_add_ints_endian_safe(Chunk*, int*, int);
int       chunk_get_ints_endian_safe(Chunk*, int*, int);

int       chunk_add_floats_endian_safe(Chunk*, float*, int);
int       chunk_get_floats_endian_safe(Chunk*, float*, int);

int       chunk_add_char_endian_safe    (Chunk*, char);
int       chunk_get_char_endian_safe    (Chunk*, char*);

int       chunk_add_int_endian_safe     (Chunk*, int);
int       chunk_get_int_endian_safe     (Chunk*, int*);

int       chunk_add_float_endian_safe   (Chunk*, float);
int       chunk_get_float_endian_safe   (Chunk*, float*);

int       chunk_swap_int(int);
float     chunk_swap_float(float);

