# -*- indent-tabs-mode: t -*-

# joints

# For every joint type there is a separate class that wraps that joint.
# These classes are derived from the base class "Joint" that contains
# all the common stuff (including destruction).
# The ODE joint is created in the constructor and destroyed in the destructor.
# So it's the respective Python wrapper class that has ownership of the
# ODE joint. If joint groups are used it can happen that an ODE joint gets
# destroyed outside of its Python wrapper (whenever you empty the group).
# In such cases the Python wrapper has to be notified so that it dismisses
# its pointer. This is done by calling _destroyed() on the respective
# Python wrapper (which is done by the _JointGroup wrapper).

# author:
#	modified by Marmoute - Pierre-Yves David - marmoute@nekeme.net


######################################################################

# _JointGroup
cdef class _JointGroup:
		"""Joint group.

		"""

		# _JointGroup ID
		#cdef dJointGroupID gid
		# A list of Python joints that were added to the group
		#cdef object jointlist

		#def __new__(self, *args, **kw):

		def __init__(_JointGroup self):
			self._OdeGroupJoinID = dJointGroupCreate(0)
			self.jointlist = []
			#print "bli"
			#print "list : %s"%self.jointlist

		def __dealloc__(self):
				if self._OdeGroupJoinID!=NULL:
					dJointGroupDestroy(self._OdeGroupJoinID)
		def __len__(self):
			return len(self.jointlist)
		# empty
		def empty(self):
				"""empty()

				Destroy all joints in the group.
				"""
				cdef _Joint j
				#print "gonna empty at the ode side"
				dJointGroupEmpty(self._OdeGroupJoinID)
				#print "have empty"
				#print "gonna print len of %s"%self.jointlist
				#print "notify deletions for %i joints"%len(self.jointlist)
				for j in self.jointlist:
					#print "hip"
					#print "notify %s" %j
					j._destroyed()
					#print "hop"
				#print "ready to proceed"		
				self.jointlist = []
				#print "proceed"


		def _addjoint(self, j):
				"""_addjoint(j)

				Add a joint to the group.  This is an internal method that is
				called by the joints.  The group has to know the Python
				wrappers because it has to notify them when the group is
				emptied (so that the ODE joints won't get destroyed
				twice). The notification is done by calling _destroyed() on
				the Python joints.

				@param j: The joint to add
				@type j: Joint
				"""
				#print "add %s to join group"%j
				self.jointlist.append(j)


######################################################################

