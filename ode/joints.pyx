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
# Python wrapper (which is done by the JointGroup wrapper).


######################################################################

# JointGroup
cdef class JointGroup:
    """Joint group.

    Constructor::
    
      JointGroup()    
    """

    # JointGroup ID
    cdef dJointGroupID gid
    # A list of Python joints that were added to the group
    cdef object jointlist

    def __new__(self, *args, **kw):
        self.gid = dJointGroupCreate(0)

    def __init__(self):
        self.jointlist = []

    def __dealloc__(self):
        if self.gid!=NULL:
            dJointGroupDestroy(self.gid)

    # empty
    def empty(self):
        """empty()

        Destroy all joints in the group.
        """
        dJointGroupEmpty(self.gid)
        for j in self.jointlist:
            j._destroyed()
        self.jointlist = []


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
        self.jointlist.append(j)


######################################################################

# Joint
cdef class Joint:
    """Base class for all joint classes."""

    # Joint id as returned by dJointCreateXxx()
    cdef dJointID jid
    # A reference to the world so that the world won't be destroyed while
    # there are still joints using it.
    cdef object world
    # The feedback buffer
    cdef dJointFeedback* feedback

    cdef readonly body1
    cdef readonly body2

    def __new__(self, *args, **kw):
        self.jid = NULL
        self.world = None
        self.feedback = NULL
        self.body1 = None
        self.body2 = None

    def __init__(self, *a, **kw):
        raise NotImplementedError, "The Joint base class can't be used directly."

    def __dealloc__(self):
        self.setFeedback(False)
        if self.jid!=NULL:
            dJointDestroy(self.jid)

    # _destroyed
    def _destroyed(self):
        """Notify the joint object about an external destruction of the ODE joint.

        This method has to be called when the underlying ODE object
        was destroyed by someone else (e.g. by a joint group). The Python
        wrapper will then refrain from destroying it again.
        """
        self.jid = NULL

    # attach
    def attach(self, _Body body1, _Body body2):
        """attach(body1, body2)

        Attach the joint to some new bodies.
        
        TODO: What if there's only one body.

        @param body1: First body
        @param body2: Second body
        @type body1: Body
        @type body2: Body
        """

        if self.body1 is not None:
            self.body1._remove_joint(self)
        if self.body2 is not None:
            self.body2._remove_joint(self)

        self.body1 = body1
        self.body2 = body2
        dJointAttach(self.jid, body1._bid, body2._bid)
        # Make sure the bodies keep a reference to the joint so that
        # the user doesn't have to
        body1._add_joint(self)
        body2._add_joint(self)

#    # getBody
#    def get_body(self, index):
#        """getBody(index) -> Body
#
#        Return the bodies that this joint connects. If index is 0 the
#        "first" body will be returned, corresponding to the body1
#        argument of the attach() method. If index is 1 the "second" body
#        will be returned, corresponding to the body2 argument of the
#        attach() method.
#
#        @param index: Body index (0 or 1).
#        @type index: int
#        """
#        
#        if (index == 0):
#            return self.body1
#        elif (index == 1):
#            return self.body2
#        else:
#            raise IndexError()

    # setFeedback
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
            dJointSetFeedback(self.jid, self.feedback)
        else:
            if self.feedback!=NULL:
                # Free a previously allocated buffer
                dJointSetFeedback(self.jid, NULL)
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
        
        fb = dJointGetFeedback(self.jid)
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
            self._setParam(ParamLoStop, value)
    
    property hi_stop:
        def __get__(self):
            return self._getParam(ParamHiStop)

        def __set__(self, dReal value):
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
            return self._getParam(ParamLoStop)

        def __set__(self, dReal value):
            self._setParam(ParamLoStop, value)
    
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
cdef class BallJoint(Joint):
    """Ball joint.

    Constructor::
    
      BallJoint(world, jointgroup=None)    
    """

    def __new__(self, _World world not None, jointgroup=None, *args, **kw):
        cdef JointGroup jg
        cdef dJointGroupID jgid

        jgid=NULL
        if jointgroup!=None:
            jg=jointgroup
            jgid=jg.gid
        self.jid = dJointCreateBall(world._wid, jgid)

    def __init__(self, _World world not None, jointgroup=None):
        self.world = world
        if jointgroup!=None:
            jointgroup._addjoint(self)
            
    property anchor:
        """setAnchor(pos)

        Set the joint anchor point which must be specified in world
        coordinates.

        @param pos: Anchor position
        @type pos: 3-sequence of floats         
        """
        def __set__(self, pos):
            dJointSetBallAnchor(self.jid, pos[0], pos[1], pos[2])
    
        def __get__(self):
            cdef dVector3 p
            dJointGetBallAnchor(self.jid, p)
            return (p[0],p[1],p[2])
    
    property anchor2:
        """getAnchor2() -> 3-tuple of floats

        Get the joint anchor point, in world coordinates.  This
        returns the point on body 2. If the joint is perfectly
        satisfied, this will be the same as the point on body 1.
        """
        def __get__(self):
            cdef dVector3 p
            dJointGetBallAnchor2(self.jid, p)
            return (p[0],p[1],p[2])

    # setParam
    cdef void _setParam(self, int param, dReal value):
        pass

    # getParam
    cdef dReal _getParam(self, int param):
        return 0.0
        
   
