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

# XXX does not allows None/NULL as a valid context, use a default context instead

cdef class Context:
	#cdef             lights
	#cdef _Atmosphere atmosphere
	#cdef _Portal     portal
	
	def __init__(self):
		self.lights = []
		
		
cdef class Renderer:
	#cdef int       engine_option
	#cdef int       state
	#cdef _World    root_object
	#cdef _Camera   current_camera
	#cdef _Material current_material
	
	#cdef Frustum*  root_frustum
	#cdef Chunk*    frustums
	#cdef CoordSyst current_coordsyst
	
	# contexts
	#cdef Context current_context
	#cdef contexts
	#cdef int nb_contexts
	#cdef int max_contexts
	#cdef _Atmosphere root_atmosphere # root atmosphere (the one to clear the screen with)
	
	# list of collected objects to render
	#cdef Chunk* opaque
	#cdef Chunk* secondpass
	#cdef Chunk* alpha
	#cdef Chunk* specials  # objects that are rendered after the shadows (= not shadowed)
	
	#cdef top_lights # contain top level activated lights
	#cdef worlds_made  # list of world whose context has been made (used by portals to determine if a world must be batched or not)
	#cdef portals  # a list of encountered portals to clear_part the atmosphere before any other rendering and to draw fog at the end
	
	# mesh renderer
	#cdef Chunk* data
	#cdef Chunk* used_opaque_packs, *used_secondpass_packs, *used_alpha_packs
	#cdef float** colors
	
	# screen
	#cdef SDL_Surface* screen
	#cdef int screen_width, screen_height
	
	#cdef float delta_time
	
	def __init__(self):
		self.engine_option = USE_MIPMAP | SHADOWS
		self.root_frustum  = <Frustum*> malloc(sizeof(Frustum))
		self.top_lights    = []
		self.worlds_made   = []
		self.portals       = []
		self.contexts      = []

		self.opaque        = get_clist()
		self.secondpass    = get_clist()
		self.alpha         = get_clist()
		self.specials      = get_clist()
		
		self.data                  = get_clist()
		self.frustums              = get_chunk()
		self.used_opaque_packs     = get_clist()
		self.used_secondpass_packs = get_clist()
		self.used_alpha_packs      = get_clist()
		
		self.current_material = _DEFAULT_MATERIAL
		
	def __dealloc__(self):
		pass
		"""
		print "renderer dealloc"
		free(self.root_frustum)
		drop_clist(self.data)
		drop_clist(self.opaque)
		drop_clist(self.secondpass)
		drop_clist(self.alpha)
		drop_clist(self.specials)
		drop_clist(self.used_opaque_packs)
		drop_clist(self.used_secondpass_packs)
		drop_clist(self.used_alpha_packs)
		chunk_dealloc(self.frustums)
		"""
	
	cdef Frustum* _frustum(self, CoordSyst coordsyst):
		if coordsyst is None: return self.root_frustum
		if coordsyst._frustum_id == -1:
			coordsyst._frustum_id = chunk_register(self.frustums, sizeof(Frustum))
			frustum_by_matrix(<Frustum*> (self.frustums.content + coordsyst._frustum_id), self.root_frustum, coordsyst._inverted_root_matrix())
		return <Frustum*> (self.frustums.content + coordsyst._frustum_id)
	
	cdef Context _context(self):
		cdef Context context
		context = Context()
		self.contexts.append(context)
		return context
		
	cdef void _activate_context_over(self, Context old, Context new):
		# XXX TODO activate / inactivate light only if necessary ?
		cdef _Light light
		if not old is None:
			# inactivate previous lights
			for light in old.lights:
				if light._id != -1:
					light._gl_id_enabled = 0
					glDisable(GL_LIGHT0 + light._id)
			if (not old.portal is None) and (old.portal._option & (PORTAL_USE_4_CLIP_PLANES | PORTAL_USE_5_CLIP_PLANES)):
				glDisable(GL_CLIP_PLANE0)
				glDisable(GL_CLIP_PLANE1)
				glDisable(GL_CLIP_PLANE2)
				glDisable(GL_CLIP_PLANE3)
				if old.portal._option & PORTAL_USE_5_CLIP_PLANES: glDisable(GL_CLIP_PLANE4)
		# activate new context
		if not new is None:
			if (not new.atmosphere is None) and ((old is None) or (not new.atmosphere is old.atmosphere)): new.atmosphere._render()
			for light in new.lights: light._activate()
		# re-activate top level lights that may have been inactivated due to too many lights
		for light in renderer.top_lights:
			if light._id == -1: light.render(None)
		# active portal clip plane
		if (not new is None) and (not new.portal is None) and (new.portal._option & (PORTAL_USE_4_CLIP_PLANES | PORTAL_USE_5_CLIP_PLANES)):
			glLoadIdentity()  # the clip planes must be defined in the camera coordsys... so identity
			glClipPlane(GL_CLIP_PLANE0, new.portal._equation)
			glClipPlane(GL_CLIP_PLANE1, new.portal._equation + 4)
			glClipPlane(GL_CLIP_PLANE2, new.portal._equation + 8)
			glClipPlane(GL_CLIP_PLANE3, new.portal._equation + 12)
			glEnable(GL_CLIP_PLANE0)
			glEnable(GL_CLIP_PLANE1)
			glEnable(GL_CLIP_PLANE2)
			glEnable(GL_CLIP_PLANE3)
			if new.portal._option & PORTAL_USE_5_CLIP_PLANES:
				glClipPlane(GL_CLIP_PLANE4, new.portal._equation + 16)
				glEnable(GL_CLIP_PLANE4)
				
	cdef void _reset(self):
		cdef _World world
		self.root_atmosphere = None
		disable_all_lights()
		for world in self.worlds_made: world._option = world._option - WORLD_BATCHED
		self.contexts   .__imul__(0)
		self.top_lights .__imul__(0)
		self.worlds_made.__imul__(0)
		self.portals    .__imul__(0)
		clist_flush(self.opaque)
		clist_flush(self.secondpass)
		clist_flush(self.alpha)
		clist_flush(self.specials)
		clist_flush(self.data)
		self.delta_time = 0.0
		
	cdef void _batch(self, CList* list, obj, CoordSyst coordsyst, CListHandle* data):
		clist_add(list, <void*> obj)
		clist_add(list, <void*> coordsyst)
		clist_add(list, <void*> renderer.current_context)
		clist_add(list, <void*> data)
	
	cdef void _render(self):
		cdef Context ctxt
		cdef _Portal portal
		cdef _World  world
		cdef _Light  light
		
		renderer.frustums.nb = 0
		
		# RENDERING STEP 1 : BATCH
		ctxt = self.current_context = self._context()
		self.root_object._batch(self.current_camera)
		
		# RENDERING STEP 2 : RENDER
		# clear
		if not self.root_atmosphere is None: self.root_atmosphere._clear()
		else: self._clear_screen(NULL)
		# draw the atmosphere of the worlds that are seen through portals
		self.portals.reverse()
		for portal in self.portals:
			if portal._option & PORTAL_BOUND_ATMOSPHERE: portal._atmosphere_clear_part()
		# activate top lights
		for light in self.top_lights: light._activate()
		# current context have been changed during batching -> reinitialize
		self.current_context = None
		
		# render collected objects
		# draw opaque stuff first
		self.state = RENDERER_STATE_OPAQUE
		self._render_list(self.opaque)
		
		# then draw secondpass
		self.state = RENDERER_STATE_SECONDPASS
		self._render_list(self.secondpass)
		# finally draw alpha
		self.state = RENDERER_STATE_ALPHA
		glEnable(GL_BLEND)
		glDepthMask(GL_FALSE)
		self._render_list(self.alpha)
		# reset a part of the renderer here cause it's needed for rendering the portal fog
		_DEFAULT_MATERIAL._activate()
		self._activate_context_over(self.current_context, None)
		self.current_context = None
		
		# draw fog for portal if necessary
		for portal in self.portals:
			if portal._option & PORTAL_BOUND_ATMOSPHERE:
				# get previous/parent atmosphere
				world = <_World> portal._parent
				while (not world is None) and (world._atmosphere is None): world = <_World> world._parent
				if (not world._atmosphere is None) and (world._atmosphere._option & ATMOSPHERE_FOG):
					portal._draw_fog(world._atmosphere)
		# render shadow
		# XXX don't call it if shadows are enabled, but none are currently used !!!
		if self.engine_option & SHADOWS: self._render_shadows()
		# render specials: objects that are not shadowed (sprite, particules)
		self.state = RENDERER_STATE_SPECIAL
		self._render_list (self.specials)
			
		# end of OpenGL rendering
		glDepthMask(GL_TRUE)
		glDisable(GL_BLEND)
		# auto-reset renderer
		self._reset()
		
		#drop_chunk(self.frustums)
		
	cdef void _render_list(self, CList* list):
		cdef CoordSyst    coordsyst
		cdef Context      context
		cdef CListHandle* handle
		cdef int          i, nb
		cdef _CObj        obj
		
		handle = list.begin
		while handle:
			obj               = <_CObj>        handle.data
			handle            =                handle.next
			coordsyst         = <CoordSyst>    handle.data
			handle            =                handle.next
			context           = <Context>      handle.data
			handle            =                handle.next
			self.current_data = <CListHandle*> handle.data
			
			# context
			if not context is self.current_context:
				self._activate_context_over(self.current_context, context)
				self.current_context = context
				
			# coordsyst
			self.current_coordsyst = coordsyst
			if not coordsyst is None:
				glLoadMatrixf(coordsyst._render_matrix)
				if coordsyst._render_matrix[17] != 1.0: glEnable(GL_NORMALIZE)
			
			if isinstance(obj, _Model): (<_Model>    obj)._render(coordsyst)
			else:                       (<CoordSyst> obj)._render(coordsyst)
			
			if (not coordsyst is None) and (coordsyst._render_matrix[17] != 1.0): glDisable(GL_NORMALIZE)
			
			handle = handle.next
	
	cdef void _clear_screen(self, float* color):
		cdef int* size
		if (self.current_camera._option & CAMERA_PARTIAL):
			size = self.current_camera._viewport
			glPushAttrib(GL_ENABLE_BIT)
			glDisable(GL_LIGHTING)
			glDisable(GL_FOG)
			glDisable(GL_TEXTURE_2D)
			glDisable(GL_CULL_FACE)
			glDepthMask (GL_FALSE)
			if (color == NULL): glColor3f (0.0, 0.0, 0.0)
			else:               glColor4fv(color)
			glLoadIdentity()
			glMatrixMode(GL_PROJECTION)
			glPushMatrix()
			glLoadIdentity()
			glOrtho(0.0, <GLfloat> size[2], <GLfloat> size[3], 0.0, -1.0, 1.0)
			glBegin(GL_QUADS)
			glVertex2i(0, 0)
			glVertex2i(size[2], 0)
			glVertex2i(size[2], size[3])
			glVertex2i(0, size[3])
			glEnd()
			glMatrixMode(GL_PROJECTION)
			glPopMatrix()
			glMatrixMode(GL_MODELVIEW)
			glPopAttrib()
			glDepthMask(GL_TRUE)
			glClear(GL_DEPTH_BUFFER_BIT)
		else:
			if color == NULL: glClearColor(0.0, 0.0, 0.0, 1.0)
			else:             glClearColor(color[0], color[1], color[2], color[3])
			glClear(GL_DEPTH_BUFFER_BIT | GL_COLOR_BUFFER_BIT)
			
	cdef void _render_shadows(self):
		cdef _Light light
		cdef float  p[12]
		cdef float* ptrf
		ptrf = self.current_camera._frustum.points
		
		# compute screen surface rectangle 
		# we can't just take the frustum points cause their depth are equal to
		# the front of the camera and some OpenGL implementation won't draw the quad
		
		p[ 0] = (ptrf[0] + ptrf[12]) * 0.5
		p[ 1] = (ptrf[1] + ptrf[13]) * 0.5
		p[ 2] = (ptrf[2] + ptrf[14]) * 0.5
		p[ 3] = - p[0]
		p[ 4] =   p[1]
		p[ 5] =   p[2]
		p[ 6] = - p[0]
		p[ 7] = - p[1]
		p[ 8] =   p[2]
		p[ 9] =   p[0]
		p[10] = - p[1]
		p[11] =   p[2]
		glEnableClientState(GL_VERTEX_ARRAY)
		glVertexPointer    (3, GL_FLOAT, 0, &p[0])
		glDisable          (GL_LIGHTING)
		glDisable          (GL_TEXTURE_2D)
		glDisable          (GL_FOG)
		glDepthFunc        (GL_LEQUAL)
		glPushMatrix       ()
		glEnable      (GL_CULL_FACE)
		
		for light in LIGHTS: # XXX LIGHTS, really ???
			if (light is None) or (light._option & LIGHT_NO_SHADOW): continue
			
			glStencilMask (0xFFFFFFFF)
			glClearStencil(0)
			glClear       (GL_STENCIL_BUFFER_BIT)
			glEnable      (GL_STENCIL_TEST)
			glColorMask   (GL_FALSE, GL_FALSE, GL_FALSE, GL_FALSE)
			
			# draw shadow body
			if self.root_object._shadow(None, light):
				# draw stencil buffer on screen
				glStencilMask (0)
				glColorMask   (GL_TRUE, GL_TRUE, GL_TRUE, GL_TRUE)
				
				glColor4fv    (&light._colors[0] + 12)
				glStencilFunc (GL_NOTEQUAL, 0, 0xFFFFFFFF)
				glStencilOp   (GL_KEEP, GL_KEEP, GL_KEEP)
				glDisable     (GL_CULL_FACE)
				
				# Avoid casting shadows on the camera back plane:
				# Draws only if the depth value is different than 1.0
				# (the most far possible value).
				glEnable       (GL_DEPTH_TEST)
				glDepthFunc    (GL_NOTEQUAL)
				glDepthRange   (1.0, 1.0)
				
				glLoadIdentity()
				glDrawArrays  (GL_QUADS, 0, 4)
				glEnable      (GL_DEPTH_TEST)
				glEnable      (GL_CULL_FACE)
				glDepthFunc   (GL_LEQUAL)
				glDepthRange  (0.0, 1.0)
			else:
				glStencilMask (0)
				glColorMask   (GL_TRUE, GL_TRUE, GL_TRUE, GL_TRUE)
				
		glPopMatrix         ()
		glEnable            (GL_LIGHTING)
		glEnable            (GL_FOG)
		glEnable            (GL_TEXTURE_2D)
		glDepthFunc         (GL_LESS)
		glDisable           (GL_STENCIL_TEST)
		glDisableClientState(GL_VERTEX_ARRAY)
		
