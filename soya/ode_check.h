/*
 *   Check that ODE is configured to use floats and not doubles.
 *   Otherwise chunk_add_float_endian_safe gets passed pointers
 *   of the wrong type.
 *
 *   Greg Ewing, March 2007
 *   greg.ewing@canterbury.ac.nz
 */

#include <ode/ode.h>

#ifndef dSINGLE
#error Soya requires ODE to be configured with PRECISION=SINGLE
#endif
