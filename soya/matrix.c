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
 * matrix.c : matrix and other 3D math functions
 * Copyright (C) 2001-2003 Bertrand 'blam' LAMY
 * Copyright (C) 2003-2006 Jean-Baptiste 'Jiba' LAMY
 **********************************************/

#include "matrix.h"


GLfloat user_matrix[19];

int exp_of_2 (int a) {
  /* a = 2 ^ b
   * return b
   */
  switch (a) {
  case     1: return  0;
  case     2: return  1;
  case     4: return  2;
  case     8: return  3;
  case    16: return  4;
  case    32: return  5;
  case    64: return  6;
  case   128: return  7;
  case   256: return  8;
  case   512: return  9;
  case  1024: return 10;
  case  2048: return 11;
  case  4096: return 12;
  case  8192: return 13;
  default: return -1;
  }
}

void equation_2_2 (GLfloat* result, GLfloat a1, GLfloat b1, GLfloat c1, GLfloat a2, GLfloat b2, GLfloat c2) {
  /* a1 * result[0] + b1 * result[1] + c1 = 0
   * a2 * result[0] + b2 * result[1] + c2 = 0
   */
  GLfloat d = b2 * a1 - b1 * a2;
  if (d == 0.0f) return;
  d = 1.0f / d;
  result[0] = (b1 * c2 - b2 * c1) * d;
  result[1] = (a2 * c1 - a1 * c2) * d;
}

int float_array_compare (GLfloat* values, GLfloat* references, int nb) {
  int i;
  for (i = 0; i < nb; i++) {
    if (fabs (values[i] - references[i]) > EPSILON) return FALSE;
  }
  return TRUE;
}

int cone_from_sphere_and_origin (GLfloat* cone, GLfloat* sphere, GLfloat* point, GLfloat length) {
  GLfloat f;
  GLfloat g;
  GLfloat h;
  /* CONE (float[9]): start x, y, z + vector x, y, z + length + radius at start + radius gain 
   * radius gain = (radius at end - radius at start) / length
   */
  cone[3] = sphere[0] - point[0];
  cone[4] = sphere[1] - point[1];
  cone[5] = sphere[2] - point[2];
  f = sqrt (cone[3] * cone[3] + cone[4] * cone[4] + cone[5] * cone[5]);
  if (f <= sphere[3]) {
    /* point is inside the sphere => impossible cone! */
    return FALSE;
  }
  h = 1.0 / f;
  cone[3] *= h;
  cone[4] *= h;
  cone[5] *= h;
  g = f - sphere[3];
  cone[0] = point[0] + g * cone[3];
  cone[1] = point[1] + g * cone[4];
  cone[2] = point[2] + g * cone[5];
  cone[6] = length;
  cone[7] = sphere[3] * g * h;
  cone[8] = 1.0 - f / g;
  return TRUE;
}

void cone_from_sphere_and_vector (GLfloat* cone, GLfloat* sphere, GLfloat* vector, GLfloat length) {
  /* return a cone that is, in fact, a cylinder */
  cone[0] = sphere[0] - sphere[3] * vector[0];
  cone[1] = sphere[1] - sphere[3] * vector[1];
  cone[2] = sphere[2] - sphere[3] * vector[2];
  /* assume vector is normalized */
  memcpy (cone + 3, vector, 3 * sizeof (GLfloat));
  cone[6] = length;
  cone[7] = sphere[3];
  cone[8] = 0.0;
}

int sphere_is_in_cone (GLfloat* sphere, GLfloat* cone) {
  GLfloat n[3];
  GLfloat k;
  /* compute square distance from sphere center to cone axis */
  n[0] = sphere[0] - cone[0];
  n[1] = sphere[1] - cone[1];
  n[2] = sphere[2] - cone[2];
  k = (cone[3] * n[0] + cone[4] * n[1] + cone[5] * n[2]) / (cone[3] * cone[3] + cone[4] * cone[4] + cone[5] * cone[5]);
  n[0] -= k * cone[3];
  n[1] -= k * cone[4];
  n[2] -= k * cone[5];
  if ((k < 0.0 && fabs (k) > sphere[3]) || (k > cone[6] + sphere[3])) {
    /* sphere is before start or after end */
    return FALSE;
  }
  k = sphere[3] + k * cone[8] + cone[7];
  if (n[0] * n[0] + n[1] * n[1] + n[2] * n[2] > k * k) {
    /* sphere is too far from cone axis */
    return FALSE;
  }
  return TRUE;
}

int point_is_in_sphere (GLfloat sphere[4], GLfloat point[3]) {
  GLfloat x, y, z;
  x = sphere[0] - point[0];
  y = sphere[1] - point[1];
  z = sphere[2] - point[2];
  if (x * x + y * y + z * z > sphere[3] * sphere[3]) {
    return FALSE;
  } else {
    return TRUE;
  }
}

int spheres_overlap (GLfloat sphere1[4], GLfloat sphere2[4]) {
  GLfloat x, y, z, d;
  x = sphere1[0] - sphere2[0];
  y = sphere1[1] - sphere2[1];
  z = sphere1[2] - sphere2[2];
  d = sphere1[3] + sphere2[3];
  if (x * x + y * y + z * z > d * d) {
    return FALSE;
  } else {
    return TRUE;
  }
}

/* distance between a point and a sphere. negative if the point is in the sphere */
GLfloat sphere_distance_point (GLfloat sphere[4], GLfloat point[3]) {
  GLfloat x; GLfloat y; GLfloat z;
  x = sphere[0] - point[0];
  y = sphere[1] - point[1];
  z = sphere[2] - point[2];
  return sqrt (x * x + y * y + z * z) - sphere[3];
}

/* distance between 2 spheres. negative if the spheres overlap. */
GLfloat sphere_distance_sphere (GLfloat sphere1[4], GLfloat sphere2[4]) {
  GLfloat x; GLfloat y; GLfloat z;
  x = sphere1[0] - sphere2[0];
  y = sphere1[1] - sphere2[1];
  z = sphere1[2] - sphere2[2];
  return sqrt (x * x + y * y + z * z) - sphere1[3] - sphere2[3];
}

void sphere_instance_into (GLfloat s[4], GLfloat* old, GLfloat* new) {
  GLfloat* matrix = NULL;
  GLfloat scalefactor[3] = { 1.0f, 1.0f, 1.0f };
  GLfloat scaling;
  /* change sphere s from coordsys oldc to coordsys newc */
  if (old == new) return;
  /* change center of coordsys */
  if (old != NULL) {
    point_by_matrix (s, old);
    scalefactor[0] *= matrix[16];
    scalefactor[1] *= matrix[17];
    scalefactor[2] *= matrix[18];
  }
  if (new != NULL) {
    point_by_matrix (s, new);
    scalefactor[0] *= matrix[16];
    scalefactor[1] *= matrix[17];
    scalefactor[2] *= matrix[18];
  }
  /* re-compute radius */
  scaling = scalefactor[0];
  if(scalefactor[1] > scaling) { scaling = scalefactor[1]; }
  if(scalefactor[2] > scaling) { scaling = scalefactor[2]; }
  s[3] *= scaling;
}

void sphere_from_2_spheres (GLfloat r[4], GLfloat s1[4], GLfloat s2[4]) {
  GLfloat k;
  GLfloat x = s2[0] - s1[0]; 
  GLfloat y = s2[1] - s1[1]; 
  GLfloat z = s2[2] - s1[2];
  GLfloat d = sqrt(x * x + y * y + z * z);
  /* check if one sphere is inside the other */
  if(d + s1[3] <= s2[3]) {
    r[0] = s2[0];
    r[1] = s2[1];
    r[2] = s2[2];
    r[3] = s2[3];
    return;
  }
  if(d + s2[3] <= s1[3]) {
    r[0] = s1[0];
    r[1] = s1[1];
    r[2] = s1[2];
    r[3] = s1[3];
    return;
  }
  /* compute a new sphere */
  k = (s2[3] - s1[3]) / d;
  r[0] = (s2[0] + s1[0] + k * x) * 0.5;
  r[1] = (s2[1] + s1[1] + k * y) * 0.5;
  r[2] = (s2[2] + s1[2] + k * z) * 0.5;
  r[3] = (d + s1[3] + s2[3]) * 0.5;
}

/* compute the smallest sphere enclosing nb spheres 
 * ok, that's not always the smaller sphere but...
 */
void sphere_from_spheres (GLfloat r[4], GLfloat* spheres, int nb) {
  int i; int j;
  GLfloat x; GLfloat y; GLfloat z;
  GLfloat d;
  GLfloat max = 0.0f;
  GLfloat* s1 = NULL;
  GLfloat* s2 = NULL;
  GLfloat* s1max = NULL;
  GLfloat* s2max = NULL;
  /* find the farthest couple of spheres */
  for (i = 0; i < nb; i++) {
    s1 = spheres + i * 4;
    for (j = i + 1; j < nb; j++) {
      s2 = spheres + j * 4;
      x = s2[0] - s1[0];
      y = s2[1] - s1[1];
      z = s2[2] - s1[2];
      d = sqrt(x * x + y * y + z * z) + s1[3] + s2[3];
      if (d > max) {
        max = d;
        s1max = s1;
        s2max = s2;
      }
    }
  }
  /* first result */
  r[0] = (s1max[0] + s2max[0]) * 0.5;
  r[1] = (s1max[1] + s2max[1]) * 0.5;
  r[2] = (s1max[2] + s2max[2]) * 0.5;
  r[3] = max * 0.5;
  /* recompute the radius */
  for (i = 0; i < nb; i++) {
    s1 = spheres + i * 4;
    x = s1[0] - r[0];
    y = s1[1] - r[1];
    z = s1[2] - r[2];
    d = sqrt (x * x + y * y + z * z) + s1[3];
    if (d > r[3]) { r[3] = d; }
  }
}

/* compute the smallest sphere enclosing nb points */
void sphere_from_points (GLfloat r[4], GLfloat* points, int nb) {
  int i; int j;
  GLfloat x; GLfloat y; GLfloat z;
  GLfloat d;
  GLfloat max = 0.0f;
  GLfloat* p1 = NULL;
  GLfloat* p2 = NULL;
  GLfloat* p1max = NULL;
  GLfloat* p2max = NULL;
  GLfloat r2[4]; 
  /* find the farthest couple of points */
  for (i = 0; i < nb; i++) {
    p1 = points + i * 3;
    for (j = i + 1; j < nb; j++) {
      p2 = points + j * 3;
      x = p2[0] - p1[0];
      y = p2[1] - p1[1];
      z = p2[2] - p1[2];
      d = x * x + y * y + z * z;
      if (d > max) {
        max = d;
        p1max = p1;
        p2max = p2;
      }
    }
  }
  /* first result */
  r[0] = (p1max[0] + p2max[0]) * 0.5;
  r[1] = (p1max[1] + p2max[1]) * 0.5;
  r[2] = (p1max[2] + p2max[2]) * 0.5;
  r[3] = sqrt (max) * 0.5;
  /* find points out of sphere */
  r2[0] = r[0];
  r2[1] = r[1];
  r2[2] = r[2];
  j = 0;
  for (i = 0; i < nb; i++) {
    if (point_distance_to (r, points + i * 3) - r[3] > 0.0f) {
      /* point i is out of sphere */
      p1 = points + i * 3;
      x = p1[0] - r[0];
      y = p1[1] - r[1];
      z = p1[2] - r[2];
      d = sqrt (x * x + y * y + z * z);
      d = 0.5 - r[3] / (d * 2.0);
      r2[0] += x * d;
      r2[1] += y * d;
      r2[2] += z * d;
      j = 1;
    }
  }
  if (j == 1) {
    /* set the new center */
    r[0] = r2[0];
    r[1] = r2[1];
    r[2] = r2[2];
    /* recompute the radius */
    max = 0.0f;
    for (i = 0; i < nb; i++) {
      p1 = points + i * 3;
      x = p1[0] - r[0];
      y = p1[1] - r[1];
      z = p1[2] - r[2];
      d = x * x + y * y + z * z;
      if (d > max) { max = d; }
    }
    r[3] = sqrt (max);
  }
}

