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


cdef class _Cal3dVolume(CoordSyst):
  """Cal3DVolume

A Cal3D volume (do not counfound with Volume!) wraps a Cal3D Model.
It displays a Cal3D shape. See Cal3DVolume.animate* methods in order to animate it."""
  
  #cdef _Cal3dShape _shape
  #cdef             _attached_meshes, _attached_coordsysts
  #cdef CalModel*   _model
  #cdef float       _delta_time
  #cdef float*      _face_planes, *_vertex_coords, *_vertex_normals
  #cdef int         _face_plane_ok, _vertex_ok
  
  cdef __getcstate__(self):
    #return self._parent, self._option, self._matrix[0], self._matrix[1], self._matrix[2], self._matrix[3], self._matrix[4], self._matrix[5], self._matrix[6], self._matrix[7], self._matrix[8], self._matrix[9], self._matrix[10], self._matrix[11], self._matrix[12], self._matrix[13], self._matrix[14], self._matrix[15], self._matrix[16], self._matrix[17], self._matrix[18], self._shape, self._attached_meshes, self._attached_coordsysts
    return CoordSyst.__getcstate__(self), self._shape, self._attached_meshes, self._attached_coordsysts
  
  cdef void __setcstate__(self, cstate):
    CoordSyst.__setcstate__(self, cstate[0])
    self._shape               = cstate[1]
    self._attached_meshes     = cstate[2]
    self._attached_coordsysts = cstate[3]
    
    if self._shape:
      self._model = CalModel_New(self._shape._core_model)
      if self._model == NULL:
        print "erreur CalModel_Create", CalError_GetLastErrorDescription()
        raise RuntimeError("CalModel_Create failed: %s" % CalError_GetLastErrorDescription())
      
      for i from 0 <= i < len(self._attached_meshes):
        if self._attached_meshes[i] == 1:
          if CalModel_AttachMesh(self._model, i) == 0:
            print "erreur CalModel_AttachMesh", CalError_GetLastErrorDescription()
            raise RuntimeError("CalModel_AttachMesh failed: %s" % CalError_GetLastErrorDescription())
      self._build_submeshes()
      
  property shape:
    def __get__(self):
      return self._shape
    def __set__(self, _Cal3dShape shape):
      self.set_shape(shape)
      
  property attached_meshes:
    def __get__(self):
      return self._attached_meshes
    
  property attached_coordsysts:
    def __get__(self):
      return self._attached_coordsysts
    
  def __init__(self, _World parent = None, _Cal3dShape shape = None, attached_meshes = None):
    """Cal3dVolume(parent = None, shape = None, visible_meshes = None)

Creates a new Cal3D volume. PARENT is the volume's parent, and SHAPE is the Cal3D
shape (you cannot use "normal" Soya's shape here !).

ATTACHED_MESHES is a list of meshes names to attach; if ATTACHED_MESHES is None,
all meshes are attached. See volume.shape.meshes to get the list of available
mesh names."""
    CoordSyst.__init__(self, parent)
    self._attached_meshes     = []
    self._attached_coordsysts = []
    
    if shape:
      self.set_shape(shape, attached_meshes)
      
  def __dealloc__(self):
    if self._model != NULL:
      CalModel_Delete (self._model)
      
    if self._vertex_coords  != NULL: free(self._vertex_coords)
    if self._vertex_normals != NULL: free(self._vertex_normals)
    if self._face_planes    != NULL: free(self._face_planes)
    
  def set_shape(self, _Cal3dShape shape, attached_meshes = None):
    cdef int i, nb
    if not self._shape is None:
      CalModel_Delete (self._model)
      self._attached_meshes.__imul__(0)
      
    if shape is None: self._shape = None
    else:
      self._shape = shape
      self._model = CalModel_New(shape._core_model)
      if self._model == NULL:
        print "error CalModel_Create", CalError_GetLastErrorDescription()
        raise RuntimeError("CalModel_Create failed: %s" % CalError_GetLastErrorDescription())
        
      nb = CalCoreModel_GetCoreMeshCount(shape._core_model)
      for i from 0 <= i < nb: self._attached_meshes.append(0)
      if not attached_meshes is None: self.attach(*attached_meshes)
      else:                           self._attach_all()
      
  cdef void _build_submeshes(self):
    if not(self._shape._option & CAL3D_INITED): self._shape._build_submeshes()
    
    if self._vertex_coords  != NULL: free(self._vertex_coords)
    if self._vertex_normals != NULL: free(self._vertex_normals)
    if self._face_planes    != NULL: free(self._face_planes)
    
    self._vertex_coords  = <GLfloat*> malloc(self._shape._nb_vertices * 3 * sizeof(GLfloat))
    self._vertex_normals = <GLfloat*> malloc(self._shape._nb_vertices * 3 * sizeof(GLfloat))
    self._face_planes    = <GLfloat*> malloc(self._shape._nb_faces    * 4 * sizeof(GLfloat))
    
  cdef void _build_face_planes(self):
    cdef float*        ptrf, *plane
    cdef int           i, j
    cdef _Cal3dSubMesh submesh
    
    if self._vertex_ok <= 0: self._build_vertices(1)
      
    plane = self._face_planes
    
    i = 0
    ptrf   = self._vertex_coords
    for submesh in self._shape._submeshes:
      if self._attached_meshes[submesh._mesh]:
        for j from 0 <= j < submesh._nb_faces:
          face_plane(plane + 4 * j, ptrf + 3 * submesh._faces[3 * j], ptrf + 3 * submesh._faces[3 * j + 1], ptrf + 3 * submesh._faces[3 * j + 2])
          # XXX normalize here (with plane_vector_normalize) or keep normalization in _raypick ?
          
      i = i + 1
      ptrf  = ptrf  + submesh._nb_vertices * 3
      plane = plane + submesh._nb_faces    * 4
      
    self._face_plane_ok = 1
    
  def attach(self, *mesh_names):
    """Cal3DVolume.attach(mesh_name_1, ...)

Attaches new meshes named MESH_NAME_1, ... to the volume.
See volume.shape.meshes to get the list of available mesh names.
Attaching several meshes at the same time can be faster."""
    cdef int i
    if self._model != NULL:
      for mesh_name in mesh_names:
        i = self._shape.meshes[mesh_name]
        if self._attached_meshes[i] == 0:
          if CalModel_AttachMesh(self._model, i) == 0:
            print "erreur CalModel_AttachMesh", CalError_GetLastErrorDescription()
            raise RuntimeError("CalModel_AttachMesh failed: %s" % CalError_GetLastErrorDescription())
          
          self._attached_meshes[i] = 1
      self._build_submeshes()
    
  def detach(self, *mesh_names):
    """Cal3DVolume.detach(mesh_name_1, ...)

Detaches meshes named MESH_NAME_1, ... to the volume.
Detaching several meshes at the same time can be faster."""
    cdef int i
    if self._model != NULL:
      for mesh_name in mesh_names:
        i = self._shape.meshes[mesh_name]
        if self._attached_meshes[i] == 1:
          if CalModel_DetachMesh(self._model, i) == 0:
            print "erreur CalModel_DetachMesh", CalError_GetLastErrorDescription()
            raise RuntimeError("CalModel_DetachMesh failed: %s" % CalError_GetLastErrorDescription())
          self._attached_meshes[i] = 0
      self._build_submeshes()

  cdef void _attach_all(self):
    cdef int i
    if self._model != NULL:
      for i from 0 <= i < len(self._attached_meshes):
        if self._attached_meshes[i] == 0:
          if CalModel_AttachMesh(self._model, i) == 0:
            print "erreur CalModel_AttachMesh", CalError_GetLastErrorDescription()
            raise RuntimeError("CalModel_AttachMesh failed: %s" % CalError_GetLastErrorDescription())
          self._attached_meshes[i] = 1
      self._build_submeshes()
      
  def is_attached(self, mesh_name):
    """Cal3DVolume.is_attached(mesh_name)

Checks if the mesh called MESH_NAME is attached to the volume."""
    return self._attached_meshes[self._shape.meshes[mesh_name]]
    
  def attach_to_bone(self, CoordSyst coordsyst, bone_name):
    """Cal3DVolume.attach_to_bone(coordsyst, bone_name)

Attaches COORDSYST (usually a world) to the bone named BONE_NAME.
As the bone moved (because of animation), COORDSYST will be moved too.
See tutorial character-animation-2.py."""
    cdef int i
    if not self._shape is None:
      i = CalCoreSkeleton_GetCoreBoneId(CalCoreModel_GetCoreSkeleton(self._shape._core_model), bone_name)
      if i == -1: raise ValueError("No bone named %s !" % bone_name)
      self._attached_coordsysts.append((coordsyst, i))
    else: raise ValueError("Cannot attach to bone, shape is None !")
    
  def detach_from_bone(self, CoordSyst coordsyst):
    """Cal3DVolume.detach_from_bone(coordsyst)

Detaches COORDSYST from the bone it has been attached to."""
    cdef int i
    for i from 0 <= i < len(self._attached_coordsysts):
      if self._attached_coordsysts[i][0] is coordsyst:
        del self.attached_coordsysts[i]
        break
      
  def __repr__(self):
    if self._shape is None: return "<Cal3dVolume, no shape>"
    else:                   return "<Cal3dVolume, shape %s>" % repr(self.shape)
    
  def advance_time(self, float proportion):
    import soya
    self._delta_time = self._delta_time + proportion * soya.IDLER.round_duration
    
  def animate_blend_cycle(self, animation_name, float weight = 1.0, float fade_in = 0.2):
    """Cal3DVolume.animate_blend_cycle(animation_name, weight = 1.0, fade_in = 0.2)

Plays animation ANIMATION_NAME in cycle.
See volume.shape.animations for the list of available animations.

WEIGHT is the weight of the animation (usefull is several animations are played
simultaneously), and FADE_IN is the time (in second) needed to reach this weight
(in order to avoid a brutal transition).

Notice that the animation will NOT start at its beginning, but at the current global
animation time, which is shared by all cycles (see animate_reset if you want to start
a cycle at its beginning)."""
    CalMixer_BlendCycle(CalModel_GetMixer(self._model), self._shape._animations[animation_name], weight, fade_in)
    
  def animate_clear_cycle(self, animation_name, float fade_out = 0.2):
    """Cal3DVolume.animate_clear_cycle(animation_name, fade_out = 0.2)

Stops playing animation ANIMATION_NAME in cycle.
FADE_OUT is the time (in second) needed to stop the animation (in order to avoid
a brutal transition)."""
    CalMixer_ClearCycle(CalModel_GetMixer(self._model), self._shape._animations[animation_name], fade_out)
    
  def animate_execute_action(self, animation_name, float fade_in = 0.2, float fade_out = 0.2):
    """Cal3DVolume.animate_execute_action(animation_name, fade_in = 0.2, fade_out = 0.2)

Plays animation ANIMATION_NAME once.
See volume.shape.animations for the list of available animations.
FADE_IN and FADE_OUT are the time (in second) needed to reach full weight, and to
stop the animation (in order to avoid brutal transitions)."""
    CalMixer_ExecuteAction(CalModel_GetMixer(self._model), self._shape._animations[animation_name], fade_in, fade_out)

  def animate_reset(self):
    """Cal3DVolume.animate_reset()

Removes all animations (both cycle and action animation).
It also resets the cycle animation time : i.e. cycles will restart from their beginning."""
    # Calling CalMixer_UpdateAnimation with 0.0 has a resetting effect.
    # This is an undocumented feature i've discovered by reading sources.
    CalMixer_UpdateAnimation(CalModel_GetMixer(self._model), 0.0)
    
    # Older hacks
    #CalModel_ResetMixer(self._model)
    
  def set_lod_level(self, float lod_level):
    if self._model != NULL: CalModel_SetLodLevel(self._model, lod_level)
    
  def begin_round(self):
    self._vertex_ok     = self._vertex_ok     - 1
    self._face_plane_ok = self._face_plane_ok - 1
    
    if (not self._shape is None) and (self._vertex_ok <= 0):
      self._build_vertices(0)
      
  def _build_vertices(self, int vertices):
    cdef int       bone_id
    cdef CalBone*  bone
    cdef CoordSyst csyst
    cdef float*    trans, *quat
    
    CalModel_Update(self._model, self._delta_time)
    self._delta_time = 0.0
    
    for csyst, bone_id in self._attached_coordsysts: # Updates coordsysts attached to a bone
      bone = CalSkeleton_GetBone(CalModel_GetSkeleton(self._model), bone_id)
      quat = CalQuaternion_Get(CalBone_GetRotationAbsolute(bone))
      quat[3] = -quat[3] # Cal3D use indirect frame or what ???
      matrix_from_quaternion(csyst._matrix, quat)
      trans = CalVector_Get(CalBone_GetTranslationAbsolute(bone))
      csyst._matrix[12] = <GLfloat> trans[0]
      csyst._matrix[13] = <GLfloat> trans[1]
      csyst._matrix[14] = <GLfloat> trans[2]
      csyst._invalidate()
      
    if vertices == 1:
      self._shape._build_vertices(self)
      self._vertex_ok = 1
      
      
  cdef void _batch(self, CoordSyst coordsyst):
    cdef int       bone_id
    cdef CalBone*  bone
    cdef CoordSyst csyst
    cdef float*    trans, *quat
    
    self._frustum_id = -1
    if self._shape is None: return
    
    CalModel_Update(self._model, self._delta_time)
    self._delta_time = 0.0
    
    # Updates coordsysts attached to a bone
    for csyst, bone_id in self._attached_coordsysts:
      bone = CalSkeleton_GetBone(CalModel_GetSkeleton(self._model), bone_id)
      quat = CalQuaternion_Get(CalBone_GetRotationAbsolute(bone))
      quat[3] = -quat[3] # Cal3D use indirect frame or what ???
      matrix_from_quaternion(csyst._matrix, quat)
      trans = CalVector_Get(CalBone_GetTranslationAbsolute(bone))
      csyst._matrix[12] = <GLfloat> trans[0]
      csyst._matrix[13] = <GLfloat> trans[1]
      csyst._matrix[14] = <GLfloat> trans[2]
      csyst._invalidate()
      
    if not self._option & HIDDEN:
      if (self._shape._sphere[3] != -1.0) and (sphere_in_frustum(renderer._frustum(self), self._shape._sphere) == 0): return
      #multiply_matrix(self._render_matrix, renderer.current_camera._render_matrix, self._root_matrix())
      
      # Ok, we render the Cal3D model ; rendering implies computing vertices
      self._vertex_ok = 1
      multiply_matrix(self._render_matrix, coordsyst._render_matrix, self._matrix)
      if self._shape._option & CAL3D_ALPHA:
        renderer._batch(renderer.alpha, self._shape, self, -1)
      else: 
        renderer._batch(renderer.opaque, self._shape, self, -1)
        
      # For outline
      if (self._shape._option & CAL3D_CELL_SHADING) and (self._shape._outline_width > 0.0):
        renderer._batch(renderer.secondpass, self._shape, self, -1)
        
  cdef int _shadow(self, CoordSyst coordsyst, _Light light):
    if not self._shape is None: return self._shape._shadow(self, light)
    return 0



  cdef void _raypick(self, RaypickData data, CoordSyst parent):
    if (self._shape is None) or (self._option & NON_SOLID): return
    if self._vertex_ok     <= 0: self._build_vertices(1)
    if self._face_plane_ok <= 0: self._build_face_planes()
    
    cdef float*        raydata, *ptrf, *plane
    cdef float         z, root_z
    cdef int           i, j, r
    cdef _Cal3dSubMesh submesh
    
    # XXX take into account the ray length ? e.g., if ray_length == 1.0, sphere_radius = 1.0 and (ray_origin >> self).length() > 2.0, no collision can occur
    raydata = self._raypick_data(data)
    if (self._shape._sphere[3] > 0.0) and (sphere_raypick(raydata, self._shape._sphere) == 0): return
    
    i = 0
    plane  = self._face_planes
    ptrf   = self._vertex_coords
    for submesh in self._shape._submeshes:
      if self._attached_meshes[submesh._mesh]:
        for j from 0 <= j < submesh._nb_faces:
          r = triangle_raypick(raydata, ptrf + 3 * submesh._faces[3 * j], ptrf + 3 * submesh._faces[3 * j + 1], ptrf + 3 * submesh._faces[3 * j + 2], plane + 4 * j, data.option, &z)
          
          if r != 0:
            root_z = self._distance_out(z)
            if (data.result_coordsyst is None) or (fabs(root_z) < fabs(data.root_result)):
              data.result      = z
              data.root_result = root_z
              data.result_coordsyst = self
              if   r == RAYPICK_DIRECT: memcpy(data.normal, plane + 4 * j, 3 * sizeof(float))
              elif r == RAYPICK_INDIRECT:
                if self._shape._option & CAL3D_DOUBLE_SIDED:
                  data.normal[0] = -(plane + 4 * j)[0]
                  data.normal[1] = -(plane + 4 * j)[1]
                  data.normal[2] = -(plane + 4 * j)[2]
                else: memcpy(data.normal, plane + 4 * j, 3 * sizeof(float))
              vector_normalize(data.normal)
              
      i = i + 1
      ptrf  = ptrf  + submesh._nb_vertices * 3
      plane = plane + submesh._nb_faces    * 4
      
  cdef int _raypick_b(self, RaypickData data, CoordSyst parent):
    if (self._shape is None) or (self._option & NON_SOLID): return 0
    cdef float*        raydata, *ptrf, *plane
    cdef float         z
    cdef int           i, j
    cdef _Cal3dSubMesh submesh
    
    if self._vertex_ok <= 0: self._build_vertices(1)
    
    # XXX take into account the ray length ? e.g., if ray_length == 1.0, sphere_radius = 1.0 and (ray_origin >> self).length() > 2.0, no collision can occur
    raydata = parent._raypick_data(data)
    if (self._shape._sphere[3] > 0.0) and (sphere_raypick(raydata, self._shape._sphere) == 0): return 0
    
    i = 0
    plane  = self._face_planes
    ptrf   = self._vertex_coords
    for submesh in self._shape._submeshes:
      if self._attached_meshes[submesh._mesh]:
        for j from 0 <= j < submesh._nb_faces:
          if triangle_raypick(raydata, ptrf + 3 * submesh._faces[3 * j], ptrf + 3 * submesh._faces[3 * j + 1], ptrf + 3 * submesh._faces[3 * j + 2], plane + 4 * j, data.option, &z) != 0: return 1
          
    return 0
  
  cdef void _collect_raypickables(self, Chunk* items, float* rsphere, float* sphere):
    if (self._shape._sphere[3] < 0.0) or (sphere_distance_sphere(sphere, self._shape._sphere) < 0.0):
      chunk_add_ptr(items, <void*> self)
      