def get_renderer():
	return renderer

root_widget = None


class GLError(StandardError):
	pass


def check_error(): return check_gl_error()

cdef int check_gl_error() except -1:
	cdef GLenum error
	error = glGetError()
	if error != GL_NO_ERROR:
		if   error == GL_INVALID_ENUM     : print "GL_INVALID_ENUM"     ; raise GLError, "GL_INVALID_ENUM"
		elif error == GL_INVALID_VALUE    : print "GL_INVALID_VALUE"    ; raise GLError, "GL_INVALID_VALUE"
		elif error == GL_INVALID_OPERATION: print "GL_INVALID_OPERATION"; raise GLError, "GL_INVALID_OPERATION"
		elif error == GL_STACK_OVERFLOW   : print "GL_STACK_OVERFLOW"   ; raise GLError, "GL_STACK_OVERFLOW"
		elif error == GL_STACK_UNDERFLOW  : print "GL_STACK_UNDERFLOW"  ; raise GLError, "GL_STACK_UNDERFLOW"
		elif error == GL_OUT_OF_MEMORY    : print "GL_OUT_OF_MEMORY"    ; raise GLError, "GL_OUT_OF_MEMORY"
		else:                               print "Unknown GL_ERROR 0x%X" % error    ; raise GLError, "Unknown GL_Error 0x%X" % error


