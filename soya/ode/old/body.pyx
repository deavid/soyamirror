# -*- indent-tabs-mode: t -*-

# Forward declarations
cdef class Joint

# Body
cdef class _Body(_soya._World):
		"""The rigid body class encapsulating the ODE body.

		This class represents a rigid body that has a location and orientation
		in space and that stores the mass properties of an object.

		When creating a Body object you have to pass the world it belongs to
		as argument to the constructor::

			>>> import ode
			>>> w = ode.World()
			>>> b = ode.Body(w)
		"""

		cdef dBodyID _bid
		#cdef _World _world

		#cdef dReal *_R # Rotation matrix of the ODE body
		#cdef dReal *_P # Position array of the ODE body
		cdef GLfloat _q[4] # Previous quaternion
		cdef GLfloat _p[4] # Previous position
		cdef float _t # Cumulative round time
		cdef int _valid # Is the previous quaternion/position valid?
		cdef readonly joints
		
		def __new__(self, _World world=None, *args, **kw):

				#self._world = world

				if world is None:
						self._bid = NULL
						#self._R = NULL
						#self._P = NULL
				else:
						self._bid = dBodyCreate(world._wid)
						#world._add_body(self)
						#self._R = dBodyGetRotation(self._bid)
						#self._P = dBodyGetPosition(self._bid)

				self._valid = 0

		def __init__(self, _World world=None, *args, **kw):
				self.joints = []
				_soya._World.__init__(self, world, *args, **kw)

		def __dealloc__(self):
				print '__dealloc__ ode._Body'
				if self._bid!=NULL:
						dBodyDestroy(self._bid)

		cdef void _add_joint(self, Joint joint):
				self.joints.append(joint)

		cdef void _remove_joint(self, Joint joint):
				self.joints.remove(joint)

		def begin_round(self):
				"""Save the previous quaternion and position for interpolation.
				We can do this in begin_round because the simulation calls
				begin_round before stepping."""
				cdef dReal *q

				q = dBodyGetQuaternion(self._bid)
				self._q[0] = q[1]
				self._q[1] = q[2]
				self._q[2] = q[3]
				self._q[3] = q[0]

				q = dBodyGetPosition(self._bid)
				self._p[0] = q[0]
				self._p[1] = q[1]
				self._p[2] = q[2]

				self._valid = 1 # Mark the saved stuff as valid
				self._t = 0.0   # Reset the round time accumulator

