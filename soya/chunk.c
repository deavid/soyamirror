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
 * chunk.c
 * Copyright (C) 2001-2002 Bertrand 'blam' LAMY
 **********************************************/

#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <stdarg.h>
#include <sys/types.h>
#include <signal.h>

#include "chunk.h"

#ifdef SOYA_BIG_ENDIAN
#define SWAP_INT(X) (X)
#define SWAP_FLOAT(X) (X)
#else
#define SWAP_INT(X) chunk_swap_int(X)
#define SWAP_FLOAT(X) chunk_swap_float(X)
#endif

/*=======*
 * CHUNK *
 *=======*/

/*
void on_error(void) {
#if defined(_WIN32) || defined(WIN32)
  sleep(*(int *)NULL); // really equivalent to the Unix code ???
#else
  kill(0, SIGSEGV);
#endif
}
*/

int chunk_error = 0;
void on_error(void) {
  chunk_error = 1;
}

int chunk_check_error(void) {
  int error;
  error = chunk_error;
  chunk_error = 0;
  return error;
}

Chunk* chunk_new (void) {
  Chunk *chunk = NULL;
  chunk = (Chunk*) malloc (sizeof(Chunk));
  if (chunk != NULL) {
    chunk->nb = 0;
    chunk->max = 0;
    chunk->content = NULL;
  }
  else {
    printf("error in chunk_new !\n");
    on_error();
    return NULL;
  }
  return chunk;
}

void chunk_dealloc (Chunk* chunk) {
  if (chunk != NULL) {
    if (chunk->content != NULL) {
      free (chunk->content);
    }
    free (chunk);
  }
}

static int chunk_size_up (Chunk* chunk, int size) {
  void *tmp = NULL;
  chunk->max = (chunk->nb + size) << 1;
  tmp = (void*) realloc (chunk->content, chunk->max);
  if (tmp == NULL) {
    printf("error in chunk_size_up !\n");
    on_error();
    return 1;
  }
  chunk->content = tmp;
  return 0;
}

int chunk_register (Chunk* chunk, int size) {
  int i, r;
  if (chunk->max < chunk->nb + size) {
    r = chunk_size_up (chunk, size);
    if (r < 0) {
      printf("error in chunk_register !\n");
      on_error();
      return 0;
    }
  }
  i = chunk->nb;
  chunk->nb += size;
  return i;
}

int chunk_add (Chunk* chunk, void* ptr, int size) {
  int r = 0;
  if (chunk->max < chunk->nb + size) {
    r = chunk_size_up (chunk, size);
    if (r < 0) {
      printf("error in chunk_add !\n");
      on_error();
      return 1;
    }
  }
  memcpy (chunk->content + chunk->nb, ptr, size);
  chunk->nb += size;
  return 0;
}

int chunk_add_char (Chunk* chunk, char c) {
  int r = 0;
  if (chunk->max < chunk->nb + sizeof (char)) {
    r = chunk_size_up (chunk, sizeof (char));
    if (r < 0) {
      printf("error in chunk_add_char !\n");
      on_error();
      return 1;
    }
  }
  *((char*) (chunk->content + chunk->nb)) = c;
  chunk->nb += sizeof (char);
  return 0;
}

int chunk_add_int (Chunk* chunk, int i) {
  int r = 0;
  if (chunk->max < chunk->nb + sizeof (int)) {
    r = chunk_size_up (chunk, sizeof (int));
    if (r < 0) {
      printf("error in chunk_add_int !\n");
      on_error();
      return 1;
    }
  }
  *((int*) (chunk->content + chunk->nb)) = i;
  chunk->nb += sizeof (int);
  return 0;
}

int chunk_add_float (Chunk* chunk, float f) {
  int r = 0;
  if (chunk->max < chunk->nb + sizeof (float)) {
    r = chunk_size_up (chunk, sizeof (float));
    if (r < 0) {
      printf("error in chunk_add_float !\n");
      on_error();
      return 1;
    }
  }
  *((float*) (chunk->content + chunk->nb)) = f;
  chunk->nb += sizeof (float);
  return 0;
}

