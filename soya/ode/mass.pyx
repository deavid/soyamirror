# -*- indent-tabs-mode: t -*-

# Mass class.
Mass = None
cdef class _Mass: # XXX make total for all XXX make class method for all
	"""Mass parameters of a rigid body.

	This class stores mass parameters of a rigid body which can be
	accessed through the following attributes:

	 - mass: The total mass of the body (float)
	 - c:    The center of gravity position in body frame (3-tuple of floats)
	 - I:    The 3x3 inertia tensor in body frame (3-tuple of 3-tuples)

	This class wraps the dMass structure from the C API.

	@ivar mass: The total mass of the body
	@ivar c: The center of gravity position in body frame (cx, cy, cz)
	@ivar I: The 3x3 inertia tensor in body frame ((I11, I12, I13), (I12, I22, I23), (I13, I23, I33))
	@type mass: float
	@type c: 3-tuple of floats
	@type I: 3-tuple of 3-tuples of floats 
	"""
	def __init__(self, float mass=1, float cgx=0, float cgy=0, float cgz=0,
					  float I11=1,  float I22=1, float I33=1, float I12=0,
					  float I13=0, float I23=0):
		dMassSetParameters(&self._mass, mass, cgx, cgy, cgz, I11, I22, I33, I12, I13, I23)
		
	#cdef dMass _mass
	def set_parameters(self, float  mass, float  cgx, float  cgy, float  cgz, float  I11, float  I22, float  I33, float  I12, float  I13, float  I23):
		"""setParameters(mass, cgx, cgy, cgz, I11, I22, I33, I12, I13, I23)

		Set the mass parameters to the given values.

		@param mass: Total mass of the body.
		@param cgx: Center of gravity position in the body frame (x component).
		@param cgy: Center of gravity position in the body frame (y component).
		@param cgz: Center of gravity position in the body frame (z component).
		@param I11: Inertia tensor
		@param I22: Inertia tensor
		@param I33: Inertia tensor
		@param I12: Inertia tensor
		@param I13: Inertia tensor
		@param I23: Inertia tensor
		@type mass: float
		@type cgx: float
		@type cgy: float
		@type cgz: float
		@type I11: float
		@type I22: float
		@type I33: float
		@type I12: float
		@type I13: float
		@type I23: float
		"""
		dMassSetParameters(&self._mass, mass, cgx, cgy, cgz, I11, I22, I33, I12, I13, I23)
		
	def set_inertia_tension(self, float  I11, float I22, float I33, float I12, float I13, float I23):
		"""Set the Inertia Tensor to the given values.
		/ I11, I12, I13 \
		| I12, I22, I23 |
		\ I13, I23, I33 /
		
		@param I11: Inertia tensor
		@param I22: Inertia tensor
		@param I33: Inertia tensor
		@param I12: Inertia tensor
		@param I13: Inertia tensor
		@param I23: Inertia tensor
		@type mass: float
		@type cgx: float
		@type cgy: float
		@type cgz: float
		@type I11: float
		@type I22: float
		@type I33: float
		@type I12: float
		@type I13: float
		@type I23: float"""
		dMassSetParameters(&self._mass, self._mass.mass, self._mass.c[0],
				self._mass.c[1], self._mass.c[2], I11, I22, I33, I12, I13, I23)
		
	def __getattr__(self, name):
		if name=="mass":
			return self._mass.mass
		elif name=="c":
			return (self._mass.c[0], self._mass.c[1], self._mass.c[2])
		elif name=="I":
			return ((self._mass.I[0],self._mass.I[1],self._mass.I[2]),
					(self._mass.I[4],self._mass.I[5],self._mass.I[6]),
					(self._mass.I[8],self._mass.I[9],self._mass.I[10]))
		else:
			raise AttributeError,"Mass object has no attribute '%s'"%name

	def __setattr__(self, name, value):
		if name=="mass":
			dMassAdjust(&self._mass, value)
		elif name=="c":
			dMassTranslate(&self._mass,  value[0]-self._mass.c[0],
										value[1]-self._mass.c[1],
										value[2]-self._mass.c[2])
		elif name=="I":
			raise AttributeError("use set_parameter to set I")
			#self._mass.I[ 0] = value[0][0]
			#self._mass.I[ 1] = value[0][1]
			#self._mass.I[ 2] = value[0][2]
			#self._mass.I[ 4] = value[1][0]
			#self._mass.I[ 5] = value[1][1]
			#self._mass.I[ 6] = value[1][2]
			#self._mass.I[ 8] = value[2][0]
			#self._mass.I[ 9] = value[2][1]
			#self._mass.I[10] = value[2][2]
		else:
			raise AttributeError,"Mass object has no attribute '%s'"%name

	def __iadd__(self, _Mass other):
		dMassAdd(&self._mass, &other._mass)
		return self
		
	def __add__(self, _Mass other):
		cdef _Mass new
		new = Mass()
		dMassAdd(&new._mass, &other._mass)
		dMassAdd(&new._mass, &other._mass)
		return new
	def __cmp__(self,_Mass other):
		"""compare the two mass of the two Mass object"""
		return cmp(self._mass.mass,other._mass.mass)	
	
	#def __new__(self, *args, **kw):
	#	dMassSetZero(&self._mass)
		
	cdef __getcstate__(self):
		cdef Chunk* chunk
		chunk = get_chunk()
		chunk_add_float_endian_safe(chunk,self._mass.mass)
		chunk_add_floats_endian_safe(chunk,self._mass.c,4)
		chunk_add_floats_endian_safe(chunk,self._mass.I,12)
		return drop_chunk_to_string(chunk)
	cdef __setcstate__(self,cstate):
		cdef Chunk* chunk
		chunk = string_to_chunk(cstate)
		chunk_get_float_endian_safe(chunk,&self._mass.mass)
		chunk_get_floats_endian_safe(chunk,self._mass.c,4)
		chunk_get_floats_endian_safe(chunk,self._mass.I,12)
		drop_chunk(chunk)
	def set_zero(self):
		"""setZero()

		Set all the mass parameters to zero."""
		dMassSetZero(&self._mass)

	def set_sphere(self, float density, float radius):
		"""setSphere(density, radius)
		
		Set the mass parameters to represent a sphere of the given radius
		and density, with the center of mass at (0,0,0) relative to the body.

		@param density: The density of the sphere
		@param radius: The radius of the sphere
		@type density: float
		@type radius: float
		"""
		dMassSetSphere(&self._mass, density, radius)
	def set_sphere_total(self, float total_mass, float radius):
		"""setSphere(density, radius)
		
		Set the mass parameters to represent a sphere of the given radius
		and total_mass, with the center of mass at (0,0,0) relative to the body.

		@param total_mass: The mass of the sphere
		@param radius: The radius of the sphere
		@type density: float
		@type radius: float
		"""
		dMassSetSphereTotal(&self._mass, total_mass, radius)

	def set_capsule(self, float density, direction, float r, float h):
		"""setCapsule(density, direction, r, h)
		
		Set the mass parameters to represent a capsule of the
		given parameters and density, with the center of mass at
		(0,0,0) relative to the body. The radius of the cylinder (and
		the spherical cap) is r. The length of the cylinder (not
		counting the spherical cap) is h. The cylinder's long axis is
		oriented along the body's x, y or z axis according to the
		value of direction (1=x, 2=y, 3=z).

		@param density: The density of the cylinder
		@param direction: The direction of the cylinder (1=x axis, 2=y axis, 3=z axis)
		@param r: The radius of the cylinder
		@param h: The length of the cylinder (without the caps)
		@type density: float
		@type direction: int
		@type r: float
		@type h: float
		"""
		dMassSetCapsule(&self._mass, density, direction, r, h)
		
	def set_capsule_total(self, float total_mass, direction, float r, float h):
		"""setCapsuleTotal(total_mass, direction, r, h)
		
		Set the mass parameters to represent a capsule of the
		given parameters and mass, with the center of mass at
		(0,0,0) relative to the body. The radius of the cylinder (and
		the spherical cap) is r. The length of the cylinder (not
		counting the spherical cap) is h. The cylinder's long axis is
		oriented along the body's x, y or z axis according to the
		value of direction (1=x, 2=y, 3=z).

		@param total_mass: The Mass of the cylinder
		@param direction: The direction of the cylinder (1=x axis, 2=y axis, 3=z axis)
		@param r: The radius of the cylinder
		@param h: The length of the cylinder (without the caps)
		@type total_mass: float
		@type direction: int
		@type r: float
		@type h: float
		"""
		dMassSetCapsuleTotal(&self._mass, total_mass, direction, r, h)

	def set_cylinder(self, float density, direction, float r, float h):
		"""setCylinder(density, direction, r, h)
		
		Set the mass parameters to represent a flat-ended cylinder of
		the given parameters and density, with the center of mass at
		(0,0,0) relative to the body. The radius of the cylinder is r.
		The length of the cylinder is h. The cylinder's long axis is
		oriented along the body's x, y or z axis according to the value
		of direction (1=x, 2=y, 3=z).

		@param density: The density of the cylinder
		@param direction: The direction of the cylinder (1=x axis, 2=y axis, 3=z axis)
		@param r: The radius of the cylinder
		@param h: The length of the cylinder
		@type density: float
		@type direction: int
		@type r: float
		@type h: float
		"""
		dMassSetCylinder(&self._mass, density, direction, r, h)
	def set_cylinder_total(self, float total_mass, direction, float r, float h):
		"""setCylinder(total_mass, direction, r, h)
		
		Set the mass parameters to represent a flat-ended cylinder of
		the given parameters and mass, with the center of mass at
		(0,0,0) relative to the body. The radius of the cylinder is r.
		The length of the cylinder is h. The cylinder's long axis is
		oriented along the body's x, y or z axis according to the value
		of direction (1=x, 2=y, 3=z).

		@param totam_mass: The mass of the cylinder
		@param direction: The direction of the cylinder (1=x axis, 2=y axis, 3=z axis)
		@param r: The radius of the cylinder
		@param h: The length of the cylinder
		@type math: float
		@type direction: int
		@type r: float
		@type h: float
		"""
		dMassSetCylinderTotal(&self._mass, total_mass, direction, r, h)

		

	def set_box(self, float density, float lx, float ly, float lz):
		"""setBox(density, lx, ly, lz)

		Set the mass parameters to represent a box of the given
		dimensions and density, with the center of mass at (0,0,0)
		relative to the body. The side lengths of the box along the x,
		y and z axes are lx, ly and lz.

		@param density: The density of the box
		@param lx: The length along the x axis
		@param ly: The length along the y axis
		@param lz: The length along the z axis
		@type density: float
		@type lx: float
		@type ly: float
		@type lz: float
		"""
		dMassSetBox(&self._mass, density, lx, ly, lz)

	def set_box_total(self, float total_mass, float lx, float ly, float lz):
		"""setBox(total_mass, lx, ly, lz)

		Set the mass parameters to represent a box of the given
		dimensions and mass, with the center of mass at (0,0,0)
		relative to the body. The side lengths of the box along the x,
		y and z axes are lx, ly and lz.

		@param total_mass: The mass of the box
		@param lx: The length along the x axis
		@param ly: The length along the y axis
		@param lz: The length along the z axis
		@type total_mass: float
		@type lx: float
		@type ly: float
		@type lz: float
		"""
		dMassSetBoxTotal(&self._mass, total_mass, lx, ly, lz)
