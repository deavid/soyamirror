/*
 * P3
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
 * matrix.h : matrix and other 3D math functions header
 * Copyright (C) 2001-2002 Bertrand 'blam' LAMY
 * Copyright (C) 2003-2006 Jean-Baptiste 'Jiba' LAMY
 **********************************************/

#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <stdarg.h>
#include <float.h>
#include <math.h>
#include "include_glew.h"

#define FALSE  0
#define TRUE   1

/* option for raypick functions */
#define RAYPICK_CULL_FACE  (1<<0)
#define RAYPICK_HALF_LINE  (1<<1)
/* returned by math3d raypick functions */
#define RAYPICK_DIRECT   1
#define RAYPICK_INDIRECT 2

#define pi          3.1415927
#define _2_pi        6.2831853 /* pi * 2 */
#define pi_2        1.5707963  /* pi / 2 */
#define pi_180      0.0174533  /* pi / 180 */
#define pi_180_inv  57.216848  /* 180 / pi */
#define sqrt_2      1.4142136  /* sqrt(2) */
#define sqrt_2_2    0.7071068  /* sqrt(2) / 2 */
#define EPSILON     0.001      /* values under this value are considered as 0.0 */
#define UPSILON     0.00001
#define INFINITY    HUGE_VAL

#define to_radians(angle) ((angle) * pi_180)
#define to_degrees(angle) ((angle) * pi_180_inv)

#define  rnd ((GLfloat) (((double) rand ()) / ((double) RAND_MAX)))

typedef struct {
  GLfloat position[3];  /* camera position (x,y,z) */
  GLfloat points[24];   /* points : (x,y,z) * 8 */
  GLfloat planes[24];   /* planes equation : (a,b,c,d) * 6 */
} Frustum;

void     equation_2_2                (GLfloat* result, GLfloat a1, GLfloat b1, GLfloat c1, GLfloat a2, GLfloat b2, GLfloat c2);
int      float_array_compare         (GLfloat* values, GLfloat* references, int nb);

int      exp_of_2                    (int);
#define  _2_pow_n(a) (1 << (a))

int      cone_from_sphere_and_origin (GLfloat* cone, GLfloat* sphere, GLfloat* point,  GLfloat length);
void     cone_from_sphere_and_vector (GLfloat* cone, GLfloat* sphere, GLfloat* vector, GLfloat length);
int      sphere_is_in_cone           (GLfloat* sphere, GLfloat* cone);

int      point_is_in_sphere          (GLfloat[4], GLfloat[3]);
GLfloat  sphere_distance_sphere      (GLfloat[4], GLfloat[4]);
GLfloat  sphere_distance_point       (GLfloat[4], GLfloat[3]);
void     sphere_instance_into        (GLfloat[4], GLfloat*, GLfloat*);
void     sphere_from_points          (GLfloat[4], GLfloat*, int);
void     sphere_from_3_points        (GLfloat[4], GLfloat*, GLfloat*, GLfloat*);
void     sphere_from_spheres         (GLfloat[4], GLfloat*, int);
void     sphere_from_2_spheres       (GLfloat result[4], GLfloat[4], GLfloat[4]);
char     sphere_side_plane           (GLfloat[4], GLfloat[4]);

void     face_normal                 (GLfloat result[3], GLfloat[3], GLfloat[3], GLfloat[3]);
void     face_plane                  (GLfloat result[4], GLfloat[3], GLfloat[3], GLfloat[3]);

GLfloat  point_square_distance_to    (GLfloat[3], GLfloat[3]);
GLfloat  point_distance_to           (GLfloat[3], GLfloat[3]);
double   point_distance_to_d         (double [3], double [3]);
GLfloat  point_distance_plane        (GLfloat[3], GLfloat[4]);
void     point_project_on_plane      (GLfloat*  , GLfloat[4]);
void     point_rotate_y              (GLfloat[3], GLfloat);
void     point_rotate_x              (GLfloat[3], GLfloat);
void     point_rotate_z              (GLfloat[3], GLfloat);
void     point_rotate_axe            (GLfloat[3], GLfloat, GLfloat, GLfloat, GLfloat);
void     point_rotate                (GLfloat[3], GLfloat, GLfloat[3], GLfloat[3]);

void     plane_vector_normalize      (GLfloat[4]);
float    ray_distance_plane          (GLfloat[3], GLfloat[3], GLfloat, GLfloat[4], GLfloat);

void     vector_normalize            (GLfloat[3]);
void     vector_set_length           (GLfloat[3], GLfloat);
void     vector_cross_product        (GLfloat[3], GLfloat[3], GLfloat[3]);
GLfloat  vector_length               (GLfloat[3]);
GLfloat  vector_square_length        (GLfloat[3]);
GLfloat  vector_dot_product          (GLfloat[3], GLfloat[3]);
GLfloat  vector_angle                (GLfloat[3], GLfloat[3]);
void     vector_from_points          (GLfloat[3], GLfloat[3], GLfloat[3]);