# HingeJoint
cdef class HingeJoint(Joint):
    """Hinge joint.

    Constructor::
    
      HingeJoint(world, jointgroup=None)
    """

    def __new__(self, _World world not None, jointgroup=None, *args, **kw):
        cdef JointGroup jg
        cdef dJointGroupID jgid
        
        jgid=NULL
        if jointgroup!=None:
            jg=jointgroup
            jgid=jg.gid
        self.jid = dJointCreateHinge(world._wid, jgid)
        
    def __init__(self, _World world not None, jointgroup=None):
        self.world = world
        if jointgroup!=None:
            jointgroup._addjoint(self)

    property anchor:
        """setAnchor(pos)

        Set the hinge anchor which must be given in world coordinates.

        @param pos: Anchor position
        @type pos: 3-sequence of floats         
        """
        def __set__(self, pos):
            dJointSetHingeAnchor(self.jid, pos[0], pos[1], pos[2])
    
        def __get__(self):
            cdef dVector3 p
            dJointGetHingeAnchor(self.jid, p)
            return (p[0],p[1],p[2])

    property anchor2:
        """getAnchor2() -> 3-tuple of floats

        Get the joint anchor point, in world coordinates. This returns
        the point on body 2. If the joint is perfectly satisfied, this
        will be the same as the point on body 1.
        """
        def __get__(self):
            cdef dVector3 p
            dJointGetHingeAnchor2(self.jid, p)
            return (p[0],p[1],p[2])

    property axis:
    
        """setAxis(axis)

        Set the hinge axis.

        @param axis: Hinge axis
        @type axis: 3-sequence of floats
        """
        # XXX use Soya vectors
        def __set__(self, axis):
            dJointSetHingeAxis(self.jid, axis[0], axis[1], axis[2])
    
        def __get__(self):
            cdef dVector3 a
            dJointGetHingeAxis(self.jid, a)
            return (a[0],a[1],a[2])
    
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
            return dJointGetHingeAngle(self.jid)

    property angle_rate:
        """getAngleRate() -> float

        Get the time derivative of the angle.
        """
        def __get__(self):
            return dJointGetHingeAngleRate(self.jid)

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
        
        dJointSetHingeParam(self.jid, param, value)

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
        return dJointGetHingeParam(self.jid, param)
        
        
