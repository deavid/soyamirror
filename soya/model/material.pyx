# -*- indent-tabs-mode: t -*-

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

# Material and Pack

cdef class _Material(_CObj):
	#cdef int     _option, _nb_packs
	#cdef _Image  _texture
	#cdef readonly GLuint _id # the OpenGL texture name
	#cdef public float shininess
	#cdef GLfloat _diffuse[4], _specular[4], _emissive[4]
	#cdef public  _filename
	
	#cdef Pack**  _packs # the list of packs which are based on this material
	
	def __init__(self, _Image texture = None):
		"""Material(Image texture) -> Material

Creates a new Material with texture TEXTURE."""
		self.shininess   = 128.0
		self._diffuse[0] = self._diffuse[1] = self._diffuse[2] = self._diffuse[3] = 1.0
		self._filename   = ""
		if not texture is None:
			if texture.check_for_gl() == 0: raise ValueError("Image dimensions must be power of 2 (dimensions are %s x %s)" % (texture.width, texture.height))
			self._texture = texture
			self._compute_alpha()
			self._init_texture()
			
	def __dealloc__(self):
		if self._id != 0: glDeleteTextures(1, &(self._id))
		
	cdef __getcstate__(self):
		#return struct.pack("<ifffffffffffff", self._option, self.shininess, self._diffuse[0], self._diffuse[1], self._diffuse[2], self._diffuse[3], self._specular[0], self._specular[1], self._specular[2], self._specular[3], self._emissive[0], self._emissive[1], self._emissive[2], self._emissive[3]), self._filename, self._texture
		cdef Chunk* chunk
		chunk = get_chunk()
		chunk_add_int_endian_safe   (chunk, self._option)
		chunk_add_float_endian_safe (chunk, self.shininess)
		chunk_add_floats_endian_safe(chunk, self._diffuse , 4)
		chunk_add_floats_endian_safe(chunk, self._specular, 4)
		chunk_add_floats_endian_safe(chunk, self._emissive, 4)
		return drop_chunk_to_string(chunk), self._filename, self._texture
	
	cdef void __setcstate__(self, cstate):
		#self._option, self.shininess, self._diffuse[0], self._diffuse[1], self._diffuse[2], self._diffuse[3], self._specular[0], self._specular[1], self._specular[2], self._specular[3], self._emissive[0], self._emissive[1], self._emissive[2], self._emissive[3] = struct.unpack("<ifffffffffffff", cstate[0])
		#self._filename = cstate[1]
		#self._texture  = cstate[2]
		cdef Chunk* chunk
		cstate2, self._filename, self._texture = cstate
		chunk = string_to_chunk(cstate2)
		chunk_get_int_endian_safe  (chunk, &self._option)
		chunk_get_float_endian_safe(chunk, &self.shininess)
		chunk_get_floats_endian_safe(chunk, self._diffuse , 4)
		chunk_get_floats_endian_safe(chunk, self._specular, 4)
		chunk_get_floats_endian_safe(chunk, self._emissive, 4)
		drop_chunk(chunk)
		
