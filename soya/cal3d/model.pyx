# -*- indent-tabs-mode: t -*-

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

import os.path

cdef int       cal3d_nb_faces, cal3d_nb_vertices
cdef float*    cal3d_texcoords_array, *cal3d_shades_array
cdef int*      cal3d_facesides_array
cal3d_nb_vertices  = cal3d_nb_faces = 0
cal3d_texcoords_array = cal3d_shades_array = cal3d_facesides_array = NULL


cdef void quit_cal3d():
	free(cal3d_texcoords_array)
	free(cal3d_shades_array)
	free(cal3d_facesides_array)
	
def load_raw_image(filename):
	"""Loads a ".raw" image file, which are used by Cal3D example (see cal3d_data).
Returns a Soya image object, suitable for model.material.image."""
	cdef int width, height, nb_colors, line_length, y
	import struct, array
	
	f = open(filename)
	width, height, nb_colors = struct.unpack("iii", f.read(12))
	data = array.array("c", f.read())
	
	# Flip texture around y-axis (-> opengl-style).
	data2 = array.array("c", " " * len(data))
	line_length = width * nb_colors
	for y from 0 <= y < height:
		data2[y * line_length : (y + 1) * line_length] = data[(height - y - 1) * line_length : (height - y) * line_length]
		
	return Image(data2.tostring(), width, height, nb_colors)

def parse_cal3d_cfg_file(filename):
	"""Reads a the Cal3D .cfg file, and creates and returns a Cal3D model from it."""
	import soya
	cdef _AnimatedModel model
	cdef int         i
	model                = soya.AnimatedModel()
	dirname              = os.path.dirname(filename)
	model._filename      = os.path.basename(dirname)
	model._full_filename = filename
	
	# Do NOT load several time the same materials / ...
	# (some exporter does import several time the same material)
	already_done = {}
	
	for line in open(filename).readlines():
		if line and (line[0] != "#"):
			parts = line.split("=")
			if len(parts) == 2:
				key, value = parts
				value = value.rstrip()
				#try: value = int(value)
				#except:
				#	try: value = float(value)
				#	except: pass
				
				if already_done.get((key, value)): continue
				already_done[key, value] = 1
				
				if   key == "skeleton"    : model.load_skeleton (os.path.join(dirname, value))
				elif key == "mesh"        : model.load_mesh     (os.path.join(dirname, value))
				elif key == "material"    : model.load_material (os.path.join(dirname, value))
				elif key == "animation"   : model.load_animation(os.path.join(dirname, value))
				elif key == "shadow"      : model.shadow       = int(value)
				elif key == "double_sided": model.double_sided = int(value)
				elif key == "sphere"      : model.sphere       = map(float, value.split())
				elif key == "cellshading"                    :
					if int(value): model.set_cellshading()
				elif key == "cellshading_shader"             : model._shader = soya.Material.get(value)
				elif key == "cellshading_outline_width"      : model._outline_width       = float(value)
				elif key == "cellshading_outline_attenuation": model._outline_attenuation = float(value)
				elif key == "cellshading_outline_color"      :
					value = value.split(",")
					for i from 0 <= i < 4: model._outline_color[i] = float(value[i])
				else: print "Warning: unknows Cal3D .cfg tag:   %s=%s" % (key, value)
	model.build_materials()
	return model


cdef class _Cal3dSubMesh:
	#cdef int       _option, _mesh, _submesh
	#cdef _Material _material
	#
	#cdef int       _nb_faces, _nb_vertices
	#cdef int*      _faces
	#cdef int*      _face_neighbors

	def __dealloc__(self):
		if self._faces          != NULL: free(self._faces)
		if self._face_neighbors != NULL: free(self._face_neighbors)
		
	cdef _build(self, _AnimatedModel model, CalRenderer* cal_renderer, CalCoreModel* cal_core_model, CalCoreMesh* cal_core_mesh, int mesh, int submesh):
		global cal3d_nb_faces, cal3d_nb_vertices
		global cal3d_texcoords_array, cal3d_shades_array, cal3d_facesides_array
		
		cdef CalCoreSubmesh* cal_core_submesh
		cdef float*          vertices
		
		self._mesh         = mesh
		self._submesh      = submesh
		self._material     = model._materials[CalCoreSubmesh_GetCoreMaterialThreadId(CalCoreMesh_GetCoreSubmesh(cal_core_mesh, submesh))]
		
		cal_core_submesh = CalCoreMesh_GetCoreSubmesh(cal_core_mesh, submesh)
		
		# get faces
		self._nb_faces = CalCoreSubmesh_GetFaceCount(cal_core_submesh)
		self._faces = <int*> malloc(self._nb_faces * 3 * sizeof(int))
		CalRenderer_GetFaces(cal_renderer, self._faces)
		
		if cal3d_nb_faces < self._nb_faces:
			cal3d_facesides_array = <int*>   realloc(cal3d_facesides_array, self._nb_faces * sizeof(int))
			cal3d_nb_faces = self._nb_faces
			
			
		# get vertices
		self._nb_vertices = CalCoreSubmesh_GetVertexCount(cal_core_submesh)
		
		if cal3d_nb_vertices < self._nb_vertices:
			cal3d_texcoords_array = <float*> realloc(cal3d_texcoords_array, self._nb_vertices * 2 * sizeof(float))
			cal3d_shades_array    = <float*> realloc(cal3d_shades_array,    self._nb_vertices     * sizeof(float))
			cal3d_nb_vertices = self._nb_vertices
			
		#vertices = <float*> malloc(self._nb_faces * 3 * sizeof(float))
		#CalRenderer_GetVertices(cal_renderer, vertices)
		#free(vertices)
		
	cdef void _build_neighbors(self, full_filename, float* coords):
		cdef int i, j, k, l, p1, p2
		cdef float* coord1, *coord2
		cdef Chunk* chunk
		
		self._option = self._option | CAL3D_NEIGHBORS

		self._face_neighbors = <int*> malloc(self._nb_faces * 3 * sizeof(int))
		
		cache_filename = os.path.join(os.path.dirname(full_filename), "neighbors_%s-%s" % (self._mesh, self._submesh))
		
		# Read from the cache file, if it exist.
		if os.path.exists(cache_filename):
			if os.path.getmtime(cache_filename) > os.path.getmtime(full_filename):
				file = open(cache_filename, "rb")
				chunk = string_to_chunk(file.read())
				chunk_get_ints_endian_safe(chunk, self._face_neighbors, 3 * self._nb_faces)
				drop_chunk(chunk)
				return
			
		print "* Soya * Computing neighbor for Cal3D model, and caching the result in file %s..." % cache_filename
		
		for i from 0 <= i < self._nb_faces:
			for k from 0 <= k < 3:
				p1 = self._faces[3 * i + k]
				if k == 2: p2 = self._faces[3 * i]
				else:      p2 = self._faces[3 * i + k + 1]
				
				coord1 = coords + 3 * p1
				coord2 = coords + 3 * p2
				
				for j from 0 <= j < self._nb_faces:
					if i == j: continue
					
					if ((p1 == self._faces[3 * j]) or (p1 == self._faces[3 * j + 1]) or (p1 == self._faces[3 * j + 2])) and ((p2 == self._faces[3 * j]) or (p2 == self._faces[3 * j + 1]) or (p2 == self._faces[3 * j + 2])):
						self._face_neighbors[3 * i + k] = j
						break
					
					if ((point_distance_to(coord1, coords + 3 * self._faces[3 * j]) < EPSILON) or (point_distance_to(coord1, coords + 3 * self._faces[3 * j + 1]) < EPSILON) or (point_distance_to(coord1, coords + 3 * self._faces[3 * j + 2]) < EPSILON)) and ((point_distance_to(coord2, coords + 3 * self._faces[3 * j]) < EPSILON) or (point_distance_to(coord2, coords + 3 * self._faces[3 * j + 1]) < EPSILON) or (point_distance_to(coord2, coords + 3 * self._faces[3 * j + 2]) < EPSILON)):
						self._face_neighbors[3 * i + k] = j
						break
				else:
					self._face_neighbors[3 * i + k] = -1 # No neighbor
					
		# Try to save the neighbors
		try:
			file = open(cache_filename, "wb")
		except:
			print "* Soya * Can't cache Cal3D neighbor face data in file %s" % cache_filename
			return
		
		chunk = get_chunk()
		chunk_add_ints_endian_safe(chunk, self._face_neighbors, 3 * self._nb_faces)
		file.write(drop_chunk_to_string(chunk))
		
		