# SliderJoint
cdef class SliderJoint(Joint):
    """Slider joint.
    
    Constructor::
    
      SlideJoint(world, jointgroup=None)
    """

    def __new__(self, _World world not None, jointgroup=None, *args, **kw):
        cdef JointGroup jg
        cdef dJointGroupID jgid

        jgid=NULL
        if jointgroup!=None:
            jg=jointgroup
            jgid=jg.gid
        self.jid = dJointCreateSlider(world._wid, jgid)

    def __init__(self, _World world not None, jointgroup=None):
        self.world = world
        if jointgroup!=None:
            jointgroup._addjoint(self)
          
    property axis:
        """setAxis(axis)

        Set the slider axis parameter.

        @param axis: Slider axis
        @type axis: 3-sequence of floats        
        """
        def __set__(self, axis):
            dJointSetSliderAxis(self.jid, axis[0], axis[1], axis[2])
    
        def __get__(self):
            cdef dVector3 a
            dJointGetSliderAxis(self.jid, a)
            return (a[0],a[1],a[2])

    property position:
        """getPosition() -> float

        Get the slider linear position (i.e. the slider's "extension").

        When the axis is set, the current position of the attached
        bodies is examined and that position will be the zero
        position.
        """
        def __get__(self):
            return dJointGetSliderPosition(self.jid)

    property position_rate:
        """getPositionRate() -> float

        Get the time derivative of the position.
        """
        def __get__(self):
            return dJointGetSliderPositionRate(self.jid)

    # setParam
    cdef void _setParam(self, int param, dReal value):
        dJointSetSliderParam(self.jid, param, value)

    # getParam
    cdef dReal _getParam(self, int param):
        return dJointGetSliderParam(self.jid, param)
        
    
# UniversalJoint
cdef class UniversalJoint(Joint):
    """Universal joint.

    Constructor::
    
      UniversalJoint(world, jointgroup=None)    
    """

    def __new__(self, _World world not None, jointgroup=None, *args, **kw):
        cdef JointGroup jg
        cdef dJointGroupID jgid

        jgid=NULL
        if jointgroup!=None:
            jg=jointgroup
            jgid=jg.gid
        self.jid = dJointCreateUniversal(world._wid, jgid)

    def __init__(self, _World world not None, jointgroup=None):
        self.world = world
        if jointgroup!=None:
            jointgroup._addjoint(self)

    property anchor:
        """setAnchor(pos)

        Set the hinge anchor which must be given in world coordinates.

        @param pos: Anchor position
        @type pos: 3-sequence of floats         
        """
        def __set__(self, pos):
            dJointSetUniversalAnchor(self.jid, pos[0], pos[1], pos[2])
    
        def __get__(self):
            cdef dVector3 p
            dJointGetUniversalAnchor(self.jid, p)
            return (p[0],p[1],p[2])

    property anchor2:
        """getAnchor2() -> 3-tuple of floats

        Get the joint anchor point, in world coordinates. This returns
        the point on body 2. If the joint is perfectly satisfied, this
        will be the same as the point on body 1.
        """
        def __get__(self):
            cdef dVector3 p
            dJointGetUniversalAnchor2(self.jid, p)
            return (p[0],p[1],p[2])

    property axis1:
        """setAxis1(axis)

        Set the first universal axis. Axis 1 and axis 2 should be
        perpendicular to each other.

        @param axis: Joint axis
        @type axis: 3-sequence of floats
        """
        def __set__(self, axis):
            dJointSetUniversalAxis1(self.jid, axis[0], axis[1], axis[2])
    
        def __get__(self):
            cdef dVector3 a
            dJointGetUniversalAxis1(self.jid, a)
            return (a[0],a[1],a[2])

    property axis2:
        """setAxis2(axis)

        Set the second universal axis. Axis 1 and axis 2 should be
        perpendicular to each other.

        @param axis: Joint axis
        @type axis: 3-sequence of floats        
        """
        def __set__(self, axis):
            dJointSetUniversalAxis2(self.jid, axis[0], axis[1], axis[2])
    
        def __get__(self):
            cdef dVector3 a
            dJointGetUniversalAxis2(self.jid, a)
            return (a[0],a[1],a[2])
    
    # setParam
    cdef void _setParam(self, int param, dReal value):
        dJointSetUniversalParam(self.jid, param, value)

    # getParam
    cdef dReal _getParam(self, int param):
       return dJointGetUniversalParam(self.jid, param)

    