#  def __deepcopy__(self, memo):
#    """Materials are really copied only if they are ."""
#    if memo: return _Material.__deepcopy__(self, memo)
#    else:    return self
	
	cdef Pack* _pack(self, int option):
		"""_Material._pack(int option) -> Pack*

Returns a pack corresponding to this material and the given OPTION flags.
A pack is a couple (material, drawing option) (see below).
A new pack is created if needed, but calling this method with the same arguments will
return the same pack.
You shouldn't free the returned pack."""
		cdef Pack* pack
		cdef int   opt, i

		opt = option & PACK_OPTIONS
		# look for existing packs
		for i from 0 <= i < self._nb_packs: # Don't worth a dict i think (in practice, self._nb_packs <= 3)
			pack = self._packs[i]
			if pack.option == opt: return pack
		# create a new pack
		pack = <Pack*> malloc(sizeof(Pack))
		pack.material_id   = id(self)
		pack.batched_faces = get_clist()
		pack.option        = opt
		pack.secondpass    = pack.alpha = NULL
		self._packs  = <Pack**> realloc(self._packs, (self._nb_packs + 1) * sizeof(Pack*))
		self._packs[self._nb_packs] = pack
		self._nb_packs = self._nb_packs + 1
		return pack
	
	cdef void _init_texture(self):
		"""_Material._init_texture()

Inits the texture, by creating an OpenGL texture name, and setting the different options
corresponding to the material attributes (texture, clamp) and the quality level (mipmap)."""
		cdef int border
		
		if renderer.engine_option & INITED:
			if self._texture is None:
				if self._id != 0:
					glDeleteTextures(1, &(self._id))
					self._id = 0
					
			else:
				if self._id == 0: glGenTextures(1, &(self._id))
				glPushAttrib(GL_TEXTURE_BIT)
				glBindTexture(GL_TEXTURE_2D, self._id)
				if self._option & MATERIAL_ENVIRONMENT_MAPPING:
					glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
					
				if self._option & MATERIAL_CLAMP:
					glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
					glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
				else:
					glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
					glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
					
				if self._option & MATERIAL_BORDER: border = 1
				else:                              border = 0
				
				if (renderer.engine_option & USE_MIPMAP) and (self._option & MATERIAL_MIPMAP):
					glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
					glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
					self._build_2D_mipmaps(border)
				else:
					if (self._option & MATERIAL_CLAMP) and (border == 0):
						#glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
						glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
						glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
					else:
						glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
						glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
					
					glTexImage2D(GL_TEXTURE_2D, 0, self._texture.internal_format(),
											 self._texture.width, self._texture.height, border,
											 self._texture.typ(), GL_UNSIGNED_BYTE,
											 self._texture._pixels,
											 )
				glPopAttrib()
				#renderer.current_material = None # The material
				
	cdef void _build_2D_mipmaps(self, int border):
		"""_Material._build_2D_mipmaps(int border)

Creates the mipmap textures, and set them up in this material's OpenGL texture name."""
		
		#this code was originally adapted from Mesa :)
		cdef GLuint w, h, level
		cdef GLubyte* pixels
		cdef GLubyte* new_pixels
		cdef int typ, internal_format
		w               = self._texture.width  - 2 * border # must be a power of 2
		h               = self._texture.height - 2 * border # must be a power of 2
		level           = 0
		pixels          = self._texture._pixels
		typ             = self._texture.typ()
		internal_format = self._texture.internal_format()
		
		while 1:
			glTexImage2D(GL_TEXTURE_2D, level, internal_format, w + 2 * border, h + 2 * border, border, typ, GL_UNSIGNED_BYTE, pixels)
			if (w == 1) and (h == 1): break
			
			new_pixels = pixels_scale_down_2(self._texture.nb_color, &w, &h, border, pixels)
			if pixels != self._texture._pixels: free(pixels)
			pixels = new_pixels
			
			level = level + 1
			
		if pixels != self._texture._pixels: free(pixels)
		
	cdef void _compute_alpha(self):
		"""_Material._compute_alpha()

Computes wether this material use alpha blending, or mask-based transparency,
and set the corresponding flags (MATERIAL_ALPHA, MATERIAL_MASK)
in the _option attribute."""
		cdef int i
		self._option = self._option & ~(MATERIAL_ALPHA | MATERIAL_MASK)
		if   (self._option & MATERIAL_ADDITIVE_BLENDING) or (self._diffuse[3] < 1.0 - EPSILON):
			self._option = self._option | MATERIAL_ALPHA
			
		elif (not self._texture is None) and (self._texture.nb_color == 4):
			for i from 0 <= i < self._texture.width * self._texture.height:
				if (self._texture._pixels[4 * i + 3] != 0) and (self._texture._pixels[4 * i + 3] != 255):
					self._option = self._option | MATERIAL_ALPHA
					break
			else: self._option = self._option | MATERIAL_MASK
			
	cdef void _activate(self):
		"""_Material._activate()

Set this material as the current activated one. The material properties will apply to
any further OpenGL drawing.
The previously active material is inactivated first. A single material can be active
at the same time ; you can get it with renderer.current_material."""
		# XXX display list ?
		if not self is renderer.current_material:
			renderer.current_material._inactivate()
			renderer.current_material = self
			if self._texture is None: glDisable(GL_TEXTURE_2D)
			else:
				if self._id == 0: self._init_texture()
				glBindTexture(GL_TEXTURE_2D, self._id)
				
			if (self._option & MATERIAL_SEPARATE_SPECULAR) and (quality != QUALITY_LOW): glLightModeli(GL_LIGHT_MODEL_COLOR_CONTROL, GL_SEPARATE_SPECULAR_COLOR)
			
			glMaterialf (GL_FRONT_AND_BACK, GL_SHININESS, self.shininess)
			glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR,  self._specular)
			if self._option & MATERIAL_MASK:
				glDisable  (GL_ALPHA_TEST)
				glAlphaFunc(GL_NOTEQUAL, 0.0)
				glEnable   (GL_ALPHA_TEST)
				glDepthMask(GL_TRUE)
			if self._option & MATERIAL_ADDITIVE_BLENDING:
				glBlendFunc(GL_SRC_ALPHA, GL_ONE)
				# When using additive blending, the color is ADDED TO the preceeding one, thus the
				# fog has been already applied.
				glPushAttrib(GL_FOG_BIT)
				glDisable(GL_FOG)
			if self._option & MATERIAL_ENVIRONMENT_MAPPING:
				glEnable(GL_TEXTURE_GEN_S)
				glEnable(GL_TEXTURE_GEN_T)
				glTexGeni(GL_S, GL_TEXTURE_GEN_MODE, GL_SPHERE_MAP)
				glTexGeni(GL_T, GL_TEXTURE_GEN_MODE, GL_SPHERE_MAP)
				
				
		# these values may have change due to some vertices
		# we must set that because GL_COLOR_MATERIAL is enable : ie material diffuse color is in fact glColor...
		glColor4fv(self._diffuse)
		glMaterialfv(GL_FRONT_AND_BACK, GL_EMISSION, self._emissive)
		
		
	cdef void _inactivate(self):
		"""_Material._inactivate()

De-activates this material, and reset OpenGL to the "default" state, suitable for another
material activation.
Automatically called by _Material._activate()."""
		# XXX display list ?
		glBindTexture(GL_TEXTURE_2D, 0)
		if  self._texture is None: glEnable(GL_TEXTURE_2D)
		if  self._option & MATERIAL_MASK:
			glDisable(GL_ALPHA_TEST)
			if renderer.state == RENDERER_STATE_ALPHA: glDepthMask(GL_FALSE)
		if (self._option & MATERIAL_SEPARATE_SPECULAR) and (quality != QUALITY_LOW): glLightModeli(GL_LIGHT_MODEL_COLOR_CONTROL, GL_SINGLE_COLOR)
		if  self._option & MATERIAL_ADDITIVE_BLENDING:
			glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
			glPopAttrib() # GL_FOG_BIT
		if  self._option & MATERIAL_ENVIRONMENT_MAPPING:
			glDisable(GL_TEXTURE_GEN_S)
			glDisable(GL_TEXTURE_GEN_T)
			
	def activate(self):
		"""Material.activate()

Set this material as the current activated one. The material properties will apply to
any further OpenGL drawing.
The previously active material is inactivated first. A single material can be active
at the same time. This method is a Python wrapper for _Material._activate()."""
		self._activate()
		
	def inactivate(self):
		"""Material.inactivate()

"""
		renderer.current_material._inactivate()
		renderer.current_material = None
		
	def is_alpha(self):
		"""Returns true if this material use alpha blending (i.e. semi-transparency)."""
		return (self._option & MATERIAL_ALPHA) != 0
	
	def has_mask(self):
		"""Returns true if this material has a mask (i.e. all-or-nothing transparency)."""
		return (self._option & MATERIAL_MASK) != 0
	
	property separate_specular:
		def __get__(self):
			return (self._option & MATERIAL_SEPARATE_SPECULAR) != 0
		def __set__(self, int x):
			if x: self._option = self._option |  MATERIAL_SEPARATE_SPECULAR
			else: self._option = self._option & ~MATERIAL_SEPARATE_SPECULAR
	
	property clamp:
		def __get__(self):
			return (self._option & MATERIAL_CLAMP) != 0
		def __set__(self, int x):
			if x: self._option = self._option |  MATERIAL_CLAMP
			else: self._option = self._option & ~MATERIAL_CLAMP
			self._init_texture()
			
	property environment_mapping:
		def __get__(self):
			return (self._option & MATERIAL_ENVIRONMENT_MAPPING) != 0
		def __set__(self, int x):
			if x: self._option = self._option |  MATERIAL_ENVIRONMENT_MAPPING
			else: self._option = self._option & ~MATERIAL_ENVIRONMENT_MAPPING
			self._init_texture()
			
	property mip_map:
		def __get__(self):
			return (self._option & MATERIAL_MIPMAP) != 0
		def __set__(self, int x):
			if x: self._option = self._option |  MATERIAL_MIPMAP
			else: self._option = self._option & ~MATERIAL_MIPMAP
			self._init_texture()
			
	property additive_blending:
		def __get__(self):
			return (self._option & MATERIAL_ADDITIVE_BLENDING) != 0
		def __set__(self, int x):
			if x: self._option = self._option |  MATERIAL_ADDITIVE_BLENDING
			else: self._option = self._option & ~MATERIAL_ADDITIVE_BLENDING
			self._compute_alpha()
			
	property texture:
		def __get__(self):
			return self._texture
		def __set__(self, _Image image):
			cdef int check
			if not image is None:
				check = image.check_for_gl()
				if   check == 1: self._option = self._option & ~MATERIAL_BORDER
				elif check == 2: self._option = self._option |  MATERIAL_BORDER
				else: raise ValueError("Image dimensions must be power of 2 (dimensions are %s x %s)" % (image.width, image.height))
			self._texture = image
			self._compute_alpha()
			self._init_texture()
			
	property image:
		def __get__(self):
			"""DEPRECATED, alias for texture"""
			return self._texture
		
	property diffuse:
		def __get__(self):
			return self._diffuse[0], self._diffuse[1], self._diffuse[2], self._diffuse[3]
		def __set__(self, x):
			self._diffuse[0], self._diffuse[1], self._diffuse[2], self._diffuse[3] = x
			self._compute_alpha()
			
	property specular:
		def __get__(self):
			return self._specular[0], self._specular[1], self._specular[2], self._specular[3]
		def __set__(self, x):
			self._specular[0], self._specular[1], self._specular[2], self._specular[3] = x
			
	property emissive:
		def __get__(self):
			return self._emissive[0], self._emissive[1], self._emissive[2], self._emissive[3]
		def __set__(self, x):
			self._emissive[0], self._emissive[1], self._emissive[2], self._emissive[3] = x

	property opengl_id:
		def __get__(self):
			return self._id
		
	def __repr__(self): return "<Material %s>" % self._filename