#	def adjust(self, float newmass):
#		"""adjust(newmass)
#
#		Adjust the total mass. Given mass parameters for some object,
#		adjust them so the total mass is now newmass. This is useful
#		when using the setXyz() methods to set the mass parameters for
#		certain objects - they take the object density, not the total
#		mass.
#
#		@param newmass: The new total mass
#		@type newmass: float
#		"""
#		dMassAdjust(&self._mass, newmass)

	def translate(self, t): #Make it more soya by supporting soya's vector   ???
						   #Since Mass don't have nor parent coordsyst nor body
						   # No
		"""translate(t)

		Adjust mass parameters. Given mass parameters for some object,
		adjust them to represent the object displaced by (x,y,z)
		relative to the body frame.

		@param t: Translation vector (x, y, z)
		@type t: 3-tuple of floats
		"""
		dMassTranslate(&self._mass, t[0], t[1], t[2])

	def rotate(self,R): #Make it more soya by supporting soya's orientation  ???
		                #Since Mass don't have nor parent coordsyst nor body: no
		"""
		Given mass parameters for some object, adjust them to
		represent the object rotated by R relative to the body frame.
		"""
		cdef dMatrix3  r 
		r[0] = R[0]
		r[1] = R[1]
		r[2] = R[2]
		r[3] = R[3]
		r[4] = R[4]
		r[5] = R[5]
		r[6] = R[6]
		r[7] = R[7]
		r[8] = R[8]
		r[9] = R[9]
		r[10]= R[10]
		r[11]= R[11]
		
		dMassRotate(&self._mass, r)

	def add_mass(self, _Mass other):
		"""add_mass( another_mass)

		Add the mass b to the mass object. Masses can also be added using
		the + operator.

		@param b: The mass to add to this mass
		@type b: Mass
		"""
		dMassAdd(&self._mass, &other._mass)



