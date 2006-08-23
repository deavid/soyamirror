# -*- indent-tabs-mode: t -*-

# Forward declarations
cdef class _Body(_soya._World)

# World
cdef class _World(_soya._World):
		"""Dynamics world.
		
		The simulation object is a container for rigid bodies and joints.
		
		
		Constructor::
		
			_World()
		"""

		cdef public double steptime # Should be the same as the idler's round_duration
		#cdef _bodies
		cdef dWorldID _wid

		def __new__(self, *args, **kw):
				self.steptime = 0.030 # Same as idler default
				self._wid = dWorldCreate()
				#self._bodies = []

		#def __init__(self, *args, **kw):
		#    _soya._World.__init__(self, *args, **kw)

		def __dealloc__(self):
				print "__dealloc__ ode._World"
				if self._wid is not NULL:
						dWorldDestroy(self._wid)

		#cdef _add_body(self, _Body body):
		#    self._bodies.append(body)

		#def remove(self, _soya.CoordSyst child not None):
		#    if isinstance(child, _Body):
		#        self._bodies.remove(child)
		#
		#    _soya._World.remove(self, child)

		property gravity:
				"""setGravity(gravity)
 
				Set the world's global gravity vector.

				@param gravity: Gravity vector
				@type gravity: 3-sequence of floats
				"""
				def __set__(self, gravity):
						dWorldSetGravity(self._wid, gravity[0], gravity[1], gravity[2])
		
				def __get__(self):
						cdef dVector3 g
						dWorldGetGravity(self._wid, g)
						return (g[0],g[1],g[2])

		property erp:
				"""setERP(erp)

				Set the global ERP value, that controls how much error
				correction is performed in each time step. Typical values are
				in the range 0.1-0.8. The default is 0.2.

				@param erp: Global ERP value
				@type erp: float
				"""
				def __set__(self, erp):
						dWorldSetERP(self._wid, erp)

				def __get__(self):
						return dWorldGetERP(self._wid)

		property cfm:
				"""setCFM(cfm)

				Set the global CFM (constraint force mixing) value. Typical
				values are in the range 10E-9 - 1. The default is 10E-5 if
				single precision is being used, or 10E-10 if double precision
				is being used.

				@param cfm: Constraint force mixing value
				@type cfm: float
				"""
				def __set__(self, cfm):
						dWorldSetCFM(self._wid, cfm)

				def __get__(self):
						return dWorldGetCFM(self._wid)

		# We don't bother with regular steps right now
		## step
		#def step(self):
		#    """step(stepsize)