cdef class _MainLoopingMaterial(_Material):
	def __init__(self, _Image texture = None):
		_Material.__init__(self, texture)
		MAIN_LOOP_ITEMS[self] = 1
		
	cdef void __setcstate__(self, cstate):
		_Material.__setcstate__(self, cstate)
		MAIN_LOOP_ITEMS[self] = 1
		
	def begin_round(self):
		"""_IdleingMaterial.begin_round()

Called by the MainLoop when a new round begins; default implementation does nothing."""
		pass
	
	def end_round(self):
		"""_IdleingMaterial.end_round()

Called by the MainLoop when a round is finished; default implementation does nothing."""
		pass
		
	def advance_time(self, float proportion):
		"""_IdleingMaterial.advance_time(proportion)

Called by the MainLoop when a piece of a round has occured; does nothing.
PROPORTION is the proportion of the current round's time that has passed (1.0 for an entire round)."""
		pass



cdef class _PythonMaterial(_Material):
	"""A Material class that can be extended and hacked in Python.
Just implement the following methods:
	init_texture()
	activated()
	inactivated()"""
	cdef void _init_texture(self):
		_Material._init_texture(self)
		self.init_texture()
		
	def init_texture(self):
		pass
	
	cdef void _activate(self):
		_Material._activate(self)
		self.activated()
		
	def activated(self):
		pass
	
	cdef void _inactivate(self):
		self.inactivated()
		_Material._inactivate(self)
		
	def inactivated(self):
		pass