# Joint
cdef class _Joint:
	"""Base class for all joint classes."""

	# Joint id as returned by dJointCreateXxx()
	#cdef dJointID jid
	# A reference to the world so that the world won't be destroyed while
	# there are still joints using it.
	#cdef object world
	# The feedback buffer
	#cdef dJointFeedback* feedback

	#cdef _Body _body1
	#cdef _Body _body2

	#def __new__(self, *args, **kw):
	#	self._OdeJointID = NULL
	#	self.world = None
	#	self.feedback = NULL
	#	self._body1 = None
	#	self._body2 = None
	#	#self.attach(None,None)

	def __init__(self, *a, **kw):
		raise NotImplementedError, "The Joint base class can't be used directly."
		
	cdef __getcstate__(self):
		return self._body1,self._body2
	cdef void __setcstate__(self,cstate):
		self._body1,self._body2 = cstate[0:2]
		
		
	def __getitem__(self,index):
		if index == 0:
			return self._body1
		elif index == 1:
			return self._body2
		else:
			raise IndexError("A join attach only two body")
	def __setitem__(self,index,body):
		if index == 0:
			self.attach(body,self._body2)
		elif index == 1:
			self.attach(self._body1,body)
		else:
			raise IndexError("A join attach only two body")

		
		
	def __dealloc__(self):
		self.setFeedback(False)
		#print "dealloc join"
		if self._OdeJointID!=NULL:
			self._destroy()


	cdef _destroy(self):
		#print "gonna destroy"
		dJointDestroy(self._OdeJointID)
		#print "have destroyed"
		self._destroyed()
		
	# _destroyed
	cdef void _destroyed(self):
		"""Notify the joint object about an external destruction of the ODE joint.

		This method has to be called when the underlying ODE object
		was destroyed by someone else (e.g. by a joint group). The Python
		wrapper will then refrain from destroying it again.
		"""
		#print "a"
		self._OdeJointID = NULL
		if self._body1 is not None:
			self._body1._remove_joint(self)
		if self._body2 is not None:
			self._body2._remove_joint(self)
		#print "b"

	# attach
	def attach(self, _Body body1=None, _Body body2=None):
		"""attach(body1, body2)

		Attach the joint to some new bodies.
		
		TODO: What if there's only one body.

		@param body1: First body
		@param body2: Second body
		@type body1: Body
		@type body2: Body
		"""
		cdef dBodyID bid1, bid2
		attach = False
		if body1 is not self._body1:
			attach = True
			if self._body1 is not None:
				self._body1._remove_joint(self)
			if body1 is not None:
				body1._add_joint(self)
			self._body1 = body1
		if body2 is not self._body2:
			attach = True
			if self._body2 is not None:
				self._body2._remove_joint(self)
			if body2 is not None:
				body2._add_joint(self)
			self._body2 = body2

		if attach:
			# getting the body ID
			#for 1
			if body1 is not None:
				if body1._option & BODY_ODE_INVALIDE_POS:
					body1._sync_ode_position()
				bid1 = body1._OdeBodyID
			else:
				bid1 = NULL
			#for 2
			if body2 is not None:
				if body2._option & BODY_ODE_INVALIDE_POS:
					body2._sync_ode_position()
				bid2 = body2._OdeBodyID
			else:
				bid2 = NULL
	
			dJointAttach(self._OdeJointID, bid1, bid2)
			

	def setFeedback(self, flag=1):
		"""setFeedback(flag=True)

		Create a feedback buffer. If flag is True then a buffer is
		allocated and the forces/torques applied by the joint can
		be read using the getFeedback() method. If flag is False the
		buffer is released.

		@param flag: Specifies whether a buffer should be created or released
		@type flag: bool
		"""
		
		if flag:
			# Was there already a buffer allocated? then we're finished
			if self.feedback!=NULL:
				return
			# Allocate a buffer and pass it to ODE
			self.feedback = <dJointFeedback*>malloc(sizeof(dJointFeedback))
			if self.feedback==NULL:
				raise MemoryError("can't allocate feedback buffer")
			dJointSetFeedback(self._OdeJointID, self.feedback)
		else:
			if self.feedback!=NULL:
				# Free a previously allocated buffer
				dJointSetFeedback(self._OdeJointID, NULL)
				free(self.feedback)
				self.feedback = NULL
		
	# getFeedback
	def getFeedback(self):
			"""getFeedback() -> (force1, torque1, force2, torque2)

			Get the forces/torques applied by the joint. If feedback is
			activated (i.e. setFeedback(True) was called) then this method
			returns a tuple (force1, torque1, force2, torque2) with the
			forces and torques applied to body 1 and body 2.  The
			forces/torques are given as 3-tuples.

			If feedback is deactivated then the method always returns None.
			"""
			cdef dJointFeedback* fb
			
			fb = dJointGetFeedback(self._OdeJointID)
			if (fb==NULL):
					return None
				 
			f1 = (fb.f1[0], fb.f1[1], fb.f1[2])
			t1 = (fb.t1[0], fb.t1[1], fb.t1[2])
			f2 = (fb.f2[0], fb.f2[1], fb.f2[2])
			t2 = (fb.t2[0], fb.t2[1], fb.t2[2])
			return (f1,t1,f2,t2)

	cdef void _setParam(self, int param, dReal value):
			raise ValueError, "_setParam not implemented!"

	cdef dReal _getParam(self, int param):
			raise ValueError, "_getParam not implemented!"

	property lo_stop:
			def __get__(self):
					return self._getParam(ParamLoStop)

			def __set__(self, dReal value):
					if value is None:
						value = -dInfinity
					self._setParam(ParamLoStop, value)
	
	property hi_stop:
			def __get__(self):
					return self._getParam(ParamHiStop)

			def __set__(self, dReal value):
					if value is None:
						value = dInfinity
					self._setParam(ParamHiStop, value)
	
	property velocity:
			def __get__(self):
					return self._getParam(ParamVel)

			def __set__(self, dReal value):
					self._setParam(ParamVel, value)
	
	property fmax:
			def __get__(self):
					return self._getParam(ParamFMax)

			def __set__(self, dReal value):
					self._setParam(ParamFMax, value)
	
	property fudge_factor:
			def __get__(self):
					return self._getParam(ParamFudgeFactor)

			def __set__(self, dReal value):
					self._setParam(ParamFudgeFactor, value)
	
	property bounce:
			def __get__(self):
					return self._getParam(ParamBounce)

			def __set__(self, dReal value):
					self._setParam(ParamBounce, value)
	
	property cfm:
			def __get__(self):
					return self._getParam(ParamCFM)

			def __set__(self, dReal value):
					self._setParam(ParamCFM, value)
	
	property stop_erp:
			def __get__(self):
					return self._getParam(ParamStopERP)

			def __set__(self, dReal value):
					self._setParam(ParamStopERP, value)
	
	property stop_cfm:
			def __get__(self):
					return self._getParam(ParamStopCFM)

			def __set__(self, dReal value):
					self._setParam(ParamStopCFM, value)
	
	property suspension_erp:
			def __get__(self):
					return self._getParam(ParamSuspensionERP)

			def __set__(self, dReal value):
					self._setParam(ParamSuspensionERP, value)
	
	property suspension_cfm:
			def __get__(self):
					return self._getParam(ParamSuspensionCFM)

			def __set__(self, dReal value):
					self._setParam(ParamSuspensionCFM, value)
	
	property lo_stop2:
			def __get__(self):
					return self._getParam(ParamLoStop2)

			def __set__(self, dReal value):
					self._setParam(ParamLoStop2, value)
	
	property hi_stop2:
			def __get__(self):
					return self._getParam(ParamHiStop2)

			def __set__(self, dReal value):
					self._setParam(ParamHiStop2, value)
	
	property velocity2:
			def __get__(self):
					return self._getParam(ParamVel2)

			def __set__(self, dReal value):
					self._setParam(ParamVel2, value)
	
	property fmax2:
			def __get__(self):
					return self._getParam(ParamFMax2)

			def __set__(self, dReal value):
					self._setParam(ParamFMax2, value)
	
	property fudge_factor2:
			def __get__(self):
					return self._getParam(ParamFudgeFactor2)

			def __set__(self, dReal value):
					self._setParam(ParamFudgeFactor2, value)
	
	property bounce2:
			def __get__(self):
					return self._getParam(ParamBounce2)

			def __set__(self, dReal value):
					self._setParam(ParamBounce2, value)
	
	property cfm2:
			def __get__(self):
					return self._getParam(ParamCFM2)

			def __set__(self, dReal value):
					self._setParam(ParamCFM2, value)
	
	property stop_erp2:
			def __get__(self):
					return self._getParam(ParamStopERP2)

			def __set__(self, dReal value):
					self._setParam(ParamStopERP2, value)
	
	property stop_cfm2:
			def __get__(self):
					return self._getParam(ParamStopCFM2)

			def __set__(self, dReal value):
					self._setParam(ParamStopCFM2, value)
	
	property suspension_erp2:
			def __get__(self):
					return self._getParam(ParamSuspensionERP2)

			def __set__(self, dReal value):
					self._setParam(ParamSuspensionERP2, value)
	
	property suspension_cfm2:
			def __get__(self):
					return self._getParam(ParamSuspensionCFM2)

			def __set__(self, dReal value):
					self._setParam(ParamSuspensionCFM2, value)


