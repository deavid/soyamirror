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

cdef int            NB_JOYSTICK
cdef SDL_Joystick** JOYSTICKS
cdef                DRIVER_3D
cdef int            SDL_UNICODE

def set_quality(int q):
	global quality
	quality = q
	if   q == QUALITY_LOW:
		glHint(GL_FOG_HINT                   , GL_FASTEST)
		glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_FASTEST)
		glHint(GL_POINT_SMOOTH_HINT          , GL_FASTEST)
		glHint(GL_LINE_SMOOTH_HINT           , GL_FASTEST)
		glHint(GL_POLYGON_SMOOTH_HINT        , GL_FASTEST)
		renderer.engine_option = renderer.engine_option & ~SHADOWS # Disable shadows
		
	elif q == QUALITY_MEDIUM:
		glHint(GL_FOG_HINT                   , GL_DONT_CARE)
		glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_DONT_CARE)
		glHint(GL_POINT_SMOOTH_HINT          , GL_DONT_CARE)
		glHint(GL_LINE_SMOOTH_HINT           , GL_DONT_CARE)
		glHint(GL_POLYGON_SMOOTH_HINT        , GL_DONT_CARE)
		if renderer.engine_option & HAS_STENCIL: renderer.engine_option = renderer.engine_option | SHADOWS # Enable shadows
		
	elif q == QUALITY_HIGH:
		glHint(GL_FOG_HINT                   , GL_NICEST)
		glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)
		glHint(GL_POINT_SMOOTH_HINT          , GL_NICEST)
		glHint(GL_LINE_SMOOTH_HINT           , GL_NICEST)
		glHint(GL_POLYGON_SMOOTH_HINT        , GL_NICEST)
		if renderer.engine_option & HAS_STENCIL: renderer.engine_option = renderer.engine_option | SHADOWS # Enable shadows
		
def toggle_wireframe():
	if renderer.engine_option & WIREFRAME:
		glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
		renderer.engine_option = renderer.engine_option & ~WIREFRAME
	else:
		glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
		renderer.engine_option = renderer.engine_option | WIREFRAME
		
cdef void dump_info():
	print """
* Soya * version %s
* Using OpenGL %s
*   - renderer : %s
*   - vendor   : %s
*   - maximum number of lights        : %s
*   - maximum number of clip planes   : %s
*   - maximum number of texture units : %s
*   - maximum texture size            : %s pixels""" % (
		VERSION,
		PyString_FromString(<char*> glGetString(GL_VERSION)),
		PyString_FromString(<char*> glGetString(GL_RENDERER)),
		PyString_FromString(<char*> glGetString(GL_VENDOR)),
		MAX_LIGHTS,
		MAX_CLIP_PLANES,
		MAX_TEXTURES,
		MAX_TEXTURE_SIZE,
		)
		
cdef void init_gl():
	global DRIVER_3D

	glGetIntegerv(GL_MAX_LIGHTS,        &MAX_LIGHTS)
	glGetIntegerv(GL_MAX_CLIP_PLANES,   &MAX_CLIP_PLANES)
	glGetIntegerv(GL_MAX_TEXTURE_UNITS, &MAX_TEXTURES)
	glGetIntegerv(GL_MAX_TEXTURE_SIZE,  &MAX_TEXTURE_SIZE)
	
	cdef int i
	for i from 0 <= i < MAX_LIGHTS:
		LIGHTS     .append(None)
		LAST_LIGHTS.append(None)
		
	glClearDepth(1.0)
	glDepthMask(GL_FALSE)
	glDisable(GL_DEPTH_TEST)

	glDepthFunc(GL_LESS)

	glDisable(GL_COLOR_MATERIAL)
	glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
	glEnable(GL_COLOR_MATERIAL)

	cdef GLfloat black[4]
	black[3] = 1.0
	glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, black)
	glLightModeli(GL_LIGHT_MODEL_TWO_SIDE, GL_FALSE)
	glDisable(GL_LIGHTING)

	glDisable(GL_NORMALIZE)
		
	glDisable(GL_BLEND)
	glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
	glDisable(GL_ALPHA_TEST)
	glAlphaFunc(GL_NOTEQUAL, 0.0)
	
	glEnable(GL_CULL_FACE)
	glCullFace(GL_BACK)
	glFrontFace(GL_CCW)
		
	glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
	glEnable(GL_POINT_SMOOTH)
	glDisable(GL_LINE_SMOOTH)
	glDisable(GL_POLYGON_SMOOTH)
	glShadeModel(GL_SMOOTH)

	glDisable(GL_DITHER)

	glPixelStorei(GL_PACK_ALIGNMENT  , 1)
	glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
	
	# 'activate' DEFAULT_MATERIAL
	glDisable(GL_TEXTURE_2D)
	glColor4f(1.0, 1.0, 1.0, 1.0)
	
	global SHADOW_DISPLAY_LIST, SHADOW_TESS_CHUNK, SHADOW_TESS
	SHADOW_DISPLAY_LIST = glGenLists(1)
	SHADOW_TESS_CHUNK   = chunk_new()
	SHADOW_TESS         = gluNewTess()
	
	gluTessCallback(SHADOW_TESS, GLU_TESS_BEGIN  , <_GLUfuncptr> glBegin)
	gluTessCallback(SHADOW_TESS, GLU_TESS_VERTEX , <_GLUfuncptr> glVertex3dv)
	gluTessCallback(SHADOW_TESS, GLU_TESS_END    , <_GLUfuncptr> glEnd)
	gluTessCallback(SHADOW_TESS, GLU_TESS_COMBINE, <_GLUfuncptr> model_shadow_tess_combine)
	
	
	set_quality(quality)
	