void face_normal (GLfloat r[3], GLfloat a[3], GLfloat b[3], GLfloat c[3]) {
  GLfloat v1x; GLfloat v1y; GLfloat v1z;
  GLfloat v2x; GLfloat v2y; GLfloat v2z;
  v1x = b[0] - a[0];
  v1y = b[1] - a[1];
  v1z = b[2] - a[2];
  v2x = c[0] - a[0];
  v2y = c[1] - a[1];
  v2z = c[2] - a[2];
  r[0] =  v1y * v2z - v1z * v2y;
  r[1] = -v1x * v2z + v1z * v2x;
  r[2] =  v1x * v2y - v1y * v2x;
}

void face_plane (GLfloat r[4], GLfloat a[3], GLfloat b[3], GLfloat c[3]) {
  GLfloat v1x; GLfloat v1y; GLfloat v1z;
  GLfloat v2x; GLfloat v2y; GLfloat v2z;
  v1x = b[0] - a[0];
  v1y = b[1] - a[1];
  v1z = b[2] - a[2];
  v2x = c[0] - a[0];
  v2y = c[1] - a[1];
  v2z = c[2] - a[2];
  r[0] =  v1y * v2z - v1z * v2y;
  r[1] = -v1x * v2z + v1z * v2x;
  r[2] =  v1x * v2y - v1y * v2x;
  r[3] = -(a[0] * r[0] + a[1] * r[1] + a[2] * r[2]);
}

GLfloat point_distance_to (GLfloat a[3], GLfloat b[3]) {
  GLfloat x; GLfloat y; GLfloat z;
  x = a[0] - b[0];
  y = a[1] - b[1];
  z = a[2] - b[2];
  return sqrt (x * x + y * y + z * z);
}

double point_distance_to_d (double a[3], double b[3]) {
  double x; double y; double z;
  x = a[0] - b[0];
  y = a[1] - b[1];
  z = a[2] - b[2];
  return sqrt (x * x + y * y + z * z);
}

GLfloat point_square_distance_to (GLfloat a[3], GLfloat b[3]) {
  GLfloat x; GLfloat y; GLfloat z;
  x = a[0] - b[0];
  y = a[1] - b[1];
  z = a[2] - b[2];
  return (x * x + y * y + z * z);
}

GLfloat point_distance_plane (GLfloat a[3], GLfloat b[4]) {
  return b[0] * a[0] + b[1] * a[1] + b[2] * a[2] - b[3];
}

// Test a sphere against a plane
// Return 1 if the sphere is in front of the plane, 2 if it is behind, and 3 if it cross
char sphere_side_plane (GLfloat sphere[4], GLfloat plane[4]) {
  float dist;
  char  sides;
  dist = point_distance_plane(sphere, plane);
  if (fabs(dist) < sphere[3]) sides = 3;
  else if (dist >= 0)         sides = 1;
  else                        sides = 2;
  return sides;
}

void point_project_on_plane (GLfloat* a, GLfloat b[4]) {
  float d = b[0] * a[0] + b[1] * a[1] + b[2] * a[2] + b[3];
  a[0] += d * b[0];
  a[1] += d * b[1];
  a[2] += d * b[2];
}

void plane_vector_normalize (GLfloat v[4]) {
  GLfloat l = 1.0 / sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2]);
  v[0] *= l;
  v[1] *= l;
  v[2] *= l;
  v[3] *= l;
}

// If the ray cross the plane return the distance between start and intersection
// Distance is posistive if start is in front of the plane and negative if it is behind.
// If the ray does not cross the plane return INFINITY.
// +INFINITY if the start is in front of the plane and -INFINITY if it is behind.
// If length < 0 it is considered infinit
float ray_distance_plane (GLfloat start[3], GLfloat vect[3], GLfloat length, GLfloat plane[4], GLfloat offset) {
  float dem, num, dist;
  dem = vector_dot_product(plane, vect);
  num = point_distance_plane(start, plane) - offset;
  dist = num / fabs(dem);
  if ((fabs(dem) < EPSILON) || (num >= 0. && dem > 0.) || (num < 0. && dem < 0.))
  {
    if (num >= 0.) return  INFINITY;
    else           return -INFINITY;
  }
  if (length >= 0.)
  {
    if (dist >= 0. &&  dist > length)      return  INFINITY;
    else if (dist <  0. && -dist > length) return -INFINITY;
  }
  return dist;
}

void vector_normalize (GLfloat v[3]) {
  GLfloat l = 1.0 / sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2]);
  v[0] *= l;
  v[1] *= l;
  v[2] *= l;
}

void vector_set_length (GLfloat v[3], GLfloat l) {
  GLfloat f = l / sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2]);
  v[0] *= f;
  v[1] *= f;
  v[2] *= f;
}

void vector_cross_product (GLfloat r[3], GLfloat a[3], GLfloat b[3]) {
  r[0] = a[1] * b[2] - a[2] * b[1];
  r[1] = a[2] * b[0] - a[0] * b[2];
  r[2] = a[0] * b[1] - a[1] * b[0];
}

GLfloat vector_length (GLfloat v[3]) {
  return sqrt (v[0] * v[0] + v[1] * v[1] + v[2] * v[2]);
}
GLfloat vector_square_length (GLfloat v[3]) {
  return v[0] * v[0] + v[1] * v[1] + v[2] * v[2];
}

GLfloat vector_dot_product (GLfloat a[3], GLfloat b[3]) {
  return a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
}

/* return angle in radians */
GLfloat vector_angle (GLfloat a[3], GLfloat b[3]) {
  GLfloat s;
  GLfloat f;
  s = vector_length (a) * vector_length (b);
  if (s == 0.0f) { return 0.0f; }
  f = vector_dot_product (a, b) / s;
  if (f >=  1.0f) { return 0.0f; }
  if (f <= -1.0f) { return pi; }
  return atan (-f / sqrt (1.0 - f * f)) + pi_2;
}

void vector_from_points (GLfloat r[3], GLfloat a[3], GLfloat b[3]) {
  r[0] = b[0] - a[0];
  r[1] = b[1] - a[1];
  r[2] = b[2] - a[2];
}

void quaternion_normalize (GLfloat q[4]) {
  GLfloat l;
  l = 1.0 / sqrt(q[0] * q[0] + q[1] * q[1] + q[2] * q[2] + q[3] * q[3]);
  q[0] *= l;
  q[1] *= l;
  q[2] *= l;
  q[3] *= l;
}

void matrix_from_quaternion (GLfloat m[19], GLfloat q[4]) {
  GLfloat xx;
  GLfloat yy;
  GLfloat zz;
  GLfloat xy;
  GLfloat xz;
  GLfloat yz;
  GLfloat wx;
  GLfloat wy;
  GLfloat wz;
  quaternion_normalize (q);
  xx = 2.0 * q[0] * q[0];
  yy = 2.0 * q[1] * q[1];
  zz = 2.0 * q[2] * q[2];
  xy = 2.0 * q[0] * q[1];
  xz = 2.0 * q[0] * q[2];
  yz = 2.0 * q[1] * q[2];
  wx = 2.0 * q[0] * q[3];
  wy = 2.0 * q[1] * q[3];
  wz = 2.0 * q[2] * q[3];
  m[ 0] = 1.0 - yy - zz;
  m[ 1] = xy + wz;
  m[ 2] = xz - wy;
  m[ 3] = 0.0;
  m[ 4] = xy - wz;
  m[ 5] = 1.0 - xx - zz;
  m[ 6] = yz + wx;
  m[ 7] = 0.0;
  m[ 8] = xz + wy;
  m[ 9] = yz - wx;
  m[10] = 1.0 - xx - yy;
  m[11] = 0.0;
//  m[12] = 0.0;
//  m[13] = 0.0;
//  m[14] = 0.0;
  m[15] = 1.0;
  m[16] = 1.0;
  m[17] = 1.0;
  m[18] = 1.0;
}

/* Old bug'ed version
void quaternion_from_matrix (GLfloat q[4], GLfloat m[16]) {
  GLfloat s;
  s = sqrt (fabs (m[0] + m[5] + m[10] + m[15]));
  q[0] = - m[9] + m[6];
  q[1] = - m[2] + m[8];
  q[2] = - m[4] + m[1];
  q[3] = s * 0.5;
  if (s == 0.0f) {
    GLfloat q0 = abs(q[0]);
    GLfloat q1 = abs(q[1]);
    GLfloat q2 = abs(q[2]);
    GLfloat q3 = abs(q[3]);
    if (q0 >= q1 && q0 >= q2 && q0 >= q3) {
      q[0] = 1.0f;
      q[1] = 0.0f;
      q[2] = 0.0f;
    } else {
      if (q1 >= q0 && q1 >= q2 && q1 >= q3) {
        q[0] = 0.0f;
        q[1] = 1.0f;
        q[2] = 0.0f;
      } else {
        if (q2 >= q0 && q2 >= q1 && q2 >= q3) {
          q[0] = 0.0f;
          q[1] = 0.0f;
          q[2] = 1.0f;
        }
      }
    }
  } else {
    s = 0.5 / s;
    q[0] *= s;
    q[1] *= s;
    q[2] *= s;
  }
  quaternion_normalize (q);
}
*/

void quaternion_from_matrix (GLfloat q[4], GLfloat m[16]) {
  GLfloat s;
  s = 1 + m[0] + m[5] + m[10];
  if (s > 0.00000001) {
    s    = sqrt(fabs(s)) * 2;
    q[0] = -(m[9] - m[6]) / s;
    q[1] = -(m[2] - m[8]) / s;
    q[2] = -(m[4] - m[1]) / s;
    q[3] = 0.25 * s;
  } else if ((m[0] > m[5]) && (m[0] > m[10])) {
    s    = sqrt(fabs(1.0 + m[0] - m[5] - m[10])) * 2;
    q[0] = 0.25 * s;
    q[1] = -(m[4] + m[1]) / s;
    q[2] = -(m[2] + m[8]) / s;
    q[3] = -(m[9] - m[6]) / s;
  } else if (m[5] > m[10]) {
    s    = sqrt(fabs(1.0 + m[5] - m[0] - m[10])) * 2;
    q[0] = -(m[4] + m[1]) / s;
    q[1] = 0.25 * s;
    q[2] = -(m[9] + m[6]) / s;
    q[3] = -(m[2] - m[8]) / s;
  } else {
    s    = sqrt(fabs(1.0 + m[10] - m[0] - m[5])) * 2;
    q[0] = -(m[2] + m[8]) / s;
    q[1] = -(m[9] + m[6]) / s;
    q[2] = 0.25 * s;
    q[3] = -(m[4] - m[1]) / s;
  }
  quaternion_normalize(q);
}

void quaternion_rotation (GLfloat q[4], GLfloat v[3], GLfloat angle) {
  GLfloat s;
  angle = angle * 0.5;
  s = sin (angle);
  q[0] = s * v[0];
  q[1] = s * v[1];
  q[2] = s * v[2];
  q[3] = cos (angle);
  quaternion_normalize (q);
}

void quaternion_rotation_vectors (GLfloat q[4], GLfloat v_from[3], GLfloat v_to[3]) {
  /* Computes the shortest arc quaternion that will rotate one vector to another.
   * Code adapted from Cal3D, based on equations from "Game Programming Gems" - chapter 2.10
   */
  GLfloat dot;
  GLfloat f;
  vector_cross_product (q, v_from, v_to);
  dot = vector_dot_product (v_from, v_to);
  dot = sqrt (2 * (dot + 1));
  f = 1.0 / dot;
  q[0] *= f;
  q[1] *= f;
  q[2] *= f;
  q[3] = 0.5 * dot;
}

void multiply_quaternion (GLfloat r[4], GLfloat q2[4], GLfloat q1[4]) {
  r[0] = q1[3] * q2[0] + q1[0] * q2[3] + q1[1] * q2[2] - q1[2] * q2[1];
  r[1] = q1[3] * q2[1] - q1[0] * q2[2] + q1[1] * q2[3] + q1[2] * q2[0];
  r[2] = q1[3] * q2[2] + q1[0] * q2[1] - q1[1] * q2[0] + q1[2] * q2[3];
  r[3] = q1[3] * q2[3] - q1[0] * q2[0] - q1[1] * q2[1] - q1[2] * q2[2];
  quaternion_normalize (r);
}

void quaternion_by_vector (GLfloat r[4], GLfloat q[4], GLfloat v[3]) {
  r[0] = q[3] * v[0]               + q[1] * v[2] - q[2] * v[1];
  r[1] = q[3] * v[1] - q[0] * v[2]               + q[2] * v[0];
  r[2] = q[3] * v[2] + q[0] * v[1] - q[1] * v[0];
  r[3] =             - q[0] * v[0] - q[1] * v[1] - q[2] * v[2];
}

