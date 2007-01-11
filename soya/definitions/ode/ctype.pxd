# -*- indent-tabs-mode: t -*-

####################################################################
# Python Open Dynamics Engine Wrapper
#
# Copyright (C) 2003, Matthias Baas (baas@ira.uka.de)
#
# You may distribute under the terms of the BSD license, as
# specified in the files license*.txt.
# -------------------------------------------------------------
# Open Dynamics Engine
# Copyright (c) 2001-2003, Russell L. Smith.
# All rights reserved. 
####################################################################
# author:
#	edited by Marmoute - Pierre-Yves David - marmoute@nekeme.net


cdef extern from "ode/ode.h":

		ctypedef float dReal
		
		# Dummy structs
		cdef struct dxWorld:
				int _dummy
		cdef struct dxSpace:
				int _dummy
		cdef struct dxBody:
				int _dummy
		cdef struct dxGeom:
				int _dummy
		cdef struct dxJoint:
				int _dummy
		cdef struct dxJointGroup:
				int _dummy
		cdef struct dxTriMeshData:
				int _dummy

		# Types
		ctypedef dxWorld* dWorldID
		ctypedef dxSpace* dSpaceID
		ctypedef dxBody* dBodyID
		ctypedef dxGeom* dGeomID
		ctypedef dxJoint* dJointID
		ctypedef dxJointGroup* dJointGroupID
		ctypedef dxTriMeshData* dTriMeshDataID
		ctypedef dReal dVector3[4]
		ctypedef dReal dVector4[4]
		ctypedef dReal dMatrix3[4*3]
		ctypedef dReal dMatrix4[4*4]
		ctypedef dReal dMatrix6[8*6]
		ctypedef dReal dQuaternion[4]

		cdef extern dReal dInfinity
		cdef extern int dAMotorUser
		cdef extern int dAMotorEuler

		ctypedef struct dMass:
				dReal    mass
				dVector4 c
				dMatrix3 I
				
		ctypedef struct dJointFeedback:
				dVector3 f1
				dVector3 t1
				dVector3 f2
				dVector3 t2

		ctypedef void dNearCallback(void* data, dGeomID o1, dGeomID o2)

		ctypedef struct dSurfaceParameters:
				int mode
				dReal mu

				dReal mu2
				dReal bounce
				dReal bounce_vel
				dReal soft_erp
				dReal soft_cfm
				dReal motion1,motion2
				dReal slip1,slip2

		ctypedef struct dContactGeom:
				dVector3 pos
				dVector3 normal
				dReal depth
				dGeomID g1,g2

		ctypedef struct dContact:
				dSurfaceParameters surface
				dContactGeom geom
				dVector3 fdir1

		cdef enum:
				dSphereClass = 0
				dBoxClass,
				dCapsuleClass,
				dCylinderClass,
				dPlaneClass,
				dRayClass,
				dGeomTransformClass,


		# World
		dWorldID dWorldCreate()
		void dWorldDestroy (dWorldID)

		void dCloseODE()

		void dWorldSetGravity (dWorldID, dReal x, dReal y, dReal z)
		void dWorldGetGravity (dWorldID, dVector3 gravity)
		void dWorldSetERP (dWorldID, dReal erp)
		dReal dWorldGetERP (dWorldID)
		void dWorldSetCFM (dWorldID, dReal cfm)
		dReal dWorldGetCFM (dWorldID)
		void dWorldStep (dWorldID, dReal stepsize)
		void dWorldQuickStep (dWorldID, dReal stepsize)
		void dWorldSetQuickStepNumIterations (dWorldID, int num)
		int dWorldGetQuickStepNumIterations (dWorldID)
		void dWorldSetContactMaxCorrectingVel (dWorldID, dReal vel)
		dReal dWorldGetContactMaxCorrectingVel (dWorldID)
		void dWorldSetContactSurfaceLayer (dWorldID, dReal depth)
		dReal dWorldGetContactSurfaceLayer (dWorldID)
		void dWorldSetAutoDisableFlag (dWorldID, int do_auto_disable)
		int dWorldGetAutoDisableFlag (dWorldID)
		void dWorldSetAutoDisableLinearThreshold (dWorldID, dReal linear_threshold)
		dReal dWorldGetAutoDisableLinearThreshold (dWorldID)
		void dWorldSetAutoDisableAngularThreshold (dWorldID, dReal angular_threshold)
		dReal dWorldGetAutoDisableAngularThreshold (dWorldID)
		void dWorldSetAutoDisableSteps (dWorldID, int steps)
		int dWorldGetAutoDisableSteps (dWorldID)
		void dWorldSetAutoDisableTime (dWorldID, dReal time)
		dReal dWorldGetAutoDisableTime (dWorldID)
		void dWorldImpulseToForce (dWorldID, dReal stepsize,
															 dReal ix, dReal iy, dReal iz, dVector3 force)

		# Body
		dBodyID dBodyCreate (dWorldID)
		void dBodyDestroy (dBodyID)

		void  dBodySetData (dBodyID, void *data)
		void *dBodyGetData (dBodyID)

		void dBodySetPosition   (dBodyID, dReal x, dReal y, dReal z)
		void dBodySetRotation   (dBodyID, dMatrix3 R)
		void dBodySetQuaternion (dBodyID, dQuaternion q)
		void dBodySetLinearVel  (dBodyID, dReal x, dReal y, dReal z)
		void dBodySetAngularVel (dBodyID, dReal x, dReal y, dReal z)
		dReal * dBodyGetPosition   (dBodyID)
		dReal * dBodyGetRotation   (dBodyID)
		dReal * dBodyGetQuaternion (dBodyID)
		dReal * dBodyGetLinearVel  (dBodyID)
		dReal * dBodyGetAngularVel (dBodyID)
		
		void  dBodySetAutoDisableFlag(dBodyID, int do_auto_disable) 
		int   dBodyGetAutoDisableFlag(dBodyID)
		
		void  dBodySetAutoDisableLinearThreshold(dBodyID, dReal linear_threshold)
		dReal dBodyGetAutoDisableLinearThreshold(dBodyID)
		
		void  dBodySetAutoDisableAngularThreshold(dBodyID, dReal angular_threshold)
		dReal dBodyGetAutoDisableAngularThreshold(dBodyID)

		void  dBodySetAutoDisableSteps (dBodyID, int steps)
		int   dBodyGetAutoDisableSteps (dBodyID)

		void  dBodySetAutoDisableTime (dBodyID, dReal time)
		dReal dBodyGetAutoDisableTime (dBodyID)

		void  dBodySetAutoDisableDefaults (dBodyID)
		

		void dBodySetMass (dBodyID, dMass *mass)
		void dBodyGetMass (dBodyID, dMass *mass)

		void dBodyAddForce            (dBodyID, dReal fx, dReal fy, dReal fz)
		void dBodyAddTorque           (dBodyID, dReal fx, dReal fy, dReal fz)
		void dBodyAddRelForce         (dBodyID, dReal fx, dReal fy, dReal fz)
		void dBodyAddRelTorque        (dBodyID, dReal fx, dReal fy, dReal fz)
		void dBodyAddForceAtPos       (dBodyID, dReal fx, dReal fy, dReal fz, dReal px, dReal py, dReal pz)
		void dBodyAddForceAtRelPos    (dBodyID, dReal fx, dReal fy, dReal fz, dReal px, dReal py, dReal pz)
		void dBodyAddRelForceAtPos    (dBodyID, dReal fx, dReal fy, dReal fz, dReal px, dReal py, dReal pz)
		void dBodyAddRelForceAtRelPos (dBodyID, dReal fx, dReal fy, dReal fz, dReal px, dReal py, dReal pz)

		dReal * dBodyGetForce   (dBodyID)
		dReal * dBodyGetTorque  (dBodyID)

		void dBodySetForce(dBodyID, dReal x, dReal y, dReal z)
		void dBodySetTorque(dBodyID, dReal x, dReal y, dReal z)

		void dBodyGetRelPointPos    (dBodyID, dReal px, dReal py, dReal pz, dVector3 result)
		void dBodyGetRelPointVel    (dBodyID, dReal px, dReal py, dReal pz, dVector3 result)
		void dBodyGetPointVel    (dBodyID, dReal px, dReal py, dReal pz,
															dVector3 result)
		void dBodyGetPosRelPoint (dBodyID, dReal px, dReal py, dReal pz,
															dVector3 result)
		void dBodyVectorToWorld   (dBodyID, dReal px, dReal py, dReal pz,
															 dVector3 result)
		void dBodyVectorFromWorld (dBodyID, dReal px, dReal py, dReal pz,
															 dVector3 result)

		void dBodySetFiniteRotationMode (dBodyID, int mode)
		void dBodySetFiniteRotationAxis (dBodyID, dReal x, dReal y, dReal z)

		int dBodyGetFiniteRotationMode (dBodyID)
		void dBodyGetFiniteRotationAxis (dBodyID, dVector3 result)

		int dBodyGetNumJoints (dBodyID b)
		dJointID dBodyGetJoint (dBodyID, int index)

		void dBodyEnable (dBodyID)
		void dBodyDisable (dBodyID)
		int dBodyIsEnabled (dBodyID)

		void dBodySetGravityMode (dBodyID b, int mode)
		int dBodyGetGravityMode (dBodyID b)

		# Joints
		dJointID dJointCreateBall (dWorldID, dJointGroupID)
		dJointID dJointCreateHinge (dWorldID, dJointGroupID)
		dJointID dJointCreateSlider (dWorldID, dJointGroupID)
		dJointID dJointCreateContact (dWorldID, dJointGroupID, dContact *)
		dJointID dJointCreateUniversal (dWorldID, dJointGroupID)
		dJointID dJointCreateHinge2 (dWorldID, dJointGroupID)
		dJointID dJointCreateFixed (dWorldID, dJointGroupID)
		dJointID dJointCreateNull (dWorldID, dJointGroupID)
		dJointID dJointCreateAMotor (dWorldID, dJointGroupID)

		void dJointDestroy (dJointID)

		dJointGroupID dJointGroupCreate (int max_size)
		void dJointGroupDestroy (dJointGroupID)
		void dJointGroupEmpty (dJointGroupID)

		void dJointAttach (dJointID, dBodyID body1, dBodyID body2)
		void dJointSetData (dJointID, void *data)
		void *dJointGetData (dJointID)
		int dJointGetType (dJointID)
		dBodyID dJointGetBody (dJointID, int index)

		void dJointSetBallAnchor (dJointID, dReal x, dReal y, dReal z)
		void dJointSetHingeAnchor (dJointID, dReal x, dReal y, dReal z)
		void dJointSetHingeAxis (dJointID, dReal x, dReal y, dReal z)
		void dJointSetHingeParam (dJointID, int parameter, dReal value)
		void dJointSetSliderAxis (dJointID, dReal x, dReal y, dReal z)
		void dJointSetSliderParam (dJointID, int parameter, dReal value)
		void dJointSetHinge2Anchor (dJointID, dReal x, dReal y, dReal z)
		void dJointSetHinge2Axis1 (dJointID, dReal x, dReal y, dReal z)
		void dJointSetHinge2Axis2 (dJointID, dReal x, dReal y, dReal z)
		void dJointSetHinge2Param (dJointID, int parameter, dReal value)
		void dJointSetUniversalAnchor (dJointID, dReal x, dReal y, dReal z)
		void dJointSetUniversalAxis1 (dJointID, dReal x, dReal y, dReal z)
		void dJointSetUniversalAxis2 (dJointID, dReal x, dReal y, dReal z)
		void dJointSetUniversalParam (dJointID, int parameter, dReal value)
		void dJointSetFixed (dJointID)
		void dJointSetAMotorNumAxes (dJointID, int num)
		void dJointSetAMotorAxis (dJointID, int anum, int rel, dReal x, dReal y, dReal z)
		void dJointSetAMotorAngle (dJointID, int anum, dReal angle)
		void dJointSetAMotorParam (dJointID, int parameter, dReal value)
		void dJointSetAMotorMode (dJointID, int mode)

		void dJointGetBallAnchor (dJointID, dVector3 result)
		void dJointGetBallAnchor2 (dJointID, dVector3 result)
		void dJointGetHingeAnchor (dJointID, dVector3 result)
		void dJointGetHingeAnchor2 (dJointID, dVector3 result)
		void dJointGetHingeAxis (dJointID, dVector3 result)
		dReal dJointGetHingeParam (dJointID, int parameter)
		dReal dJointGetHingeAngle (dJointID)
		dReal dJointGetHingeAngleRate (dJointID)
		dReal dJointGetSliderPosition (dJointID)
		dReal dJointGetSliderPositionRate (dJointID)
		void dJointGetSliderAxis (dJointID, dVector3 result)
		dReal dJointGetSliderParam (dJointID, int parameter)
		void dJointGetHinge2Anchor (dJointID, dVector3 result)
		void dJointGetHinge2Anchor2 (dJointID, dVector3 result)
		void dJointGetHinge2Axis1 (dJointID, dVector3 result)
		void dJointGetHinge2Axis2 (dJointID, dVector3 result)
		dReal dJointGetHinge2Param (dJointID, int parameter)
		dReal dJointGetHinge2Angle1 (dJointID)
		dReal dJointGetHinge2Angle1Rate (dJointID)
		dReal dJointGetHinge2Angle2Rate (dJointID)
		void dJointGetUniversalAnchor (dJointID, dVector3 result)
		void dJointGetUniversalAnchor2 (dJointID, dVector3 result)
		void dJointGetUniversalAxis1 (dJointID, dVector3 result)
		void dJointGetUniversalAxis2 (dJointID, dVector3 result)
		dReal dJointGetUniversalParam (dJointID, int parameter)
		int dJointGetAMotorNumAxes (dJointID)
		void dJointGetAMotorAxis (dJointID, int anum, dVector3 result)
		int dJointGetAMotorAxisRel (dJointID, int anum)
		dReal dJointGetAMotorAngle (dJointID, int anum)
		dReal dJointGetAMotorAngleRate (dJointID, int anum)
		dReal dJointGetAMotorParam (dJointID, int parameter)
		int dJointGetAMotorMode (dJointID)

		void dJointSetFeedback (dJointID, dJointFeedback *)
		dJointFeedback *dJointGetFeedback (dJointID)

		int dAreConnected (dBodyID, dBodyID)

		# Mass
		void dMassSetZero (dMass *)
		cdef void dMassSetParameters (dMass *, dReal themass,
						 dReal cgx, dReal cgy, dReal cgz,
						 dReal I11, dReal I22, dReal I33,
						 dReal I12, dReal I13, dReal I23)
		cdef void dMassSetSphere (dMass *, dReal density, dReal radius)
		cdef void dMassSetSphereTotal (dMass *, dReal total_mass, dReal radius)
		void dMassSetCapsule (dMass *, dReal density, int direction,
								 dReal a, dReal b)
		void dMassSetCapsuleTotal(dMass *, dReal total_mass, int direction,
								 dReal a, dReal b)
		void dMassSetCylinder (dMass *, dReal density, int direction,
					dReal radius, dReal length)
		void dMassSetCylinderTotal(dMass *, dReal total_mass, int direction,
					dReal radius, dReal length)
		void dMassSetBox (dMass *, dReal density,
					dReal lx, dReal ly, dReal lz)
		void dMassSetBoxTotal (dMass *, dReal total_mass,
					dReal lx, dReal ly, dReal lz)
		
		void dMassAdjust (dMass *, dReal newmass)
		void dMassTranslate (dMass *, dReal x, dReal y, dReal z)
		cdef void dMassRotate (dMass *, dMatrix3 R)
		void dMassAdd (dMass *a, dMass *b)

		# Space