# Get the driver name
	cdef char* gl_renderer
	gl_renderer = <char*> glGetString(GL_RENDERER)
	if gl_renderer == NULL:
		DRIVER_3D = ""
		print "* Soya 3D * Warning : glGetString returns NULL!"
		check_gl_error()
	else:
		DRIVER_3D = PyString_FromString(<char*> glGetString(GL_RENDERER))
	if "DRI Radeon" in DRIVER_3D:
		# Avoid a bug in free radeon driver
		global terrain_drawColor, terrain_disableColor, terrain_enableColor
		#terrain_drawColor    = terrain_drawColor_radeon
		#terrain_disableColor = terrain_disableColor_radeon
		#terrain_enableColor  = terrain_enableColor_radeon
		
		# free radeon driver print A LOT OF debug code when using texture border, which
		# slow down the rendering ! => disable texture border.
		global CAN_USE_TEX_BORDER
		CAN_USE_TEX_BORDER = 0
		
cdef void base_init():
	global renderer
	#srand (1);
	clist_init()
	renderer = Renderer()
	#terrain_tri_recycler = P3_list_new(20)
	#chunks = P3_list_new(2)

cdef void base_quit():
	cdef int i
	global JOYSTICKS, NB_JOYSTICK
 
	print "* Soya3D * Quit..."
	
	# renderer
	#P3_list_dealloc(terrain_tri_recycler)
	#free(NULL_packs)
	# fx
	if renderer.engine_option & FX_INITED: fx_quit()
	# chunks
	#for (i = 0; i < chunks->nb; i++)
	#  P3_chunk_dealloc ((P3_chunk*) P3_list_get (chunks, i));
	#P3_list_dealloc(chunks)
	
	
	if SHADOW_DISPLAY_LIST != -1:
		glDeleteLists(SHADOW_DISPLAY_LIST, 1)
		chunk_dealloc(SHADOW_TESS_CHUNK)
		gluDeleteTess(SHADOW_TESS)
	
	for i from 0 <= i < NB_JOYSTICK: SDL_JoystickClose(JOYSTICKS[i])
	SDL_Quit()
	
	free(JOYSTICKS)
	renderer.engine_option = renderer.engine_option & ~INITED
	#print "clist dealloc"
	#clist_dealloc()

cdef void init_joysticks():
	cdef int i
	global JOYSTICKS, NB_JOYSTICK
	NB_JOYSTICK = SDL_NumJoysticks()
	
	if NB_JOYSTICK > 0:
		SDL_JoystickEventState(SDL_ENABLE)
		JOYSTICKS = <SDL_Joystick**> malloc(NB_JOYSTICK * sizeof(SDL_Joystick*))
		for i from 0 <= i < NB_JOYSTICK: JOYSTICKS[i] = SDL_JoystickOpen(i)

def set_gamma(float r_gamma,float g_gamma,float b_gamma):
		"""Defines gamma correction.
		Usage : soya.set_gamma(red_gamma,green_gamma,blue_gamma)
		if XXX_gamma=1.0 : no change
		>1.0 : dark
		<1.0 : bright"""
		cdef int i    
		i=SDL_SetGamma(r_gamma,g_gamma,b_gamma)   
		if i<0:
				s = "Video query failed : %s" % SDL_GetError()
				print s
				raise RuntimeError(s)