void quaternion_slerp (GLfloat q[4], GLfloat q1[4], GLfloat q2[4], GLfloat alpha, GLfloat one_minus_alpha) {
  GLfloat scale1;
  GLfloat scale2;
  GLfloat cosTheta = q1[0] * q2[0] + q1[1] * q2[1] + q1[2] * q2[2] + q1[3] * q2[3];
  char flip;
  if (cosTheta < 0.0f) {
    flip = 1;
    cosTheta = - cosTheta;
  } else {
    flip = 0;
  }
  if (1.0 - cosTheta < 0.05) {
    scale1 = one_minus_alpha;
    scale2 = alpha;
  } else {
    GLfloat theta = acos(cosTheta);
    GLfloat sinTheta = 1.0 / sin(theta);
    if (flip == 1) 
      scale1 = - sin (theta * one_minus_alpha) * sinTheta;
    else
      scale1 =   sin (theta * one_minus_alpha) * sinTheta;
    scale2 = sin (theta * alpha) * sinTheta;
  }
  q[0] = scale1 * q1[0] + scale2 * q2[0];
  q[1] = scale1 * q1[1] + scale2 * q2[1];
  q[2] = scale1 * q1[2] + scale2 * q2[2],
  q[3] = scale1 * q1[3] + scale2 * q2[3];
  quaternion_normalize (q);
}

/*
 * WARNING : value 16, 17 and 18 of matrices are the x, y and z scaling factors
 */

void matrix_invert (GLfloat r[19], GLfloat m[19]) {
  GLfloat det;
  det = m[0] * (m[5] * m[10] - m[9] * m[6])
      - m[4] * (m[1] * m[10] - m[9] * m[2])
      + m[8] * (m[1] * m[ 6] - m[5] * m[2]);
  if(det == 0.0f) { return; }
  det = 1.0 / det;
  r[ 0] =   det * (m[5] * m[10] - m[9] * m[6]);
  r[ 4] = - det * (m[4] * m[10] - m[8] * m[6]);
  r[ 8] =   det * (m[4] * m[ 9] - m[8] * m[5]);
  r[ 1] = - det * (m[1] * m[10] - m[9] * m[2]);
  r[ 5] =   det * (m[0] * m[10] - m[8] * m[2]);
  r[ 9] = - det * (m[0] * m[ 9] - m[8] * m[1]);
  r[ 2] =   det * (m[1] * m[ 6] - m[5] * m[2]);
  r[ 6] = - det * (m[0] * m[ 6] - m[4] * m[2]);
  r[10] =   det * (m[0] * m[ 5] - m[4] * m[1]);
  r[ 3] = 0.0f;
  r[ 7] = 0.0f;
  r[11] = 0.0f;
  r[15] = 1.0f;
  r[16] = 1.0 / m[16];
  r[17] = 1.0 / m[17];
  r[18] = 1.0 / m[18];
  r[12] = -(m[12] * r[0] + m[13] * r[4] + m[14] * r[ 8]);
  r[13] = -(m[12] * r[1] + m[13] * r[5] + m[14] * r[ 9]);
  r[14] = -(m[12] * r[2] + m[13] * r[6] + m[14] * r[10]);
}

void multiply_matrix (GLfloat r[19], GLfloat b[19], GLfloat a[19]) {
  r[ 0] = a[ 0] * b[0] + a[ 1] * b[4] + a[ 2] * b[ 8];
  r[ 4] = a[ 4] * b[0] + a[ 5] * b[4] + a[ 6] * b[ 8];
  r[ 8] = a[ 8] * b[0] + a[ 9] * b[4] + a[10] * b[ 8];
  r[12] = a[12] * b[0] + a[13] * b[4] + a[14] * b[ 8] + b[12];
  r[ 1] = a[ 0] * b[1] + a[ 1] * b[5] + a[ 2] * b[ 9];
  r[ 5] = a[ 4] * b[1] + a[ 5] * b[5] + a[ 6] * b[ 9];
  r[ 9] = a[ 8] * b[1] + a[ 9] * b[5] + a[10] * b[ 9];
  r[13] = a[12] * b[1] + a[13] * b[5] + a[14] * b[ 9] + b[13];
  r[ 2] = a[ 0] * b[2] + a[ 1] * b[6] + a[ 2] * b[10];
  r[ 6] = a[ 4] * b[2] + a[ 5] * b[6] + a[ 6] * b[10];
  r[10] = a[ 8] * b[2] + a[ 9] * b[6] + a[10] * b[10];
  r[14] = a[12] * b[2] + a[13] * b[6] + a[14] * b[10] + b[14];
  r[ 3] = 0.0f;
  r[ 7] = 0.0f;
  r[11] = 0.0f;
  r[15] = 1.0f;
  r[16] = a[16] * b[16];
  r[17] = a[17] * b[17];
  r[18] = a[18] * b[18];
}

void point_by_matrix (GLfloat p[3], GLfloat m[19]) {
  GLfloat x; GLfloat y; GLfloat z;
  x = p[0] * m[0] + p[1] * m[4] + p[2] * m[ 8] + m[12];
  y = p[0] * m[1] + p[1] * m[5] + p[2] * m[ 9] + m[13];
  z = p[0] * m[2] + p[1] * m[6] + p[2] * m[10] + m[14];
  p[0] = x;
  p[1] = y;
  p[2] = z;
}

void point_by_matrix_copy (GLfloat r[3], GLfloat p[3], GLfloat m[19]) {
  r[0] = p[0] * m[0] + p[1] * m[4] + p[2] * m[ 8] + m[12];
  r[1] = p[0] * m[1] + p[1] * m[5] + p[2] * m[ 9] + m[13];
  r[2] = p[0] * m[2] + p[1] * m[6] + p[2] * m[10] + m[14];
}

void sphere_by_matrix (GLfloat p[4], GLfloat m[19]) {
  GLfloat scaling, a, b, c, d;
  scaling = m[16];
  if (m[17] > scaling) { scaling = m[17]; }
  if (m[18] > scaling) { scaling = m[18]; }
  a = p[0] * m[0] + p[1] * m[4] + p[2] * m[ 8] + m[12];
  b = p[0] * m[1] + p[1] * m[5] + p[2] * m[ 9] + m[13];
  c = p[0] * m[2] + p[1] * m[6] + p[2] * m[10] + m[14];
  d = p[3] * scaling;
	p[0] = a;
  p[1] = b;
  p[2] = c;
  p[3] = d;
}

void sphere_by_matrix_copy (GLfloat r[4], GLfloat p[4], GLfloat m[19]) {
  GLfloat scaling;
  scaling = m[16];
  if (m[17] > scaling) { scaling = m[17]; }
  if (m[18] > scaling) { scaling = m[18]; }
  r[0] = p[0] * m[0] + p[1] * m[4] + p[2] * m[ 8] + m[12];
  r[1] = p[0] * m[1] + p[1] * m[5] + p[2] * m[ 9] + m[13];
  r[2] = p[0] * m[2] + p[1] * m[6] + p[2] * m[10] + m[14];
  r[3] = p[3] * scaling;
}

void point4_by_matrix (GLfloat p[4], GLfloat m[19]) {
  GLfloat x; GLfloat y; GLfloat z; GLfloat w;
  x = p[0] * m[0] + p[1] * m[4] + p[2] * m[ 8] + p[3] * m[12];
  y = p[0] * m[1] + p[1] * m[5] + p[2] * m[ 9] + p[3] * m[13];
  z = p[0] * m[2] + p[1] * m[6] + p[2] * m[10] + p[3] * m[14];
  w = p[0] * m[3] + p[1] * m[7] + p[2] * m[11] + p[3] * m[15];
  p[0] = x;
  p[1] = y;
  p[2] = z;
  p[3] = w;
}

void point_rotate_y (GLfloat p[3], GLfloat angle) {
  GLfloat old_1;
  GLfloat old_2;
  GLfloat co = cos (angle);
  GLfloat si = sin (angle);
  /* rotate around Y axis */
  old_1 = p[0];
  old_2 = p[2];
  p[0] = old_1 * co - old_2 * si;
  p[2] = old_2 * co + old_1 * si;
}

void point_rotate_x (GLfloat p[3], GLfloat angle) {
  GLfloat old_1;
  GLfloat old_2;
  GLfloat co = cos (angle);
  GLfloat si = sin (angle);
  /* rotate around X axis */
  old_1 = p[1];
  old_2 = p[2];
  p[1] = old_1 * co - old_2 * si;
  p[2] = old_2 * co + old_1 * si;
}

void point_rotate_z (GLfloat p[3], GLfloat angle) {
  GLfloat old_1;
  GLfloat old_2;
  GLfloat co = cos (angle);
  GLfloat si = sin (angle);
  /* rotate around Z axis */
  old_1 = p[0];
  old_2 = p[1];
  p[0] = old_1 * co - old_2 * si;
  p[1] = old_2 * co + old_1 * si;
}

void point_rotate_axe (GLfloat p[3], GLfloat angle, GLfloat x, GLfloat y, GLfloat z) {
  GLfloat d;
  GLfloat c;
  GLfloat s;
  GLfloat co;
  GLfloat nx; GLfloat ny; GLfloat nz;
  GLfloat xco; GLfloat yco; GLfloat zco;
  GLfloat xs; GLfloat ys; GLfloat zs;
  d = sqrt (x * x + y * y + z * z);
  if (d != 1.0f) {
    x /= d;
    y /= d;
    z /= d;
  }
  c = cos(angle);
  s = sin(angle);
  co = 1.0 - c;
  nx = p[0];
  ny = p[1];
  nz = p[2];
  xco = x * co;
  yco = y * co;
  zco = z * co;
  xs = x * s;
  ys = y * s;
  zs = z * s;
  p[0] = nx * (x * xco + c)  + ny * (x * yco - zs) + nz * (x * zco + ys);
  p[1] = nx * (y * xco + zs) + ny * (y * yco + c)  + nz * (y * zco - xs);
  p[2] = nx * (z * xco - ys) + ny * (z * yco + xs) + nz * (z * zco + c);
}

void point_rotate (GLfloat p[3], GLfloat angle, GLfloat p1[3], GLfloat p2[3]) {
  /* translate and rotate around axe */
  point_rotate_axe (p, angle, p2[0] - p1[0], p2[1] - p1[1], p2[2] - p1[2]);
  p[0] += p1[0];
  p[1] += p1[1];
  p[2] += p1[2];
}

void vector_by_matrix (GLfloat v[3], GLfloat m[19]) {
  GLfloat x; GLfloat y; GLfloat z;
  x = v[0] * m[0] + v[1] * m[4] + v[2] * m[ 8];
  y = v[0] * m[1] + v[1] * m[5] + v[2] * m[ 9];
  z = v[0] * m[2] + v[1] * m[6] + v[2] * m[10];
  v[0] = x;
  v[1] = y;
  v[2] = z;
}

void vector_by_matrix_copy (GLfloat r[3], GLfloat v[3], GLfloat m[19]) {
  r[0] = v[0] * m[0] + v[1] * m[4] + v[2] * m[ 8];
  r[1] = v[0] * m[1] + v[1] * m[5] + v[2] * m[ 9];
  r[2] = v[0] * m[2] + v[1] * m[6] + v[2] * m[10];
}

void plane_by_matrix (GLfloat p[4], GLfloat m[19]) {
  GLfloat a; GLfloat b; GLfloat c; GLfloat d;
  a = p[0] * m[ 0] + p[1] * m[ 4] + p[2] * m[ 8];
  b = p[0] * m[ 1] + p[1] * m[ 5] + p[2] * m[ 9];
  c = p[0] * m[ 2] + p[1] * m[ 6] + p[2] * m[10];
  d = p[0] * m[12] + p[1] * m[13] + p[2] * m[14] + p[3];
	p[0] = a;
	p[1] = b;
	p[2] = c;
	p[3] = d;
}

void plane_by_matrix_copy (GLfloat r[4], GLfloat p[4], GLfloat m[19]) {
  r[0] = p[0] * m[ 0] + p[1] * m[ 4] + p[2] * m[ 8];
  r[1] = p[0] * m[ 1] + p[1] * m[ 5] + p[2] * m[ 9];
  r[2] = p[0] * m[ 2] + p[1] * m[ 6] + p[2] * m[10];
	r[3] = p[0] * m[12] + p[1] * m[13] + p[2] * m[14] + p[3];
}

