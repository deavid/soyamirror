############################# Constants ###############################
cdef enum:
	paramLoStop        = 0
	paramHiStop        = 1
	paramVel           = 2
	paramFMax          = 3
	paramFudgeFactor   = 4
	paramBounce        = 5
	paramCFM           = 6
	paramStopERP       = 7
	paramStopCFM       = 8
	paramSuspensionERP = 9
	paramSuspensionCFM = 10
	
	ParamLoStop        = 0
	ParamHiStop        = 1
	ParamVel           = 2
	ParamFMax          = 3
	ParamFudgeFactor   = 4
	ParamBounce        = 5
	ParamCFM           = 6
	ParamStopERP       = 7
	ParamStopCFM       = 8
	ParamSuspensionERP = 9
	ParamSuspensionCFM = 10
	
	ParamLoStop2        = 256+0
	ParamHiStop2        = 256+1
	ParamVel2           = 256+2
	ParamFMax2          = 256+3
	ParamFudgeFactor2   = 256+4
	ParamBounce2        = 256+5
	ParamCFM2           = 256+6
	ParamStopERP2       = 256+7
	ParamStopCFM2       = 256+8
	ParamSuspensionERP2 = 256+9
	ParamSuspensionCFM2 = 256+10
	
	ContactMu2	= 0x001
	ContactFDir1	= 0x002
	ContactBounce	= 0x004
	ContactSoftERP	= 0x008
	ContactSoftCFM	= 0x010
	ContactMotion1	= 0x020
	ContactMotion2	= 0x040
	ContactSlip1	= 0x080
	ContactSlip2	= 0x100
	
	ContactApprox0 = 0x0000
	ContactApprox1_1	= 0x1000
	ContactApprox1_2	= 0x2000
	ContactApprox1	= 0x3000
	
	#AMotorUser  = dAMotorUser
	#AMotorEuler = dAMotorEuler
	
	#Infinity = dInfinity