cdef class _PythonMainLoopingMaterial(_MainLoopingMaterial):
	"""A Material class that can be extended and hacked in Python.
Just implement the following methods:
	init_texture()
	activated()
	inactivated()

In addition to PythonMaterial, PythonMainLoopingMaterial also has begin_round, advance_time and end_round method."""
	cdef void _init_texture(self):
		_Material._init_texture(self)
		self.init_texture()
		
	def init_texture(self):
		pass
	
	cdef void _activate(self):
		_Material._activate(self)
		self.activated()
		
	def activated(self):
		pass
	
	cdef void _inactivate(self):
		self.inactivated()
		_Material._inactivate(self)
		
	def inactivated(self):
		pass


# A pack is the combination of a material, drawing options (triangle/quad, alpha,
# double_sided, non_lit), and a renderer batching state (opaque, alpha or second_pass).
# Packs are used to sort the triangle / quad according to the material, the drawing
# options and the renderer batching state, in particular in complex object (terrain, tree).
#
# Attributes are:
#
#  - option: the drawing option flags (a combination of FACE_* constant).
#
#  - material_id: a pointer to the material python objet, stored as a integer
#    (can't put a python object in a c structure).
#
#  - alpha:  a pointer to another pack, with the same material and drawing options,
#    but using the alpha renderer batching state.
#
#  - secondpass: a pointer to another pack, with the same material and drawing options,
#    but using the second_pass renderer batching state.
#
#  - batched_faces: a linked list which is used to store data during the rendering process.