GLfloat length_by_matrix (GLfloat length, GLfloat m[19]) {
  GLfloat max;
  if (m[17] > m[16]) max = m[17]; else max = m[16];
  if (m[18] > max)   max = m[18];
  length *= fabs (max);
  return length;
}

void matrix_set_identity (GLfloat m[19]) {
  m[ 0] = 1.0f;
  m[ 1] = 0.0f;
  m[ 2] = 0.0f;
  m[ 3] = 0.0f;
  m[ 4] = 0.0f;
  m[ 5] = 1.0f;
  m[ 6] = 0.0f;
  m[ 7] = 0.0f;
  m[ 8] = 0.0f;
  m[ 9] = 0.0f;
  m[10] = 1.0f;
  m[11] = 0.0f;
  m[12] = 0.0f;
  m[13] = 0.0f;
  m[14] = 0.0f;
  m[15] = 1.0f;
  m[16] = 1.0f;
  m[17] = 1.0f;
  m[18] = 1.0f;
}

void matrix_scale(GLfloat m[19], GLfloat x, GLfloat y, GLfloat z) {
  m[ 0] *= x;
  m[ 1] *= x;
  m[ 2] *= x;
  m[ 4] *= y;
  m[ 5] *= y;
  m[ 6] *= y;
  m[ 8] *= z;
  m[ 9] *= z;
  m[10] *= z;
  m[16] *= x;
  m[17] *= y;
  m[18] *= z;
}

void matrix_turn_y (GLfloat m[19], GLfloat angle) {
  GLfloat c; GLfloat s;
  GLfloat m0; GLfloat m1; GLfloat m2; 
  /* rotate along Y axis of the matrix */
  /* Following code is equivalent (with simplifications!) to:
   *   matrix_set_identity (b);
   *   matrix_rotate_y (b, angle);
   *   multiply_matrix (r, m, b);
   */
  c = cos (angle);
  s = sin (angle);
  m0 = m[0];
  m1 = m[1];
  m2 = m[2];
  m[ 0] = c * m0 - s * m[ 8];
  m[ 1] = c * m1 - s * m[ 9];
  m[ 2] = c * m2 - s * m[10];
  m[ 8] = s * m0 + c * m[ 8];
  m[ 9] = s * m1 + c * m[ 9];
  m[10] = s * m2 + c * m[10];
}

void matrix_turn_x (GLfloat m[19], GLfloat angle) {
  GLfloat c; GLfloat s;
  GLfloat m4; GLfloat m5; GLfloat m6; 
  /* rotate along X axis of the matrix */
  /* Following code is equivalent (with simplifications!) to:
   *   matrix_set_identity (b);
   *   matrix_rotate_x (b, angle);
   *   multiply_matrix (r, m, b);
   */
  c = cos (angle);
  s = sin (angle);
  m4 = m[4];
  m5 = m[5];
  m6 = m[6];
  m[ 4] =   c * m4 + s * m[ 8];
  m[ 5] =   c * m5 + s * m[ 9];
  m[ 6] =   c * m6 + s * m[10];
  m[ 8] = - s * m4 + c * m[ 8];
  m[ 9] = - s * m5 + c * m[ 9];
  m[10] = - s * m6 + c * m[10];
}

void matrix_turn_z (GLfloat m[19], GLfloat angle) {
  GLfloat c; GLfloat s;
  GLfloat m0; GLfloat m1; GLfloat m2;
  /* rotate along Z axis of the matrix */
  /* Following code is equivalent (with simplifications!) to:
   *   matrix_set_identity (b);
   *   matrix_rotate_z (b, angle);
   *   multiply_matrix (r, m, b);
   */
  c = cos (angle);
  s = sin (angle);
  m0 = m[0];
  m1 = m[1];
  m2 = m[2];
  m[0] =   c * m0 + s * m[4];
  m[1] =   c * m1 + s * m[5];
  m[2] =   c * m2 + s * m[6];
  m[4] = - s * m0 + c * m[4];
  m[5] = - s * m1 + c * m[5];
  m[6] = - s * m2 + c * m[6];
}

void matrix_turn_axe (GLfloat m[19], GLfloat angle, GLfloat x, GLfloat y, GLfloat z) {
  GLfloat p[3];
  GLfloat o[19];
  GLfloat d;
  GLfloat s;
  GLfloat c; GLfloat co;
  GLfloat xco; GLfloat yco; GLfloat zco;
  GLfloat xs; GLfloat ys; GLfloat zs;
  d = sqrt (x * x + y * y + z * z);
  if (d != 1.0) {
    x /= d;
    y /= d;
    z /= d;
  }
  c = cos(angle);
  s = sin(angle);
  co = 1.0 - c;
  xco = x * co;
  yco = y * co;
  zco = z * co;
  xs = x * s;
  ys = y * s;
  zs = z * s;
  matrix_copy (o, m);
  m[0] = x * xco + c;
  m[1] = y * xco + zs;
  m[2] = z * xco - ys;
  vector_by_matrix (m, o);
  m[4] = x * yco - zs;
  m[5] = y * yco + c;
  m[6] = z * yco + xs;
  vector_by_matrix (p, o);
  m[ 8] = x * zco + ys;
  m[ 9] = y * zco - xs;
  m[10] = z * zco + c;
  vector_by_matrix (p, o);
}

void matrix_rotate_axe (GLfloat m[19], GLfloat angle, GLfloat x, GLfloat y, GLfloat z) {
  /* This is equivalent to:
   *   point_rotate_axe (m,     angle, x, y, z);
   *   point_rotate_axe (m + 4, angle, x, y, z);
   *   point_rotate_axe (m + 8, angle, x, y, z);
   */
  GLfloat d;
  GLfloat c;
  GLfloat s;
  GLfloat co;
  GLfloat ox; GLfloat oy; GLfloat oz;
  GLfloat f1; GLfloat f2; GLfloat f3; GLfloat f4; GLfloat f5; GLfloat f6; GLfloat f7; GLfloat f8; GLfloat f9;
  d = sqrt (x * x + y * y + z * z);
  if (d != 1.0) {
    x /= d;
    y /= d;
    z /= d;
  }
  c = cos(angle);
  s = sin(angle);
  co = 1.0 - c;
  ox = x * co;
  oy = y * co;
  oz = z * co;
  f1 = x * ox + c;
  f5 = y * oy + c;
  f9 = z * oz + c;
  d = z * s;
  f2 = x * oy - d;
  f4 = y * ox + d;
  d = y * s;
  f3 = x * oz + d;
  f7 = z * ox - d;
  d = x * s;
  f6 = y * oz - d;
  f8 = z * oy + d;
  ox = m[0];
  oy = m[1];
  oz = m[2];
  m[0] = ox * f1 + oy * f2 + oz * f3;
  m[1] = ox * f4 + oy * f5 + oz * f6;
  m[2] = ox * f7 + oy * f8 + oz * f9;
  ox = m[4];
  oy = m[5];
  oz = m[6];
  m[4] = ox * f1 + oy * f2 + oz * f3;
  m[5] = ox * f4 + oy * f5 + oz * f6;
  m[6] = ox * f7 + oy * f8 + oz * f9;
  ox = m[ 8];
  oy = m[ 9];
  oz = m[10];
  m[ 8] = ox * f1 + oy * f2 + oz * f3;
  m[ 9] = ox * f4 + oy * f5 + oz * f6;
  m[10] = ox * f7 + oy * f8 + oz * f9;
}

void matrix_rotate_y (GLfloat m[19], GLfloat angle) {
  GLfloat c; GLfloat s;
  GLfloat m0; GLfloat m4; GLfloat m8;
  /* rotate along Y axis of parent with matrix origin */
  c = cos (angle);
  s = sin (angle);
  m0 = m[0];
  m4 = m[4];
  m8 = m[8];
  m[ 0] =   m0 * c + m[ 2] * s;
  m[ 4] =   m4 * c + m[ 6] * s;
  m[ 8] =   m8 * c + m[10] * s;
  m[ 2] = - m0 * s + m[ 2] * c;
  m[ 6] = - m4 * s + m[ 6] * c;
  m[10] = - m8 * s + m[10] * c;
  /*
   * m[12] =   m12 * c + m[14] * s;
   * m[14] = - m12 * s + m[14] * c;
   */
}

void matrix_rotate_x (GLfloat m[19], GLfloat angle) {
  GLfloat c; GLfloat s;
  GLfloat m1; GLfloat m5; GLfloat m9;
  /* rotate along X axis of parent with matrix origin */
  c = cos (angle);
  s = sin (angle);
  m1 = m[1];
  m5 = m[5];
  m9 = m[9];
  m[ 1] = m[1] * c - m[ 2] * s;
  m[ 5] = m[5] * c - m[ 6] * s;
  m[ 9] = m[9] * c - m[10] * s;
  m[ 2] = m1   * s + m[ 2] * c;
  m[ 6] = m5   * s + m[ 6] * c;
  m[10] = m9   * s + m[10] * c;
  /*
   * m[13] = m[13] * c - m[14] * s;
   * m[14] = m13 * s + m[14] * c;
   */
}

void matrix_rotate_z (GLfloat m[19], GLfloat angle) {
  GLfloat c; GLfloat s; 
  GLfloat m0; GLfloat m4; GLfloat m8;
  /* rotate along Z axis of parent with matrix origin */
  c = cos (angle);
  s = sin (angle);
  m0 = m[0];
  m4 = m[4];
  m8 = m[8];
  m[0] = m[0] * c - m[1] * s;
  m[4] = m[4] * c - m[5] * s;
  m[8] = m[8] * c - m[9] * s;
  m[1] = m0   * s + m[1] * c;
  m[5] = m4   * s + m[5] * c;
  m[9] = m8   * s + m[9] * c;
  /*
   * m[12] = m12 * c - m[13] * s;
   * m[13] = m12 * s + m[13] * c;
   */
}

#if 0
void matrix_rotate_axe (GLfloat m[19], GLfloat angle, GLfloat x, GLfloat y, GLfloat z) {
  GLfloat r[19]; GLfloat f[19];
  GLfloat d; GLfloat c; GLfloat s; GLfloat co;
  d = sqrt (x * x + y * y + z * z);
  if (d != 1.0) {
    x /= d;
    y /= d;
    z /= d;
  }
  c = cos(angle);
  s = sin(angle);
  co = 1.0 - c;
  d = x * co;
  r[ 0] = x * d + c;
  r[ 1] = y * d + z * s;
  r[ 2] = z * d - y * s;
  r[ 3] = 0.0;
  d = y * co;
  r[ 4] = x * d - z * s;
  r[ 5] = y * d + c;
  r[ 6] = z * d + x * s;
  r[ 7] = 0.0;
  d = z * co;
  r[ 8] = x * d + y * s;
  r[ 9] = y * d - x * s;
  r[10] = z * d + c;
  r[11] = 0.0;
  r[12] = 0.0;
  r[13] = 0.0;
  r[14] = 0.0;
  r[15] = 1.0;
  r[16] = 1.0;
  r[17] = 1.0;
  r[18] = 1.0;
  matrix_copy (f, m);
  multiply_matrix (m, r, f);
}
#endif