######################################################################

# BallJoint
cdef class BallJoint(_Joint):
	"""Ball joint.

	"""

	#def __new__(self, _World world not None, jointgroup=None, *args, **kw):
	#		cdef _JointGroup jg
	#		cdef dJointGroupID jgid
	#
	#		jgid=NULL
	#		if jointgroup!=None:
	#				jg=jointgroup
	#				jgid=jg._OdeGroupJoinID
	#		self._OdeJointID = dJointCreateBall(world._OdeWorldID, jgid)

	def __init__(self,_Body body1=None, _Body body2=None,_World world=None,_JointGroup group= None):
		cdef dJointGroupID gid
		if body1 is not None:
			world = body1._ode_parent
			if body2 is not None and body2.ode_parent is not world:
				raise RuntimeError("two body must be into the same world to be jointed")
		elif body2 is not None:
			world = body2._ode_parent
		elif world is None:
			raise RuntimeError("A joint need a world to be created, specify a least a body to joint or a world to create a limbo Joint")
		if group is not None:
			group._addjoint(self)
			gid = group._OdeGroupJoinID
		else:
			gid = NULL
		self._OdeJointID = dJointCreateBall(world._OdeWorldID,gid)
		self.world = world
		self.attach(body1, body2)
				
	property anchor:
			"""setAnchor(pos)

			Set the joint anchor point.

			@param pos: Anchor position
			@type pos: Point
			"""
			def __set__(self, _Point pos):
					cdef float p[3]
					pos._into(self.world, p)
					dJointSetBallAnchor(self._OdeJointID, p[0], p[1], p[2])
	
			def __get__(self):
					cdef dVector3 p
					dJointGetBallAnchor(self._OdeJointID, p)
					return Point(self.world, p[0],p[1],p[2])
	
	property anchor2:
			"""getAnchor2() -> Point

			Get the joint anchor point,  This
			returns the point on body 2. If the joint is perfectly
			satisfied, this will be the same as the point on body 1.
			"""
			def __get__(self):
					cdef dVector3 p
					dJointGetBallAnchor2(self._OdeJointID, p)
					return Point(self.world, p[0],p[1],p[2])

	# setParam #XXX what's that ?
	cdef void _setParam(self, int param, dReal value):
			pass

	# getParam
	cdef dReal _getParam(self, int param):
			return 0.0
			
 