def set_root_widget(widget):
	"""set_root_widget(widget)

Sets the root widget of Soya3D. The root widget is the one used for rendering.
It is typically a camera, or a group of widget (soya.widget.Group) which includes
a camera."""
	global root_widget
	root_widget = widget
	if root_widget:
		root_widget.resize(0, 0, renderer.screen_width, renderer.screen_height)
		
def render(int swap_buffer = 1):
	"""render()

Renders the 3D scene. Use set_root_widget() to choose which camera is used."""
	if root_widget and (renderer.engine_option & INITED):
		root_widget.render()
		check_gl_error()
		if swap_buffer: SDL_GL_SwapBuffers()

def get_screen_width (): return renderer.screen_width
def get_screen_height(): return renderer.screen_height


cdef class _DisplayList(_CObj):
	property id:
		def __get__(self):
			if self._id == 0: self._id = glGenLists(1)
			return self._id
		
	def __dealloc__(self):
		if not self._id == 0:
			glDeleteLists(self._id, 1)
			self._id = -1

# cdef class _FrameBufferData(_CObj):
# 	def __init__(self):
# 		cdef int red, green, blue, alpha, depth
# 		glGetIntegerv(GL_RED_BITS  , &red)
# 		glGetIntegerv(GL_GREEN_BITS, &green)
# 		glGetIntegerv(GL_BLUE_BITS , &blue)
# 		glGetIntegerv(GL_ALPHA_BITS, &alpha)
# 		bbp = max(red, green, blue, alpha)
# 		if   bpp <  8: bpp =  8
# 		elif bpp < 16: bpp = 16
# 		elif bpp < 32: bpp = 32
# 		elif bpp < 64: bpp = 64
		