void matrix_rotate (GLfloat m[19], GLfloat angle, GLfloat p[3], GLfloat v[3]) {
  GLfloat r[19]; GLfloat f[19];
  GLfloat cosAlpha; GLfloat sinAlpha;
  GLfloat cosTheta; GLfloat cosTheta2; GLfloat sinTheta; GLfloat sinTheta2;
  GLfloat cosPhi; GLfloat cosPhi2; GLfloat sinPhi; GLfloat sinPhi2;
  GLfloat c;
  double phi; double theta;
  theta = atan2 (v[1], v[0]);
  phi = atan2 (sqrt (v[0] * v[0] + v[1] * v[1]), v[2]);
  cosAlpha = cos(angle);
  sinAlpha = sin(angle);
  cosTheta = cos(theta);
  cosTheta2 = cosTheta * cosTheta;
  sinTheta = sin(theta);
  sinTheta2 = sinTheta * sinTheta;
  cosPhi = cos(phi);
  cosPhi2 = cosPhi * cosPhi;
  sinPhi = sin(phi);
  sinPhi2 = sinPhi * sinPhi;
  c = 1.0 - cosAlpha;
  r[ 0] = cosTheta2 * (cosAlpha * cosPhi2 + sinPhi2) + cosAlpha * sinTheta2;
  r[ 1] = sinAlpha * cosPhi + c * sinPhi2 * cosTheta * sinTheta;
  r[ 2] = sinPhi * (cosPhi * cosTheta * c - sinAlpha * sinTheta);
  r[ 3] = 0.0;
  r[ 4] = sinPhi2 * cosTheta * sinTheta*c - sinAlpha * cosPhi;
  r[ 5] = sinTheta2 * (cosAlpha * cosPhi2 + sinPhi2) + cosAlpha * cosTheta2;
  r[ 6] = sinPhi * (cosPhi * sinTheta * c + sinAlpha * cosTheta);
  r[ 7] = 0.0;
  r[ 8] = sinPhi * (cosPhi * cosTheta * c + sinAlpha * sinTheta);
  r[ 9] = sinPhi * (cosPhi * sinTheta * c - sinAlpha * cosTheta);
  r[10] = cosAlpha * sinPhi2 + cosPhi2;
  r[11] = 0.0;
  r[12] = p[0] - p[0] * m[0] - p[1] * m[4] - p[2] * m[ 8];
  r[13] = p[1] - p[0] * m[1] - p[1] * m[5] - p[2] * m[ 9];
  r[14] = p[2] - p[0] * m[2] - p[1] * m[6] - p[2] * m[10];
  r[15] = 1.0;
  r[16] = 1.0;
  r[17] = 1.0;
  r[18] = 1.0;
  matrix_copy(f, m);
  multiply_matrix(m, r, f);
}

void matrix_translate (GLfloat m[19], GLfloat x, GLfloat y, GLfloat z) {
  m[12] += x;
  m[13] += y;
  m[14] += z;
}

int matrix_is_direct (GLfloat m[19]) {
  GLfloat param = m[ 0] * m[5] * m[10]
                + m[ 1] * m[6] * m[ 8]
                + m[ 2] * m[4] * m[ 9]
                - m[ 8] * m[5] * m[ 2]
                - m[ 9] * m[6] * m[ 0]
                - m[10] * m[4] * m[ 1];
  if (param >= 0.0) { return FALSE; } else { return TRUE; }
}

void matrix_look_at_Z (GLfloat m[19], GLfloat p[3]) {
  GLfloat q[3];
  /* - Z axis of the matrix will look to p */
  q[0] = p[0] - m[12];
  q[1] = p[1] - m[13];
  q[2] = p[2] - m[14];
  matrix_look_to_Z (m, q);
}

void matrix_look_at_Y (GLfloat m[19], GLfloat p[3]) {
  GLfloat q[3];
  /* Y axis of the matrix will look to p */
  q[0] = p[0] - m[12];
  q[1] = p[1] - m[13];
  q[2] = p[2] - m[14];
  matrix_look_to_Y (m, q);
}

void matrix_look_at_X (GLfloat m[19], GLfloat p[3]) {
  GLfloat q[3];
  /* X axis of the matrix will look to p */
  q[0] = p[0] - m[12];
  q[1] = p[1] - m[13];
  q[2] = p[2] - m[14];
  matrix_look_to_X (m, q);
}

void matrix_look_to_Z (GLfloat m[19], GLfloat w[3]) {
  /* works only for ortho coordsys */
  GLfloat k; GLfloat t; GLfloat v;
  int direct;
  if (w[0] == 0.0 && w[1] == 0.0 && w[2] == 0.0) return;
  /* check wether coordsys is direct or not */
  direct = - 1;
  if (m[16] < 0.0) direct = 1;
  if (m[17] < 0.0) direct = - direct;
  if (m[18] < 0.0) direct = - direct;
  /* determine the w vector (= Oz) */
  /* NB : negative value cause our matrix looks to -z */
  v = - 1.0 / sqrt (w[0] * w[0] + w[1] * w[1] + w[2] * w[2]);
  user_matrix[ 8] = w[0] * v;
  user_matrix[ 9] = w[1] * v;
  user_matrix[10] = w[2] * v;
  /* determine horizontality and verticality vector, for old matrix (m) 
   * horizontality : old Z projection on the Oxz plane
   * verticality   : cross product old Z . horizontality
   * length must be 1
   */
  if (fabs (m[10]) <= EPSILON && fabs (m[8]) <= EPSILON) {
    user_matrix[0] = - 1.0;
    user_matrix[2] =   0.0;
  } else {
    v = 1.0 / sqrt (m[8] * m[8] + m[10] * m[10]);
    user_matrix[0] = - m[10] * v;
    user_matrix[2] =   m[ 8] * v;
  }
  user_matrix[4] = - user_matrix[2] * m[9];
  user_matrix[5] =   user_matrix[2] * m[8] - user_matrix[0] * m[10];
  user_matrix[6] =   user_matrix[0] * m[9];
  /* determine incline angle = parameters k and t 
   * express old X vector in function of horizontality and verticality
   * old X = k * horizontality + t * verticality
   */
  if (fabs (user_matrix[5]) > EPSILON) {
    t = m[1] / user_matrix[5];
    if (fabs (user_matrix[0]) > EPSILON) {
      k = (m[0] - t * user_matrix[4]) / user_matrix[0];
    } else {
      k = (m[2] - t * user_matrix[6]) / user_matrix[2];
    }
  } else {
    v = user_matrix[2] * user_matrix[4] - user_matrix[0] * user_matrix[6];
    t = (m[0] * user_matrix[2] - m[2] * user_matrix[0]) / v;
    k = (m[2] * user_matrix[4] - m[0] * user_matrix[6]) / v;
  }
  /* determine horizontality and verticality vector, for new matrix */
  if (fabs (user_matrix[10]) <= EPSILON && fabs (user_matrix[8]) <= EPSILON) {
    user_matrix[4] = - 1.0;
    user_matrix[6] =   0.0;
  } else {
    v = 1.0 / sqrt (user_matrix[8] * user_matrix[8] + user_matrix[10] * user_matrix[10]);
    user_matrix[4] = - user_matrix[10] * v;
    user_matrix[6] =   user_matrix[ 8] * v;
  }
  /* determine the u vector (= Ox) */
  user_matrix[0] = k * user_matrix[4] - t *  user_matrix[6] * user_matrix[9];
  user_matrix[1] =                      t * (user_matrix[6] * user_matrix[8] - user_matrix[4] * user_matrix[10]);
  user_matrix[2] = k * user_matrix[6] + t *  user_matrix[4] * user_matrix[9];
  /* determine the v vector (= Oy) <=> cross product Ox . Oz */
  if (direct == - 1) {
    m[4] = (- user_matrix[1] * user_matrix[10] + user_matrix[2] * user_matrix[ 9]) * m[17];
    m[5] = (- user_matrix[2] * user_matrix[ 8] + user_matrix[0] * user_matrix[10]) * m[17];
    m[6] = (- user_matrix[0] * user_matrix[ 9] + user_matrix[1] * user_matrix[ 8]) * m[17];
  } else {
    m[4] = (  user_matrix[1] * user_matrix[10] - user_matrix[2] * user_matrix[ 9]) * m[17];
    m[5] = (  user_matrix[2] * user_matrix[ 8] - user_matrix[0] * user_matrix[10]) * m[17];
    m[6] = (  user_matrix[0] * user_matrix[ 9] - user_matrix[1] * user_matrix[ 8]) * m[17];
  }
  /* scale vectors to the size given by old matrix */
  m[ 0] = user_matrix[ 0];
  m[ 1] = user_matrix[ 1];
  m[ 2] = user_matrix[ 2];
  m[ 8] = user_matrix[ 8] * m[18];
  m[ 9] = user_matrix[ 9] * m[18];
  m[10] = user_matrix[10] * m[18];
}

void matrix_look_to_Y (GLfloat m[19], GLfloat w[3]) {
  /* works only for ortho coordsys */
  GLfloat k; GLfloat t; GLfloat v;
  int direct;
  if (w[0] == 0.0 && w[1] == 0.0 && w[2] == 0.0) { return; }
  /* check wether coordsys is direct or not */
  direct = 1;
  if (m[16] < 0.0) { direct = - 1; }
  if (m[17] < 0.0) { direct = - direct; }
  if (m[18] < 0.0) { direct = - direct; }
  /* determine the v vector (= Oy) */
  v = 1.0 / sqrt (w[0] * w[0] + w[1] * w[1] + w[2] * w[2]);
  user_matrix[4] = w[0] * v;
  user_matrix[5] = w[1] * v;
  user_matrix[6] = w[2] * v;
  /* determine horizontality and verticality vector, for old matrix (m) 
   * horizontality : old Y projection on the Oyz plane
   * verticality   : cross product old Y . horizontality
   * length must be 1
   */
  if (fabs (m[5]) <= EPSILON && fabs (m[6]) <= EPSILON) {
    user_matrix[1] = 1.0;
    user_matrix[2] = 0.0;
  } else {
    v = 1.0 / sqrt (m[5] * m[5] + m[6] * m[6]);
    user_matrix[1] = - m[6] * v;
    user_matrix[2] =   m[5] * v;
  }
  user_matrix[ 8] =   user_matrix[1] * m[6] - user_matrix[2] * m[5];
  user_matrix[ 9] =   user_matrix[2] * m[4];
  user_matrix[10] = - user_matrix[1] * m[4];
  /* determine incline angle = parameters k and t 
   * express old X vector in function of horizontality and verticality
   * old X = k * horizontality + t * verticality
   */
  if (fabs (user_matrix[8]) > EPSILON) {
    t = m[0] / user_matrix[8];
    if (fabs (user_matrix[2]) > EPSILON) {
      k = (m[2] - t * user_matrix[10]) / user_matrix[2];
    } else {
      k = (m[1] - t * user_matrix[9]) / user_matrix[1];
    }
  } else {
    v = (user_matrix[9] * user_matrix[2] - user_matrix[10] * user_matrix[1]);
    t = (m[1] * user_matrix[2] - m[2] * user_matrix[ 1]) / v;
    k = (m[2] * user_matrix[9] - m[1] * user_matrix[10]) / v;
  }
  /* determine horizontality and verticality vector, for new matrix */
  if (fabs (user_matrix[5]) <= EPSILON && fabs (user_matrix[6]) <= EPSILON) {
    user_matrix[ 9] = 1.0;
    user_matrix[10] = 0.0;
  } else {
    v = 1.0 / sqrt (user_matrix[5] * user_matrix[5] + user_matrix[6] * user_matrix[6]);
    user_matrix[ 9] = - user_matrix[6] * v;
    user_matrix[10] =   user_matrix[5] * v;
  }
  /* determine the u vector (= Ox) */
  user_matrix[0] =                       t * (user_matrix[ 9] * user_matrix[6] - user_matrix[10] * user_matrix[5]);
  user_matrix[1] = k * user_matrix[ 9] + t *  user_matrix[10] * user_matrix[4];
  user_matrix[2] = k * user_matrix[10] - t *  user_matrix[ 9] * user_matrix[4];
  /* determine the w vector (= Oz) <=> cross product Ox . Oy */
  if (direct == - 1) {
    m[ 8] = (- user_matrix[1] * user_matrix[6] + user_matrix[2] * user_matrix[5]) * m[18];
    m[ 9] = (- user_matrix[2] * user_matrix[4] + user_matrix[0] * user_matrix[6]) * m[18];
    m[10] = (- user_matrix[0] * user_matrix[5] + user_matrix[1] * user_matrix[4]) * m[18];
  } else {
    m[ 8] = (  user_matrix[1] * user_matrix[6] - user_matrix[2] * user_matrix[5]) * m[18];
    m[ 9] = (  user_matrix[2] * user_matrix[4] - user_matrix[0] * user_matrix[6]) * m[18];
    m[10] = (  user_matrix[0] * user_matrix[5] - user_matrix[1] * user_matrix[4]) * m[18];
  }
  /* scale vectors to the size given by old matrix */
  m[0] = user_matrix[0];
  m[1] = user_matrix[1];
  m[2] = user_matrix[2];
  m[4] = user_matrix[4] * m[17];
  m[5] = user_matrix[5] * m[17];
  m[6] = user_matrix[6] * m[17];
}

