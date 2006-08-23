# -*- indent-tabs-mode: t -*-
cdef _World _find_or_create_most_probable_ode_parent_from(_World world):
	while not (world._option & WORLD_HAS_ODE or world.parent is None):
		world = world.parent
	if not world._option & WORLD_HAS_ODE:
		world._activate_ode_world()
	return world