# Speudo class

def CapsuleMass(value, direction, r, h,mode="density"):
	"""
	Create a Mass representing a capsule of the
	given parameters, with the center of mass at
	(0,0,0) relative to the body. The radius of the cylinder (and
	the spherical cap) is r. The length of the cylinder (not
	counting the spherical cap) is h. The cylinder's long axis is
	oriented along the body's x, y or z axis according to the
	value of direction (1=x, 2=y, 3=z).

	@param value: The value of the density or the total mass (according the mode)
	@param direction: The direction of the cylinder (1=x axis, 2=y axis, 3=z axis)
	@param r: The radius of the cylinder
	@param h: The length of the cylinder (without the caps)
	@param mode: "density" or "total_mass" the way the Mass is created
	@type density: float
	@type direction: int
	@type r: float
	@type h: float
	"""
	sph = Mass()
	if mode == "density":
		sph.set_capsule(value, r)
	elif mode == "total_mass":
		sph.set_capsuleTotal(value, r)
	else:
		raise ValueError("Unsupported CapsuleMass Mode : %s"%mode)
	return sph
	
def CylindricalMass(value=1, direction=1, r=1, h=1, mode="density"):
	"""
	Create a Mass parameters representing a flat-ended cylinder of
	the given parameters, with the center of mass at
	(0,0,0) relative to the body. The radius of the cylinder is r.
	The length of the cylinder is h. The cylinder's long axis is
	oriented along the body's x, y or z axis according to the value
	of direction (1=x, 2=y, 3=z).

	@param value: The value of the density or the total mass (according the mode)
	@param direction: The direction of the cylinder (1=x axis, 2=y axis, 3=z axis)
	@param r: The radius of the cylinder
	@param h: The length of the cylinder
	@param mode: "density" or "total_mass" the way the Mass is created
	@type value: float
	@type direction: int
	@type r: float
	@type h: float
	"""
	sph = Mass()
	if mode == "density":
		sph.set_cylinder(value, direction, r, h)
	elif mode == "total_mass":
		sph.set_cylinder_total(value, direction, r, h)
	else:
		raise ValueError("Unsupported CylindricalMass Mode : %s"%mode)
	return sph
	