# HingeJoint
cdef class HingeJoint(_Joint):
	"""Hinge joint.

	"""

	#def __new__(self, _World world not None, _JointGroup jointgroup=None, *args, **kw):
	#		cdef _JointGroup jg
	#		cdef dJointGroupID jgid
	#		
	#		jgid=NULL
	#		if jointgroup!=None:
	#				jg=jointgroup
	#				jgid=jg._OdeGroupJoinID
	#		self._OdeJointID = dJointCreateHinge(world._OdeWorldID, jgid)
	#		
	def __init__(self,_Body body1=None, _Body body2=None,_World world=None,_JointGroup group= None):
		cdef dJointGroupID gid
		if body1 is not None:
			world = body1._ode_parent
			if body2 is not None and body2.ode_parent is not world:
				raise RuntimeError("two body must be into the same world to be jointed")
		elif body2 is not None:
			world = body2._ode_parent
		elif world is None:
			raise RuntimeError("A joint need a world to be created, specify a least a body to joint or a world to create a limbo Joint")
		if group is not None:
			group._addjoint(self)
			gid = group._OdeGroupJoinID
		else:
			gid = NULL
		self._OdeJointID = dJointCreateHinge(world._OdeWorldID,gid)
		self.world = world
		self.attach(body1, body2)
		
		
	property anchor:
			"""setAnchor(pos)

			Set the joint anchor point.

			@param pos: Anchor position
			@type pos: Point
			"""
			def __set__(self, _Point pos):
					cdef float p[3]
					pos._into(self.world, p)
					dJointSetHingeAnchor(self._OdeJointID, p[0], p[1], p[2])
	
			def __get__(self):
					cdef dVector3 p
					dJointGetHingeAnchor(self._OdeJointID, p)
					return Point(self.world, p[0],p[1],p[2])
	
	property anchor2:
		"""getAnchor2() -> Point

		Get the joint anchor point,  This
		returns the point on body 2. If the joint is perfectly
		satisfied, this will be the same as the point on body 1.
		"""
		def __get__(self):
				cdef dVector3 p
				dJointGetHingeAnchor2(self._OdeJointID, p)
				return Point(self.world, p[0],p[1],p[2])

	property axis:

		"""setAxis(axis)

		Set the hinge axis.

		@param axis: Hinge axis
		@type axis: Vector
		"""
		# XXX use Soya vectors
		def __set__(self, _Vector axis):
			cdef float a[3]
			axis._into(self.world, a)
			dJointSetHingeAxis(self._OdeJointID, a[0], a[1], a[2])

		def __get__(self):
			cdef dVector3 a
			dJointGetHingeAxis(self._OdeJointID, a)
			return Vector(self.world,a[0],a[1],a[2])
	
	property angle:
			"""getAngle() -> float

			Get the hinge angle. The angle is measured between the two
			bodies, or between the body and the static environment. The
			angle will be between -pi..pi.

			When the hinge anchor or axis is set, the current position of
			the attached bodies is examined and that position will be the
			zero angle.
			"""
			def __get__(self):
					return dJointGetHingeAngle(self._OdeJointID)

	property angle_rate:
			"""getAngleRate() -> float

			Get the time derivative of the angle.
			"""
			def __get__(self):
					return dJointGetHingeAngleRate(self._OdeJointID)

	# setParam
	cdef void _setParam(self, int param, dReal value):
			"""setParam(param, value)

			Set limit/motor parameters for the joint.

			param is one of ParamLoStop, ParamHiStop, ParamVel, ParamFMax,
			ParamFudgeFactor, ParamBounce, ParamCFM, ParamStopERP, ParamStopCFM,
			ParamSuspensionERP, ParamSuspensionCFM.

			These parameter names can be optionally followed by a digit (2
			or 3) to indicate the second or third set of parameters.

			@param param: Selects the parameter to set
			@param value: Parameter value 
			@type param: int
			@type value: float
			"""
			
			dJointSetHingeParam(self._OdeJointID, param, value)

	# getParam
	cdef dReal _getParam(self, int param):
			"""getParam(param) -> float

			Get limit/motor parameters for the joint.

			param is one of ParamLoStop, ParamHiStop, ParamVel, ParamFMax,
			ParamFudgeFactor, ParamBounce, ParamCFM, ParamStopERP, ParamStopCFM,
			ParamSuspensionERP, ParamSuspensionCFM.

			These parameter names can be optionally followed by a digit (2
			or 3) to indicate the second or third set of parameters.

			@param param: Selects the parameter to read
			@type param: int        
			"""
			return dJointGetHingeParam(self._OdeJointID, param)
			
			