void matrix_look_to_X (GLfloat m[19], GLfloat w[3]) {
  /* works only for ortho coordsys */
  GLfloat k; GLfloat t; GLfloat v;
  int direct;
  if (w[0] == 0.0 && w[1] == 0.0 && w[2] == 0.0) { return; }
  /* check wether coordsys is direct or not */
  direct = 1;
  if (m[16] < 0.0) { direct = - 1; }
  if (m[17] < 0.0) { direct = - direct; }
  if (m[18] < 0.0) { direct = - direct; }
  /* determine the x vector (= Ox) */
  v = 1.0 / sqrt (w[0] * w[0] + w[1] * w[1] + w[2] * w[2]);
  user_matrix[0] = w[0] * v;
  user_matrix[1] = w[1] * v;
  user_matrix[2] = w[2] * v;
  /* determine horizontality and verticality vector, for old matrix (m) 
   * horizontality : old X projection on the Oxz plane
   * verticality   : cross product old X . horizontality
   * length must be 1
   */
  if (fabs (m[0]) <= EPSILON && fabs (m[2]) <= EPSILON) {
    user_matrix[4] = 1.0;
    user_matrix[6] = 0.0;
  } else {
    v = 1.0 / sqrt (m[0] * m[0] + m[2] * m[2]);
    user_matrix[4] = - m[2] * v;
    user_matrix[6] =   m[0] * v;
  }
  user_matrix[ 8] = - user_matrix[6] * m[1];
  user_matrix[ 9] =   user_matrix[6] * m[0] - user_matrix[4] * m[2];
  user_matrix[10] =   user_matrix[4] * m[1];
  /* determine incline angle = parameters k and t 
   * express old Z vector in function of horizontality and verticality
   * old Z = k * horizontality + t * verticality
   */
  if (fabs (user_matrix[9]) > EPSILON) {
    t = m[9] / user_matrix[9];
    if (fabs (user_matrix[4]) > EPSILON) {
      k = (m[8] - t * user_matrix[8]) / user_matrix[4];
    } else {
      k = (m[10] - t * user_matrix[10]) / user_matrix[6];
    }
  } else {
    v = (user_matrix[8] * user_matrix[6] - user_matrix[10] * user_matrix[4]);
    t = (m[ 8] * user_matrix[6] - m[10] * user_matrix[ 4]) / v;
    k = (m[10] * user_matrix[8] - m[ 8] * user_matrix[10]) / v;
  }
  /* determine horizontality and verticality vector, for new matrix */
  if (fabs (user_matrix[0]) <= EPSILON && fabs (user_matrix[2]) <= EPSILON) {
    user_matrix[4] = 1.0;
    user_matrix[6] = 0.0;
  } else {
    v = 1.0 / sqrt (user_matrix[0] * user_matrix[0] + user_matrix[2] * user_matrix[2]);
    user_matrix[4] = - user_matrix[2] * v;
    user_matrix[6] =   user_matrix[0] * v;
  }
  /* determine the w vector (= Oz) */
  user_matrix[ 8] = k * user_matrix[4] - t *  user_matrix[6] * user_matrix[1];
  user_matrix[ 9] =                      t * (user_matrix[6] * user_matrix[0] - user_matrix[4] * user_matrix[2]);
  user_matrix[10] = k * user_matrix[6] + t *  user_matrix[4] * user_matrix[1];
  /* determine the v vector (= Oy) <=> cross product Ox . Oz */
  if (direct == - 1) {
    m[4] = (- user_matrix[1] * user_matrix[10] + user_matrix[2] * user_matrix[ 9]) * m[17];
    m[5] = (- user_matrix[2] * user_matrix[ 8] + user_matrix[0] * user_matrix[10]) * m[17];
    m[6] = (- user_matrix[0] * user_matrix[ 9] + user_matrix[1] * user_matrix[ 8]) * m[17];
  } else {
    m[4] = (  user_matrix[1] * user_matrix[10] - user_matrix[2] * user_matrix[ 9]) * m[17];
    m[5] = (  user_matrix[2] * user_matrix[ 8] - user_matrix[0] * user_matrix[10]) * m[17];
    m[6] = (  user_matrix[0] * user_matrix[ 9] - user_matrix[1] * user_matrix[ 8]) * m[17];
  }
  /* scale vectors to the size given by old matrix */
  m[ 0] = user_matrix[ 0] * m[16];
  m[ 1] = user_matrix[ 1] * m[16];
  m[ 2] = user_matrix[ 2] * m[16];
  m[ 8] = user_matrix[ 8];
  m[ 9] = user_matrix[ 9];
  m[10] = user_matrix[10];
}

void matrix_frustum (GLfloat r[19], GLfloat left, GLfloat right, GLfloat bottom, GLfloat top, GLfloat near, GLfloat far) {
  /* this code is adapted from Mesa :) */
  GLfloat a = 2.0 * near;
  GLfloat b = top - bottom;
  GLfloat c = right - left;
  GLfloat d = far - near;
  r[ 0] = a / c;
  r[ 1] = 0.0;
  r[ 2] = 0.0;
  r[ 3] = 0.0;
  r[ 4] = 0.0;
  r[ 5] = a / b;
  r[ 6] = 0.0;
  r[ 7] = 0.0;
  r[ 8] = (right + left) / c;
  r[ 9] = (top + bottom) / b;
  r[10] = -(far + near) / d;
  r[11] = -1.0;
  r[12] = 0.0;
  r[13] = 0.0;
  r[14] = -(2.0 * far * near) / d;  /* error ? (this rem was in Mesa) */
  r[15] = 0.0;
// TO DO ok ?
  r[16] = 1.0;
  r[17] = 1.0;
  r[18] = 1.0;
}

void matrix_print (GLfloat m[19], char* comment) {
  printf("MATRIX : %s\n", comment);
  printf("  %f | %f | %f | %f (%f)\n", m[ 0], m[ 1], m[ 2], m[ 3], vector_length (m));
  printf("  %f | %f | %f | %f (%f)\n", m[ 4], m[ 5], m[ 6], m[ 7], vector_length (m + 4));
  printf("  %f | %f | %f | %f (%f)\n", m[ 8], m[ 9], m[10], m[11], vector_length (m + 8));
  printf("  %f | %f | %f | %f\n", m[12], m[13], m[14], m[15]);
  printf("  %f | %f | %f\n",      m[16], m[17], m[18]);
}

void face_intersect_plane (GLfloat* face, int nbpoints, GLfloat plane[4], GLfloat** freturn, int* nbreturn) {
  int i; int j; int k; int l;
  GLfloat* points = NULL;
  int nb = 0;
  GLfloat* vs = (GLfloat*) malloc (nbpoints * sizeof (GLfloat));
  GLfloat v[3];
  GLfloat f;
  if (nbpoints == 0) {
    *freturn = NULL;
    *nbreturn = 0; 
    return;
  }
  /* compute the distances from points to plane */
  for (i = 0; i < nbpoints; i++) {
    j = i * 3;
    vs[i] = plane[0] * face[j] + plane[1] * face[j + 1] + plane[2] * face[j + 2] + plane[3];
  }
  for (i = 0; i < nbpoints; i++) {
    j = i + 1;
    if (j >= nbpoints) { j = 0; }
    if (vs[i] <= 0.0) {
      /* point is on the good side of the plane -> we take it */
      points = (GLfloat*) realloc (points, (nb + 1) * 3 * sizeof (GLfloat));
      k = i * 3;
      l = nb * 3;
      points[l]     = face[k];
      points[l + 1] = face[k + 1];
      points[l + 2] = face[k + 2];
      nb++;
    }
    if ((vs[i] > 0.0 && vs[j] < 0.0) || (vs[i] < 0.0 && vs[j] > 0.0)) {
      /* must compute an intersection */
      k = i * 3;
      l = j * 3;
      v[0] = face[k]     - face[l];
      v[1] = face[k + 1] - face[l + 1];
      v[2] = face[k + 2] - face[l + 2];
      f = - (plane[0] * face[k] + plane[1] * face[k + 1] + plane[2] * face[k + 2] + plane[3]) / (plane[0] * v[0] + plane[1] * v[1] + plane[2] * v[2]);
      points = (GLfloat*) realloc (points, (nb + 1) * 3 * sizeof (GLfloat));
      l = nb * 3;
      points[l]     = face[k]     + f * v[0];
      points[l + 1] = face[k + 1] + f * v[1];
      points[l + 2] = face[k + 2] + f * v[2];
      nb++;
    }
  }
  free (vs);
  *freturn = points;
  *nbreturn = nb;
}

void face_cut_by_plane (GLfloat* face, int nbpoints, GLfloat plane[4], GLfloat** freturn1, GLfloat** freturn2, int* nbreturn1, int* nbreturn2) {
  int i; int j; int k; int l;
  int side = 0;
  GLfloat* vs = (GLfloat*) malloc (nbpoints * sizeof (GLfloat));
  GLfloat v[3];
  GLfloat inter[3];
  GLfloat f;
  if (nbpoints == 0) { return; }
  
  freturn1[0] = NULL;
  freturn2[0] = NULL;
  nbreturn1[0] = 0;
  nbreturn2[0] = 0;
  
  /* compute the distances from points to plane */
  for (i = 0; i < nbpoints; i++) {
    j = i * 3;
    vs[i] = plane[0] * face[j] + plane[1] * face[j + 1] + plane[2] * face[j + 2] + plane[3];
  }
  for (i = 0; i < nbpoints; i++) {
    j = i + 1;
    if (j >= nbpoints) { j = 0; }
    
    // Add current point
    if (side == 0) {
      freturn1[0] = (GLfloat*) realloc (freturn1[0], (nbreturn1[0] + 1) * 3 * sizeof (GLfloat));
      memcpy(freturn1[0] + 3 * nbreturn1[0], face + 3 * i, 3 * sizeof(float));
      nbreturn1[0]++;
    } else {
      freturn2[0] = (GLfloat*) realloc (freturn2[0], (nbreturn2[0] + 1) * 3 * sizeof (GLfloat));
      memcpy(freturn2[0] + 3 * nbreturn2[0], face + 3 * i, 3 * sizeof(float));
      nbreturn2[0]++;
    }
    
    if ((vs[i] > 0.0 && vs[j] < 0.0) || (vs[i] < 0.0 && vs[j] > 0.0)) {
      /* intersection */
      k = i * 3;
      l = j * 3;
      v[0] = face[k    ] - face[l    ];
      v[1] = face[k + 1] - face[l + 1];
      v[2] = face[k + 2] - face[l + 2];
      f = - (plane[0] * face[k] + plane[1] * face[k + 1] + plane[2] * face[k + 2] + plane[3]) / (plane[0] * v[0] + plane[1] * v[1] + plane[2] * v[2]);
      inter[0] = face[k    ] + f * v[0];
      inter[1] = face[k + 1] + f * v[1];
      inter[2] = face[k + 2] + f * v[2];
      
      // Add intersection in both faces
      freturn1[0] = (GLfloat*) realloc (freturn1[0], (nbreturn1[0] + 1) * 3 * sizeof (GLfloat));
      memcpy(freturn1[0] + 3 * nbreturn1[0], inter, 3 * sizeof(float));
      nbreturn1[0]++;
      
      freturn2[0] = (GLfloat*) realloc (freturn2[0], (nbreturn2[0] + 1) * 3 * sizeof (GLfloat));
      memcpy(freturn2[0] + 3 * nbreturn2[0], inter, 3 * sizeof(float));
      nbreturn2[0]++;
      
      if (side == 0) { side = 1; }
      else           { side = 0; }
    }
  }
  free (vs);
}

int sphere_raypick (GLfloat* data, GLfloat sphere[4]) {
  GLfloat n[3];
  GLfloat k;
  n[0] = sphere[0] - data[0];
  n[1] = sphere[1] - data[1];
  n[2] = sphere[2] - data[2];
  if (data[6] > 0.0) {
    k = sphere[3] + data[6];
    if (fabs (n[0]) > k || fabs (n[1]) > k || fabs (n[2]) > k ||
        n[0] * n[0] + n[1] * n[1] + n[2] + n[2] > k * k) {
//        sqrt (n[0] * n[0] + n[1] * n[1] + n[2] + n[2]) > k) {
      return FALSE;
    }
  }
  /* compute distance from line to sphere center */
  k = (data[3] * n[0] + data[4] * n[1] + data[5] * n[2]) / (data[3] * data[3] + data[4] * data[4] + data[5] * data[5]);
  n[0] -= k * data[3];
  n[1] -= k * data[4];
  n[2] -= k * data[5];
  if (n[0] * n[0] + n[1] * n[1] + n[2] * n[2] > sphere[3] * sphere[3]) {
//  if (sqrt (n[0] * n[0] + n[1] * n[1] + n[2] * n[2]) > sphere[3]) {
    return FALSE;
  }
  return TRUE;
}