# cdef struct _Pack:
#   int       option
#   long      material_id
#   _Pack*    alpha
#   _Pack*    secondpass
#   CList* batched_faces
# ctypedef _Pack Pack



cdef Pack* pack_get_alpha(Pack* pack):
	"""pack_get_alpha(Pack* pack) -> Pack*

Returns a pack with the same material and drawing options, but that uses the alpha
renderer batching state (for drawing alpha triangle / quad).
If called twice with the same argument, the returned pack is the same, and it should
not be free'ed."""
	if pack.alpha == NULL: # create a new pack
		pack.alpha               = <Pack*> malloc(sizeof(Pack))
		pack.alpha.material_id   = pack.material_id
		pack.alpha.batched_faces = get_clist()
		pack.alpha.option        = pack.option | FACE_ALPHA
		pack.alpha.secondpass    = pack.alpha.alpha = NULL
	return pack.alpha

cdef Pack* pack_get_secondpass(Pack* pack):
	"""pack_get_secondpass(Pack* pack) -> Pack*

Returns a pack with the same material and drawing options, but that uses the second pass
renderer batching state (for drawing triangle / quad after all the other).
If called twice with the same argument, the returned pack is the same, and it should
not be free'ed."""
	if pack.secondpass == NULL: # create a new pack
		pack.secondpass               = <Pack*> malloc(sizeof(Pack))
		pack.secondpass.material_id   = pack.material_id
		pack.secondpass.batched_faces = get_clist()
		if pack.option & PACK_SECONDPASS: pack.secondpass.option = pack.option | PACK_SPECIAL
		else:                             pack.secondpass.option = pack.option | PACK_SECONDPASS
		pack.secondpass.secondpass    = pack.secondpass.alpha = NULL
	return pack.secondpass