#
#        Step the world. This uses a "big matrix" method that takes
#        time on the order of O(m3) and memory on the order of O(m2), where m
#        is the total number of constraint rows.
#
#        For large systems this will use a lot of memory and can be
#        very slow, but this is currently the most accurate method.
#
#        @param stepsize: Time step
#        @type stepsize: float
#        """
#
#        dWorldStep(self._wid, self.steptime)

		def begin_round(self):
				"""quickStep(stepsize)
				
				Step the world. This uses an iterative method that takes time
				on the order of O(m*N) and memory on the order of O(m), where m is
				the total number of constraint rows and N is the number of
				iterations.

				For large systems this is a lot faster than dWorldStep, but it
				is less accurate.

				@param stepsize: Time step
				@type stepsize: float        
				"""
				#cdef _Body body

				# We call _soya._World's begin_round before stepping the simulation
				_soya._World.begin_round(self)

				# Step the simulation
				dWorldQuickStep(self._wid, self.steptime)
				
				#for body in self._bodies:
				#    body._update_matrix()

		property quickstep_num_iterations:
				"""setQuickStepNumIterations(num)
				
				Set the number of iterations that the QuickStep method
				performs per step. More iterations will give a more accurate
				solution, but will take longer to compute. The default is 20
				iterations.

				@param num: Number of iterations
				@type num: int
				"""
				def __set__(self, num):
				
						dWorldSetQuickStepNumIterations(self._wid, num)

				def __get__(self):
						return dWorldGetQuickStepNumIterations(self._wid)

		property contact_max_correcting_velocity:
				"""setContactMaxCorrectingVel(vel)

				Set the maximum correcting velocity that contacts are allowed
				to generate. The default value is infinity (i.e. no
				limit). Reducing this value can help prevent "popping" of
				deeply embedded objects.

				@param vel: Maximum correcting velocity
				@type vel: float
				"""
				def __set__(self, vel):
						dWorldSetContactMaxCorrectingVel(self._wid, vel)

				def __get__(self):
						return dWorldGetContactMaxCorrectingVel(self._wid)

		property contact_surface_layer:
				"""setContactSurfaceLayer(depth)

				Set the depth of the surface layer around all geometry
				objects. Contacts are allowed to sink into the surface layer
				up to the given depth before coming to rest. The default value
				is zero. Increasing this to some small value (e.g. 0.001) can
				help prevent jittering problems due to contacts being
				repeatedly made and broken.

				@param depth: Surface layer depth
				@type depth: float
				"""
				def __set__(self, depth):
						dWorldSetContactSurfaceLayer(self._wid, depth)

				def __get__(self):
						return dWorldGetContactSurfaceLayer(self._wid)

		property auto_disable:
				"""setAutoDisableFlag(flag)
				
				Set the default auto-disable flag for newly created bodies.

				@param flag: True = Do auto disable
				@type flag: bool
				"""
				def __set__(self, flag):
						dWorldSetAutoDisableFlag(self._wid, flag)
				
				def __get__(self):
						return dWorldGetAutoDisableFlag(self._wid)

		property auto_disable_linear_threshold:
				"""setAutoDisableLinearThreshold(threshold)
				
				Set the default auto-disable linear threshold for newly created
				bodies.

				@param threshold: Linear threshold
				@type threshold: float
				"""
				def __set__(self, threshold):
						dWorldSetAutoDisableLinearThreshold(self._wid, threshold)

				def __get__(self):
						return dWorldGetAutoDisableLinearThreshold(self._wid)

		property auto_disable_angular_threshold:
				"""setAutoDisableAngularThreshold(threshold)
				
				Set the default auto-disable angular threshold for newly created
				bodies.

				@param threshold: Angular threshold
				@type threshold: float
				"""
				def __set__(self, threshold):
						dWorldSetAutoDisableAngularThreshold(self._wid, threshold)

				def __get__(self):
						return dWorldGetAutoDisableAngularThreshold(self._wid)

		property auto_disable_steps:
				"""setAutoDisableSteps(steps)
				
				Set the default auto-disable steps for newly created bodies.

				@param steps: Auto disable steps
				@type steps: int
				"""
				def __set__(self, steps):
						dWorldSetAutoDisableSteps(self._wid, steps)

				def __get__(self):
						return dWorldGetAutoDisableSteps(self._wid)

		property auto_disable_time:
				"""setAutoDisableTime(time)
				
				Set the default auto-disable time for newly created bodies.

				@param time: Auto disable time
				@type time: float
				"""
				def __set__(self, time):
						dWorldSetAutoDisableTime(self._wid, time)

				def __get__(self):
						return dWorldGetAutoDisableTime(self._wid)

		# impulseToForce
		def impulseToForce(self, stepsize, impulse):
				"""impulseToForce(stepsize, impulse) -> 3-tuple

				If you want to apply a linear or angular impulse to a rigid
				body, instead of a force or a torque, then you can use this
				function to convert the desired impulse into a force/torque
				vector before calling the dBodyAdd... function.

				@param stepsize: Time step
				@param impulse: Impulse vector
				@type stepsize: float
				@type impulse: 3-tuple of floats
				"""
				cdef dVector3 force
				dWorldImpulseToForce(self._wid, stepsize, impulse[0], impulse[1], impulse[2], force)
				return (force[0], force[1], force[2])

#    def add_space(self, SpaceBase space not None):
#        self.spaces.append(space)

		# We use step now instead of begin_round
#    def begin_round(self):
#        """Step the simulation. This is done before the children get
#        begin_round"""
#
#        # The user needs to handle collisions
#        #for space in self.spaces:
#        #    space.collide()
#
#        dWorldQuickStep(self._wid, self.round_duration)
#
#        # Make sure all the children get the end of the round
#        _soya._World.begin_round(self)