#    cdef void _update_matrix(self):
#        """Copy attributes from the body back to _matrix"""
#
#        cdef GLfloat *m
#
#        # Only copy if the body is enabled
#        if dBodyIsEnabled(self._bid):
#            m = self._matrix
#            m[12] = self._P[0]
#            m[13] = self._P[1]
#            m[14] = self._P[2]
#            m[16] = 1.0
#            m[17] = 1.0
#            m[18] = 1.0
#
#            m[0] = self._R[0]
#            m[1] = self._R[4]
#            m[2] = self._R[8]
#            m[4] = self._R[1]
#            m[5] = self._R[5]
#            m[6] = self._R[9]
#            m[8] = self._R[2]
#            m[9] = self._R[6]
#            m[10] = self._R[10]
#
#            # Don't need to do this now because we require that bodies
#            # be direct children of the Simulation
#            #_soya.multiply_matrix(r, self.world._root_matrix(), m)
#            #_soya.multiply_matrix(self._matrix, self._parent._inverted_root_matrix(), r)
#            # We call _soya._World._invalidate instead of self._invalidate
#            # because self._invalidate has been overridden to to update
#            # the ODE rotation and position when the Body is moved manually.
#            _soya._World._invalidate(self)


		cdef void _invalidate(self):
				"""Update the body's matrix after invalidating the root and inverted
				root matrices. We do this here because all movement methods must
				call this."""

				cdef dMatrix3 R
				cdef GLfloat *m

				_soya._World._invalidate(self)
				# Don't need to do this any more because we know we are a direct
				# child of the Simulation.
				#_soya.multiply_matrix(m, self._root_matrix(), self.world._inverted_root_matrix())

				m = self._matrix
				R[0] = m[0]
				R[1] = m[4]
				R[2] = m[8]
				R[3] = 0.0
				R[4] = m[1]
				R[5] = m[5]
				R[6] = m[9]
				R[7] = 0.0
				R[8] = m[2]
				R[9] = m[6]
				R[10] = m[10]
				R[11] = 0.0

				# XXX Overriding the movement methods would be faster due to the fact
				# that we wouldn't have to copy the rotation matrix as well
				dBodySetPosition(self._bid, m[12], m[13], m[14])
				dBodySetRotation(self._bid, R)

				# Mark the previous position and quaternion as invalid
				self._valid = 0

		def advance_time(self, float proportion):
				"""Interpolate between the last two quaternions"""
				cdef GLfloat q[4]
				cdef dReal *r, *p
				cdef float t

				self._t = self._t + proportion

				if dBodyIsEnabled(self._bid):
						r = dBodyGetQuaternion(self._bid)
						p = dBodyGetPosition(self._bid)
						if self._valid:
								t = 1.0 - self._t
		
								# Linearly interpolate between the current quaternion and the last
								# one
								q[0] = t * self._q[0] + self._t * r[1]
								q[1] = t * self._q[1] + self._t * r[2]
								q[2] = t * self._q[2] + self._t * r[3]
								q[3] = t * self._q[3] + self._t * r[0]
						
								# Convert the quaternion to a matrix (also normalizes)
								_soya.matrix_from_quaternion(self._matrix, q)
								# Interpolate the position, too
				
								self._matrix[12] = t * self._p[0] + self._t * p[0]
								self._matrix[13] = t * self._p[1] + self._t * p[1]
								self._matrix[14] = t * self._p[2] + self._t * p[2]
				
						else:
								# Use the current quaternion and position
								q[0] = r[1]
								q[1] = r[2]
								q[2] = r[3]
								q[3] = r[0]
								_soya.matrix_from_quaternion(self._matrix, q)
								self._matrix[12] = p[0]
								self._matrix[13] = p[1]
								self._matrix[14] = p[2]
				
						# Call _soya._World's _invalidate since we override _invalidate
						# to detect when the position is updated externally
						_soya._World._invalidate(self)

				# Make sure advance_time is called on all our children
				_soya._World.advance_time(self, proportion)

		property linear_velocity:
				def __set__(self, vel):
						dBodySetLinearVel(self._bid, vel[0], vel[1], vel[2])


				def __get__(self):
						cdef dReal* p
						p = <dReal*>dBodyGetLinearVel(self._bid)
						return (p[0], p[1], p[2])

		property angular_velocity:
				def __set__(self, vel):
						"""setAngularVel(vel)

						Set the angular velocity of the body.
		
						@param vel: New angular velocity
						@type vel: 3-sequence of floats
						"""
						dBodySetAngularVel(self._bid, vel[0], vel[1], vel[2])

				def __get__(self):
						"""getAngularVel() -> 3-tuple

						Get the current angular velocity of the body.
						"""
						cdef dReal* p
						# The "const" in the original return value is cast away
						p = <dReal*>dBodyGetAngularVel(self._bid)
						return (p[0],p[1],p[2])
		
		property mass:
				def __set__(self, Mass mass):
						"""setMass(mass)
		
						Set the mass properties of the body. The argument mass must be
						an instance of a Mass object.
		
						@param mass: Mass properties
						@type mass: Mass
						"""
						dBodySetMass(self._bid, &mass._mass)
		
				def __get__(self):
						"""getMass() -> mass
		
						Return the mass properties as a Mass object.
						"""
						cdef Mass m
						m=Mass()
						dBodyGetMass(self._bid, &m._mass)
						return m

		# addForce
		def addForce(self, f):
				"""addForce(f)

				Add an external force f given in absolute coordinates. The force
				is applied at the center of mass.

				@param f: Force
				@type f: 3-sequence of floats
				"""
				dBodyAddForce(self._bid, f[0], f[1], f[2])

		# addTorque
		def addTorque(self, t):
				"""addTorque(t)

				Add an external torque t given in absolute coordinates.

				@param t: Torque
				@type t: 3-sequence of floats
				"""
				dBodyAddTorque(self._bid, t[0], t[1], t[2])

		# addRelForce
		def addRelForce(self, f):
				"""addRelForce(f)

				Add an external force f given in relative coordinates
				(relative to the body's own frame of reference). The force
				is applied at the center of mass.

				@param f: Force
				@type f: 3-sequence of floats
				"""
				dBodyAddRelForce(self._bid, f[0], f[1], f[2])

		# addRelTorque
		def addRelTorque(self, t):
				"""addRelTorque(t)

				Add an external torque t given in relative coordinates
				(relative to the body's own frame of reference).

				@param t: Torque
				@type t: 3-sequence of floats
				"""
				dBodyAddRelTorque(self._bid, t[0], t[1], t[2])

		# addForceAtPos
		def addForceAtPos(self, f, p):
				"""addForceAtPos(f, p)

				Add an external force f at position p. Both arguments must be
				given in absolute coordinates.

				@param f: Force
				@param p: Position
				@type f: 3-sequence of floats
				@type p: 3-sequence of floats
				"""
				dBodyAddForceAtPos(self._bid, f[0], f[1], f[2], p[0], p[1], p[2])

		# addForceAtRelPos
		def addForceAtRelPos(self, f, p):
				"""addForceAtRelPos(f, p)

				Add an external force f at position p. f is given in absolute
				coordinates and p in absolute coordinates.

				@param f: Force
				@param p: Position
				@type f: 3-sequence of floats
				@type p: 3-sequence of floats
				"""
				dBodyAddForceAtRelPos(self._bid, f[0], f[1], f[2], p[0], p[1], p[2])

		# addRelForceAtPos
		def addRelForceAtPos(self, f, p):
				"""addRelForceAtPos(f, p)

				Add an external force f at position p. f is given in relative
				coordinates and p in relative coordinates.

				@param f: Force
				@param p: Position
				@type f: 3-sequence of floats
				@type p: 3-sequence of floats
				"""
				dBodyAddRelForceAtPos(self._bid, f[0], f[1], f[2], p[0], p[1], p[2])

		# addRelForceAtRelPos
		def addRelForceAtRelPos(self, f, p):
				"""addRelForceAtRelPos(f, p)

				Add an external force f at position p. Both arguments must be
				given in relative coordinates.

				@param f: Force
				@param p: Position
				@type f: 3-sequence of floats
				@type p: 3-sequence of floats
				"""
				dBodyAddRelForceAtRelPos(self._bid, f[0], f[1], f[2], p[0], p[1], p[2])

		# getForce
		def getForce(self):
				"""getForce() -> 3-tuple

				Return the current accumulated force.
				"""
				cdef dReal* f
				# The "const" in the original return value is cast away
				f = <dReal*>dBodyGetForce(self._bid)
				return (f[0],f[1],f[2])

		# getTorque
		def getTorque(self):
				"""getTorque() -> 3-tuple

				Return the current accumulated torque.
				"""
				cdef dReal* f
				# The "const" in the original return value is cast away
				f = <dReal*>dBodyGetTorque(self._bid)
				return (f[0],f[1],f[2])

		# setForce
		def setForce(self, f):
				"""setForce(f)

				Set the body force accumulation vector.

				@param f: Force
				@type f: 3-tuple of floats
				"""
				dBodySetForce(self._bid, f[0], f[1], f[2])

		# setTorque
		def setTorque(self, t):
				"""setTorque(t)

				Set the body torque accumulation vector.

				@param t: Torque
				@type t: 3-tuple of floats
				"""
				dBodySetTorque(self._bid, t[0], t[1], t[2])

		# getRelPointPos
		def getRelPointPos(self, p):
				"""getRelPointPos(p) -> 3-tuple

				Utility function that takes a point p on a body and returns
				that point's position in global coordinates. The point p
				must be given in body relative coordinates.

				@param p: Body point (local coordinates)
				@type p: 3-sequence of floats
				"""

				cdef dVector3 res 
				dBodyGetRelPointPos(self._bid, p[0], p[1], p[2], res)
				return (res[0], res[1], res[2])

		# getRelPointVel
		def getRelPointVel(self, p):
				"""getRelPointVel(p) -> 3-tuple

				Utility function that takes a point p on a body and returns
				that point's velocity in global coordinates. The point p
				must be given in body relative coordinates.

				@param p: Body point (local coordinates)
				@type p: 3-sequence of floats
				"""
				cdef dVector3 res 
				dBodyGetRelPointVel(self._bid, p[0], p[1], p[2], res)
				return (res[0], res[1], res[2])

		# getPointVel
		def getPointVel(self, p):
				"""getPointVel(p) -> 3-tuple

				Utility function that takes a point p on a body and returns
				that point's velocity in global coordinates. The point p
				must be given in global coordinates.

				@param p: Body point (global coordinates)
				@type p: 3-sequence of floats
				"""
				cdef dVector3 res 
				dBodyGetPointVel(self._bid, p[0], p[1], p[2], res)
				return (res[0], res[1], res[2])

		# getPosRelPoint
		def getPosRelPoint(self, p):
				"""getPosRelPoint(p) -> 3-tuple

				This is the inverse of getRelPointPos(). It takes a point p in
				global coordinates and returns the point's position in
				body-relative coordinates.

				@param p: Body point (global coordinates)
				@type p: 3-sequence of floats
				"""
				cdef dVector3 res 
				dBodyGetPosRelPoint(self._bid, p[0], p[1], p[2], res)
				return (res[0], res[1], res[2])

		# vectorToWorld
		def vectorToWorld(self, v):
				"""vectorToWorld(v) -> 3-tuple

				Given a vector v expressed in the body coordinate system, rotate
				it to the world coordinate system.

				@param v: Vector in body coordinate system
				@type v: 3-sequence of floats
				"""
				cdef dVector3 res
				dBodyVectorToWorld(self._bid, v[0], v[1], v[2], res)
				return (res[0], res[1], res[2])

		# vectorFromWorld
		def vectorFromWorld(self, v):
				"""vectorFromWorld(v) -> 3-tuple

				Given a vector v expressed in the world coordinate system, rotate
				it to the body coordinate system.

				@param v: Vector in world coordinate system
				@type v: 3-sequence of floats
				"""
				cdef dVector3 res
				dBodyVectorFromWorld(self._bid, v[0], v[1], v[2], res)
				return (res[0], res[1], res[2])        
				
				
		property enabled:
				def __set__(self, flag):
						"""enable()
		
						Manually enable a body.
						"""
						
						if flag:
								dBodyEnable(self._bid)
						else:
								dBodyDisable(self._bid)
						
				def __get__(self):
						"""isEnabled() -> bool
		
						Check if a body is currently enabled.
						"""
						return dBodyIsEnabled(self._bid)
						
		property finite_rotation_mode:
				def __set__(self, mode):
						"""setFiniteRotationMode(mode)
		
						This function controls the way a body's orientation is updated at
						each time step. The mode argument can be:
						
						 - 0: An "infinitesimal" orientation update is used. This is
							 fast to compute, but it can occasionally cause inaccuracies
							 for bodies that are rotating at high speed, especially when
							 those bodies are joined to other bodies. This is the default
							 for every new body that is created.
						
						 - 1: A "finite" orientation update is used. This is more
							 costly to compute, but will be more accurate for high speed
							 rotations. Note however that high speed rotations can result
							 in many types of error in a world, and this mode will
							 only fix one of those sources of error.
		
						@param mode: Rotation mode (0/1)
						@type mode: int
						"""
						dBodySetFiniteRotationMode(self._bid, mode)
				
				def __get__(self):
						"""getFiniteRotationMode() -> mode (0/1)
		
						Return the current finite rotation mode of a body (0 or 1).
						See setFiniteRotationMode().
						"""
						return dBodyGetFiniteRotationMode(self._bid)

		property finite_rotation_axis:
				def __set__(self, a):
						"""setFiniteRotationAxis(a)

						Set the finite rotation axis of the body.  This axis only has a
						meaning when the finite rotation mode is set
						(see setFiniteRotationMode()).
						
						@param a: Axis
						@type a: 3-sequence of floats
						"""
						dBodySetFiniteRotationAxis(self._bid, a[0], a[1], a[2])

				def __get__(self):
						"""getFiniteRotationAxis() -> 3-tuple
		
						Return the current finite rotation axis of the body.
						"""
						cdef dVector3 p
						# The "const" in the original return value is cast away
						dBodyGetFiniteRotationAxis(self._bid, p)
						return (p[0],p[1],p[2])
				
		property num_joints:
				def __get__(self):
						"""getNumJoints() -> int

						Return the number of joints that are attached to this body.
						"""
						return dBodyGetNumJoints(self._bid)

		property gravity_mode:
				def __set__(self, mode):
						"""setGravityMode(mode)
		
						Set whether the body is influenced by the world's gravity
						or not. If mode is True it is, otherwise it isn't.
						Newly created bodies are always influenced by the world's gravity.
		
						@param mode: Gravity mode
						@type mode: bool
						"""
						dBodySetGravityMode(self._bid, mode)
				
				def __get__(self):
						"""getGravityMode() -> bool
		
						Return True if the body is influenced by the world's gravity.
						"""
						return dBodyGetGravityMode(self._bid)