# Hinge2Joint
cdef class Hinge2Joint(Joint):
    """Hinge2 joint.

    Constructor::
    
      Hinge2Joint(world, jointgroup=None)
    """

    def __new__(self, _World world not None, jointgroup=None, *args, **kw):
        cdef JointGroup jg
        cdef dJointGroupID jgid

        jgid=NULL
        if jointgroup!=None:
            jg=jointgroup
            jgid=jg.gid
        self.jid = dJointCreateHinge2(world._wid, jgid)

    def __init__(self, _World world, jointgroup=None):
        self.world = world
        if jointgroup!=None:
            jointgroup._addjoint(self)

    property anchor:
        """setAnchor(pos)

        Set the hinge anchor which must be given in world coordinates.

        @param pos: Anchor position
        @type pos: 3-sequence of floats         
        """
        def __set__(self, pos):
            dJointSetHinge2Anchor(self.jid, pos[0], pos[1], pos[2])
    
        def __get__(self):
            cdef dVector3 p
            dJointGetHinge2Anchor(self.jid, p)
            return (p[0],p[1],p[2])

    property anchor2:
        """getAnchor2() -> 3-tuple of floats

        Get the joint anchor point, in world coordinates. This returns
        the point on body 2. If the joint is perfectly satisfied, this
        will be the same as the point on body 1.
        """
        def __get__(self):
            cdef dVector3 p
            dJointGetHinge2Anchor2(self.jid, p)
            return (p[0],p[1],p[2])

    property axis1:
        """setAxis1(axis)

        Set the first universal axis. Axis 1 and axis 2 should be
        perpendicular to each other.

        @param axis: Joint axis
        @type axis: 3-sequence of floats
        """
        def __set__(self, axis):
            dJointSetHinge2Axis1(self.jid, axis[0], axis[1], axis[2])
    
        def __get__(self):
            cdef dVector3 a
            dJointGetHinge2Axis1(self.jid, a)
            return (a[0],a[1],a[2])

    property axis2:
        """setAxis2(axis)

        Set the second universal axis. Axis 1 and axis 2 should be
        perpendicular to each other.

        @param axis: Joint axis
        @type axis: 3-sequence of floats        
        """
        def __set__(self, axis):
            dJointSetHinge2Axis2(self.jid, axis[0], axis[1], axis[2])
    
        def __get__(self):
            cdef dVector3 a
            dJointGetHinge2Axis2(self.jid, a)
            return (a[0],a[1],a[2])
    
    property angle1:
        """getAngle1() -> float

        Get the first hinge-2 angle (around axis 1).

        When the anchor or axis is set, the current position of the
        attached bodies is examined and that position will be the zero
        angle.
        """
        def __get__(self):
            return dJointGetHinge2Angle1(self.jid)

    property angle1_rate:
        """getAngle1Rate() -> float

        Get the time derivative of the first hinge-2 angle.
        """
        def __get__(self):
            return dJointGetHinge2Angle1Rate(self.jid)

    property angle2_rate:
        """getAngle2Rate() -> float

        Get the time derivative of the second hinge-2 angle.
        """
        def __get__(self):
            return dJointGetHinge2Angle2Rate(self.jid)

    # setParam
    cdef void _setParam(self, int param, dReal value):
        dJointSetHinge2Param(self.jid, param, value)

    # getParam
    cdef dReal _getParam(self, int param):
        return dJointGetHinge2Param(self.jid, param)

    
# FixedJoint
cdef class FixedJoint(Joint):
    """Fixed joint.

    Constructor::
    
      FixedJoint(world, jointgroup=None)    
    """

    def __new__(self, _World world not None, jointgroup=None, *args, **kw):
        cdef JointGroup jg
        cdef dJointGroupID jgid

        jgid=NULL
        if jointgroup!=None:
            jg=jointgroup
            jgid=jg.gid
        self.jid = dJointCreateFixed(world._wid, jgid)

    def __init__(self, _World world not None, jointgroup=None):
        self.world = world
        if jointgroup!=None:
            jointgroup._addjoint(self)

    # setFixed
    def setFixed(self):
        """setFixed()

        Call this on the fixed joint after it has been attached to
        remember the current desired relative offset and desired
        relative rotation between the bodies.
        """
        dJointSetFixed(self.jid)

        
# ContactJoint
cdef class ContactJoint(Joint):
    """Contact joint.

    Constructor::
    
      ContactJoint(world, jointgroup, contact)
    """

    def __new__(self, _World world not None, jointgroup, Contact contact, *args, **kw):
        cdef JointGroup jg
        cdef dJointGroupID jgid
        jgid=NULL
        if jointgroup!=None:
            jg=jointgroup
            jgid=jg.gid
        self.jid = dJointCreateContact(world._wid, jgid, &contact._contact)

    def __init__(self, _World world not None, jointgroup, Contact contact):
        self.world = world
        if jointgroup!=None:
            jointgroup._addjoint(self)