int chunk_add_double (Chunk* chunk, double f) {
  int r = 0;
  if (chunk->max < chunk->nb + sizeof (double)) {
    r = chunk_size_up (chunk, sizeof (double));
    if (r < 0) {
      printf("error in chunk_add_double !\n");
      on_error();
      return 1;
    }
  }
  *((double*) (chunk->content + chunk->nb)) = f;
  chunk->nb += sizeof (double);
  return 0;
}

int chunk_add_ptr (Chunk* chunk, void* ptr) {
  int r = 0;
  if (chunk->max < chunk->nb + sizeof (void*)) {
    r = chunk_size_up (chunk, sizeof (void*));
    if (r < 0) {
      printf("error in chunk_add_ptr !\n");
      on_error();
      return 1;
    }
  }
  *((void**) (chunk->content + chunk->nb)) = ptr;
  chunk->nb += sizeof (void*);
  return 0;
}

int chunk_get (Chunk* chunk, void* ptr, int size) {
  if (chunk->nb + size <= chunk->max) {
    memcpy (ptr, chunk->content + chunk->nb, size);
    chunk->nb += size;
    return 0;
  }
  printf("error in chunk_get !\n");
  on_error();
  return 1;
}

char chunk_get_char (Chunk* chunk) {
  char c = 0;
  if (chunk->nb + sizeof (char) <= chunk->max) {
	c = *((char*) (chunk->content + chunk->nb));
	chunk->nb += sizeof (char);
  }
  else {
    printf("error in chunk_get_char !\n");
    on_error();
    return 0;
  }
  return c;
}

int chunk_get_int (Chunk* chunk) {
  int i = 0;
  if (chunk->nb + sizeof (int) <= chunk->max) {
	i = *((int*) (chunk->content + chunk->nb));
	chunk->nb += sizeof (int);
  }
  else {
    printf("error in chunk_get_int !\n");
    on_error();
    return 0;
  }
  return i;
}

float chunk_get_float (Chunk* chunk) {
  float f = 0;
  if (chunk->nb + sizeof (float) <= chunk->max) {
	f = *((float*) (chunk->content + chunk->nb));
	chunk->nb += sizeof (float);
  }
  else {
    printf("error in chunk_get_float !\n");
    on_error();
    return 0.0;
  }
  return f;
}

void* chunk_get_ptr (Chunk* chunk) {
  void* ptr = NULL;
  if (chunk->nb + sizeof (void*) <= chunk->max) {
	ptr = *((void**) (chunk->content + chunk->nb));
	chunk->nb += sizeof (void*);
  }
  else {
    printf("error in chunk_get_ptr !\n");
    on_error();
    return NULL;
  }
  return ptr;
}



/*==========*
 * RECYCLER *
 *==========*/

/* extern list* chunks; */

/* Chunk* get_chunk (void) { */
/*   if (chunks->nb == 0) */
/*     return chunk_new (); */
/*   else */
/*     return chunks->content[--(chunks->nb)]; */
/* } */

/* void drop_chunk (Chunk* chunk) { */
/*   chunk->nb = 0; */
/*   list_add (chunks, chunk); */
/* } */

Chunk* chunks[20];
int nb_recyclable_chunks = 0;

Chunk* get_chunk (void) {
  if (nb_recyclable_chunks == 0) return chunk_new ();
  else                           return chunks[--nb_recyclable_chunks];
}

void drop_chunk (Chunk* chunk) {
  chunk->nb = 0;
  if (nb_recyclable_chunks == 20) chunk_dealloc (chunk);
  else                            chunks[nb_recyclable_chunks++] = chunk;
}



// endian safe

int chunk_add_chars_endian_safe(Chunk* chunk, char* ptr, int nb) {
  int r = 0;
  nb *=  sizeof(char);
  if (chunk->max < (chunk->nb + nb)) {
    r = chunk_size_up (chunk, nb);
    if (r < 0) {
      printf("error in chunk_add_chars_endian_safe !\n");
      on_error();
      return 1;
    }
  }
  memcpy (chunk->content + chunk->nb, ptr, nb);
  chunk->nb += nb;
  return 0;
}

int chunk_get_chars_endian_safe(Chunk* chunk, char* result, int nb) {
  nb *=  sizeof(char);
  if ((chunk->nb + nb) <= chunk->max) {
    memcpy (result, chunk->content + chunk->nb, nb);
    chunk->nb += nb;
    return 0;
  }
  printf("error in chunk_get_chars_endian_safe !\n");
  on_error();
  return 1;
}


