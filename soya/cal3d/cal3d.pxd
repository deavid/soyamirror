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

cdef extern from "cal3d_wrapper.h":
	ctypedef void *CalUserData
	
	cdef enum:
		ANIMATION_TYPE_NONE = 0
		ANIMATION_TYPE_CYCLE
		ANIMATION_TYPE_POSE
		ANIMATION_TYPE_ACTION
		
	cdef enum:
		ANIMATION_STATE_NONE = 0
		ANIMATION_STATE_SYNC
		ANIMATION_STATE_ASYNC
		ANIMATION_STATE_IN
		ANIMATION_STATE_STEADY
		ANIMATION_STATE_OUT
	
	cdef struct CalAnimation:
		int _dummy
	cdef struct CalAnimationAction:
		int _dummy
	cdef struct CalAnimationCycle:
		int _dummy
	cdef struct CalBone:
		int _dummy
	cdef struct CalCoreAnimation:
		int _dummy
	cdef struct CalCoreBone:
		int _dummy
	cdef struct CalCoreKeyframe:
		int _dummy
	cdef struct CalCoreMaterial:
		int _dummy
	cdef struct CalCoreMesh:
		int _dummy
	cdef struct CalCoreModel:
		int _dummy
	cdef struct CalCoreSkeleton:
		int _dummy
	cdef struct CalCoreSubmesh:
		int _dummy
	cdef struct CalCoreTrack:
		int _dummy
	cdef struct CalLoader:
		int _dummy
	cdef struct CalMatrix:
		int _dummy
	cdef struct CalMesh:
		int _dummy
	cdef struct CalMixer:
		int _dummy
	cdef struct CalModel:
		int _dummy
	cdef struct CalPhysique:
		int _dummy
	cdef struct CalPlatform:
		int _dummy
	cdef struct CalQuaternion:
		int _dummy
	cdef struct CalRenderer:
		int _dummy
	cdef struct CalSaver:
		int _dummy
	cdef struct CalSkeleton:
		int _dummy
	cdef struct CalSpringSystem:
		int _dummy
	cdef struct CalSubmesh:
		int _dummy
	cdef struct CalVector:
		int _dummy
	
	cdef void CalAnimation_Delete(CalAnimation *self)
	cdef CalCoreAnimation *CalAnimation_GetCoreAnimation(CalAnimation *self)
	cdef int CalAnimation_GetState(CalAnimation *self)
	cdef float CalAnimation_GetTime(CalAnimation *self)
	cdef int CalAnimation_GetType(CalAnimation *self)
	cdef float CalAnimation_GetWeight(CalAnimation *self)
	cdef void CalAnimationAction_Delete(CalAnimationAction *self)
	cdef int CalAnimationAction_Execute(CalAnimationAction *self, float delayIn, float delayOut)
	cdef CalAnimationAction *CalAnimationAction_New(CalCoreAnimation *pCoreAnimation)
	cdef int CalAnimationAction_Update(CalAnimationAction *self, float deltaTime)
	cdef int CalAnimationCycle_Blend(CalAnimationCycle *self, float weight, float delay)
	cdef void CalAnimationCycle_Delete(CalAnimationCycle *self)
	cdef CalAnimationCycle *CalAnimationCycle_New(CalCoreAnimation *pCoreAnimation)
	cdef void CalAnimationCycle_SetAsync(CalAnimationCycle *self, float time, float duration)
	cdef int CalAnimationCycle_Update(CalAnimationCycle *self, float deltaTime)
	cdef void CalBone_BlendState(CalBone *self, float weight, CalVector *pTranslation, CalQuaternion *pRotation)
	cdef void CalBone_CalculateState(CalBone *self)
	cdef void CalBone_ClearState(CalBone *self)
	cdef void CalBone_Delete(CalBone *self)
	cdef CalCoreBone *CalBone_GetCoreBone(CalBone *self)
	cdef CalQuaternion *CalBone_GetRotation(CalBone *self)
	cdef CalQuaternion *CalBone_GetRotationAbsolute(CalBone *self)
	cdef CalQuaternion *CalBone_GetRotationBoneSpace(CalBone *self)
	cdef CalVector *CalBone_GetTranslation(CalBone *self)
	cdef CalVector *CalBone_GetTranslationAbsolute(CalBone *self)
	cdef CalVector *CalBone_GetTranslationBoneSpace(CalBone *self)
	cdef void CalBone_LockState(CalBone *self)
	cdef CalBone *CalBone_New(CalCoreBone *pCoreBone)
	cdef void CalBone_SetSkeleton(CalBone *self, CalSkeleton *pSkeleton)
	cdef void CalBone_SetTranslation(CalBone *self, CalVector *pTranslation)
	cdef void CalBone_SetRotation(CalBone *self, CalQuaternion *pRotation)
	cdef void CalBone_SetCoreState(CalBone *self)
	cdef void CalBone_SetCoreStateRecursive(CalBone *self)
	cdef int CalCoreAnimation_AddCoreTrack(CalCoreAnimation *self, CalCoreTrack *pCoreTrack)
	cdef void CalCoreAnimation_Delete(CalCoreAnimation *self)
	cdef CalCoreTrack *CalCoreAnimation_GetCoreTrack(CalCoreAnimation *self, int coreBoneId)
	cdef float CalCoreAnimation_GetDuration(CalCoreAnimation *self)
	cdef CalCoreAnimation *CalCoreAnimation_New()
	cdef void CalCoreAnimation_SetDuration(CalCoreAnimation *self, float duration)
	cdef int CalCoreBone_AddChildId(CalCoreBone *self, int childId)
	cdef void CalCoreBone_CalculateState(CalCoreBone *self)
	cdef void CalCoreBone_Delete(CalCoreBone *self)
	cdef char *CalCoreBone_GetName(CalCoreBone *self)
	cdef int CalCoreBone_GetParentId(CalCoreBone *self)
	cdef CalQuaternion *CalCoreBone_GetRotation(CalCoreBone *self)
	cdef CalQuaternion *CalCoreBone_GetRotationAbsolute(CalCoreBone *self)
	cdef CalQuaternion *CalCoreBone_GetRotationBoneSpace(CalCoreBone *self)
	cdef CalVector *CalCoreBone_GetTranslation(CalCoreBone *self)
	cdef CalVector *CalCoreBone_GetTranslationAbsolute(CalCoreBone *self)
	cdef CalVector *CalCoreBone_GetTranslationBoneSpace(CalCoreBone *self)
	cdef CalUserData CalCoreBone_GetUserData(CalCoreBone *self)
	cdef CalCoreBone *CalCoreBone_New(char *strName)
	cdef void CalCoreBone_SetCoreSkeleton(CalCoreBone *self, CalCoreSkeleton *pCoreSkeleton)
	cdef void CalCoreBone_SetParentId(CalCoreBone *self, int parentId)
	cdef void CalCoreBone_SetRotation(CalCoreBone *self, CalQuaternion *pRotation)
	cdef void CalCoreBone_SetRotationBoneSpace(CalCoreBone *self, CalQuaternion *pRotation)
	cdef void CalCoreBone_SetTranslation(CalCoreBone *self, CalVector *pTranslation)
	cdef void CalCoreBone_SetTranslationBoneSpace(CalCoreBone *self, CalVector *pTranslation)
	cdef void CalCoreBone_SetUserData(CalCoreBone *self, CalUserData userData)
	cdef void CalCoreKeyframe_Delete(CalCoreKeyframe *self)
	cdef CalQuaternion *CalCoreKeyframe_GetRotation(CalCoreKeyframe *self)
	cdef float CalCoreKeyframe_GetTime(CalCoreKeyframe *self)
	cdef CalVector *CalCoreKeyframe_GetTranslation(CalCoreKeyframe *self)
	cdef CalCoreKeyframe *CalCoreKeyframe_New()
	cdef void CalCoreKeyframe_SetRotation(CalCoreKeyframe *self, CalQuaternion *pRotation)
	cdef void CalCoreKeyframe_SetTime(CalCoreKeyframe *self, float time)
	cdef void CalCoreKeyframe_SetTranslation(CalCoreKeyframe *self, CalVector *pTranslation)
	cdef void CalCoreMaterial_Delete(CalCoreMaterial *self)
	cdef int CalCoreMaterial_GetMapCount(CalCoreMaterial *self)
	cdef char *CalCoreMaterial_GetMapFilename(CalCoreMaterial *self, int mapId)
	cdef CalUserData CalCoreMaterial_GetMapUserData(CalCoreMaterial *self, int mapId)
	cdef float CalCoreMaterial_GetShininess(CalCoreMaterial *self)
	cdef CalUserData CalCoreMaterial_GetUserData(CalCoreMaterial *self)
	cdef CalCoreMaterial *CalCoreMaterial_New()
	cdef int CalCoreMaterial_Reserve(CalCoreMaterial *self, int mapCount)
	cdef int CalCoreMaterial_SetMapUserData(CalCoreMaterial *self, int mapId, CalUserData userData)
	cdef void CalCoreMaterial_SetShininess(CalCoreMaterial *self, float shininess)
	cdef void CalCoreMaterial_SetUserData(CalCoreMaterial *self, CalUserData userData)
	cdef int CalCoreMesh_AddCoreSubmesh(CalCoreMesh *self, CalCoreSubmesh *pCoreSubmesh)
	cdef void CalCoreMesh_Delete(CalCoreMesh *self)
	cdef CalCoreSubmesh *CalCoreMesh_GetCoreSubmesh(CalCoreMesh *self, int id)
	cdef int CalCoreMesh_GetCoreSubmeshCount(CalCoreMesh *self)
	cdef CalCoreMesh *CalCoreMesh_New()
	cdef int CalCoreModel_AddCoreAnimation(CalCoreModel *self, CalCoreAnimation *pCoreAnimation)
	cdef int CalCoreModel_AddCoreMaterial(CalCoreModel *self, CalCoreMaterial *pCoreMaterial)
	cdef int CalCoreModel_AddCoreMesh(CalCoreModel *self, CalCoreMesh *pCoreMesh)
	cdef int CalCoreModel_CreateCoreMaterialThread(CalCoreModel *self, int coreMaterialThreadId)
	cdef void CalCoreModel_Delete(CalCoreModel *self)
	cdef CalCoreAnimation *CalCoreModel_GetCoreAnimation(CalCoreModel *self, int coreAnimationId)
	cdef int CalCoreModel_GetCoreAnimationCount(CalCoreModel *self)
	cdef CalCoreMaterial *CalCoreModel_GetCoreMaterial(CalCoreModel *self, int coreMaterialId)
	cdef int CalCoreModel_GetCoreMaterialCount(CalCoreModel *self)
	cdef int CalCoreModel_GetCoreMaterialId(CalCoreModel *self, int coreMaterialThreadId, int coreMaterialSetId)
	cdef CalCoreMesh *CalCoreModel_GetCoreMesh(CalCoreModel *self, int coreMeshId)
	cdef int CalCoreModel_GetCoreMeshCount(CalCoreModel *self)
	cdef CalCoreSkeleton *CalCoreModel_GetCoreSkeleton(CalCoreModel *self)
	cdef CalUserData CalCoreModel_GetUserData(CalCoreModel *self)
	cdef int CalCoreModel_LoadCoreAnimation(CalCoreModel *self, char *strFilename)
	cdef int CalCoreModel_LoadCoreMaterial(CalCoreModel *self, char *strFilename)
	cdef int CalCoreModel_LoadCoreMesh(CalCoreModel *self, char *strFilename)
	cdef int CalCoreModel_LoadCoreSkeleton(CalCoreModel *self, char *strFilename)
	cdef CalCoreModel *CalCoreModel_New(char *strName)
	cdef int CalCoreModel_SaveCoreAnimation(CalCoreModel *self, char *strFilename, int coreAnimtionId)
	cdef int CalCoreModel_SaveCoreMaterial(CalCoreModel *self, char *strFilename, int coreMaterialId)
	cdef int CalCoreModel_SaveCoreMesh(CalCoreModel *self, char *strFilename, int coreMeshId)
	cdef int CalCoreModel_SaveCoreSkeleton(CalCoreModel *self, char *strFilename)
	cdef int CalCoreModel_SetCoreMaterialId(CalCoreModel *self, int coreMaterialThreadId, int coreMaterialSetId, int coreMaterialId)
	cdef void CalCoreModel_SetCoreSkeleton(CalCoreModel *self, CalCoreSkeleton *pCoreSkeleton)
	cdef void CalCoreModel_SetUserData(CalCoreModel *self, CalUserData userData)
	cdef int CalCoreSkeleton_AddCoreBone(CalCoreSkeleton *self, CalCoreBone *pCoreBone)
	cdef void CalCoreSkeleton_CalculateState(CalCoreSkeleton *self)
	cdef void CalCoreSkeleton_Delete(CalCoreSkeleton *self)
	cdef CalCoreBone *CalCoreSkeleton_GetCoreBone(CalCoreSkeleton *self, int coreBoneId)
	cdef int CalCoreSkeleton_GetCoreBoneId(CalCoreSkeleton *self, char *strName)
	cdef CalCoreSkeleton *CalCoreSkeleton_New()
	cdef void CalCoreSubmesh_Delete(CalCoreSubmesh *self)
	cdef int CalCoreSubmesh_GetCoreMaterialThreadId(CalCoreSubmesh *self)
	cdef int CalCoreSubmesh_GetFaceCount(CalCoreSubmesh *self)
	cdef int CalCoreSubmesh_GetLodCount(CalCoreSubmesh *self)
	cdef int CalCoreSubmesh_GetSpringCount(CalCoreSubmesh *self)
	cdef int CalCoreSubmesh_GetVertexCount(CalCoreSubmesh *self)
	cdef CalCoreSubmesh *CalCoreSubmesh_New()
	cdef int CalCoreSubmesh_Reserve(CalCoreSubmesh *self, int vertexCount, int textureCoordinateCount, int faceCount, int springCount)
	cdef void CalCoreSubmesh_SetCoreMaterialThreadId(CalCoreSubmesh *self, int coreMaterialThreadId)
	cdef void CalCoreSubmesh_SetLodCount(CalCoreSubmesh *self, int lodCount)
	cdef int CalCoreSubmesh_IsTangentsEnabled(CalCoreSubmesh *self, int mapId)
	cdef int CalCoreSubmesh_EnableTangents(CalCoreSubmesh *self, int mapId, int enabled)
	cdef int CalCoreTrack_AddCoreKeyframe(CalCoreTrack *self, CalCoreKeyframe *pCoreKeyframe)
	cdef void CalCoreTrack_Delete(CalCoreTrack *self)
	cdef int CalCoreTrack_GetCoreBoneId(CalCoreTrack *self)
	cdef int CalCoreTrack_GetState(CalCoreTrack *self, float time, CalVector *pTranslation, CalQuaternion *pRotation)
	cdef CalCoreTrack *CalCoreTrack_New()
	cdef int CalCoreTrack_SetCoreBoneId(CalCoreTrack *self, int coreBoneId)
	cdef int CalError_GetLastErrorCode()
	cdef char *CalError_GetLastErrorDescription()
	cdef char *CalError_GetLastErrorFile()
	cdef int CalError_GetLastErrorLine()
	cdef char *CalError_GetLastErrorText()
	cdef void CalError_PrintLastError()
	cdef void CalLoader_Delete(CalLoader *self)
	cdef CalCoreAnimation *CalLoader_LoadCoreAnimation(CalLoader *self, char *strFilename)
	cdef CalCoreMaterial *CalLoader_LoadCoreMaterial(CalLoader *self, char *strFilename)
	cdef CalCoreMesh *CalLoader_LoadCoreMesh(CalLoader *self, char *strFilename)
	cdef CalCoreSkeleton *CalLoader_LoadCoreSkeleton(CalLoader *self, char *strFilename)
	cdef CalLoader *CalLoader_New()
	cdef void CalMesh_Delete(CalMesh *self)
	cdef CalCoreMesh *CalMesh_GetCoreMesh(CalMesh *self)
	cdef CalSubmesh *CalMesh_GetSubmesh(CalMesh *self, int id)
	cdef int CalMesh_GetSubmeshCount(CalMesh *self)
	cdef CalMesh *CalMesh_New(CalCoreMesh *pCoreMesh)
	cdef void CalMesh_SetLodLevel(CalMesh *self, float lodLevel)
	cdef void CalMesh_SetMaterialSet(CalMesh *self, int setId)
	cdef void CalMesh_SetModel(CalMesh *self, CalModel *pModel)
	cdef int CalMixer_BlendCycle(CalMixer *self, int id, float weight, float delay)
	cdef int CalMixer_ClearCycle(CalMixer *self, int id, float delay)
	cdef void CalMixer_Delete(CalMixer *self)
	cdef int CalMixer_ExecuteAction(CalMixer *self, int id, float delayIn, float delayOut)
	cdef CalMixer *CalMixer_New(CalModel *pModel)
	cdef void CalMixer_UpdateAnimation(CalMixer *self, float deltaTime)
	cdef void CalMixer_UpdateSkeleton(CalMixer *self)
	cdef int CalModel_AttachMesh(CalModel *self, int coreMeshId)
	cdef void CalModel_Delete(CalModel *self)
	cdef int CalModel_DetachMesh(CalModel *self, int coreMeshId)
	cdef CalCoreModel *CalModel_GetCoreModel(CalModel *self)
	cdef CalMesh *CalModel_GetMesh(CalModel *self, int coreMeshId)
	cdef CalMixer *CalModel_GetMixer(CalModel *self)
	cdef CalPhysique *CalModel_GetPhysique(CalModel *self)
	cdef CalRenderer *CalModel_GetRenderer(CalModel *self)
	cdef CalSkeleton *CalModel_GetSkeleton(CalModel *self)
	cdef CalSpringSystem *CalModel_GetSpringSystem(CalModel *self)
	cdef CalUserData CalModel_GetUserData(CalModel *self)
	cdef CalModel *CalModel_New(CalCoreModel *pCoreModel)
	cdef void CalModel_SetLodLevel(CalModel *self, float lodLevel)
	cdef void CalModel_SetMaterialSet(CalModel *self, int setId)
	cdef void CalModel_SetUserData(CalModel *self, CalUserData userData)
	cdef void CalModel_Update(CalModel *self, float deltaTime)
	cdef int CalPhysique_CalculateNormals(CalPhysique *self, CalSubmesh *pSubmesh, float *pNormalBuffer)
	cdef int CalPhysique_CalculateVertices(CalPhysique *self, CalSubmesh *pSubmesh, float *pVertexBuffer)
	cdef int CalPhysique_CalculateVerticesAndNormals(CalPhysique *self, CalSubmesh *pSubmesh, float *pVertexBuffer)
	cdef int CalPhysique_CalculateVerticesNormalsAndTexCoords(CalPhysique *self, CalSubmesh *pSubmesh, float *pVertexBuffer, int NumTexCoords)
	cdef int CalPhysique_CalculateTangentSpaces(CalPhysique *self, CalSubmesh *pSubmesh, int mapId, float *pTangentSpaceBuffer)
	cdef void CalPhysique_Delete(CalPhysique *self)
	cdef CalPhysique *CalPhysique_New(CalModel *pModel)
	cdef void CalPhysique_Update(CalPhysique *self)
	cdef void CalQuaternion_Blend(CalQuaternion *self, float d, CalQuaternion *pQ)
	cdef void CalQuaternion_Clear(CalQuaternion *self)
	cdef void CalQuaternion_Conjugate(CalQuaternion *self)
	cdef void CalQuaternion_Delete(CalQuaternion *self)
	cdef void CalQuaternion_Equal(CalQuaternion *self, CalQuaternion *pQ)
	cdef float *CalQuaternion_Get(CalQuaternion *self)
	cdef void CalQuaternion_Multiply(CalQuaternion *self, CalQuaternion *pQ)
	cdef void CalQuaternion_MultiplyVector(CalQuaternion *self, CalVector *pV)
	cdef CalQuaternion *CalQuaternion_New()
	cdef void CalQuaternion_Op_Multiply(CalQuaternion *pResult, CalQuaternion *pQ, CalQuaternion *pR)
	cdef void CalQuaternion_Set(CalQuaternion *self, float qx, float qy, float qz, float qw)
	cdef int CalRenderer_BeginRendering(CalRenderer *self)
	cdef void CalRenderer_Delete(CalRenderer *self)
	cdef void CalRenderer_EndRendering(CalRenderer *self)
	cdef void CalRenderer_GetAmbientColor(CalRenderer *self, unsigned char *pColorBuffer)
	cdef void CalRenderer_GetDiffuseColor(CalRenderer *self, unsigned char *pColorBuffer)
	cdef int CalRenderer_GetFaceCount(CalRenderer *self)
	cdef int CalRenderer_GetFaces(CalRenderer *self, int *pFaceBuffer)
	cdef int CalRenderer_GetMapCount(CalRenderer *self)
	cdef CalUserData CalRenderer_GetMapUserData(CalRenderer *self, int mapId)
	cdef int CalRenderer_GetMeshCount(CalRenderer *self)
	cdef int CalRenderer_GetNormals(CalRenderer *self, float *pNormalBuffer)
	cdef float CalRenderer_GetShininess(CalRenderer *self)
	cdef void CalRenderer_GetSpecularColor(CalRenderer *self, unsigned char *pColorBuffer)
	cdef int CalRenderer_GetSubmeshCount(CalRenderer *self, int meshId)
	cdef int CalRenderer_GetTextureCoordinates(CalRenderer *self, int mapId, float *pTextureCoordinateBuffer)
	cdef int CalRenderer_GetVertexCount(CalRenderer *self)
	cdef int CalRenderer_GetVertices(CalRenderer *self, float *pVertexBuffer)
	cdef int CalRenderer_GetVerticesAndNormals(CalRenderer *self, float *pVertexBuffer)
	cdef int CalRenderer_GetVerticesNormalsAndTexCoords(CalRenderer *self, float *pVertexBuffer, int NumTexCoords)
	cdef int CalRenderer_GetTangentSpaces(CalRenderer *self, int mapId, float *pTangentSpaceBuffer)
	cdef int CalRenderer_IsTangentsEnabled(CalRenderer *self, int mapId)
	cdef CalRenderer *CalRenderer_New(CalModel* pModel)
	cdef int CalRenderer_SelectMeshSubmesh(CalRenderer *self, int meshId, int submeshId)
	cdef void CalSaver_Delete(CalSaver *self)
	cdef CalSaver *CalSaver_New()
	cdef int CalSaver_SaveCoreAnimation(CalSaver *self, char *strFilename, CalCoreAnimation *pCoreAnimation)
	cdef int CalSaver_SaveCoreMaterial(CalSaver *self, char *strFilename, CalCoreMaterial *pCoreMaterial)
	cdef int CalSaver_SaveCoreMesh(CalSaver *self, char *strFilename, CalCoreMesh *pCoreMesh)
	cdef int CalSaver_SaveCoreSkeleton(CalSaver *self, char *strFilename, CalCoreSkeleton *pCoreSkeleton)
	cdef void CalSkeleton_CalculateState(CalSkeleton *self)
	cdef void CalSkeleton_ClearState(CalSkeleton *self)
	cdef void CalSkeleton_Delete(CalSkeleton *self)
	cdef CalBone *CalSkeleton_GetBone(CalSkeleton *self, int boneId)
	cdef CalCoreSkeleton *CalSkeleton_GetCoreSkeleton(CalSkeleton *self)
	cdef void CalSkeleton_LockState(CalSkeleton *self)
	cdef CalSkeleton *CalSkeleton_New(CalCoreSkeleton *pCoreSkeleton)
	cdef int CalSkeleton_GetBonePoints(CalSkeleton *self, float *pPoints)
	cdef int CalSkeleton_GetBonePointsStatic(CalSkeleton *self, float *pPoints)
	cdef int CalSkeleton_GetBoneLines(CalSkeleton *self, float *pLines)
	cdef int CalSkeleton_GetBoneLinesStatic(CalSkeleton *self, float *pLines)
	cdef void CalSpringSystem_CalculateForces(CalSpringSystem *self, CalSubmesh *pSubmesh, float deltaTime)
	cdef void CalSpringSystem_CalculateVertices(CalSpringSystem *self, CalSubmesh *pSubmesh, float deltaTime)
	cdef void CalSpringSystem_Delete(CalSpringSystem *self)
	cdef CalSpringSystem *CalSpringSystem_New(CalModel *pModel)
	cdef void CalSpringSystem_Update(CalSpringSystem *self, float deltaTime)
	cdef void CalSubmesh_Delete(CalSubmesh *self)
	cdef CalCoreSubmesh *CalSubmesh_GetCoreSubmesh(CalSubmesh *self)
	cdef int CalSubmesh_GetCoreMaterialId(CalSubmesh *self)
	cdef int CalSubmesh_GetFaceCount(CalSubmesh *self)
	cdef int CalSubmesh_GetFaces(CalSubmesh *self, int *pFaceBuffer)
	cdef int CalSubmesh_GetVertexCount(CalSubmesh *self)
	cdef int CalSubmesh_HasInternalData(CalSubmesh *self)
	cdef CalSubmesh *CalSubmesh_New(CalCoreSubmesh *pCoreSubmesh)
	cdef void CalSubmesh_SetCoreMaterialId(CalSubmesh *self, int coreMaterialId)
	cdef void CalSubmesh_SetLodLevel(CalSubmesh *self, float lodLevel)
	cdef void CalVector_Add(CalVector *self, CalVector *pV)
	cdef void CalVector_Blend(CalVector *self, float d, CalVector *pV)
	cdef void CalVector_Clear(CalVector *self)
	cdef void CalVector_Delete(CalVector *self)
	cdef void CalVector_Equal(CalVector *self, CalVector *pV)
	cdef void CalVector_InverseScale(CalVector *self, float d)
	cdef float *CalVector_Get(CalVector *self)
	cdef float CalVector_Length(CalVector *self)
	cdef CalVector *CalVector_New()
	cdef float CalVector_Normalize(CalVector *self)
	cdef void CalVector_Op_Add(CalVector *pResult, CalVector *pV, CalVector *pU)
	cdef void CalVector_Op_Subtract(CalVector *pResult, CalVector *pV, CalVector *pU)
	cdef void CalVector_CalVector_Op_Scale(CalVector *pResult, CalVector *pV, float d)
	cdef void CalVector_CalVector_Op_InverseScale(CalVector *pResult, CalVector *pV, float d)
	cdef float CalVector_Op_Scalar(CalVector *pV, CalVector *pU)
	cdef void CalVector_Op_Cross(CalVector *pResult, CalVector *pV, CalVector *pU)
	cdef void CalVector_Scale(CalVector *self, float d)
	cdef void CalVector_Set(CalVector *self, float vx, float vy, float vz)
	cdef void CalVector_Subtract(CalVector *self, CalVector *pV)
	cdef void CalVector_Transform(CalVector *self, CalQuaternion *pQ)

#cdef extern from "cal3d_hack.h":
#  cdef void CalModel_ResetMixer(CalModel *self)
	
	