# AMotor
cdef class AMotor(Joint):
    """AMotor joint.
    
    Constructor::
    
      AMotor(world, jointgroup=None)
    """

    def __new__(self, _World world not None, jointgroup=None, *args, **kw):
        cdef JointGroup jg
        cdef dJointGroupID jgid

        jgid = NULL
        if jointgroup!=None:
            jg = jointgroup
            jgid = jg.gid
        self.jid = dJointCreateAMotor(world._wid, jgid)

    def __init__(self, _World world not None, jointgroup=None):
        self.world = world
        if jointgroup!=None:
            jointgroup._addjoint(self)
            
    property mode:
        """setMode(mode)

        Set the angular motor mode.  mode must be either AMotorUser or
        AMotorEuler.

        @param mode: Angular motor mode
        @type mode: int
        """
        def __set__(self, mode):
            dJointSetAMotorMode(self.jid, mode)

        def __get__(self):
            return dJointGetAMotorMode(self.jid)

    # setNumAxes
    def setNumAxes(self, int num):
        """setNumAxes(num)

        Set the number of angular axes that will be controlled by the AMotor.
        num may be in the range from 0 to 3.

        @param num: Number of axes (0-3)
        @type num: int
        """
        dJointSetAMotorNumAxes(self.jid, num)

    # getNumAxes
    def getNumAxes(self):
        """getNumAxes() -> int

        Get the number of angular axes that are controlled by the AMotor.
        """
        return dJointGetAMotorNumAxes(self.jid)

    # XXX this can be converted to properties by using Soya vectors and
    # choosing the relative orientation mode automatically based on the
    # coordinate system of the vector.
    # setAxis
    def setAxis(self, int anum, int rel, axis):
        """setAxis(anum, rel, axis)

        Set an AMotor axis.

        The anum argument selects the axis to change (0,1 or 2).
        Each axis can have one of three "relative orientation" modes,
        selected by rel:
        
        0: The axis is anchored to the global frame. 
        1: The axis is anchored to the first body. 
        2: The axis is anchored to the second body.

        The axis vector is always specified in global coordinates
        regardless of the setting of rel.

        @param anum: Axis number
        @param rel: Relative orientation mode
        @param axis: Axis
        @type anum: int
        @type rel: int
        @type axis: 3-sequence of floats
        """
        dJointSetAMotorAxis(self.jid, anum, rel, axis[0], axis[1], axis[2])

    # getAxis
    def getAxis(self, int anum):
        """getAxis(anum)

        Get an AMotor axis.

        @param anum: Axis index (0-2)
        @type anum: int        
        """
        cdef dVector3 a
        dJointGetAMotorAxis(self.jid, anum, a)
        return (a[0],a[1],a[2])

    # getAxisRel
    def getAxisRel(self, int anum):
        """getAxisRel(anum) -> int

        Get the relative mode of an axis.

        @param anum: Axis index (0-2)
        @type anum: int        
        """
        return dJointGetAMotorAxisRel(self.jid, anum)

    # XXX these should be converted to three properties each, one for each
    # axis.
    # setAngle
    def setAngle(self, int anum, angle):
        """setAngle(anum, angle)

        Tell the AMotor what the current angle is along axis anum.

        @param anum: Axis index
        @param angle: Angle
        @type anum: int
        @type angle: float
        """
        dJointSetAMotorAngle(self.jid, anum, angle)

    # getAngle
    def getAngle(self, int anum):
        """getAngle(anum) -> float

        Return the current angle for axis anum.

        @param anum: Axis index
        @type anum: int        
        """
        return dJointGetAMotorAngle(self.jid, anum)

    # getAngleRate
    def getAngleRate(self, int anum):
        """getAngleRate(anum) -> float

        Return the current angle rate for axis anum.

        @param anum: Axis index
        @type anum: int        
        """
        return dJointGetAMotorAngleRate(self.jid, anum)

    # setParam
    cdef void _setParam(self, int param, dReal value):
        dJointSetAMotorParam(self.jid, param, value)

    # getParam
    cdef dReal _getParam(self, int param):
        return dJointGetAMotorParam(self.jid, param)