# 		self.color_data = malloc(3 * bpp * renderer.screen_width * renderer.screen_height)
		
# 		glGetIntegerv(GL_DEPTH_BITS, &depth)
# 		bpp = depth
# 		if   bpp <  8: bpp =  8
# 		elif bpp < 16: bpp = 16
# 		elif bpp < 32: bpp = 32
# 		elif bpp < 64: bpp = 64
		
# 		self.depth_data = malloc(    depth * renderer.screen_width * renderer.screen_height)
		
# 	def __dealloc__(self):
# 		free(self.color_data)
# 		free(self.depth_data)
		
# 	def capture(self, int x = 0, int y = 0, int width = 0, int height = 0):
# 		width  = width  or renderer.screen_width
# 		height = height or renderer.screen_height
# 		glReadBuffer(GL_BACK)
# 		glReadPixels(x, y, width, height, GL_RGB, GL_UNSIGNED_BYTE, self.color_data)
# 		glReadPixels(x, y, width, height, GL_DEPTH_COMPONENT, GL_FLOAT, self.depth_data)
		
# 	def restore(self, int x = 0, int y = 0, int width = 0, int height = 0):
# 		width  = width  or renderer.screen_width
# 		height = height or renderer.screen_height
		
# 		glDisable(GL_TEXTURE_2D)
# 		glDisable(GL_LIGHTING)
# 		glDisable(GL_ALPHA_TEST)
# 		glDisable(GL_DEPTH_TEST)
		