cdef class _AnimatedModel(_Model):
	#cdef int   _option
	#cdef int   _nb_faces, _nb_vertices
	#cdef float _sphere[4]
	#cdef _meshes, _animations, _materials, _submeshes
	#cdef _full_filename
	
	#cdef CalCoreModel* _core_model
	
	# Cellshading stuff
	#cdef _Material _shader
	#cdef float     _outline_color[4]
	#cdef float     _outline_width, _outline_attenuation
	
	cdef void _instanced(self, _Body body, opt):
		body._data = _AnimatedModelData(body, self, opt)
		
	property filename:
		def __get__(self):
			return self._filename
		
	property full_filename:
		def __get__(self):
			return self._full_filename
		
	property materials:
		def __get__(self):
			return self._materials
		
	property meshes:
		def __get__(self):
			return self._meshes

	property animations:
		def __get__(self):
			return self._animations

	property sphere:
		def __get__(self):
			return self._sphere[0], self._sphere[1], self._sphere[2], self._sphere[3]
		def __set__(self, sphere):
			self._sphere[0], self._sphere[1], self._sphere[2], self._sphere[3] = sphere
			
			
	def __init__(self):
		self._meshes     = {} # Maps mesh / animation names to the
		self._animations = {} # corresponding ID (index)
		self._materials  = []
		self._submeshes  = []
		self._sphere[3]  = -1.0
		self._core_model = CalCoreModel_New("")
		if self._core_model == NULL: raise RuntimeError("CalCoreModel_Create failed: %s" % CalError_GetLastErrorDescription())
		
		self._option = CAL3D_DOUBLE_SIDED
		
	property double_sided:
		def __get__(self):
			return self._option & CAL3D_DOUBLE_SIDED
		def __set__(self, int x):
			if x: self._option = self._option |  CAL3D_DOUBLE_SIDED
			else: self._option = self._option & ~CAL3D_DOUBLE_SIDED
			
	property shadow:
		def __get__(self):
			return self._option & CAL3D_SHADOW
		def __set__(self, int x):
			if x: self._option = self._option |  CAL3D_SHADOW
			else: self._option = self._option & ~CAL3D_SHADOW
			
	property cellshading:
		def __get__(self):
			return self._option & CAL3D_CELL_SHADING
			
	def set_cellshading(self, _Material shader = None, outline_color = BLACK, float outline_width = 4.0, float outline_attenuation = 0.3):
		cdef int i
		self._shader              = shader or _SHADER_DEFAULT_MATERIAL
		self._outline_width       = outline_width
		self._outline_attenuation = outline_attenuation
		for i from 0 <= i < 4: self._outline_color[i] = outline_color[i]
		
		self._option = self._option | CAL3D_CELL_SHADING
		
	cdef void _build_submeshes(self):
		cdef CalRenderer*    cal_renderer
		cdef CalModel*       cal_model
		cdef CalCoreMesh*    cal_core_mesh
		cdef _Cal3dSubMesh   my_submesh
		cdef int             nb_mesh, nb_submesh, i, j
		
		cal_model = CalModel_New(self._core_model)
		nb_mesh = CalCoreModel_GetCoreMeshCount(self._core_model)
		for i from 0 <= i < nb_mesh: CalModel_AttachMesh(cal_model, i)
		CalModel_SetMaterialSet(cal_model, 0)
		
		cal_renderer = CalModel_GetRenderer(cal_model)
		if CalRenderer_BeginRendering(cal_renderer) == 0: raise RuntimeError("CalRenderer_BeginRendering failed: %s" % CalError_GetLastErrorDescription())
		
		self._nb_faces = self._nb_vertices = 0
		
		for i from 0 <= i < nb_mesh:
			cal_core_mesh = CalCoreModel_GetCoreMesh(self._core_model, i)
			nb_submesh    = CalCoreMesh_GetCoreSubmeshCount(cal_core_mesh)
			for j from 0 <= j < nb_submesh:
				CalRenderer_SelectMeshSubmesh(cal_renderer, i, j)
				# create my new submesh
				my_submesh = _Cal3dSubMesh()
				my_submesh._build(self, cal_renderer, self._core_model, cal_core_mesh, i, j)
				self._submeshes.append(my_submesh)
				self._nb_faces    = self._nb_faces    + my_submesh._nb_faces
				self._nb_vertices = self._nb_vertices + my_submesh._nb_vertices
				if my_submesh._material._option & MATERIAL_ALPHA: self._option = self._option | CAL3D_ALPHA
				
		CalRenderer_EndRendering(cal_renderer)
		CalModel_Delete (cal_model)
		self._option = self._option | CAL3D_INITED
		