int triangle_raypick (GLfloat* data, 
                         GLfloat p1[3], GLfloat p2[3], GLfloat p3[3],
                         GLfloat normal[3], int option, GLfloat* result) 
{
  GLfloat det;
  GLfloat x; GLfloat y; GLfloat z;
  GLfloat d;
//  GLfloat m[19];
//  GLfloat mi[19];

  user_matrix[15] = data[0] - p1[0];
  user_matrix[16] = data[1] - p1[1];
  user_matrix[17] = data[2] - p1[2];
  d = user_matrix[15] * normal[0] + user_matrix[16] * normal[1] + user_matrix[17] * normal[2];
  if (data[6] > 0.0 && fabs (d) > data[6]) return FALSE;
  /* test culling */
  if (option & RAYPICK_CULL_FACE) {
    if (option & RAYPICK_HALF_LINE) {
      if (normal[0] * data[3] + normal[1] * data[4] + normal[2] * data[5] >= 0.0) return FALSE;
    } else {
      if (d <= 0.0) return FALSE;
//      if ((data[0] - p1[0]) * normal[0] + (data[1] - p1[1]) * normal[1] + (data[2] - p1[2]) * normal[2] <= 0.0) { return FALSE; }
    }
  } else {
//    d = (data[0] - p1[0]) * normal[0] + (data[1] - p1[1]) * normal[1] + (data[2] - p1[2]) * normal[2];
    if (option & RAYPICK_HALF_LINE) {
      x = normal[0] * data[3] + normal[1] * data[4] + normal[2] * data[5];
      if ((x <= 0.0 && d <= 0.0) || (x >= 0.0 && d >= 0.0)) return FALSE;
    }
  }
  /* compute intersection */

/*
      // compute intersection
      m[ 0] = p2[0] - p1[0];
      m[ 1] = p2[1] - p1[1];
      m[ 2] = p2[2] - p1[2];
      m[ 3] = 0.0;
      m[ 4] = p3[0] - p1[0];
      m[ 5] = p3[1] - p1[1];
      m[ 6] = p3[2] - p1[2];
      m[ 7] = 0.0;
      m[ 8] = data[3];
      m[ 9] = data[4];
      m[10] = data[5];
      m[11] = 0.0;
      m[12] = p1[0];
      m[13] = p1[1];
      m[14] = p1[2];
      m[15] = 1.0;
      matrix_invert (mi, m);
      x = data[0] * mi[0] + data[1] * mi[4] + data[2] * mi[ 8] + mi[12];
      y = data[0] * mi[1] + data[1] * mi[5] + data[2] * mi[ 9] + mi[13];
      z = data[0] * mi[2] + data[1] * mi[6] + data[2] * mi[10] + mi[14];
*/

/* OPTIMIZED CODE */
  user_matrix[0] = p2[0] - p1[0];
  user_matrix[1] = p2[1] - p1[1];
  user_matrix[2] = p2[2] - p1[2];
//  user_matrix[ 3] = 0.0;
  user_matrix[3] = p3[0] - p1[0];
  user_matrix[4] = p3[1] - p1[1];
  user_matrix[5] = p3[2] - p1[2];
//  user_matrix[ 7] = 0.0;
//  user_matrix[ 8] = direction[0];
//  user_matrix[ 9] = direction[1];
//  user_matrix[10] = direction[2];
//  user_matrix[11] = 0.0;
//  user_matrix[12] = p1[0];
//  user_matrix[13] = p1[1];
//  user_matrix[14] = p1[2];
//  user_matrix[15] = 1.0;
//  user_matrix[16] = 1.0;
//  user_matrix[17] = 1.0;
//  user_matrix[18] = 1.0;
  // matrix inversion code

  user_matrix[ 6] = user_matrix[4] * data[5] - data[4] * user_matrix[5];
  user_matrix[ 9] = user_matrix[1] * data[5] - data[4] * user_matrix[2];
  user_matrix[12] = user_matrix[1] * user_matrix[5] - user_matrix[4] * user_matrix[2];

  det = user_matrix[0] * user_matrix[6] - user_matrix[3] * user_matrix[9] + data[3] * user_matrix[12];
  if (det == 0) return FALSE;
  
  det = 1 / det;
  user_matrix[ 6] *= det;
  user_matrix[ 7] = - det * (user_matrix[3] * data[5] - data[3] * user_matrix[5]);
  user_matrix[ 8] =   det * (user_matrix[3] * data[4] - data[3] * user_matrix[4]);
  user_matrix[ 9] *= - det;
  user_matrix[10] =   det * (user_matrix[0] * data[5] - data[3] * user_matrix[2]);
  user_matrix[11] = - det * (user_matrix[0] * data[4] - data[3] * user_matrix[1]);
  user_matrix[12] *= det;
  user_matrix[13] = - det * (user_matrix[0] * user_matrix[5] - user_matrix[3] * user_matrix[2]);
  user_matrix[14] =   det * (user_matrix[0] * user_matrix[4] - user_matrix[3] * user_matrix[1]);

/*
  det = user_matrix[0] * (user_matrix[4] * data[5]        - data[4]        * user_matrix[5])
      - user_matrix[3] * (user_matrix[1] * data[5]        - data[4]        * user_matrix[2])
      + data[3]        * (user_matrix[1] * user_matrix[5] - user_matrix[4] * user_matrix[2]);
  if (det == 0) { return FALSE; }
  det = 1 / det;
  user_matrix[ 6] =   det * (user_matrix[4] * data[5] - data[4] * user_matrix[5]);
  user_matrix[ 7] = - det * (user_matrix[3] * data[5] - data[3] * user_matrix[5]);
  user_matrix[ 8] =   det * (user_matrix[3] * data[4] - data[3] * user_matrix[4]);
  user_matrix[ 9] = - det * (user_matrix[1] * data[5] - data[4] * user_matrix[2]);
  user_matrix[10] =   det * (user_matrix[0] * data[5] - data[3] * user_matrix[2]);
  user_matrix[11] = - det * (user_matrix[0] * data[4] - data[3] * user_matrix[1]);
  user_matrix[12] =   det * (user_matrix[1] * user_matrix[5] - user_matrix[4] * user_matrix[2]);
  user_matrix[13] = - det * (user_matrix[0] * user_matrix[5] - user_matrix[3] * user_matrix[2]);
  user_matrix[14] =   det * (user_matrix[0] * user_matrix[4] - user_matrix[3] * user_matrix[1]);
*/
//  user_matrix[15] = data[0] - p1[0];
//  user_matrix[16] = data[1] - p1[1];
//  user_matrix[17] = data[2] - p1[2];

//  matrix_invert (mi, m);
  z = user_matrix[15] * user_matrix[12] + user_matrix[16] * user_matrix[13] + user_matrix[17] * user_matrix[14];
  if (fabs (z) < EPSILON || (option & RAYPICK_HALF_LINE && z > 0.0)) return FALSE;
  x = user_matrix[15] * user_matrix[ 6] + user_matrix[16] * user_matrix[ 7] + user_matrix[17] * user_matrix[ 8];
  if (x < 0.0) return FALSE;

  y = user_matrix[15] * user_matrix[ 9] + user_matrix[16] * user_matrix[10] + user_matrix[17] * user_matrix[11];
  if (y < 0.0 || x + y > 1.0 + UPSILON) return FALSE;
  
  /* there is an intersection (X,Y,Z) = o + z * d 
   *   X = origin[0] + z * direction[0]
   *   Y = origin[1] + z * direction[1]
   *   Z = origin[2] + z * direction[2]
   */
  if (data[6] <= 0.0 || fabs (z) < data[6]) { 
    *result = -z;
    if (option & RAYPICK_CULL_FACE) {
      return RAYPICK_DIRECT;
    } else {
      if (d < 0.0) {
        return RAYPICK_INDIRECT;
      } else {
        return RAYPICK_DIRECT;
      }
    }
  }
  return FALSE;
}

int quad_raypick (GLfloat* data, 
                     GLfloat p1[3], GLfloat p2[3], GLfloat p3[3], GLfloat p4[3],
                     GLfloat normal[3], int option, GLfloat* result) 
{
  GLfloat det;
  GLfloat x;  GLfloat y; GLfloat z;
  GLfloat d;
  GLfloat x4; GLfloat y4;

  user_matrix[15] = data[0] - p1[0];
  user_matrix[16] = data[1] - p1[1];
  user_matrix[17] = data[2] - p1[2];
  d = user_matrix[15] * normal[0] + user_matrix[16] * normal[1] + user_matrix[17] * normal[2];
  if (data[6] > 0.0 && fabs (d) > data[6]) return FALSE;

  /* test culling */
  if (option & RAYPICK_CULL_FACE) {
    if (option & RAYPICK_HALF_LINE) {
      if (normal[0] * data[3] + normal[1] * data[4] + normal[2] * data[5] >= 0.0) return FALSE;
    } else {
      if (d <= 0.0) return FALSE;
//      if ((data[0] - p1[0]) * normal[0] + (data[1] - p1[1]) * normal[1] + (data[2] - p1[2]) * normal[2] < 0.0) { return FALSE; }
    }
  } else {
//    d = (data[0] - p1[0]) * normal[0] + (data[1] - p1[1]) * normal[1] + (data[2] - p1[2]) * normal[2];
    if (option & RAYPICK_HALF_LINE) {
      x = normal[0] * data[3] + normal[1] * data[4] + normal[2] * data[5];
      if ((x <= 0.0 && d <= 0.0) || (x >= 0.0 && d >= 0.0)) return FALSE;
    }
  }
  /* compute intersection */
  user_matrix[0] = p2[0] - p1[0];
  user_matrix[1] = p2[1] - p1[1];
  user_matrix[2] = p2[2] - p1[2];
  user_matrix[3] = p4[0] - p1[0];
  user_matrix[4] = p4[1] - p1[1];
  user_matrix[5] = p4[2] - p1[2];
  /* matrix inversion code */

  user_matrix[ 6] = user_matrix[4] * data[5] - data[4] * user_matrix[5];
  user_matrix[ 9] = user_matrix[1] * data[5] - data[4] * user_matrix[2];
  user_matrix[12] = user_matrix[1] * user_matrix[5] - user_matrix[4] * user_matrix[2];

  det = user_matrix[0] * user_matrix[6] - user_matrix[3] * user_matrix[9] + data[3] * user_matrix[12];
  if (det == 0) return FALSE;
  det = 1 / det;
  user_matrix[ 6] *= det;
  user_matrix[ 7] = - det * (user_matrix[3] * data[5] - data[3] * user_matrix[5]);
  user_matrix[ 8] =   det * (user_matrix[3] * data[4] - data[3] * user_matrix[4]);
  user_matrix[ 9] *= - det;
  user_matrix[10] =   det * (user_matrix[0] * data[5] - data[3] * user_matrix[2]);
  user_matrix[11] = - det * (user_matrix[0] * data[4] - data[3] * user_matrix[1]);
  user_matrix[12] *= det;
  user_matrix[13] = - det * (user_matrix[0] * user_matrix[5] - user_matrix[3] * user_matrix[2]);
  user_matrix[14] =   det * (user_matrix[0] * user_matrix[4] - user_matrix[3] * user_matrix[1]);

/*
  det = user_matrix[0] * (user_matrix[4] * data[5]        - data[4]        * user_matrix[5])
      - user_matrix[3] * (user_matrix[1] * data[5]        - data[4]        * user_matrix[2])
      + data[3]        * (user_matrix[1] * user_matrix[5] - user_matrix[4] * user_matrix[2]);
  if (det == 0) { return FALSE; }
  det = 1 / det;
  user_matrix[ 6] =   det * (user_matrix[4] * data[5] - data[4] * user_matrix[5]);
  user_matrix[ 7] = - det * (user_matrix[3] * data[5] - data[3] * user_matrix[5]);
  user_matrix[ 8] =   det * (user_matrix[3] * data[4] - data[3] * user_matrix[4]);
  user_matrix[ 9] = - det * (user_matrix[1] * data[5] - data[4] * user_matrix[2]);
  user_matrix[10] =   det * (user_matrix[0] * data[5] - data[3] * user_matrix[2]);
  user_matrix[11] = - det * (user_matrix[0] * data[4] - data[3] * user_matrix[1]);
  user_matrix[12] =   det * (user_matrix[1] * user_matrix[5] - user_matrix[4] * user_matrix[2]);
  user_matrix[13] = - det * (user_matrix[0] * user_matrix[5] - user_matrix[3] * user_matrix[2]);
  user_matrix[14] =   det * (user_matrix[0] * user_matrix[4] - user_matrix[3] * user_matrix[1]);
*/

//  user_matrix[15] = data[0] - p1[0];
//  user_matrix[16] = data[1] - p1[1];
//  user_matrix[17] = data[2] - p1[2];

  z = user_matrix[15] * user_matrix[12] + user_matrix[16] * user_matrix[13] + user_matrix[17] * user_matrix[14];
  if (fabs (z) < EPSILON || (option & RAYPICK_HALF_LINE && z > 0.0)) return FALSE;
  x = user_matrix[15] * user_matrix[ 6] + user_matrix[16] * user_matrix[ 7] + user_matrix[17] * user_matrix[ 8];
  if (x < 0.0) return FALSE;
  y = user_matrix[15] * user_matrix[ 9] + user_matrix[16] * user_matrix[10] + user_matrix[17] * user_matrix[11];
  if (y < 0.0) return FALSE;
  /* push the 4th point in the plane */
  user_matrix[15] = p3[0] - p1[0];
  user_matrix[16] = p3[1] - p1[1];
  user_matrix[17] = p3[2] - p1[2];
  x4 = user_matrix[15] * user_matrix[ 6] + user_matrix[16] * user_matrix[ 7] + user_matrix[17] * user_matrix[ 8];
  y4 = user_matrix[15] * user_matrix[ 9] + user_matrix[16] * user_matrix[10] + user_matrix[17] * user_matrix[11];
  /* test for the quad */
  user_matrix[0] = x * y4 - y * x4;
  if ((user_matrix[0] - x + x4 < 0.0) || (-user_matrix[0] - y + y4 < 0.0)) return FALSE;
//  if ((y * (x4 - 1.0) - y4 * (x - 1.0)) < 0.0 || (x * (y4 - 1.0) - x4 * (y - 1.0)) < 0.0) { return FALSE; }
  /* there is an intersection = o + z * d */
  if (data[6] <= 0.0 || fabs (z) < data[6]) { 
    *result = -z;
    if (option & RAYPICK_CULL_FACE) {
      return RAYPICK_DIRECT;
    } else {
      if (d < 0.0) {
        return RAYPICK_INDIRECT;
      } else {
        return RAYPICK_DIRECT;
      }
    }
//    return TRUE;
  }
  return FALSE;
}