int chunk_add_ints_endian_safe(Chunk* chunk, int* ptr, int nb) {
  int i = 0;
  int *dest;
  int size = sizeof(int);
  int r = 0;
  if (chunk->max < (chunk->nb + (nb * size))) {
    r = chunk_size_up (chunk, (nb * size));
    if (r < 0) {
      printf("error in chunk_add_ints_endian_safe !\n");
      on_error();
      return 1;
    }
  }
  dest = (int*) (chunk->content + chunk->nb);
  for (i = 0; i < nb; i++) {
    dest[i] = SWAP_INT(ptr[i]);
  }
  chunk->nb += (nb * size);
  return 0;
}

int chunk_get_ints_endian_safe(Chunk* chunk, int* result, int nb) {
  int i = 0;
  int *src = (int*) (chunk->content + chunk->nb);
  int size = sizeof(int);
  if ((chunk->nb + (size * nb)) <= chunk->max) {
    for (i = 0; i < nb; i++) {
      result[i] = SWAP_INT(src[i]);
    }
    chunk->nb += (nb * size);
    return 0;
  }
  printf("error in chunk_get_ints_endian_safe !\n");
  on_error();
  return 1;
}


int chunk_add_floats_endian_safe(Chunk* chunk, float* ptr, int nb) {
  int i = 0;
  float *dest;
  int size = sizeof(float);
  int r = 0;
  if (chunk->max < (chunk->nb + (nb * size))) {
    r = chunk_size_up (chunk, (nb * size));
    if (r < 0) {
      printf("error in chunk_add_floats_endian_safe !\n");
      on_error();
      return 1;
    }
  }
  
  dest = (float*) (chunk->content + chunk->nb);
  for (i = 0; i < nb; i++) {
    dest[i] = SWAP_FLOAT(ptr[i]);
  }
  chunk->nb += (nb * size);
  return 0;
}

int chunk_get_floats_endian_safe(Chunk* chunk, float* result, int nb) {
  int i = 0;
  float *src = (float*) (chunk->content + chunk->nb);
  int size = sizeof(float);
  if ((chunk->nb + (size * nb)) <= chunk->max) {
    for (i = 0; i < nb; i++) {
      result[i] = SWAP_FLOAT(src[i]);
    }
    chunk->nb += (nb * size);
    return 0;
  }
  printf("error in chunk_get_floats_endian_safe !\n");
  on_error();
  return 1;
}


int chunk_add_char_endian_safe (Chunk* chunk, char c) {
  return chunk_add_chars_endian_safe(chunk, &c, 1);
}

int chunk_get_char_endian_safe (Chunk* chunk, char* result) {
  return chunk_get_chars_endian_safe(chunk, result, 1);
}


int chunk_add_int_endian_safe (Chunk* chunk, int i) {
  return chunk_add_ints_endian_safe(chunk, &i, 1);
}

int chunk_get_int_endian_safe (Chunk* chunk, int* result) {
  return chunk_get_ints_endian_safe(chunk, result, 1);
}


int chunk_add_float_endian_safe (Chunk* chunk, float f) {
  return chunk_add_floats_endian_safe(chunk, (&f), 1);
}

int chunk_get_float_endian_safe (Chunk* chunk, float* result) {
  return chunk_get_floats_endian_safe(chunk, result, 1);
}


int chunk_swap_int(int i) {
  union {
    int i;
    unsigned char b[4];
  } dat1, dat2;

  dat1.i = i;
  dat2.b[0] = dat1.b[3];
  dat2.b[1] = dat1.b[2];
  dat2.b[2] = dat1.b[1];
  dat2.b[3] = dat1.b[0];
  return dat2.i;
}

float chunk_swap_float(float f) {
  union {
    float f;
    unsigned char b[4];
  } dat1, dat2;

  dat1.f = f;
  dat2.b[0] = dat1.b[3];
  dat2.b[1] = dat1.b[2];
  dat2.b[2] = dat1.b[1];
  dat2.b[3] = dat1.b[0];
  return dat2.f;
}