#   def dump(self):
#     cdef int i
#     cdef _Cal3dSubMesh submesh
#     i = 0
#     print 
#     print "_nb_faces", self._nb_faces, "_nb_vertices", self._nb_vertices
#     for submesh in self._submeshes:
#       print i, submesh
#       print "_mesh", submesh._mesh, "_submesh", submesh._submesh
#       print "_nb_vertices", submesh._nb_vertices, "_nb_faces", submesh._nb_faces
#       i = i + 1
#     print 
		
	cdef void _set_face_neighborhood(self, int index1, int index2, GLfloat* vertices):
		# XXX TODO
		pass
	
	cdef void _set_cell_shading(self, _Material shader, GLfloat* color, GLfloat line_width_factor):
		# XXX TODO
		pass
	
	
	cdef void _batch(self, _Body body):
		cdef _AnimatedModelData data
		cdef float sphere[4]
		data   = <_AnimatedModelData> body._data
		
		data._build_vertices(0)
		
		if not body._option & HIDDEN:
			if self._sphere[3] != -1.0:
				sphere_by_matrix_copy(sphere, self._sphere, body._root_matrix())
				if sphere_in_frustum(renderer.root_frustum, sphere) == 0: return
				
			#if (self._sphere[3] != -1.0) and (sphere_in_frustum(renderer._frustum(body), self._sphere) == 0): return
			
			# Ok, we render the Cal3D model ; rendering implies computing vertices
			data._vertex_ok = 1
			if self._option & CAL3D_ALPHA: renderer._batch(renderer.alpha , self, body, NULL)
			else:                          renderer._batch(renderer.opaque, self, body, NULL)
			
			# For outline
			if (self._option & CAL3D_CELL_SHADING) and (self._outline_width > 0.0):
				#renderer._batch(renderer.secondpass, self, body, -1)
				if not self._option & CAL3D_ALPHA: renderer._batch(renderer.alpha, self, body, NULL)
				
				
	cdef void _render(self, _Body body):
		global cal3d_texcoords_array, cal3d_shades_array
		
		cdef _AnimatedModelData data
		cdef CalRenderer*               cal_renderer
		cdef _Cal3dSubMesh              submesh
		cdef GLfloat*                   ptrf, *ptrn
		cdef int                        j
		
		cdef float*                     shades, *plane
		cdef Frustum*                   frustum
		
		data   = body._data
		ptrf   = data._coords
		ptrn   = data._vnormals
		
		#if renderer.state == RENDERER_STATE_SECONDPASS:
		if renderer.state == RENDERER_STATE_ALPHA:
			if data._face_plane_ok <= 0: data._build_face_planes()
			
			frustum = renderer._frustum(body)
			plane = data._face_planes
			for submesh in self._submeshes:
				if data._attached_meshes[submesh._mesh]:
					self._render_outline(submesh, frustum, ptrf, ptrn, plane)
				ptrf  = ptrf  + submesh._nb_vertices * 3
				ptrn  = ptrn  + submesh._nb_vertices * 3
				plane = plane + submesh._nb_faces    * 4
			return
		
		cal_renderer = CalModel_GetRenderer(data._cal_model)
		
		if (CalRenderer_BeginRendering(cal_renderer) == 0):
			print "error 1", CalError_GetLastErrorDescription()
			raise RuntimeError("CalRenderer_BeginRendering failed: %s" % CalError_GetLastErrorDescription())
		
		if self._option & CAL3D_DOUBLE_SIDED: glDisable (GL_CULL_FACE)
		glEnableClientState(GL_VERTEX_ARRAY)
		glEnableClientState(GL_NORMAL_ARRAY)
		glEnableClientState(GL_TEXTURE_COORD_ARRAY)
		if body._option & LEFTHANDED: glFrontFace(GL_CW)
		
		for submesh in self._submeshes:
			if data._attached_meshes[submesh._mesh]:
				
				# TO DO sort alpha and opaque submesh ?
				# Do this once, in __init__ ?
				
				CalRenderer_SelectMeshSubmesh(cal_renderer, submesh._mesh, submesh._submesh)
				
				# get all vertices
				CalRenderer_GetVertices          (cal_renderer, ptrf)
				CalRenderer_GetNormals           (cal_renderer, ptrn)
				CalRenderer_GetTextureCoordinates(cal_renderer, 0, cal3d_texcoords_array)
				glVertexPointer  (3, GL_FLOAT, 0, ptrf)
				glNormalPointer  (   GL_FLOAT, 0, ptrn)
				glTexCoordPointer(2, GL_FLOAT, 0, cal3d_texcoords_array)
				
				submesh._material.activate()
				
				if self._option & CAL3D_CELL_SHADING:
					if not (submesh._option & CAL3D_NEIGHBORS):
						submesh._build_neighbors(self._full_filename, ptrf)
						
					shades = cal3d_shades_array
					self._prepare_cellshading(body, shades, submesh._nb_vertices, ptrf, ptrn)
					
					# Activate shader texture
					glActiveTextureARB(GL_TEXTURE1)
					if self._shader._id == 0: self._shader._init_texture()
					glEnable          (GL_TEXTURE_2D)
					glTexEnvi         (GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
					glBindTexture     (GL_TEXTURE_2D, self._shader._id)
					glActiveTextureARB(GL_TEXTURE0)
					
					glDisable         (GL_LIGHTING)
					
					glBegin(GL_TRIANGLES)
					for j from 0 <= j < submesh._nb_faces * 3:
						glMultiTexCoord2fARB(GL_TEXTURE1, shades[submesh._faces[j]], shades[submesh._faces[j]])
						#glTexCoord2fv(cal3d_texcoords_array + (2 * submesh._faces[j]))
						#glNormal3fv(ptrn + (3 * submesh._faces[j]))
						#glVertex3fv(ptrf + (3 * submesh._faces[j]))
						glArrayElement(submesh._faces[j])
					glEnd()
					
					# Unactivate shader texture
					glActiveTextureARB(GL_TEXTURE1)
					glDisable         (GL_TEXTURE_2D)
					glActiveTextureARB(GL_TEXTURE0)

					glEnable          (GL_LIGHTING)
					
				else:
					if (self._option & CAL3D_SHADOW) and not (submesh._option & CAL3D_NEIGHBORS):
						submesh._build_neighbors(self._full_filename, ptrf)
						
					glBegin(GL_TRIANGLES)
					for j from 0 <= j < submesh._nb_faces * 3:
						#glTexCoord2fv(cal3d_texcoords_array + (2 * submesh._faces[j]))
						#glNormal3fv(ptrn + (3 * submesh._faces[j]))
						#glVertex3fv(ptrf + (3 * submesh._faces[j]))
						glArrayElement(submesh._faces[j])
					glEnd()
					
			ptrf = ptrf + submesh._nb_vertices * 3
			ptrn = ptrn + submesh._nb_vertices * 3
			
		CalRenderer_EndRendering(cal_renderer)
		glDisableClientState(GL_NORMAL_ARRAY)
		glDisableClientState(GL_TEXTURE_COORD_ARRAY)
		glDisableClientState(GL_VERTEX_ARRAY)
		if body._option & LEFTHANDED: glFrontFace(GL_CCW)
		if self._option & CAL3D_DOUBLE_SIDED: glEnable(GL_CULL_FACE)


	cdef void _build_vertices(self, _AnimatedModelData data):
		cdef CalRenderer*    cal_renderer
		cdef _Cal3dSubMesh   submesh
		cdef GLfloat*        ptrf, *ptrn
		
		ptrf   = data._coords
		ptrn   = data._vnormals
		
		cal_renderer = CalModel_GetRenderer(data._cal_model)
		
		if (CalRenderer_BeginRendering(cal_renderer) == 0):
			print "error 1", CalError_GetLastErrorDescription()
			raise RuntimeError("CalRenderer_BeginRendering failed: %s" % CalError_GetLastErrorDescription())
		
		for submesh in self._submeshes:
			if data._attached_meshes[submesh._mesh]:
				CalRenderer_SelectMeshSubmesh(cal_renderer, submesh._mesh, submesh._submesh)
				
				# get all vertices
				CalRenderer_GetVertices          (cal_renderer, ptrf)
				CalRenderer_GetNormals           (cal_renderer, ptrn)
				
			ptrf = ptrf + submesh._nb_vertices * 3
			ptrn = ptrn + submesh._nb_vertices * 3
			
		CalRenderer_EndRendering(cal_renderer)
		
		
	cdef void _prepare_cellshading(self, CoordSyst coordsyst, float* shades, int nb_vertices, float* coords, float* vnormals):
		cdef int    n
		cdef _Light light
		for light in renderer.top_lights:             light._cast_into(coordsyst)
		for light in renderer.current_context.lights: light._cast_into(coordsyst)
		
		for n from 0 <= n < nb_vertices: shades[n] = 0.5
		self._prepare_cellshading_shades(shades, renderer.top_lights            , nb_vertices, coords, vnormals)
		self._prepare_cellshading_shades(shades, renderer.current_context.lights, nb_vertices, coords, vnormals)
		
		# clip shade texcoord values
		for n from 0 <= n < nb_vertices:
			# do not clip with interval [0, 1] because smooth magnification of texture
			# causes visual bugs
			if   shades[n] > 0.95: shades[n] = 0.95
			elif shades[n] < 0.05: shades[n] = 0.05
			
	cdef void _prepare_cellshading_shades(self, float* shades, lights, int nb_vertices, float* coords, float* vnormals):
		cdef _Light light
		cdef float* ptr1, *ptr2
		cdef float  v[3]
		cdef float  tmp
		cdef int    j
		
		for light in lights:
			ptr1 = vnormals
			if light._w == 0.0: # directional light
				for j from 0 <= j < nb_vertices:
					tmp = -vector_dot_product(ptr1, light._data)
					shades[j] = shades[j] + tmp
					ptr1 = ptr1 + 3
					
			else: # positional light
				ptr2 = coords
				for j from 0 <= j < nb_vertices:
					v[0] = light._data[0] - ptr2[0]
					v[1] = light._data[1] - ptr2[1]
					v[2] = light._data[2] - ptr2[2]
					vector_normalize(v)
					tmp = vector_dot_product(ptr1, v)
					shades[j] = shades[j] + tmp
					ptr1 = ptr1 + 3
					ptr2 = ptr2 + 3
					


	cdef void _render_outline(self, _Cal3dSubMesh submesh, Frustum* frustum, float* coords, float* vnormals, float* plane):
		global cal3d_facesides_array

		cdef int        i, j, k
		cdef float      d
		cdef float      plane2[4]
		
		cdef int*       facesides
		facesides = cal3d_facesides_array
		
		# Compute outline width, which depends on distance to camera
		d = sphere_distance_point(self._sphere, frustum.position) * self._outline_attenuation
		if d < 1.0: d = self._outline_width
		else:
			d = self._outline_width / d
			if d < 2.0: d = 2.0
			
		_DEFAULT_MATERIAL._activate()
		glLineWidth(d)
		glColor4fv (self._outline_color)
		glDisable  (GL_LIGHTING)
		glDepthFunc(GL_LEQUAL)
		
		glEnable   (GL_LINE_SMOOTH)
		glPolygonOffset(2.0, 2.0)
		glEnable   (GL_POLYGON_OFFSET_LINE)
		
		# mark faces as either front or back
		for i from 0 <= i < submesh._nb_faces:
			if plane[0] * frustum.position[0] + plane[1] * frustum.position[1] + plane[2] * frustum.position[2] + plane[3] > 0.0:
				facesides[i] = FACE_FRONT
			else:
				facesides[i] = FACE_BACK
				
			plane = plane + 4
			
		cdef Chunk* chunk
		chunk = get_chunk()
		chunk_register(chunk, submesh._nb_vertices * sizeof(int))
		cdef int* vertex_used
		vertex_used = <int*> (chunk.content)
		for i from 0 <= i < submesh._nb_vertices: vertex_used[i] = -1
		
		
		# find and draw edges   
		glBegin(GL_LINES)
		if self._option & CAL3D_DOUBLE_SIDED:
			for i from 0 <= i < submesh._nb_faces:
				for j from 0 <= j < 3:
					k = submesh._face_neighbors[3 * i + j]
					if (k == -1) or (facesides[k] != facesides[i]):
						vertex_used[submesh._faces[3 * i + j]] = 1
						
						# draw edge between vertices j and j + 1
						glVertex3fv(coords + 3 * submesh._faces[3 * i + j])
						if j < 2: glVertex3fv(coords + 3 * submesh._faces[3 * i + j + 1])
						else:     glVertex3fv(coords + 3 * submesh._faces[3 * i])
						
		else:
			for i from 0 <= i < submesh._nb_faces:
				if facesides[i] == FACE_FRONT:
					# test if neighbors are back
					for j from 0 <= j < 3:
						k = submesh._face_neighbors[3 * i + j]
						if (k == -1) or (facesides[k] == FACE_BACK):
							vertex_used[submesh._faces[3 * i + j]] = 1

							# draw edge between vertices j and j + 1
							glVertex3fv(coords + 3 * submesh._faces[3 * i + j])
							if j < 2: glVertex3fv(coords + 3 * submesh._faces[3 * i + j + 1])
							else:     glVertex3fv(coords + 3 * submesh._faces[3 * i])
						
		glEnd()
		
		glPointSize(d * 0.7)
		
		glBegin(GL_POINTS)
		for i from 0 <= i < submesh._nb_vertices:
			if vertex_used[i] == 1: glVertex3fv(coords + i * 3)
		glEnd()
		
		drop_chunk(chunk)
		
		glLineWidth(1.0) # Reset to default
		glPointSize(1.0) # Reset to default
		glEnable   (GL_LIGHTING)
		glDepthFunc(GL_LESS)
		glColor4fv (white)
		
		glDisable   (GL_POLYGON_OFFSET_LINE)



	def __dealloc__(self):
		CalCoreModel_Delete (self._core_model)
		
	def load_skeleton(self, filename):
		if CalCoreModel_LoadCoreSkeleton(self._core_model, filename) == 0: raise RuntimeError("CalCoreModel_LoadCoreSkeleton failed: %s" % CalError_GetLastErrorDescription())

	def load_mesh(self, filename):
		cdef int i
		i = CalCoreModel_LoadCoreMesh(self._core_model, filename)
		if i == -1: raise RuntimeError("CalCoreModel_LoadCoreMesh failed on file %s: %s" % (filename, CalError_GetLastErrorDescription()))
		self._meshes[os.path.basename(filename)[:-4]] = i
		return i
	
	def load_material(self, filename):
		cdef int i
		i = CalCoreModel_LoadCoreMaterial(self._core_model, filename)
		if i == -1: raise RuntimeError("CalCoreModel_LoadCoreMaterial failed on file %s: %s" % (filename, CalError_GetLastErrorDescription()))
		return i
	
	def load_animation(self, filename):
		cdef int i
		i = CalCoreModel_LoadCoreAnimation(self._core_model, filename)
		if i == -1: raise RuntimeError("CalCoreModel_LoadCoreAnimation failed on file %s: %s" % (filename, CalError_GetLastErrorDescription()))
		self._animations[os.path.basename(filename)[:-4]] = i
		return i
		
	def build_materials(self):
		cdef int              i, nb
		cdef CalCoreMaterial* material
		
		self._materials.__imul__(0)
		if self._core_model == NULL: return
		
		nb = CalCoreModel_GetCoreMaterialCount(self._core_model)
		for i from 0 <= i < nb:
			material = CalCoreModel_GetCoreMaterial(self._core_model, i)
			
			# It seems that the Cal3D C wrapper does not support yet the CalCoreMaterial_Get*Color functions
			self._materials.append(self._get_material_4_cal3d(CalCoreMaterial_GetMapFilename(material, 0), 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, CalCoreMaterial_GetShininess(material)))
			
			CalCoreModel_CreateCoreMaterialThread(self._core_model, i)
			CalCoreModel_SetCoreMaterialId(self._core_model, i, 0, i)
			CalCoreMaterial_SetUserData(material, <CalUserData> i)
		
# This method is split in 3 ; this is a work-around for a bug in Pyrex

#   cdef _Material _get_material_4_cal3d(self, image_filename, float diffuse_r, float diffuse_g, float diffuse_b, float diffuse_a, float specular_r, float specular_g, float specular_b, float specular_a, float shininess):
#     material_name = os.path.basename(image_filename)
#     material_name = material_name[:material_name.find(".")]
#     try:
#       return Material.get(material_name) # Check for a Soya material with the same name
#     except ValueError: # Not a Soya material
#       material = Material()
#       material.diffuse   = (diffuse_r , diffuse_g , diffuse_b , diffuse_a )
#       material.specular  = (specular_r, specular_g, specular_b, specular_a)
#       material.shininess = shininess
			
#       import soya
#       for path in soya.path:
#         file = os.path.join(path, Image.DIRNAME, os.path.basename(image_filename))
#         if os.path.exists(file):
#           if   image_filename.endswith(".raw"): material.texture = load_raw_image(file)
#           else:                                 material.texture = open_image    (file)
#           break
#       else:
#         image_filename = os.path.join(os.path.dirname(self._full_filename), image_filename)
#         print "WARNING: Using image that is not in {soya.path}/images : %s !" % image_filename
#         if   image_filename.endswith(".raw"): material.texture = load_raw_image(image_filename)
#         else:                                 material.texture = open_image    (image_filename)
				
#     return material

	cdef _Material _get_material_4_cal3d(self, image_filename, float diffuse_r, float diffuse_g, float diffuse_b, float diffuse_a, float specular_r, float specular_g, float specular_b, float specular_a, float shininess):
		material_name = os.path.basename(image_filename)
		material_name = material_name[:material_name.find(".")]
		if material_name in Material.availables(): return Material.get(material_name)
		else: return self._create_material_4_cal3d(image_filename, diffuse_r, diffuse_g, diffuse_b, diffuse_a, specular_r, specular_g, specular_b, specular_a, shininess)

		#try:
		#	return Material.get(material_name) # Check for a Soya material with the same name
		#except ValueError: # Not a Soya material
		#	return self._create_material_4_cal3d(image_filename, diffuse_r, diffuse_g, diffuse_b, diffuse_a, specular_r, specular_g, specular_b, specular_a, shininess)
		
	cdef _Material _create_material_4_cal3d(self, image_filename, float diffuse_r, float diffuse_g, float diffuse_b, float diffuse_a, float specular_r, float specular_g, float specular_b, float specular_a, float shininess):
		material_name = "__cal3dmaterial_texture_%s_diffuse_%s_%s_%s_%s_specular_%s_%s_%s_%s_shininess_%s__" % (image_filename, diffuse_r , diffuse_g , diffuse_b , diffuse_a, specular_r, specular_g, specular_b, specular_a, shininess)
		if material_name in Material.availables(): return Material.get(material_name)
		
		#try:
		#	return Material.get(material_name) # Check for an already created material with the same name
		#except ValueError: # Not a Soya material
		#	pass
		
		cdef _Material material
		material = Material()
		material.filename  = material_name
		material.diffuse   = (diffuse_r , diffuse_g , diffuse_b , diffuse_a )
		material.specular  = (specular_r, specular_g, specular_b, specular_a)
		material.shininess = shininess
		
		if image_filename != "":
			import soya
			for path in soya.path:
				file = os.path.join(path, Image.DIRNAME, os.path.basename(image_filename))
				if os.path.exists(file):
					if   image_filename.endswith(".raw"): material.texture = load_raw_image(file)
					else:                                 material.texture = open_image    (file)
					break
			else:  self._set_texture_from_model(material, image_filename)
			
		return material

	cdef void _set_texture_from_model(self, _Material material, image_filename):
		#print "WARNING: Using image that is not in {soya.path}/images : %s !" % image_filename
		image_filename = os.path.join(os.path.dirname(self._full_filename), image_filename)
		if   image_filename.endswith(".raw"): material.texture = load_raw_image(image_filename)
		else:                                 material.texture = open_image    (image_filename)
		

	cdef int _shadow(self, CoordSyst coordsyst, _Light light):
		if not(self._option & CAL3D_SHADOW): return 0
		
		cdef _Cal3dSubMesh              submesh
		cdef _Body                    body
		cdef _AnimatedModelData data
		cdef GLfloat*                   ptrf, *ptrn, *plane
		cdef int                        i, r
		
		body = coordsyst
		data   = body._data
		if data._face_plane_ok <= 0: data._build_face_planes()
		
		ptrf   = data._coords
		ptrn   = data._vnormals
		plane  = data._face_planes
		i      = 0
		r      = 0
		
		for submesh in self._submeshes:
			if data._attached_meshes[submesh._mesh]:
				if self._shadow2(submesh, body, light, ptrf, ptrn, plane): r = 1
			ptrf  = ptrf  + submesh._nb_vertices * 3
			ptrn  = ptrn  + submesh._nb_vertices * 3
			plane = plane + submesh._nb_faces    * 4
			i = i + 1
			
		return r
			
	cdef int _shadow2(self, _Cal3dSubMesh submesh, _Body body, _Light light, float* coords, float* vnormals, float* plane):
		if not (submesh._option & CAL3D_NEIGHBORS): return 0 # Not yet initialized ???
		
		global cal3d_facesides_array
		
		cdef Frustum*     frustum
		cdef int          neighbor_face
		cdef float*       coord_ptr
		cdef double*      coord_ptrd
#    cdef float        fnormal[4]
		cdef float        coord[4]
		cdef float        cone[9]
		cdef float        b
		cdef int          i, j, k, p1, p2, nb_inter, nb_segment
		cdef int*         facesides
		facesides = cal3d_facesides_array
		
		cdef Chunk*       chunk, *chunk2
		cdef float        fp1[3], fp2[3], inter1[3], inter2[3], face_data[15]
		#cdef float        plane[4]
		cdef float        v1[3], v2[3]
		cdef int          nb_points[3]
		
		b = renderer.current_camera._back
		
		# Tag all faces front or back, for the given light
		
		light._cast_into(body)
		if light._w == 0.0: # Directional light
			cone_from_sphere_and_vector(cone, self._sphere, light._data, b)
			for i from 0 <= i < submesh._nb_faces:
				#face_normal(fnormal, coords + 3 * submesh._faces[3 * i], coords + 3 * submesh._faces[3 * i + 1], coords + 3 * submesh._faces[3 * i + 2])
				if vector_dot_product(light._data, plane + 4 * i) >= 0.0: facesides[i] = FACE_LIGHT_BACK
				else:                                                     facesides[i] = FACE_LIGHT_FRONT
				
		else:
			if cone_from_sphere_and_origin(cone, self._sphere, light._data, b) == 0: return 0
			for i from 0 <= i < submesh._nb_faces:
				#face_plane(fnormal, coords + 3 * submesh._faces[3 * i], coords + 3 * submesh._faces[3 * i + 1], coords + 3 * submesh._faces[3 * i + 2])
				if light._data[0] * plane[0] + light._data[1] * plane[1] + light._data[2] * plane[2] + plane[3] > 0.0:
					facesides[i] = FACE_LIGHT_FRONT
				else:
					facesides[i] = FACE_LIGHT_BACK
				plane = plane + 4
				
		# draw shadow body 1rst step
		glStencilFunc(GL_ALWAYS, 1, 0xFFFFFFFF)
		glFrontFace  (GL_CW)

		
		glStencilOp  (GL_KEEP, GL_KEEP, GL_INCR)
		glLoadMatrixf(body._render_matrix)
		glNewList    (SHADOW_DISPLAY_LIST, GL_COMPILE_AND_EXECUTE)
		
		# test if camera is inside the shadow
		frustum = renderer._frustum(body)
		coord[0] = 0.5 * (frustum.points[0] + frustum.points[6])
		coord[1] = 0.5 * (frustum.points[1] + frustum.points[7])
		coord[2] = 0.5 * (frustum.points[2] + frustum.points[8])
		coord[3] = point_distance_to(coord, frustum.points)
		if sphere_is_in_cone(coord, cone):
			# camera is inside the shadow => special case 
			# we must draw the intersection of the shadow body with the camera front plane
			# by chance we already have functions to do such thing in the watercube ;)
			
			plane[0], plane[1], plane[2], plane[3] = 0.0, 0.0, -1.0, -0.1 - renderer.current_camera._front
			
			chunk    = get_chunk()
			chunk2   = get_chunk()
			nb_inter = nb_segment = 0
			
			# find edges and draw shadow body
			for i from 0 <= i < submesh._nb_faces:
				if facesides[i] == FACE_LIGHT_BACK:
					# test if neighbors are front
					for k from 0 <= k < 3:
						neighbor_face = submesh._face_neighbors[3 * i + k]
						
						#if (neighbor_face != -1) and (facesides[neighbor_face] == FACE_LIGHT_FRONT):
						if (neighbor_face == -1) or (facesides[neighbor_face] == FACE_LIGHT_FRONT):
							
							if facesides[i] == FACE_LIGHT_BACK:
								p1 = k 
								if k < 2: p2 = k + 1
								else:     p2 = 0
							else: # Trace in reverse order
								if k < 2: p1 = k + 1
								else:     p1 = 0
								p2 = k
								
							nb_segment = nb_segment + 1
							chunk_add(chunk, coords + 3 * submesh._faces[3 * i + p1], 3 * sizeof(float))
							chunk_add(chunk, coords + 3 * submesh._faces[3 * i + p2], 3 * sizeof(float))
							chunk_add_int(chunk, -1)
							
			# Joins the segments
			joined = {}
			for i from 0 <= i < nb_segment:
				for j from 0 <= j < nb_segment:
					if i == j: continue
					if joined.has_key(j): continue
					
					if memcmp(chunk.content + i * (6 * sizeof(float) + sizeof(int)) + 3 * sizeof(float), chunk.content + j * (6 * sizeof(float) + sizeof(int)), 3 * sizeof(float)) == 0:
						(<int*> (chunk.content + (i * (6 * sizeof(float) + sizeof(int)) + 6 * sizeof(float))))[0] = j
						joined[j] = 1
						break
				else:
					print "* Soya * warning : drawing shadow for non-closed model (can't join segments)!"
					
			glLoadIdentity()
			i = 0
			for k from 0 <= k < nb_segment:
				if i == -1: break # error, was not able to join segments
				coord_ptr = <float*> (chunk.content + i * (6 * sizeof(float) + sizeof(int)))
				
				i = (<int*> (chunk.content + (i * (6 * sizeof(float) + sizeof(int)) + 6 * sizeof(float))))[0]
				
				memcpy(&fp1[0], coord_ptr    , 3 * sizeof(float))
				memcpy(&fp2[0], coord_ptr + 3, 3 * sizeof(float))
				
				if light._w == 0.0: # Directional light
					memcpy(&v1[0], &light._data[0], 3 * sizeof(float))
					memcpy(&v2[0], &light._data[0], 3 * sizeof(float))
				else:
					v1[0] = fp1[0] - light._data[0]
					v1[1] = fp1[1] - light._data[1]
					v1[2] = fp1[2] - light._data[2]
					vector_normalize(v1)
					
					v2[0] = fp2[0] - light._data[0]
					v2[1] = fp2[1] - light._data[1]
					v2[2] = fp2[2] - light._data[2]
					vector_normalize(v2)
					
					
				point_by_matrix(fp1, body._root_matrix())
				point_by_matrix(fp1, renderer.current_camera._inverted_root_matrix())
				
				point_by_matrix(fp2, body._root_matrix())
				point_by_matrix(fp2, renderer.current_camera._inverted_root_matrix())
				
				vector_by_matrix(v1, body._root_matrix())
				vector_by_matrix(v1, renderer.current_camera._inverted_root_matrix())
				
				vector_by_matrix(v2, body._root_matrix())
				vector_by_matrix(v2, renderer.current_camera._inverted_root_matrix())
				
				
				segment_projection_intersect_plane(fp1, v1, fp2, v2, b, plane, inter1, inter2, face_data, nb_points)
				
				glBegin(GL_POLYGON)
				for j from 0 <= j < nb_points[0]:
					glVertex3fv(&face_data[0] + j * 3)
				glEnd()
				
				if nb_points[1]:
					chunk_add_double(chunk2, <double> (inter1[0]))
					chunk_add_double(chunk2, <double> (inter1[1]))
					chunk_add_double(chunk2, <double> (inter1[2]))
					nb_inter = nb_inter + 1
					
				if nb_points[2]:
					chunk_add_double(chunk2, <double> (inter2[0]))
					chunk_add_double(chunk2, <double> (inter2[1]))
					chunk_add_double(chunk2, <double> (inter2[2]))
					nb_inter = nb_inter + 1
				
			glLoadMatrixf(body._render_matrix)
			
			glEndList()
			
			# draw shadow body 3rd step
			glDisable(GL_CULL_FACE)
			glLoadIdentity()
			gluTessBeginPolygon(SHADOW_TESS, NULL)
			gluTessBeginContour(SHADOW_TESS)
			for i from 0 <= i < nb_inter:
				gluTessVertex(SHADOW_TESS, (<double*> chunk2.content) + i * 3, (<double*> chunk2.content) + i * 3)
			gluTessEndContour(SHADOW_TESS)
			gluTessEndPolygon(SHADOW_TESS)
			glLoadMatrixf(body._render_matrix)
			glEnable(GL_CULL_FACE)
			
			
			# draw shadow body 2nd step
			glFrontFace(GL_CCW)
			glStencilOp(GL_KEEP, GL_KEEP, GL_DECR)
			glCallList (SHADOW_DISPLAY_LIST)
			
			# Cleaning
			# Free the double[3] created by model_shadow_tess_combine
			i = SHADOW_TESS_CHUNK.nb
			SHADOW_TESS_CHUNK.nb = 0
			while SHADOW_TESS_CHUNK.nb < i: free(chunk_get_ptr(SHADOW_TESS_CHUNK))
			
			SHADOW_TESS_CHUNK.nb = 0 # reset the chunk
			
			drop_chunk(chunk)
			drop_chunk(chunk2)
			
			
		else:
			# find edges and draw shadow body
			glBegin(GL_QUADS)
			for i from 0 <= i < submesh._nb_faces:
				if (self._option & CAL3D_DOUBLE_SIDED) or (facesides[i] == FACE_LIGHT_BACK):
					for k from 0 <= k < 3:
						neighbor_face = submesh._face_neighbors[3 * i + k]
						
						#if (neighbor_face != -1) and (facesides[neighbor_face] == FACE_LIGHT_FRONT):
						#if (neighbor_face == -1) or (facesides[neighbor_face] == FACE_LIGHT_FRONT):
						if (neighbor_face == -1) or (facesides[neighbor_face] != facesides[i]):
							
							if facesides[i] == FACE_LIGHT_BACK:
								p1 = k 
								if k < 2: p2 = k + 1
								else:     p2 = 0
							else: # Trace in reverse order
								if k < 2: p1 = k + 1
								else:     p1 = 0
								p2 = k
							
							coord_ptr = coords + 3 * submesh._faces[3 * i + p1]
							glVertex3fv(coord_ptr)
							
							# push coord far away
							if light._w == 0.0: # Directional light
								glVertex3f(coord_ptr[0] + b * light._data[0], coord_ptr[1] + b * light._data[1], coord_ptr[2] + b * light._data[2])
							else:
								coord[0] = coord_ptr[0] - light._data[0]
								coord[1] = coord_ptr[1] - light._data[1]
								coord[2] = coord_ptr[2] - light._data[2]
								vector_normalize(coord)
								glVertex3f(coord_ptr[0] + b * coord[0], coord_ptr[1] + b * coord[1], coord_ptr[2] + b * coord[2])
								
							coord_ptr = coords + 3 * submesh._faces[3 * i + p2]
							
							# push coord far away
							if light._w == 0.0: # Directional light
								glVertex3f(coord_ptr[0] + b * light._data[0], coord_ptr[1] + b * light._data[1], coord_ptr[2] + b * light._data[2])
							else:
								coord[0] = coord_ptr[0] - light._data[0]
								coord[1] = coord_ptr[1] - light._data[1]
								coord[2] = coord_ptr[2] - light._data[2]
								vector_normalize(coord)
								glVertex3f(coord_ptr[0] + b * coord[0], coord_ptr[1] + b * coord[1], coord_ptr[2] + b * coord[2])
								
							glVertex3fv(coord_ptr)
							
							
			glEnd    ()
			glEndList()
			
			# draw shadow body 2nd step
			glFrontFace(GL_CCW)
			glStencilOp(GL_KEEP, GL_KEEP, GL_DECR)
			glCallList (SHADOW_DISPLAY_LIST)


		return 1
	
	
	
	
	cdef void _raypick(self, RaypickData data, CoordSyst raypickable):
		cdef _Body                    body
		cdef _AnimatedModelData da
		body = <_Body> raypickable
		da     = body._data
		
		if da._vertex_ok     <= 0: da._build_vertices   (1)
		if da._face_plane_ok <= 0: da._build_face_planes()
		
		cdef float*        raydata, *ptrf, *plane
		cdef float         z, root_z
		cdef int           i, j, r
		cdef _Cal3dSubMesh submesh
		
		# XXX take into account the ray length ? e.g., if ray_length == 1.0, sphere_radius = 1.0 and (ray_origin >> self).length() > 2.0, no collision can occur
		raydata = body._raypick_data(data)
		if (self._sphere[3] > 0.0) and (sphere_raypick(raydata, self._sphere) == 0): return
		
		i = 0
		plane  = da._face_planes
		ptrf   = da._coords
		for submesh in self._submeshes:
			if da._attached_meshes[submesh._mesh]:
				for j from 0 <= j < submesh._nb_faces:
					r = triangle_raypick(raydata, ptrf + 3 * submesh._faces[3 * j], ptrf + 3 * submesh._faces[3 * j + 1], ptrf + 3 * submesh._faces[3 * j + 2], plane + 4 * j, data.option, &z)
					
					if r != 0:
						root_z = body._distance_out(z)
						if (data.result_coordsyst is None) or (fabs(root_z) < fabs(data.root_result)):
							data.result      = z
							data.root_result = root_z
							data.result_coordsyst = body
							if   r == RAYPICK_DIRECT: memcpy(&data.normal[0], plane + 4 * j, 3 * sizeof(float))
							elif r == RAYPICK_INDIRECT:
								if self._option & CAL3D_DOUBLE_SIDED:
									data.normal[0] = -(plane + 4 * j)[0]
									data.normal[1] = -(plane + 4 * j)[1]
									data.normal[2] = -(plane + 4 * j)[2]
								else: memcpy(&data.normal[0], plane + 4 * j, 3 * sizeof(float))
							vector_normalize(data.normal)
							
			i = i + 1
			ptrf  = ptrf  + submesh._nb_vertices * 3
			plane = plane + submesh._nb_faces    * 4
	
	cdef int _raypick_b(self, RaypickData data, CoordSyst raypickable):
		cdef float*                     raydata, *ptrf, *plane
		cdef float                      z
		cdef int                        i, j
		cdef _Cal3dSubMesh              submesh
		cdef _Body                    body
		cdef _AnimatedModelData da
		body = <_Body> raypickable
		da     = body._data
		
		if da._vertex_ok     <= 0: da._build_vertices   (1)
		if da._face_plane_ok <= 0: da._build_face_planes()
		
		# XXX take into account the ray length ? e.g., if ray_length == 1.0, sphere_radius = 1.0 and (ray_origin >> self).length() > 2.0, no collision can occur
		raydata = body._raypick_data(data)
		if (self._sphere[3] > 0.0) and (sphere_raypick(raydata, self._sphere) == 0): return 0
		
		i = 0
		plane  = da._face_planes
		ptrf   = da._coords
		for submesh in self._submeshes:
			if da._attached_meshes[submesh._mesh]:
				for j from 0 <= j < submesh._nb_faces:
					if triangle_raypick(raydata, ptrf + 3 * submesh._faces[3 * j], ptrf + 3 * submesh._faces[3 * j + 1], ptrf + 3 * submesh._faces[3 * j + 2], plane + 4 * j, data.option, &z) != 0: return 1
					
		return 0
	
	cdef void _collect_raypickables(self, Chunk* items, float* rsphere, float* sphere, CoordSyst parent):
		if (self._sphere[3] < 0.0) or (sphere_distance_sphere(sphere, self._sphere) < 0.0):
			chunk_add_ptr(items, <void*> parent)





	
cdef class _AnimatedModelData(_ModelData):
	#cdef _Body          _body
	#cdef _AnimatedModel _model
	#cdef                _attached_meshes, _attached_coordsysts
	#cdef CalModel*      _cal_model
	#cdef float          _delta_time
	#cdef float*         _face_planes, *_coords, *_vnormals
	#cdef int            _face_plane_ok, _vertex_ok
	
	def __init__(self, _Body body, _AnimatedModel model, attached_meshes = None):
		self._body  = body
		self._model = model
		
		self._cal_model = CalModel_New(model._core_model)
		if self._cal_model == NULL:
			print "error CalModel_Create", CalError_GetLastErrorDescription()
			raise RuntimeError("CalModel_Create failed: %s" % CalError_GetLastErrorDescription())
		
		self._attached_meshes     = []
		self._attached_coordsysts = []
		nb = CalCoreModel_GetCoreMeshCount(model._core_model)
		for i from 0 <= i < nb: self._attached_meshes.append(0)
		if not attached_meshes is None: self._attach(attached_meshes)
		else:                           self._attach_all()
		
	def __dealloc__(self):
		CalModel_Delete (self._cal_model)
		if self._coords      != NULL: free(self._coords)
		if self._vnormals    != NULL: free(self._vnormals)
		if self._face_planes != NULL: free(self._face_planes)
		
	cdef __getcstate__(self):
		return (self._body, self._model, self._attached_meshes, self._attached_coordsysts)
	
	cdef void __setcstate__(self, cstate):
		print "SETCSTATE", cstate
		self._body, self._model, self._attached_meshes, self._attached_coordsysts = cstate
		
		self._cal_model = CalModel_New(self._model._core_model)
		if self._cal_model == NULL:
			print "error CalModel_Create", CalError_GetLastErrorDescription()
			raise RuntimeError("CalModel_Create failed: %s" % CalError_GetLastErrorDescription())
		
		for i from 0 <= i < len(self._attached_meshes):
			if self._attached_meshes[i] == 1:
				if CalModel_AttachMesh(self._cal_model, i) == 0:
					print "error CalModel_AttachMesh", CalError_GetLastErrorDescription()
					raise RuntimeError("CalModel_AttachMesh failed: %s" % CalError_GetLastErrorDescription())
		self._build_submeshes()
		
	cdef void _build_submeshes(self):
		if not(self._model._option & CAL3D_INITED): self._model._build_submeshes()
		
		if self._coords  != NULL: free(self._coords)
		if self._vnormals != NULL: free(self._vnormals)
		if self._face_planes    != NULL: free(self._face_planes)
		
		self._coords      = <GLfloat*> malloc(self._model._nb_vertices * 3 * sizeof(GLfloat))
		self._vnormals    = <GLfloat*> malloc(self._model._nb_vertices * 3 * sizeof(GLfloat))
		self._face_planes = <GLfloat*> malloc(self._model._nb_faces    * 4 * sizeof(GLfloat))
		
	cdef void _build_face_planes(self):
		cdef float*        ptrf, *plane
		cdef int           i, j
		cdef _Cal3dSubMesh submesh
		
		if self._vertex_ok <= 0: self._build_vertices(1)
		
		i     = 0
		plane = self._face_planes
		ptrf  = self._coords
		for submesh in self._model._submeshes:
			if self._attached_meshes[submesh._mesh]:
				for j from 0 <= j < submesh._nb_faces:
					face_plane(plane + 4 * j, ptrf + 3 * submesh._faces[3 * j], ptrf + 3 * submesh._faces[3 * j + 1], ptrf + 3 * submesh._faces[3 * j + 2])
					# XXX normalize here (with plane_vector_normalize) or keep normalization in _raypick ?
					
			i = i + 1
			ptrf  = ptrf  + submesh._nb_vertices * 3
			plane = plane + submesh._nb_faces    * 4
			
		self._face_plane_ok = 1
		
	cdef void _attach(self, mesh_names):
		cdef int i
		for mesh_name in mesh_names:
			i = self._model.meshes[mesh_name]
			if self._attached_meshes[i] == 0:
				if CalModel_AttachMesh(self._cal_model, i) == 0:
					print "error CalModel_AttachMesh", CalError_GetLastErrorDescription()
					raise RuntimeError("CalModel_AttachMesh failed: %s" % CalError_GetLastErrorDescription())

				self._attached_meshes[i] = 1
		self._build_submeshes()
		
	cdef void _detach(self, mesh_names):
		cdef int i
		for mesh_name in mesh_names:
			i = self._model.meshes[mesh_name]
			if self._attached_meshes[i] == 1:
				if CalModel_DetachMesh(self._cal_model, i) == 0:
					print "error CalModel_DetachMesh", CalError_GetLastErrorDescription()
					raise RuntimeError("CalModel_DetachMesh failed: %s" % CalError_GetLastErrorDescription())
				self._attached_meshes[i] = 0
		self._build_submeshes()
			
	cdef void _attach_all(self):
		cdef int i
		for i from 0 <= i < len(self._attached_meshes):
			if self._attached_meshes[i] == 0:
				if CalModel_AttachMesh(self._cal_model, i) == 0:
					print "error CalModel_AttachMesh", CalError_GetLastErrorDescription()
					raise RuntimeError("CalModel_AttachMesh failed: %s" % CalError_GetLastErrorDescription())
				self._attached_meshes[i] = 1
		self._build_submeshes()
		
	cdef int _is_attached(self, mesh_name):
		return self._attached_meshes[self._model.meshes[mesh_name]]
		
	cdef void _attach_to_bone(self, CoordSyst coordsyst, bone_name):
		cdef int i
		i = CalCoreSkeleton_GetCoreBoneId(CalCoreModel_GetCoreSkeleton(self._model._core_model), bone_name)
		if i == -1: raise ValueError("No bone named %s !" % bone_name)
		self._attached_coordsysts.append((coordsyst, i, 1))
		
	cdef void _detach_from_bone(self, CoordSyst coordsyst):
		cdef int i
		for i from 0 <= i < len(self._attached_coordsysts):
			if self._attached_coordsysts[i][0] is coordsyst:
				del self._attached_coordsysts[i]
				break


	cdef _get_attached_meshes    (self): return self._attached_meshes
	cdef _get_attached_coordsysts(self): return self._attached_coordsysts


	cdef void _animate_blend_cycle(self, animation_name, float weight, float fade_in):
		CalMixer_BlendCycle(CalModel_GetMixer(self._cal_model), self._model._animations[animation_name], weight, fade_in)
		
	cdef void _animate_clear_cycle(self, animation_name, float fade_out):
		CalMixer_ClearCycle(CalModel_GetMixer(self._cal_model), self._model._animations[animation_name], fade_out)
		
	cdef void _animate_execute_action(self, animation_name, float fade_in, float fade_out):
		CalMixer_ExecuteAction(CalModel_GetMixer(self._cal_model), self._model._animations[animation_name], fade_in, fade_out)
		
	cdef void _animate_reset(self):
		# Calling CalMixer_UpdateAnimation with 0.0 has a resetting effect.
		# This is an undocumented feature i've discovered by reading sources.
		CalMixer_UpdateAnimation(CalModel_GetMixer(self._cal_model), 0.0)
		
		# Older hacks
		#CalModel_ResetMixer(self._cal_model)
		
		
	cdef void _set_lod_level(self, float lod_level):
		CalModel_SetLodLevel(self._cal_model, lod_level)
		
	cdef void _begin_round(self):
		self._vertex_ok     = self._vertex_ok     - 1
		self._face_plane_ok = self._face_plane_ok - 1
		if self._vertex_ok <= 0: self._build_vertices(0)
		
	cdef void _advance_time(self, float proportion):
		import soya # XXX optimizable! probably slow!
		self._delta_time = self._delta_time + proportion * soya.MAIN_LOOP.round_duration
		
	cdef void _build_vertices(self, int vertices):
		cdef int       bone_id, option
		cdef CalBone*  bone
		cdef CoordSyst csyst
		cdef float*    trans, *quat

		CalModel_Update(self._cal_model, self._delta_time)
		self._delta_time = 0.0
		
		for csyst, bone_id, option in self._attached_coordsysts: # Updates coordsysts attached to a bone
			bone = CalSkeleton_GetBone(CalModel_GetSkeleton(self._cal_model), bone_id)
			quat = CalQuaternion_Get(CalBone_GetRotationAbsolute(bone))
			quat[3] = -quat[3] # Cal3D use indirect frame or what ???
			matrix_from_quaternion(csyst._matrix, quat)
			trans = CalVector_Get(CalBone_GetTranslationAbsolute(bone))
			csyst._matrix[12] = <GLfloat> trans[0]
			csyst._matrix[13] = <GLfloat> trans[1]
			csyst._matrix[14] = <GLfloat> trans[2]
			csyst._invalidate()
			
		if vertices == 1:
			self._model._build_vertices(self)
			self._vertex_ok = 1
	
	cdef void _batch               (self, _Body body): self._model._batch(body)
	cdef void _render              (self, _Body body): self._model._render(body)
	cdef int  _shadow              (self, CoordSyst coord_syst, _Light light): return self._model._shadow(coord_syst, light)
	cdef void _get_box             (self, float* box, float* matrix): self._model._get_box(box, matrix)
	cdef void _raypick             (self, RaypickData raypick_data, CoordSyst raypickable):        self._model._raypick  (raypick_data, raypickable)
	cdef int  _raypick_b           (self, RaypickData raypick_data, CoordSyst raypickable): return self._model._raypick_b(raypick_data, raypickable)
	cdef void _collect_raypickables(self, Chunk* items, float* rsphere, float* sphere, CoordSyst parent): self._model._collect_raypickables(items, rsphere, sphere, parent)