cdef void pack_batch_face(Pack* pack, void* face, int no_double):
	"""pack_batch_face(Pack* pack, void* face)

Batches face, i.e. store a pointer to face for a future rendering (at the rendering time)
using the pack's attributes.
If no_double is not 0 the function will only batch the face if it hasn't been already"""
	if pack.batched_faces.begin == NULL: # first time we use this pack (for the object we are rendering)
		if   pack.option & FACE_ALPHA:      clist_add(renderer.used_alpha_packs     , <void*> pack)
		elif pack.option & PACK_SECONDPASS: clist_add(renderer.used_secondpass_packs, <void*> pack)
		else:                               clist_add(renderer.used_opaque_packs    , <void*> pack)
		clist_add(pack.batched_faces, face)
	elif no_double:
		if clist_find(pack.batched_faces, face) == NULL: clist_add(pack.batched_faces, face)
	else:                                              clist_add(pack.batched_faces, face)

# pack_batch_end replace the xmesh_batch_end of Soya 0.6.1 (Blam C code)
# there is no pack_batch_start (formely xmesh_batch_start) ; it is no longer necessary
cdef void pack_batch_end(batched_object, CoordSyst coordsyst):
	cdef Pack*        pack
	cdef CListHandle* current_data
	cdef CListHandle* current_pack
	
	if not renderer.used_opaque_packs.begin == NULL:
		current_data = renderer.data.end
		current_pack = renderer.used_opaque_packs.begin
		while current_pack != NULL:
			pack = <Pack*> current_pack.data
			clist_add(renderer.data, <void*> pack)
			clist_transfer(pack.batched_faces, renderer.data)
			clist_add(renderer.data, NULL) # NULL terminated list
			current_pack = current_pack.next
		clist_add(renderer.data, NULL) # NULL terminated list
		if current_data == NULL: current_data = renderer.data.begin
		else:                    current_data = current_data.next
		renderer._batch(renderer.opaque, batched_object, coordsyst, current_data)
		clist_flush(renderer.used_opaque_packs)
	
	if not renderer.used_alpha_packs.begin == NULL:
		current_data = renderer.data.end
		current_pack = renderer.used_alpha_packs.begin
		while current_pack != NULL:
			pack = <Pack*> current_pack.data
			clist_add(renderer.data, <void*> pack)
			clist_transfer(pack.batched_faces, renderer.data)
			clist_add(renderer.data, NULL) # NULL terminated list
			current_pack = current_pack.next
		clist_add(renderer.data, NULL) # NULL terminated list
		if current_data == NULL: current_data = renderer.data.begin
		else:                    current_data = current_data.next
		renderer._batch(renderer.alpha, batched_object, coordsyst, current_data)
		clist_flush(renderer.used_alpha_packs)
	
	if not renderer.used_secondpass_packs.begin == NULL:
		current_data = renderer.data.end
		current_pack = renderer.used_secondpass_packs.begin
		while current_pack != NULL:
			pack = <Pack*> current_pack.data
			clist_add(renderer.data, <void*> pack)
			clist_transfer(pack.batched_faces, renderer.data)
			clist_add(renderer.data, NULL) # NULL terminated list
			current_pack = current_pack.next
		clist_add(renderer.data, NULL) # NULL terminated list
		if current_data == NULL: current_data = renderer.data.begin
		else:                    current_data = current_data.next
		renderer._batch(renderer.secondpass, batched_object, coordsyst, current_data)
		clist_flush(renderer.used_secondpass_packs)