def BoxedMass(value=1, lx=1, ly=1, lz=1,mode="density"):
	"""
	Create a Mass representing a box of the given
	dimensions, with the center of mass at (0,0,0)
	relative to the body. The side lengths of the box along the x,
	y and z axes are lx, ly and lz.

	@param value: The value of the density or the total mass (according the mode)
	@param lx: The length along the x axis
	@param ly: The length along the y axis
	@param lz: The length along the z axis
	@param mode: "density" or "total_mass" the way the Mass is created
	@type value: float
	@type lx: float
	@type ly: float
	@type lz: float
	"""
	sph = Mass()
	if mode == "density":
		sph.set_box(value, lx, ly, lz)
	elif mode == "total_mass":
		sph.set_box_total(value, lx, ly, lz)
	else:
		raise ValueError("Unsupported BoxedSphere Mode : %s"%mode)
	return sph
	
def SphericalMass(value=1, radius=1,mode="density"):
	"""
	Create a Spherical Mass according to the parameter, with the center of mass at (0,0,0)
	
	@param value: The value of the density or the total mass (according the mode)
	@param radius: The radius of the sphere
	@param mode: "density" or "total_mass" the way the Mass is created
	@type density: float
	@type radius: float
	"""
	sph = Mass()
	if mode == "density":
		sph.set_sphere(value,radius)
	elif mode == "total_mass":
		sph.set_sphere_total(value,radius)
	else:
		raise ValueError("Unsupported MassSphere Mode : %s"%mode)
	return sph