# 		glRasterPos2i(x, y)
# 		glDrawPixels(width, height, GL_RGB, GL_UNSIGNED_BYTE, self.color_data)
# 		glDrawPixels(width, height, GL_DEPTH_COMPONENT, GL_FLOAT, self.depth_data)
		
# 		glEnable(GL_LIGHTING)
# 		glEnable(GL_DEPTH_TEST)
		
# cdef class _FrameBufferData(_CObj):
# 	def __init__(self):
# 		cdef int depth
# 		glGetIntegerv(GL_DEPTH_BITS, &depth)
# 		bpp = depth
# 		if   bpp <  8: bpp =  8
# 		elif bpp < 16: bpp = 16
# 		elif bpp < 32: bpp = 32
# 		elif bpp < 64: bpp = 64
		
# 		self.depth_data = malloc(    depth * renderer.screen_width * renderer.screen_height)
# 		self.surface = NULL
		
# 	def __dealloc__(self):
# 		pass
	
# 	def capture(self, int x = 0, int y = 0, int width = 0, int height = 0):
# 		width  = width  or renderer.screen_width
# 		height = height or renderer.screen_height
# 		glReadBuffer(GL_BACK)
# 		glReadPixels(x, y, width, height, GL_DEPTH_COMPONENT, GL_FLOAT, self.depth_data)

# 		cdef SDL_Rect rect
# 		rect.x = 0
# 		rect.y = 0
# 		rect.w = 1
# 		rect.h = 1
		
# 		if self.surface != NULL:
# 			SDL_FreeSurface(self.surface)
			
# 		self.surface = SDL_DisplayFormat(renderer.screen);
# 		print renderer.screen != self.surface
		
# 	def restore(self, int x = 0, int y = 0, int width = 0, int height = 0):
# 		width  = width  or renderer.screen_width
# 		height = height or renderer.screen_height
		