def set_video(int width, int height, int fullscreen, int resizable):
	cdef int stencil, bits_per_pixel
	cdef unsigned int flags
	cdef SDL_VideoInfo* info
	renderer.screen_width  = width
	renderer.screen_height = height
	# Information about the current video settings
	info = SDL_GetVideoInfo()
	if info == NULL:
		s = "Video query failed : %s" % SDL_GetError()
		print s
		raise RuntimeError(s)
	
	# On X11, VidMode can't change resolution, so this is probably being overly safe.
	# Under Win32, ChangeDisplaySettings can change the bpp.
	
	bits_per_pixel = info.vfmt.BitsPerPixel
	flags = SDL_OPENGL | SDL_GL_DOUBLEBUFFER | SDL_HWPALETTE
	if fullscreen == 0: renderer.engine_option = renderer.engine_option & ~FULLSCREEN
	else:
		renderer.engine_option = renderer.engine_option |  FULLSCREEN
		flags = flags | SDL_FULLSCREEN
	
	if resizable == 1:    flags = flags | SDL_RESIZABLE
	if info.hw_available: flags = flags | SDL_HWSURFACE
	else:                 flags = flags | SDL_SWSURFACE
# Useless (see http://www.devolution.com/pipermail/sdl/2004-September/064784.html)
#	if info.blit_hw :     flags = flags | SDL_HWACCEL
	stencil = 16
	
	while stencil > 1:
		SDL_GL_SetAttribute(SDL_GL_STENCIL_SIZE, stencil)
		# Set the video mode
		renderer.screen = SDL_SetVideoMode(width, height, bits_per_pixel, flags)
		if renderer.screen == NULL: stencil = stencil >> 1
		else: break
		
	if renderer.screen == NULL:
		SDL_GL_SetAttribute(SDL_GL_STENCIL_SIZE, 0)
		renderer.screen = SDL_SetVideoMode(width, height, bits_per_pixel, flags)
		if renderer.screen == NULL:
			s = "Video mode set failed : %s" % SDL_GetError()
			print s
			raise RuntimeError(s)
		print "* Soya * Failed to set stencil buffer, shadows will be disabled."
		renderer.engine_option = renderer.engine_option & ~HAS_STENCIL
		renderer.engine_option = renderer.engine_option & ~SHADOWS
	else:
		print "* Soya * Using %i bits stencil buffer" % stencil
		renderer.engine_option = renderer.engine_option | HAS_STENCIL

	# Wait until OpenGL is REALLY ready
	cdef int i
	from time import sleep
	for i from 0 <= i < 10:
		if glGetString(GL_RENDERER) != NULL: break
		sleep(0.1)
	else:
		print "* Soya * ERROR : OpenGL is not ready... Soya will crash soon i guess :-("
	
		
	glViewport(0, 0, renderer.screen_width, renderer.screen_height)
	glMatrixMode(GL_PROJECTION)
	glLoadIdentity()
	glOrtho(0.0, <GLfloat> width, <GLfloat> height, 0.0, -1.0, 1.0)
	glMatrixMode(GL_MODELVIEW)
	glLoadIdentity()
	
	global root_widget
	if not root_widget is None:
		root_widget.resize(0, 0, renderer.screen_width, renderer.screen_height)
		
		
cdef void init_video(char* title, int width, int height, int fullscreen, int resizable):
	import sys
	if sys.platform == "darwin":
		print "* Soya * Initializing for MacOSX..."
		import soya.macosx
		
	# initialize SDL
	if SDL_Init(SDL_INIT_VIDEO | SDL_INIT_JOYSTICK  | SDL_INIT_NOPARACHUTE) < 0:
		s = "Could not initialize SDL : %s" % SDL_GetError()
		print s
		raise RuntimeError(s)
	set_video(width, height, fullscreen, resizable)
	if title != NULL: SDL_WM_SetCaption(title, NULL)


def init(title = "Soya 3D", int width = 640, int height = 480, int fullscreen = 0, int resizeable = 1, int create_surface = 1, int sound = 0, sound_device = "'( ( devices '( native esd sdl alsa arts null ) ) )", int sound_frequency = 44100, float sound_reference_distance = 1.0, float sound_doppler_factor = 0.01):
	"""init(title = "Soya 3D", width = 640, height = 480, fullscreen = 0, resizeable = 1, create_surface = 1, sound = 0, sound_device = "'( ( devices '( native esd sdl alsa arts null ) ) )", sound_frequency = 44100, sound_reference_distance = 1.0, sound_doppler_factor = 0.01)

Inits Soya 3D and display the 3D view.

TITLE is the title of the window.
WIDTH and HEIGHT the dimensions of the 3D view.
FULLSCREEN is true for fullscreen and false for windowed mode.
RESIZEABLE is true for a resizeable window.

Set SOUND to true to initialize 3D sound support (default to false for backward compatibility)
The following arguments are meaningful only if SOUND is true:
SOUND_DEVICE is the OpenAL device names, the default value should be nice.
SOUND_FREQUENCY is the sound frequency.
SOUND_REFERENCE_DISTANCE is the reference distance for sound attenuation.
SOUND_DOPPLER_FACTOR can be used to increase or decrease the Doppler effect."""

	if not(renderer.engine_option & INITED):
		base_init()
		if create_surface:
			init_video(title, width, height, fullscreen, resizeable)
		init_joysticks()
		init_gl()
		glewInit()
		
		SDL_UNICODE=0
		
		renderer.engine_option = renderer.engine_option | INITED
		
		if not root_widget is None: root_widget.resize(0, 0, width, height)
		
		import atexit
		atexit.register(quit)
		
		import soya
		soya.inited = 1

	dump_info()
	
	if sound:
		_init_sound(sound_device, sound_frequency, sound_reference_distance, sound_doppler_factor)
		
	print
		