# SliderJoint
cdef class SliderJoint(_Joint):
	"""Slider joint.
	
	"""

	#def __new__(self, _World world not None, jointgroup=None, *args, **kw):
	#		cdef _JointGroup jg
	#		cdef dJointGroupID jgid
	#
	#		jgid=NULL
	#		if jointgroup!=None:
	#				jg=jointgroup
	#				jgid=jg._OdeGroupJoinID
	#		self._OdeJointID = dJointCreateSlider(world._OdeWorldID, jgid)

	def __init__(self,_Body body1=None, _Body body2=None,_World world=None,_JointGroup group= None):
		cdef dJointGroupID gid
		if body1 is not None:
			world = body1._ode_parent
			if body2 is not None and body2.ode_parent is not world:
				raise RuntimeError("two body must be into the same world to be jointed")
		elif body2 is not None:
			world = body2._ode_parent
		elif world is None:
			raise RuntimeError("A joint need a world to be created, specify a least a body to joint or a world to create a limbo Joint")
		if group is not None:
			group._addjoint(self)
			gid = group._OdeGroupJoinID
		else:
			gid = NULL
		self._OdeJointID = dJointCreateSlider(world._OdeWorldID,gid)
		self.world = world
		self.attach(body1, body2)
			
	property axis:
		"""setAxis(axis)

		Set the slider axis parameter.

		@param axis: Slider axis
		@type axis: 3-sequence of floats        
		"""
		def __set__(self, _Vector axis):
			cdef float a[3]
			axis._into(self.world, a)
			dJointSetSliderAxis(self._OdeJointID, a[0], a[1], a[2])

		def __get__(self):
			cdef dVector3 a
			dJointGetSliderAxis(self._OdeJointID, a)
			return Vector(self.world, a[0],a[1],a[2])

	property position:
			"""getPosition() -> float

			Get the slider linear position (i.e. the slider's "extension").

			When the axis is set, the current position of the attached
			bodies is examined and that position will be the zero
			position.
			"""
			def __get__(self):
					return dJointGetSliderPosition(self._OdeJointID)

	property position_rate:
			"""getPositionRate() -> float

			Get the time derivative of the position.
			"""
			def __get__(self):
					return dJointGetSliderPositionRate(self._OdeJointID)

	# setParam
	cdef void _setParam(self, int param, dReal value):
			dJointSetSliderParam(self._OdeJointID, param, value)

	# getParam
	cdef dReal _getParam(self, int param):
			return dJointGetSliderParam(self._OdeJointID, param)
			
	