void     quaternion_normalize        (GLfloat[4]);
void     matrix_from_quaternion      (GLfloat[19], GLfloat[4]);
void     quaternion_from_matrix      (GLfloat[4], GLfloat[16]);
void     quaternion_rotation         (GLfloat[4], GLfloat[4], GLfloat);
void     multiply_quaternion         (GLfloat[4], GLfloat[4], GLfloat[4]);
void     quaternion_slerp            (GLfloat[4], GLfloat[4] ,GLfloat[4], GLfloat, GLfloat);
void     quaternion_copy             (GLfloat[4], GLfloat[4]);

#define  matrix_copy(dest, src) memcpy(dest, src, 19 * sizeof (GLfloat))
void     matrix_invert               (GLfloat[19], GLfloat[19]);
void     multiply_matrix             (GLfloat[19], GLfloat[19], GLfloat[19]);
void     point_by_matrix             (GLfloat[3], GLfloat[19]);
void     point_by_matrix_copy        (GLfloat result[3], GLfloat[3], GLfloat[19]);
void     point4_by_matrix            (GLfloat[4], GLfloat[19]);
void     vector_by_matrix            (GLfloat[3], GLfloat[19]);
void     vector_by_matrix_copy       (GLfloat result[3], GLfloat[3], GLfloat[19]);
void     plane_by_matrix             (GLfloat p[4], GLfloat m[19]);
void     plane_by_matrix_copy        (GLfloat r[4], GLfloat p[4], GLfloat m[19]);
GLfloat  length_by_matrix            (GLfloat, GLfloat[19]);
void     sphere_by_matrix            (GLfloat[4], GLfloat[19]);
void     sphere_by_matrix_copy       (GLfloat result[4], GLfloat[4], GLfloat[19]);

void     matrix_set_identity         (GLfloat[19]);
void     matrix_scale                (GLfloat[19], GLfloat, GLfloat, GLfloat);
void     matrix_turn_y               (GLfloat[19], GLfloat);
void     matrix_turn_x               (GLfloat[19], GLfloat);
void     matrix_turn_z               (GLfloat[19], GLfloat);
void     matrix_turn_axe             (GLfloat[19], GLfloat angle, GLfloat, GLfloat, GLfloat);
void     matrix_rotate_y             (GLfloat[19], GLfloat);
void     matrix_rotate_x             (GLfloat[19], GLfloat);
void     matrix_rotate_z             (GLfloat[19], GLfloat);
void     matrix_rotate_axe           (GLfloat[16], GLfloat angle, GLfloat, GLfloat, GLfloat);
void     matrix_rotate               (GLfloat[19], GLfloat, GLfloat[3], GLfloat[3]);
void     matrix_translate            (GLfloat[19], GLfloat, GLfloat, GLfloat);
void     matrix_look_at_Z            (GLfloat[19], GLfloat[3]);
void     matrix_look_at_Y            (GLfloat[19], GLfloat[3]);
void     matrix_look_at_X            (GLfloat[19], GLfloat[3]);
void     matrix_look_to_Z            (GLfloat[19], GLfloat[3]);
void     matrix_look_to_Y            (GLfloat[19], GLfloat[3]);
void     matrix_look_to_X            (GLfloat[19], GLfloat[3]);
void     matrix_frustum              (GLfloat[19], GLfloat, GLfloat, GLfloat, GLfloat, GLfloat, GLfloat);
void     matrix_print                (GLfloat[19], char*);
int      matrix_is_direct            (GLfloat[19]);

void     face_intersect_plane        (GLfloat*, int, GLfloat[4], GLfloat**, int*);
int      sphere_raypick              (GLfloat* data, GLfloat sphere[4]);
int      triangle_raypick            (GLfloat* data,
                                         GLfloat[3], GLfloat[3], GLfloat[3], GLfloat normal[3],
                                         int option, GLfloat* result);
int      quad_raypick                (GLfloat* data,
                                         GLfloat p1[3], GLfloat p2[3], GLfloat p3[3], GLfloat p4[3], GLfloat normal[3],
                                         int option, GLfloat* result);

int      point_in_frustum            (Frustum*, GLfloat[3]);
int      sphere_in_frustum           (Frustum*, GLfloat[4]);
int      box_in_frustum              (Frustum* f, GLfloat b[6]);
Frustum* frustum_by_matrix           (Frustum*, Frustum*, GLfloat*);
void     frustum_to_box              (Frustum*, GLfloat*);


