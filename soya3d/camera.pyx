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

cdef class _Camera(CoordSyst):
  #cdef _World   _to_render
  #cdef float    _front, _back, _fov
  #cdef Frustum* _frustum
  #cdef int      _viewport[4]
  #cdef          _master
  
  def __new__(self, *args, **kargs):
    self.__raypick_data     = -1
    self._render_matrix[15] = 1.0
    self._frustum           = <Frustum*> malloc(sizeof(Frustum))
    self._viewport[2]       = renderer.screen_width
    self._viewport[3]       = renderer.screen_height
    
  def __dealloc__(self):
    free(self._frustum)
    
  def __init__(self, _World parent = None):
    CoordSyst.__init__(self, parent)
    self._fov   = 60.0
    self._front = 0.1
    self._back  = 100.0
    self._init_frustum()
    
  cdef __getcstate__(self):
    #return struct.pack("<iffffffffffffffffffffff", self._option, self._matrix[0], self._matrix[1], self._matrix[2], self._matrix[3], self._matrix[4], self._matrix[5], self._matrix[6], self._matrix[7], self._matrix[8], self._matrix[9], self._matrix[10], self._matrix[11], self._matrix[12], self._matrix[13], self._matrix[14], self._matrix[15], self._matrix[16], self._matrix[17], self._matrix[18], self._front, self._back, self._fov), self._to_render
    cdef Chunk* chunk
    chunk = get_chunk()
    chunk_add_int_endian_safe   (chunk, self._option)
    chunk_add_floats_endian_safe(chunk, self._matrix, 19)
    chunk_add_float_endian_safe (chunk, self._front)
    chunk_add_float_endian_safe (chunk, self._back)
    chunk_add_float_endian_safe (chunk, self._fov)
    return drop_chunk_to_string(chunk), self._to_render
  
  cdef void __setcstate__(self, cstate):
    self._validity = COORDSYS_INVALID
    #self._option, self._matrix[0], self._matrix[1], self._matrix[2], self._matrix[3], self._matrix[4], self._matrix[5], self._matrix[6], self._matrix[7], self._matrix[8], self._matrix[9], self._matrix[10], self._matrix[11], self._matrix[12], self._matrix[13], self._matrix[14], self._matrix[15], self._matrix[16], self._matrix[17], self._matrix[18], self._front, self._back, self._fov = struct.unpack("<iffffffffffffffffffffff", cstate[0])
    cstate2, self._to_render = cstate
    
    cdef Chunk* chunk
    chunk = string_to_chunk(cstate2)
    chunk_get_int_endian_safe(chunk, &self._option)
    chunk_get_floats_endian_safe(chunk, self._matrix, 19)
    chunk_get_float_endian_safe(chunk, &self._front)
    chunk_get_float_endian_safe(chunk, &self._back)
    chunk_get_float_endian_safe(chunk, &self._fov)
    drop_chunk(chunk)
    
  property master:
    def __get__(self):
      return self._master
    def __set__(self, master):
      self._master = master
      
  property to_render:
    def __get__(self):
      return self._to_render
    def __set__(self, _World to_render):
      self._to_render = to_render
      
  property front:
    def __get__(self):
      return self._front
    def __set__(self, float x):
      self._front = x
      self._init_frustum()
      
  property back:
    def __get__(self):
      return self._back
    def __set__(self, float x):
      self._back = x
      self._init_frustum()

  property fov:
    def __get__(self):
      return self._fov
    def __set__(self, float x):
      self._fov = x
      self._init_frustum()
    
  property left:
    def __get__(self):
      return self._viewport[0]
    def __set__(self, int x):
      self._viewport[0] = x
    
  property top:
    def __get__(self):
      return self._viewport[1]
    def __set__(self, int x):
      self._viewport[1] = x
      
  property width:
    def __get__(self):
      return self._viewport[2]
    def __set__(self, int x):
      self._viewport[2] = x
      self._init_frustum()
    
  property height:
    def __get__(self):
      return self._viewport[3]
    def __set__(self, int x):
      self._viewport[3] = x
      self._init_frustum()

  def set_viewport(self, int left, int top, int width, int height):
    """Camera.set_viewport(LEFT, TOP, WIDTH, HEIGHT)

Sets the Camera's viewport, i.e. the part of the screen where it renders.
LEFT, TOP, WIDTH, HEIGHT are integer pixel values."""
    self._viewport[0] = left
    self._viewport[1] = top
    self._viewport[2] = width
    self._viewport[3] = height
    self._init_frustum()
    
  property partial:
    def __get__(self):
      return self._option & CAMERA_PARTIAL != 0
    def __set__(self, int x):
      if x: self._option = self._option |  CAMERA_PARTIAL
      else: self._option = self._option & ~CAMERA_PARTIAL
      
  property ortho:
    def __get__(self):
      return self._option & CAMERA_ORTHO != 0
    def __set__(self, int x):
      if x: self._option = self._option |  CAMERA_ORTHO
      else: self._option = self._option & ~CAMERA_ORTHO
      self._init_frustum()

  def resize(self, int left, int top, int width, int height):
    self._viewport[0] = left
    self._viewport[1] = top
    self._viewport[2] = width
    self._viewport[3] = height
    self._init_frustum()
    
  def get_screen_width(self):
    """Camera.get_screen_width() -> int

Gets the width of the rendering screen, in pixel."""
    return renderer.screen_width
  def get_screen_height(self):
    """Camera.get_screen_height() -> int

Gets the height of the rendering screen, in pixel."""
    return renderer.screen_height
  
  cdef void _init_frustum(self):
    cdef float l, x, y, ff, ratio
    cdef Frustum* f
    f = self._frustum
    f.position[0] = 0.0
    f.position[1] = 0.0
    f.position[2] = 0.0
    ratio = (<float> self._viewport[3]) / (<float> self._viewport[2])
    # we use -front and -back cause our camera is looking toward -Z
    f.points[ 2] = f.points[ 5] = f.points[ 8] = f.points[11] = -self._front
    f.points[14] = f.points[17] = f.points[20] = f.points[23] = -self._back
    if self._option & CAMERA_ORTHO:
      l     = self._fov / 20.0
      ratio = l * ratio
      f.points[ 0] =    l; f.points[ 1] =  ratio
      f.points[ 3] =   -l; f.points[ 4] =  ratio
      f.points[ 6] =   -l; f.points[ 7] = -ratio
      f.points[ 9] =    l; f.points[10] = -ratio
      f.points[12] =    l; f.points[13] =  ratio
      f.points[15] =   -l; f.points[16] =  ratio
      f.points[18] =   -l; f.points[19] = -ratio
      f.points[21] =    l; f.points[22] = -ratio
      f.planes[ 0] =  0.0; f.planes[ 1] =   0.0; f.planes[ 2] =  1.0; f.planes[ 3] = -self._front
      f.planes[ 4] =  0.0; f.planes[ 5] =   1.0; f.planes[ 6] =  0.0; f.planes[ 7] =  ratio
      f.planes[ 8] =  0.0; f.planes[ 9] =  -1.0; f.planes[10] =  0.0; f.planes[11] = -ratio
      f.planes[12] =  1.0; f.planes[13] =   0.0; f.planes[14] =  0.0; f.planes[15] =  l
      f.planes[16] = -1.0; f.planes[17] =   0.0; f.planes[18] =  0.0; f.planes[19] = -l
      f.planes[20] =  0.0; f.planes[21] =   0.0; f.planes[22] = -1.0; f.planes[23] = -self._back
    else:
      l = tan(to_radians(self._fov) / 2.0)
      y = self._back * l  # y >= 0
      x = y / ratio       # x >= 0
      f.points[12] =  x; f.points[13] =  y
      f.points[15] = -x; f.points[16] =  y
      f.points[18] = -x; f.points[19] = -y
      f.points[21] =  x; f.points[22] = -y
      f.planes[0] = 0.0; f.planes[1] = 0.0; f.planes[2] = 1.0; f.planes[3] = -self._front
      ff = sqrt (y * y + self._back * self._back)
      f.planes[4] = 0.0; f.planes[5] = self._back / ff; f.planes[ 6] = y / ff;      f.planes[ 7] = 0.0
      f.planes[8] = 0.0; f.planes[9] = - f.planes[5]  ; f.planes[10] = f.planes[6]; f.planes[11] = 0.0
      ff = sqrt (x * x + self._back * self._back)
      f.planes[12] = self._back / ff; f.planes[13] = 0.0; f.planes[14] = x / ff;       f.planes[15] = 0.0
      f.planes[16] = - f.planes[12] ; f.planes[17] = 0.0; f.planes[18] = f.planes[14]; f.planes[19] = 0.0
      f.planes[20] =  0.0;            f.planes[21] = 0.0; f.planes[22] = -1.0;         f.planes[23] = -self._back
      y = self._front * l
      x = y / ratio
      f.points[0] =  x; f.points[ 1] =  y
      f.points[3] = -x; f.points[ 4] =  y
      f.points[6] = -x; f.points[ 7] = -y
      f.points[9] =  x; f.points[10] = -y
      
  cdef void _subrender_scene(self):
    cdef float v1, v2
    cdef float* m, *p, *r
    cdef CoordSyst root
    
    if renderer.engine_option & INITED == 0: 
      return 
      
    renderer.current_camera = self
    # compute the model matrix
    m = self._inverted_root_matrix()
    r = self._root_matrix()
    
    # simplified computation (for the processor, not for comprehension ;)
    p = self._render_matrix
    p[ 0] = m[0]
    p[ 4] = m[4]
    p[ 8] = m[8]
    p[12] = -r[12] * m[0] - r[13] * m[4] - r[14] * m[8]
    p[ 1] = m[1]
    p[ 5] = m[5]
    p[ 9] = m[9]
    p[13] = -r[12] * m[1] - r[13] * m[5] - r[14] * m[9]
    p[ 2] = m[2]
    p[ 6] = m[6]
    p[10] = m[10]
    p[14] = -r[12] * m[2] - r[13] * m[6] - r[14] * m[10]
    p[16] = m[16]
    p[17] = m[17]
    p[18] = m[18]
    
    # compute the projection matrix
    # TO DO really do it before each rendering ?
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    if self._option & CAMERA_ORTHO:
      v1 = self._fov / 20.0
      v2 = v1 * (<float> self._viewport[3]) / (<float> self._viewport[2])
      glOrtho(-v1, v1, -v2, v2, self._front, self._back)
    else:
      #perspective(self._fov, (<float> self._viewport[2]) / (<float> self._viewport[3]), self._front, self._back)
      gluPerspective(self._fov, (<float> self._viewport[2]) / (<float> self._viewport[3]), self._front, self._back)
    glMatrixMode (GL_MODELVIEW)
    
    # draw
    if self.to_render is None:
      root = self._get_root()
      if root is None: return 
      else: renderer.root_object = root
    else:   renderer.root_object = self.to_render
    
    frustum_coordsyst_into(renderer.root_frustum, self._frustum, self._root_matrix(), NULL)
    
    renderer._render()

  cdef void _render_scene(self):
    glPushAttrib(GL_VIEWPORT)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glViewport(self._viewport[0], renderer.screen_height - self._viewport[1] - self._viewport[3], self._viewport[2], self._viewport[3])
    glEnable(GL_LIGHTING)
    glEnable(GL_CULL_FACE)
    glDepthMask(GL_TRUE)
    glEnable(GL_DEPTH_TEST)
    
    self._subrender_scene()
    
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()
    glPopAttrib()
    glDepthMask (GL_FALSE)
    glDisable(GL_DEPTH_TEST)
    glDisable(GL_LIGHTING)
    glDisable(GL_FOG)
    glDisable(GL_CULL_FACE)
    
  def render(self):
    self._render_scene()

  def render_to_material(self, _Material mat, int what):
    """ render_to_material(self, material, what)
    render the camera to a soya.Material's texture.
    'what' is one of GL_LUMINANCE, GL_RGBA, GL_ALPHA.. etc. 
    """
    
    cdef int w, h

    w, h = mat.texture.width, mat.texture.height

    glPushAttrib(GL_VIEWPORT_BIT)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glViewport(0, 0, w, h)
    glEnable(GL_LIGHTING)
    glEnable(GL_CULL_FACE)
    glDepthMask(GL_TRUE)
    glEnable(GL_DEPTH_TEST)
    
    self._subrender_scene()

    glBindTexture(GL_TEXTURE_2D, mat._id)

    glCopyTexImage2D(GL_TEXTURE_2D, 0, what, 0, 0, w, h, 0 )

    glBindTexture(GL_TEXTURE_2D, 0)
    
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()
    glPopAttrib()
    glDepthMask (GL_FALSE)
    glDisable(GL_DEPTH_TEST)
    glDisable(GL_LIGHTING)
    glDisable(GL_FOG)
    glDisable(GL_CULL_FACE)
 

  def coord2d_to_3d(self, int x, int y, float z = -1.0, _Point result = None):
    """coord2d_to_3d(x, y, z = -1.0, result) -> Point

Converts 2D coordinates X and Y in pixel (e.g. mouse position) into 3D coordinates.
Z is the point Z coordinates (in the camera coordinates system) ; it should be negative
and defaults to -1.0.
RESULT is an optionnal Point that is used to store the result, if you want to avoid the
creation of a new object and prefer reuse an existant one (for speed purpose)."""
    cdef float k
    if result is None: result = Point(self)
    if self._option & CAMERA_ORTHO:
      result.set_xyz(
                     (( float(x) / self._viewport[2]) - 0.5) * self._viewport[2] / self._viewport[3] * 2.0 * self._fov / 20.0 * 0.75,
                     ((-float(y) / self._viewport[3]) + 0.5) * 2.0 * self._fov / 20.0 * 0.75,
                     z,
                     )
    else:
      # XXX 1.15 should be replaced by a FOV-dependent value (but which formula ???)
      k = tan(to_radians(self._fov) / 2.0)
      result.set_xyz(
                     ((-float(x) / self._viewport[2]) + 0.5) * self._viewport[2] / self._viewport[3] * 2.0 * k * z,
                     (( float(y) / self._viewport[3]) - 0.5) * 2.0 * k * z,
                     z,
                     )
    return result
  
  def coord3d_to_2d(self, Position p):
    """coord3d_to_2d(position) -> x, y

Converts a 3D Position into 2D screen coordinates X, Y in pixel."""
    cdef float f[3]
    cdef float k
    p._into(self, f)
    if self._option & CAMERA_ORTHO:
      return (
        (-f[0] / (float(self._viewport[2]) / self._viewport[3]) / self._fov * 20.0 / 2.0 + 0.5) * self._viewport[2],
        ( f[1] /                                                  self._fov * 20.0 / 2.0 + 0.5) * self._viewport[3],
        )
    else:
      k = tan(to_radians(self._fov) / 2.0)
      return (
        (-f[0] / ((float(self._viewport[2]) / self._viewport[3]) * 2.0 * k * f[2]) + 0.5) * self._viewport[2],
        ( f[1] / (                                                 2.0 * k * f[2]) + 0.5) * self._viewport[3],
        )
  
  def widget_begin_round(self): pass
  def widget_advance_time(self, proportion): pass
  def widget_end_round(self): pass
  
  def is_in_frustum(self, CoordSyst coordsyst):
    cdef CoordSyst child
    cdef float sphere[4]
    
    if isinstance(coordsyst, World):
      # Check it as Volume
      _Volume._get_sphere(coordsyst, sphere)
      coordsyst._frustum_id = -1
      if sphere_in_frustum(renderer._frustum(coordsyst), sphere): return 1
      
      for child in (<_World> coordsyst).children:
        if self.is_in_frustum(child): return 1
      return 0
    
    coordsyst._get_sphere(sphere)
    coordsyst._frustum_id = -1
    
    
#     print
#     print sphere[0], sphere[1], sphere[2], sphere[3]

#     cdef Frustum* f
#     f = renderer._frustum(coordsyst)
#     print f.position[0], f.position[1], f.position[2]
#     cdef int i
#     for i from 0 <= i < 8:
#       print f.points[3 * i], f.points[3 * i + 1], f.points[3 * i + 2]
      
#     print sphere_in_frustum(renderer._frustum(coordsyst), sphere)
    
    return sphere_in_frustum(renderer._frustum(coordsyst), sphere)
    
    
    