def quit():
	import soya
	if soya.inited:
		soya.inited = 0
		base_quit()
		quit_cal3d()

def set_use_unicode(state):
	"""when set, process_event will return a 4 part tuple for a keydown event.
	the fourth part contains the unicode symbol for the key.
	usefull for getting CAPITALS and !$% etc in text boxes for example """
	global SDL_UNICODE

	if state:
		SDL_UNICODE=1
		SDL_EnableUNICODE( 1 )
	else:
		SDL_UNICODE=0
		SDL_EnableUNICODE( 0 )

# SDL-related funcs, though not initialization-related
	
def process_event():
	cdef object    events
	cdef SDL_Event event

	global SDL_UNICODE
	
	events = []
	
	while SDL_PollEvent(&event):
		if   (event.type == SDL_KEYDOWN) or (event.type == SDL_KEYUP):
			if SDL_UNICODE==1 and event.type==SDL_KEYDOWN:
				events.append((event.type, event.key.keysym.sym, event.key.keysym.mod, event.key.keysym.unicode))
			else:
				events.append((event.type, event.key.keysym.sym, event.key.keysym.mod))
		elif  event.type == SDL_MOUSEMOTION:
			events.append((SDL_MOUSEMOTION, event.motion.x, event.motion.y, event.motion.xrel, event.motion.yrel, event.motion.state))
		elif (event.type == SDL_MOUSEBUTTONDOWN) or (event.type == SDL_MOUSEBUTTONUP):
			events.append((event.type, event.button.button, event.button.x, event.button.y))
			
		elif  event.type == SDL_JOYAXISMOTION:
			events.append((SDL_JOYAXISMOTION, event.jaxis.axis, event.jaxis.value))
		elif (event.type == SDL_JOYBUTTONDOWN) or (event.type == SDL_JOYBUTTONUP):
			events.append((event.type, event.jbutton.button))
			
		elif (event.type == SDL_QUIT) or (event.type == SDL_VIDEOEXPOSE):
			events.append((event.type,))
		elif  event.type == SDL_VIDEORESIZE:
			if renderer.engine_option & FULLSCREEN: set_video(event.resize.w, event.resize.h, 1, 1)
			else:                                   set_video(event.resize.w, event.resize.h, 0, 1)
			
			events.append((SDL_VIDEORESIZE, event.resize.w, event.resize.h))
						
	return events

def get_mod():
	return SDL_GetModState()

def cursor_set_visible(int visibility):
	if visibility == 0: SDL_ShowCursor(SDL_DISABLE)
	else:               SDL_ShowCursor(SDL_ENABLE)

# there are many more masks defined in SDL/SDL_event
# this is the mask for _all_ events 
SDL_ALLEVENTS=0xFFFFFFFF
ALL_EVENTS=SDL_ALLEVENTS

def set_mouse_pos(int x,int y):
	""" move the mouse cursor to x,y"""
	SDL_WarpMouse(x,y)

def get_grab_input():
	""" queries mouse grabbing
	returns 1 or 0"""

	if SDL_WM_GrabInput(SDL_GRAB_QUERY)==SDL_GRAB_ON:
		return 1
	
	return 0

def set_grab_input(int mode):
	""" grabs the mouse and keyboard input to our window
	set_grab_state(0|1) to set state
	"""

	if mode==1:
		SDL_WM_GrabInput(SDL_GRAB_ON)
	else:
		SDL_WM_GrabInput(SDL_GRAB_OFF)


def clear_events(mask=ALL_EVENTS):
	""" go through all the events in the key and remove them.
	mask currently on supports ALL_EVENTS
	"""
	# in homage to http://cvs.seul.org/cgi-bin/cvsweb-1.80.cgi/games/pygame/src/event.c?rev=1.40&content-type=text/x-cvsweb-markup

	cdef SDL_Event event

	SDL_PumpEvents()
	
	while SDL_PeepEvents(&event,1,SDL_GETEVENT,mask)==1:
		pass

def get_mouse_rel_pos():
	""" return the relative mouse position since the last call to this function"""
	cdef int x
	cdef int y

	SDL_GetRelativeMouseState(&x,&y)

	return (x,y)