# UniversalJoint
cdef class UniversalJoint(_Joint):
	"""Universal joint."""

	#def __new__(self, _World world not None, jointgroup=None, *args, **kw):
	#		cdef _JointGroup jg
	#		cdef dJointGroupID jgid
	#
	#		jgid=NULL
	#		if jointgroup!=None:
	#				jg=jointgroup
	#				jgid=jg._OdeGroupJoinID
	#		self._OdeJointID = dJointCreateUniversal(world._OdeWorldID, jgid)

	def __init__(self,_Body body1=None, _Body body2=None,_World world=None,_JointGroup group= None):
		cdef dJointGroupID gid
		if body1 is not None:
			world = body1._ode_parent
			if body2 is not None and body2.ode_parent is not world:
				raise RuntimeError("two body must be into the same world to be jointed")
		elif body2 is not None:
			world = body2._ode_parent
		elif world is None:
			raise RuntimeError("A joint need a world to be created, specify a least a body to joint or a world to create a limbo Joint")
		if group is not None:
			group._addjoint(self)
			gid = group._OdeGroupJoinID
		else:
			gid = NULL
		self._OdeJointID = dJointCreateUniversal(world._OdeWorldID,gid)
		self.world = world
		self.attach(body1, body2)

	property anchor:
			"""setAnchor(pos)

			Set the hinge anchor.

			@param pos: Anchor position
			@type pos: Point         
			"""
			def __set__(self,_Point pos):
				cdef float p[3]
				pos._into(self.world, p)
				dJointSetUniversalAnchor(self._OdeJointID, p[0], p[1], p[2])
	
			def __get__(self):
				cdef dVector3 p
				dJointGetUniversalAnchor(self._OdeJointID, p)
				return Point(self.world, p[0], p[1], p[2])

	property anchor2:
			"""getAnchor2() -> Point

			Get the joint anchor point, in world coordinates. This returns
			the point on body 2. If the joint is perfectly satisfied, this
			will be the same as the point on body 1.
			"""
			def __get__(self):
					cdef dVector3 p
					dJointGetUniversalAnchor2(self._OdeJointID, p)
					return Point(self.world, p[0], p[1], p[2])

	property axis1:
		"""setAxis1(axis)

		Set the first universal axis. Axis 1 and axis 2 should be
		perpendicular to each other.

		@param axis: Joint axis
		@type axis: Vector
		"""
		def __set__(self, _Vector axis):
			cdef float a[3]
			axis._into(self.world, a)
			dJointSetUniversalAxis1(self._OdeJointID, a[0], a[1], a[2])

		def __get__(self):
			cdef dVector3 a
			dJointGetUniversalAxis1(self._OdeJointID, a)
			return Vector(self.world, a[0], a[1], a[2])

	property axis2:
		"""setAxis2(axis)

		Set the second universal axis. Axis 1 and axis 2 should be
		perpendicular to each other.

		@param axis: Joint axis
		@type axis: Vector
		"""
		def __set__(self, _Vector axis):
			cdef float a[3]
			axis._into(self.world, a)
			dJointSetUniversalAxis2(self._OdeJointID, a[0], a[1], a[2])

		def __get__(self):
			cdef dVector3 a
			dJointGetUniversalAxis2(self._OdeJointID, a)
			return Vector(self.world, a[0], a[1], a[2])
	
	# setParam
	cdef void _setParam(self, int param, dReal value):
			dJointSetUniversalParam(self._OdeJointID, param, value)

	# getParam
	cdef dReal _getParam(self, int param):
			return dJointGetUniversalParam(self._OdeJointID, param)

	