/*
  det = m[0] * (m[5] * direction[2] - direction[1] * m[6])
      - m[4] * (m[1] * direction[2] - direction[1] * m[2])
      + direction[0] * (m[1] * m[6] - m[5] * m[2]);
  if (det == 0) { return FLASE; }
  det = 1 / det;
  r[ 0] =   det * (m[5] * direction[2] - direction[1] * m[6]);
  r[ 4] = - det * (m[4] * direction[2] - direction[0] * m[6]);
  r[ 8] =   det * (m[4] * direction[1] - direction[0] * m[5]);
  r[ 1] = - det * (m[1] * direction[2] - direction[1] * m[2]);
  r[ 5] =   det * (m[0] * direction[2] - direction[0] * m[2]);
  r[ 9] = - det * (m[0] * direction[1] - direction[0] * m[1]);
  r[ 2] =   det * (m[1] * m[ 6] - m[5] * m[2]);
  r[ 6] = - det * (m[0] * m[ 6] - m[4] * m[2]);
  r[10] =   det * (m[0] * m[ 5] - m[4] * m[1]);
  r[12] = - (p1[0] * r[0] + p1[1] * r[4] + p1[2] * r[ 8]);
  r[13] = - (p1[0] * r[1] + p1[1] * r[5] + p1[2] * r[ 9]);
  r[14] = - (p1[0] * r[2] + p1[1] * r[6] + p1[2] * r[10]);

//  matrix_invert (mi, m);
  x = origin[0] * r[0] + origin[1] * r[4] + origin[2] * r[ 8] + r[12];
  y = origin[0] * r[1] + origin[1] * r[5] + origin[2] * r[ 9] + r[13];
  z = origin[0] * r[2] + origin[1] * r[6] + origin[2] * r[10] + r[14];
*/

/*
0   user_matrix[ 6] =   det * (user_matrix[4] * direction[2] - direction[1] * user_matrix[5]);
4   user_matrix[ 7] = - det * (user_matrix[3] * direction[2] - direction[0] * user_matrix[5]);
8   user_matrix[ 8] =   det * (user_matrix[3] * direction[1] - direction[0] * user_matrix[4]);
1   user_matrix[ 9] = - det * (user_matrix[1] * direction[2] - direction[1] * user_matrix[2]);
5   user_matrix[10] =   det * (user_matrix[0] * direction[2] - direction[0] * user_matrix[2]);
9   user_matrix[11] = - det * (user_matrix[0] * direction[1] - direction[0] * user_matrix[1]);
2   user_matrix[12] =   det * (user_matrix[1] * user_matrix[5] - user_matrix[4] * user_matrix[2]);
6   user_matrix[13] = - det * (user_matrix[0] * user_matrix[5] - user_matrix[3] * user_matrix[2]);
10  user_matrix[14] =   det * (user_matrix[0] * user_matrix[4] - user_matrix[3] * user_matrix[1]);
//12  user_matrix[15] = - (p1[0] * user_matrix[ 6] + p1[1] * user_matrix[ 7] + p1[2] * user_matrix[ 8]);
//13  user_matrix[16] = - (p1[0] * user_matrix[ 9] + p1[1] * user_matrix[10] + p1[2] * user_matrix[11]);
//14  user_matrix[17] = - (p1[0] * user_matrix[12] + p1[1] * user_matrix[13] + p1[2] * user_matrix[14]);

user_matrix[15] = origin[0] - p1[0];
user_matrix[16] = origin[1] - p1[1];
user_matrix[17] = origin[2] - p1[2];

//  matrix_invert (mi, m);
  x = origin[0] * r[ 6] + origin[1] * r[ 7] + origin[2] * r[ 8] + r[15];
  y = origin[0] * r[ 9] + origin[1] * r[10] + origin[2] * r[11] + r[16];
  z = origin[0] * r[12] + origin[1] * r[13] + origin[2] * r[14] + r[17];
*/






/*

EQUATION 2 2

ak + ut + x = 0
bk + vt + y = 0

akv + vut + vx = 0
bku + vut + uy = 0

akv + vx - bku - uy = 0
k (av - bu) + vx - uy = 0

akb + utb + xb = 0
bka + vta + ya = 0

utb + xb - vta - ya = 0
t (ub - va) + xb - ya = 0
t = (ay - bx) / (ub - va)


k = (uy - vx) / (va - ub)
t = (bx - ay) / (va - ub)

*/


int point_in_frustum (Frustum* f, GLfloat p[3]) {
  int i;
  GLfloat d;
  for (i = 0; i < 24; i += 4) {
    d = p[0] * f->planes[i] + p[1] * f->planes[i + 1] + p[2] * f->planes[i + 2] + f->planes[i + 3];
    if (d > 0.0) return FALSE;
  }
  return TRUE;
}

int sphere_in_frustum (Frustum* f, GLfloat s[4]) {
  int i;
// TO DO box test 1rst ?
  for (i = 0; i < 24; i += 4) {
    if (s[0] * f->planes[i] + s[1] * f->planes[i + 1] + s[2] * f->planes[i + 2] + f->planes[i + 3] > s[3])
      return FALSE; 
  }
  return TRUE;
}

int box_in_frustum (Frustum* f, GLfloat b[6]) {
	int i, j, InCount, PtIn, TotalIn = 0;
	GLfloat d;
	
	// test if the camera is inside the box
	if ((f->position[0] > b[0] && f->position[0] < b[3])
		&& (f->position[1] > b[1] && f->position[1] < b[4])
		&& (f->position[2] > b[2] && f->position[2] < b[5]))
		return(1);
	// test each frustum plane
	for(i = 0; i < 24; i += 4) {
		InCount = 8;
		PtIn = 1;
		// test every corner of te box
		for(j = 0; j < 8; ++j) {
			d = b[((j>>2)%2)?3:0] * f->planes[i]
			  + b[((j>>1)%2)?4:1] * f->planes[i+1]
				+ b[(j%2)?5:2]      * f->planes[i+2]
				+ f->planes[i+3];
			// if corner is behind the plane
			if (d > 0.) {
				PtIn = 0;
				--InCount;
			}
		}
		// if all corner are behind the plane the box is out
		if(InCount == 0)
			return(0);
		TotalIn += PtIn;
	}
	// if TotalIn is 6 then all corner are inside the frustum
	if(TotalIn == 6)
		return(2);
	// else the box intesec the frustum
	return(1);
}

Frustum* frustum_by_matrix (Frustum* r, Frustum* f, GLfloat* m) {
  int i;
  GLfloat scaling;
  /* copy */
  memcpy (r->points, f->points, 24 * sizeof (GLfloat));
  memcpy (r->planes, f->planes, 24 * sizeof (GLfloat));
  memcpy (r->position, f->position, 3 * sizeof (GLfloat));
  /* multiply */
  for (i = 0; i < 24; i += 3) { point_by_matrix (r->points + i, m); }
  point_by_matrix (r->position, m); 
  scaling = m[16];
  if (m[17] > scaling) { scaling = m[17]; }
  if (m[18] > scaling) { scaling = m[18]; }
  /* re-compute the normals */
  face_normal (r->planes     , r->points     , r->points +  3, r->points +  9); vector_set_length (r->planes     , scaling);
  face_normal (r->planes +  4, r->points + 12, r->points + 15, r->points     ); vector_set_length (r->planes +  4, scaling);
  face_normal (r->planes +  8, r->points + 9 , r->points +  6, r->points + 21); vector_set_length (r->planes +  8, scaling);
  face_normal (r->planes + 12, r->points + 12, r->points     , r->points + 21); vector_set_length (r->planes + 12, scaling);
  face_normal (r->planes + 16, r->points + 3 , r->points + 15, r->points +  6); vector_set_length (r->planes + 16, scaling);
  face_normal (r->planes + 20, r->points + 15, r->points + 12, r->points + 18); vector_set_length (r->planes + 20, scaling);
  /* re-compute the constants */
  r->planes[ 3] = -(r->planes[ 0] * r->points[ 0] + r->planes[ 1] * r->points[ 1] + r->planes[ 2] * r->points[ 2]);
  r->planes[ 7] = -(r->planes[ 4] * r->points[ 0] + r->planes[ 5] * r->points[ 1] + r->planes[ 6] * r->points[ 2]);
  r->planes[11] = -(r->planes[ 8] * r->points[ 6] + r->planes[ 9] * r->points[ 7] + r->planes[10] * r->points[ 8]);
  r->planes[15] = -(r->planes[12] * r->points[ 0] + r->planes[13] * r->points[ 1] + r->planes[14] * r->points[ 2]);
  r->planes[19] = -(r->planes[16] * r->points[ 6] + r->planes[17] * r->points[ 7] + r->planes[18] * r->points[ 8]);
  r->planes[23] = -(r->planes[20] * r->points[12] + r->planes[21] * r->points[13] + r->planes[22] * r->points[14]);

  if (m[16] * m[17] * m[18] < 0.0f) { // left-handed matrix
    for (i = 0; i < 24; i++) { r->planes[i] = -r->planes[i]; }
  }
  /* sphere */
//  point_by_matrix (r->sphere, m);
//  r->sphere[3] *= scaling;
  return r;
}

void frustum_to_box (Frustum* frustum, GLfloat* box) {
  GLfloat* ptr = frustum->points;
  int i;
  memcpy (box,     ptr, 3 * sizeof (GLfloat));
  memcpy (box + 3, ptr, 3 * sizeof (GLfloat));
  ptr += 3;
  for (i = 0; i < 7; i++) {
    if      (ptr[0] < box[0]) box[0] = ptr[0];
    else if (ptr[0] > box[3]) box[3] = ptr[0];
    if      (ptr[1] < box[1]) box[1] = ptr[1];
    else if (ptr[1] > box[4]) box[4] = ptr[1];
    if      (ptr[2] < box[2]) box[2] = ptr[2];
    else if (ptr[2] > box[5]) box[5] = ptr[2];
    ptr += 3;
  }
}