# 		glDisable(GL_TEXTURE_2D)
# 		glDisable(GL_LIGHTING)
# 		glDisable(GL_ALPHA_TEST)
# 		glDisable(GL_DEPTH_TEST)
		
# 		glRasterPos2i(x, y)
# 		glDrawPixels(width, height, GL_DEPTH_COMPONENT, GL_FLOAT, self.depth_data)
		
# 		glEnable(GL_LIGHTING)
# 		glEnable(GL_DEPTH_TEST)
		
# 		cdef SDL_Rect rect
# 		rect.x = x
# 		rect.y = y
# 		rect.w = width
# 		rect.h = height
# 		SDL_BlitSurface(self.surface, &rect, renderer.screen, &rect);


cdef class _FrameBufferData(_CObj):
	def __init__(self):
		cdef int depth
		glGetIntegerv(GL_DEPTH_BITS, &depth)
		bpp = depth
		if   bpp <  8: bpp =  8
		elif bpp < 16: bpp = 16
		elif bpp < 32: bpp = 32
		elif bpp < 64: bpp = 64
		
		self.depth_data = malloc(    depth * renderer.screen_width * renderer.screen_height)
		self.surface = NULL
		
	def __dealloc__(self):
		pass
	
	def capture(self, int x = 0, int y = 0, int width = 0, int height = 0):
		glFlush()

		self.x = x
		self.y = y
		self.width  = power_of_2(width  or renderer.screen_width )
		self.height = power_of_2(height or renderer.screen_height)
		glReadBuffer(GL_BACK)
		glReadPixels(self.x, self.y, self.width, self.height, GL_DEPTH_COMPONENT, GL_FLOAT, self.depth_data)
		
		glGenTextures(1, &(self._tex_id))
		glPushAttrib(GL_TEXTURE_BIT)
		glBindTexture(GL_TEXTURE_2D, self._tex_id)
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
		glCopyTexImage2D(GL_TEXTURE_2D,
										 0,
										 GL_RGBA,
										 self.x, self.y,
										 self.width, self.height,
										 0,
										 )
		glPopAttrib()
		
	def restore(self):
		width  = width  or renderer.screen_width
		height = height or renderer.screen_height
		
		glDisable(GL_TEXTURE_2D)
		glDisable(GL_LIGHTING)
		glDisable(GL_ALPHA_TEST)
		glDisable(GL_DEPTH_TEST)
		glDisable(GL_FOG)
		glDisable(GL_CULL_FACE)
		
		glRasterPos2i(self.x, self.y)
		glColorMask(GL_FALSE, GL_FALSE, GL_FALSE, GL_FALSE)
		glDrawPixels(self.width, self.height, GL_DEPTH_COMPONENT, GL_FLOAT, self.depth_data)
		glColorMask(GL_TRUE, GL_TRUE, GL_TRUE, GL_TRUE)
		
		global _DEFAULT_MATERIAL
		_DEFAULT_MATERIAL.activate()
		
		glEnable(GL_TEXTURE_2D)
		glBindTexture(GL_TEXTURE_2D, self._tex_id)
		glDepthMask(GL_FALSE)
		glPushMatrix()
		glLoadIdentity()
		glMatrixMode(GL_PROJECTION)
		glPushMatrix()
		glLoadIdentity()
		glOrtho(0.0, renderer.screen_width, 0.0, renderer.screen_height, -1.0, 1.0)
		
		glBegin(GL_QUADS)
		glTexCoord2f(0.0, 0.0); glVertex2i(self.x             , self.y)
		glTexCoord2f(0.0, 1.0); glVertex2i(self.x             , self.y + self.height)
		glTexCoord2f(1.0, 1.0); glVertex2i(self.x + self.width, self.y + self.height)
		glTexCoord2f(1.0, 0.0); glVertex2i(self.x + self.width, self.y)
		glEnd()
		glPopMatrix()
		glMatrixMode(GL_MODELVIEW)
		glPopMatrix()
		glDisable(GL_TEXTURE_2D)
		
		glEnable(GL_CULL_FACE)
		glEnable(GL_FOG)
		glEnable(GL_LIGHTING)
		glEnable(GL_DEPTH_TEST)
		