# Hinge2Joint
cdef class Hinge2Joint(_Joint):
	"""Hinge2 joint.

	"""

	#def __new__(self, _World world not None, jointgroup=None, *args, **kw):
	#		cdef _JointGroup jg
	#		cdef dJointGroupID jgid
	#
	#		jgid=NULL
	#		if jointgroup!=None:
	#				jg=jointgroup
	#				jgid=jg._OdeGroupJoinID
	#		self._OdeJointID = dJointCreateHinge2(world._OdeWorldID, jgid)

	def __init__(self,_Body body1=None, _Body body2=None,_World world=None,_JointGroup group= None):
		cdef dJointGroupID gid
		if body1 is not None:
			world = body1._ode_parent
			if body2 is not None and body2.ode_parent is not world:
				raise RuntimeError("two body must be into the same world to be jointed")
		elif body2 is not None:
			world = body2._ode_parent
		elif world is None:
			raise RuntimeError("A joint need a world to be created, specify a least a body to joint or a world to create a limbo Joint")
		if group is not None:
			group._addjoint(self)
			gid = group._OdeGroupJoinID
		else:
			gid = NULL
		self._OdeJointID = dJointCreateHinge2(world._OdeWorldID,gid)
		self.world = world
		self.attach(body1, body2)

	property anchor:
		"""setAnchor(pos)

		Set the hinge anchor.

		@param pos: Anchor position
		@type pos: Point
		"""
		def __set__(self,_Point pos):
			cdef float p[3]
			pos._into(self.world, p)
			dJointSetHinge2Anchor(self._OdeJointID, pos.x, pos.y, pos.z)

		def __get__(self):
			cdef dVector3 p
			dJointGetHinge2Anchor(self._OdeJointID, p)
			return Point(self.world,p[0],p[1],p[2])

	property anchor2:
		"""getAnchor2() -> Point

		Get the joint anchor point, in world coordinates. This returns
		the point on body 2. If the joint is perfectly satisfied, this
		will be the same as the point on body 1.
		"""
		def __get__(self):
			cdef dVector3 p
			dJointGetHinge2Anchor2(self._OdeJointID, p)
			return Point(self.world,p[0],p[1],p[2])

	property axis1:
		"""setAxis1(axis)

		Set the first universal axis. Axis 1 and axis 2 should be
		perpendicular to each other.

		@param axis: Joint axis
		@type axis: 3-sequence of floats
		"""
		def __set__(self, _Vector axis):
			cdef float a[3]
			axis._into(self.world, a)
			dJointSetHinge2Axis1(self._OdeJointID, a[0], a[1], a[2])

		def __get__(self):
			cdef dVector3 a
			dJointGetHinge2Axis1(self._OdeJointID, a)
			return Vector(self.world,a[0],a[1],a[2])

	property axis2:
		"""setAxis2(axis)

		Set the second universal axis. Axis 1 and axis 2 should be
		perpendicular to each other.

		@param axis: Joint axis
		@type axis: 3-sequence of floats        
		"""
		def __set__(self, _Vector axis):
			cdef float a[3]
			axis._into(self.world, a)
			dJointSetHinge2Axis2(self._OdeJointID, a[0], a[1], a[2])

		def __get__(self):
			cdef dVector3 a
			dJointGetHinge2Axis2(self._OdeJointID, a)
			return Vector(self.world,a[0],a[1],a[2])
	
	property angle1:
			"""getAngle1() -> float

			Get the first hinge-2 angle (around axis 1).

			When the anchor or axis is set, the current position of the
			attached bodies is examined and that position will be the zero
			angle.
			"""
			def __get__(self):
					return dJointGetHinge2Angle1(self._OdeJointID)
					#YYY check this value

	property angle1_rate:
		"""getAngle1Rate() -> float

		Get the time derivative of the first hinge-2 angle.
		"""
		def __get__(self):
			return dJointGetHinge2Angle1Rate(self._OdeJointID)
			#YYY check this value

	property angle2_rate:
		"""getAngle2Rate() -> float

		Get the time derivative of the second hinge-2 angle.
		"""
		def __get__(self):
			return dJointGetHinge2Angle2Rate(self._OdeJointID)
			#YYY check this value

	# setParam
	cdef void _setParam(self, int param, dReal value):
			dJointSetHinge2Param(self._OdeJointID, param, value)

	# getParam
	cdef dReal _getParam(self, int param):
			return dJointGetHinge2Param(self._OdeJointID, param)

	
# FixedJoint
cdef class FixedJoint(_Joint):
	"""Fixed joint.

	"""

	#def __new__(self, _World world not None, jointgroup=None, *args, **kw):
	#		cdef _JointGroup jg
	#		cdef dJointGroupID jgid
	#
	#		jgid=NULL
	#		if jointgroup!=None:
	#				jg=jointgroup
	#				jgid=jg._OdeGroupJoinID
	#		self._OdeJointID = dJointCreateFixed(world._OdeWorldID, jgid)

	def __init__(self,_Body body1=None, _Body body2=None,_World world=None,_JointGroup group= None):
		cdef dJointGroupID gid
		if body1 is not None:
			world = body1._ode_parent
			if body2 is not None and body2.ode_parent is not world:
				raise RuntimeError("two body must be into the same world to be jointed")
		elif body2 is not None:
			world = body2._ode_parent
		elif world is None:
			raise RuntimeError("A joint need a world to be created, specify a least a body to joint or a world to create a limbo Joint")
		if group is not None:
			group._addjoint(self)
			gid = group._OdeGroupJoinID
		else:
			gid = NULL
		self._OdeJointID = dJointCreateFixed(world._OdeWorldID,gid)
		self.world = world
		self.attach(body1, body2)

	# setFixed
	def setFixed(self):
			"""setFixed()

			Call this on the fixed joint after it has been attached to
			remember the current desired relative offset and desired
			relative rotation between the bodies.
			"""
			dJointSetFixed(self._OdeJointID)

			