#    dSpaceID dSimpleSpaceCreate(int space)
#    dSpaceID dHashSpaceCreate(int space)
		dSpaceID dSimpleSpaceCreate(dSpaceID space)
		dSpaceID dHashSpaceCreate(dSpaceID space)
		dSpaceID dQuadTreeSpaceCreate (dSpaceID space, dVector3 Center,
																	 dVector3 Extents, int Depth)

		void dSpaceDestroy (dSpaceID)
		void dSpaceAdd (dSpaceID, dGeomID)
		void dSpaceRemove (dSpaceID, dGeomID)
		int dSpaceQuery (dSpaceID, dGeomID)
		void dSpaceCollide (dSpaceID space, void *data, dNearCallback *callback)
		void dSpaceCollide2 (dGeomID g1, dGeomID g2, void *data, dNearCallback *callback)

		void dHashSpaceSetLevels (dSpaceID space, int minlevel, int maxlevel)
		void dHashSpaceGetLevels (dSpaceID space, int *minlevel, int *maxlevel)

		void dSpaceSetCleanup (dSpaceID space, int mode)
		int dSpaceGetCleanup (dSpaceID space)

		int dSpaceGetNumGeoms (dSpaceID)
		dGeomID dSpaceGetGeom (dSpaceID, int i)

		# Geom
		dGeomID dCreateSphere (dSpaceID space, dReal radius)
		dGeomID dCreateBox (dSpaceID space, dReal lx, dReal ly, dReal lz)
		dGeomID dCreatePlane (dSpaceID space, dReal a, dReal b, dReal c, dReal d)
		dGeomID dCreateCapsule (dSpaceID space, dReal radius, dReal length)
		dGeomID dCreateCylinder (dSpaceID space, dReal radius, dReal length)
		dGeomID dCreateGeomGroup (dSpaceID space)

		void dGeomSphereSetRadius (dGeomID sphere, dReal radius)
		void dGeomBoxSetLengths (dGeomID box, dReal lx, dReal ly, dReal lz)
		void dGeomPlaneSetParams (dGeomID plane, dReal a, dReal b, dReal c, dReal d)
		void dGeomCapsuleSetParams (dGeomID ccylinder, dReal radius, dReal length)
		void dGeomCylinderSetParams (dGeomID ccylinder, dReal radius, dReal length)


		dReal dGeomSphereGetRadius (dGeomID sphere)
		void  dGeomBoxGetLengths (dGeomID box, dVector3 result)
		void  dGeomPlaneGetParams (dGeomID plane, dVector4 result)
		void  dGeomCapsuleGetParams (dGeomID ccylinder, dReal *radius, dReal *length)
		void  dGeomCylinderGetParams (dGeomID ccylinder, dReal *radius, dReal *length)

		
		dReal dGeomSpherePointDepth (dGeomID sphere, dReal x, dReal y, dReal z)
		dReal dGeomBoxPointDepth (dGeomID box, dReal x, dReal y, dReal z)
		dReal dGeomPlanePointDepth (dGeomID plane, dReal x, dReal y, dReal z)
		dReal dGeomCapsulePointDepth (dGeomID ccylinder, dReal x, dReal y, dReal z)
		#dReal dGeomCylinderPointDepth (dGeomID ccylinder, dReal x, dReal y, dReal z)

		dGeomID dCreateRay (dSpaceID space, dReal length)
		void dGeomRaySetLength (dGeomID ray, dReal length)
		dReal dGeomRayGetLength (dGeomID ray)
		void dGeomRaySet (dGeomID ray, dReal px, dReal py, dReal pz,
												dReal dx, dReal dy, dReal dz)
		void dGeomRayGet (dGeomID ray, dVector3 start, dVector3 dir)

		void dGeomSetData (dGeomID, void *)
		void *dGeomGetData (dGeomID)
		void dGeomSetBody (dGeomID, dBodyID)
		dBodyID dGeomGetBody (dGeomID)
		void dGeomSetPosition (dGeomID, dReal x, dReal y, dReal z)
		void dGeomSetRotation (dGeomID, dMatrix3 R)
		dReal * dGeomGetPosition (dGeomID)
		dReal * dGeomGetRotation (dGeomID)
		void dGeomDestroy (dGeomID)
		void dGeomGetAABB (dGeomID, dReal aabb[6])
		dReal *dGeomGetSpaceAABB (dGeomID)
		int dGeomIsSpace (dGeomID)
		dSpaceID dGeomGetSpace (dGeomID)
		int dGeomGetClass (dGeomID)

		void dGeomSetCategoryBits(dGeomID, unsigned long bits)
		void dGeomSetCollideBits(dGeomID, unsigned long bits)
		unsigned long dGeomGetCategoryBits(dGeomID)
		unsigned long dGeomGetCollideBits(dGeomID)     

		void dGeomEnable (dGeomID)
		void dGeomDisable (dGeomID)
		int dGeomIsEnabled (dGeomID)

		void dGeomGroupAdd (dGeomID group, dGeomID x)
		void dGeomGroupRemove (dGeomID group, dGeomID x)
		int dGeomGroupGetNumGeoms (dGeomID group)
		dGeomID dGeomGroupGetGeom (dGeomID group, int i)

		dGeomID dCreateGeomTransform (dSpaceID space)
		void dGeomTransformSetGeom (dGeomID g, dGeomID obj)
		dGeomID dGeomTransformGetGeom (dGeomID g)
		void dGeomTransformSetCleanup (dGeomID g, int mode)
		int dGeomTransformGetCleanup (dGeomID g)
		void dGeomTransformSetInfo (dGeomID g, int mode)
		int dGeomTransformGetInfo (dGeomID g)

		int dCollide (dGeomID o1, dGeomID o2, int flags, dContactGeom *contact, int skip)

		# Trimesh
		dTriMeshDataID dGeomTriMeshDataCreate()
		void dGeomTriMeshDataDestroy(dTriMeshDataID g)
		void dGeomTriMeshDataBuildSingle1(dTriMeshDataID g, void* Vertices,
																int VertexStride, int VertexCount,
																void* Indices, int IndexCount,
																int TriStride, void* Normals)
		
		void dGeomTriMeshDataBuildSimple(dTriMeshDataID g,
																 dReal* Vertices, int VertexCount,
																 int* Indices, int IndexCount)

		dGeomID dCreateTriMesh (dSpaceID space, dTriMeshDataID Data,
														void* Callback,
														void* ArrayCallback,
														void* RayCallback)   

		void dGeomTriMeshSetData (dGeomID g, dTriMeshDataID Data)

		void dGeomTriMeshDataSet (dTriMeshDataID data, int what, void *ptr)
		
		void dGeomTriMeshClearTCCache (dGeomID g)

		void dGeomTriMeshGetTriangle (dGeomID g, int Index, dVector3 *v0,
																	dVector3 *v1, dVector3 *v2)

		void dGeomTriMeshGetPoint (dGeomID g, int Index, dReal u, dReal v,
															 dVector3 Out)

		void dGeomTriMeshEnableTC(dGeomID g, int geomClass, int enable)
		int dGeomTriMeshIsTCEnabled(dGeomID g, int geomClass)

		cdef enum:
				TRIMESH_FACE_NORMALS = 0
				TRIMESH_LAST_TRANSFORMATION

		# User-defined classes
		ctypedef void dGetAABBFn (dGeomID, dReal aabb[6])
		ctypedef int dColliderFn (dGeomID o1, dGeomID o2,
															int flags, dContactGeom *contact, int skip)
		ctypedef dColliderFn * dGetColliderFnFn (int num)
		ctypedef void dGeomDtorFn (dGeomID o)
		ctypedef int dAABBTestFn (dGeomID o1, dGeomID o2, dReal aabb[6])

		ctypedef struct dGeomClass:
			int bytes
			dGetColliderFnFn *collider
			dGetAABBFn *aabb
			dAABBTestFn *aabb_test
			dGeomDtorFn *dtor

		int dCreateGeomClass (dGeomClass *classptr)
		void * dGeomGetClassData (dGeomID)
		dGeomID dCreateGeom (int classnum)

		dGetAABBFn *dInfiniteAABB


		
## For the custom colliders
## Not needed any more
#ctypedef dReal dGetDepthFn(dGeomID g, dReal x, dReal y, dReal z)