# AMotor
cdef class AngularMotor(_Joint):
	"""AMotor joint.
	"""

	#def __new__(self, _World world not None, jointgroup=None, *args, **kw):
	#		cdef _JointGroup jg
	#		cdef dJointGroupID jgid
	#
	#		jgid = NULL
	#		if jointgroup!=None:
	#				jg = jointgroup
	#				jgid = jg._OdeGroupJoinID
	#		self._OdeJointID = dJointCreateAMotor(world._OdeWorldID, jgid)

	def __init__(self,_Body body1=None, _Body body2=None,_World world=None,_JointGroup group= None):
		cdef dJointGroupID gid
		if body1 is not None:
			world = body1._ode_parent
			if body2 is not None and body2.ode_parent is not world:
				raise RuntimeError("two body must be into the same world to be jointed")
		elif body2 is not None:
			world = body2._ode_parent
		elif world is None:
			raise RuntimeError("A joint need a world to be created, specify a least a body to joint or a world to create a limbo Joint")
		if group is not None:
			group._addjoint(self)
			gid = group._OdeGroupJoinID
		else:
			gid = NULL
		self._OdeJointID = dJointCreateAMotor(world._OdeWorldID,gid)
		self.world = world
		self.attach(body1, body2)
		self.mode = dAMotorUser
		
					
	property mode:
			"""setMode(mode)

			Set the angular motor mode.  mode must be either AMotorUser or
			AMotorEuler.

			@param mode: Angular motor mode
			@type mode: int
			"""
			def __set__(self, mode):
					dJointSetAMotorMode(self._OdeJointID, mode)

			def __get__(self):
					return dJointGetAMotorMode(self._OdeJointID)
	
	property nb_axes:
		def __get__(self):
			"""get nb_axes() -> int

			Get the number of angular axes that are controlled by the AMotor.
			"""
			return dJointGetAMotorNumAxes(self._OdeJointID)
		def __set__(self, int num):
			"""set nb_Axes(num)

			Set the number of angular axes that will be controlled by the AMotor.
			num must be in the range from 0 to 3.

			@param num: Number of axes (0-3)
			@type num: int
			"""
			if 0 < num <= 3:
				dJointSetAMotorNumAxes(self._OdeJointID, num)
			else:
				raise RuntimeError("An the number of angle must be in the range 0-3")

			
			
	

	def setAxis(self, int anum, int rel, _Vector axis):
			"""setAxis(anum, rel, axis)

			Set an AMotor axis.

			The anum argument selects the axis to change (0,1 or 2).

			rel:    Each axis can have one of three ``relative orientation'' modes.
				0: The axis is anchored to the global frame.
				1: The axis is anchored to the first body.
				2: The axis is anchored to the second body.


			The axis vector is always specified in global coordinates
			regardless of the setting of rel.

			@param anum: Axis number
			@param axis: Axis
			@type anum: int
			@type axis: Vector
			"""
			cdef float a[3]
			axis._into(self.world, a)
			if rel < 0 or rel > 2:
				raise RuntimeError("rel paramets must be in the range 0, 1 or 2")
			dJointSetAMotorAxis(self._OdeJointID, anum, rel, a[0], a[1], a[2])

	# getAxis
	def getAxis(self, int anum):
			"""getAxis(anum)

			Get an AMotor axis.

			@param anum: Axis index (0-2)
			@type anum: int        
			"""
			cdef dVector3 a
			dJointGetAMotorAxis(self._OdeJointID, anum, a)
			return Vector(self.world,a[0],a[1],a[2])

	
	def setAngle(self, int anum, angle):
			"""setAngle(anum, angle)

			Tell the AMotor what the current angle is along axis anum.

			@param anum: Axis index
			@param angle: Angle
			@type anum: int
			@type angle: float
			"""
			dJointSetAMotorAngle(self._OdeJointID, anum, angle)

	# getAngle
	def getAngle(self, int anum):
			"""getAngle(anum) -> float

			Return the current angle for axis anum.

			@param anum: Axis index
			@type anum: int        
			"""
			return dJointGetAMotorAngle(self._OdeJointID, anum)

	# getAngleRate
	def getAngleRate(self, int anum):
			"""getAngleRate(anum) -> float

			Return the current angle rate for axis anum.

			@param anum: Axis index
			@type anum: int        
			"""
			return dJointGetAMotorAngleRate(self._OdeJointID, anum)

	# setAngleRate
	def setAngleRate(self, int anum, dReal rate):
			"""getAngleRate(anum) -> float

			Set the angle rate for axis anum.

			@param anum: Axis index
			@type anum: int        

			@param anum: Angular Rate
			@type anum: float
			"""
			dJointSetAMotorParam(self._OdeJointID, anum, rate)

	# setParam
	cdef void _setParam(self, int param, dReal value):
			dJointSetAMotorParam(self._OdeJointID, param, value)

	# getParam
	cdef dReal _getParam(self, int param):
			return dJointGetAMotorParam(self._OdeJointID, param)


