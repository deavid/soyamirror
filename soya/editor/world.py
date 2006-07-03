# -*- indent-tabs-mode: t -*-

# Soya 3D
# Copyright (C) 2001-2002 Jean-Baptiste LAMY
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


from editobj.observe import *
import editobj.custom as custom
import Tkinter, time, weakref
import soya, soya.opengl, soya.sdlconst, soya.cube as cube, soya.cursor as cursor

STEP    = 0.125
EPSILON = 0.001

# Additionnal key binding. (A dict mapping key ID to a lambda taking 2 args, the root world and the edited object).
KEY_BINDINGS = {}

class WorldEditor:
	def __init__(self, world, dialog):
		self.active              = 0
		self.dialog              = dialog
		self.handles             = []
		self.vertex_handles      = []
		self.children_visibility = { world : 1 }
		
		self.world = self.current = world
		
		self.scene  = soya.World()
		self.scene.name = "__scene__"
		self.scene.atmosphere = soya.Atmosphere()
		self.scene.atmosphere.ambient = (0.5, 0.5, 0.5, 1.0)
		
		self.camera = soya.Camera(self.scene)
		self.camera.set_xyz(0.0, 0.0, 5.0)
		self.camera.rotate_y(45)
		soya.set_root_widget(self.camera)
		
		self.light = soya.Light(self.scene)
		self.light.set_xyz(0.2, 2.0, 2.2)
		self.light.top_level = 1
		self.light.cast_shadow = 0
		
		self.cursor = Cursor(self.scene, self.camera, self.handles, self.light)
		self.cursor.name = "cursor"
		
		self.content = soya.World(self.scene)
		self.content.name = "__content__"
		self.content.append(world)
		
		self.add_handles_for(world)
		
		observe_tree(world, self.on_changed)
		
		self.last_click  = 0
		self.camera_mode = 0
		
	def add_handles_for(self, item):
		if   isinstance(item, soya.Sprite):
			self.handles.append(PositionHandle(self.content, self, item))
			
		elif isinstance(item, soya.Face):
			for vertex in item.vertices: self.add_handles_for_vertex(vertex)
			
		elif isinstance(item, soya.CoordSyst):
			self.handles.append(PositionHandle   (self.content, self, item))
			self.handles.append(OrientationHandle(self.content, self, item))
			
		if   isinstance(item, soya.World) and self.children_visibility.get(item, 0):
			for subitem in item.children: self.add_handles_for(subitem)
			
	def add_handles_for_vertex(self, vertex):
		if getattr(vertex, "immature", 0): return
		
		for handle in self.vertex_handles:
			if handle.is_for(vertex): return
		
		for handle in self.vertex_handles:
			v = handle.vertices[0]
			if (v.parent is vertex.parent) and (abs(v.x - vertex.x) < EPSILON) and (abs(v.y - vertex.y) < EPSILON) and (abs(v.z - vertex.z) < EPSILON):
				handle.add_vertex(vertex)
				return handle
		else:
			handle = VertexHandle(self.content, self, vertex)
			self.handles.append(handle)
			self.vertex_handles.append(handle)
			
	def remove_handles_of(self, item):
		for handle in self.handles[:]: handle.del_for(item)
		
		if   isinstance(item, soya.Face):
			for handle in self.vertex_handles[:]:
				for vertex in item.vertices: handle.del_for(vertex)
				
		elif isinstance(item, soya.World):
			for subitem in item: self.remove_handles_of(subitem)
			
	def select_handles_for(self, item):
		self.current = item
		for handle in self.handles:
			if handle.is_for(item): handle.select()
			
	def children_edited(self, world, visible):
		self.children_visibility[world] = visible
		if visible:
			for item in world.children:
				for handle in self.handles:
					if handle.is_for(item): continue
				self.add_handles_for(item)
		else:
			for item in world.children: self.remove_handles_of(item)
			
	def on_event(self, event):
		#print event
		if   event[0] == soya.sdlconst.MOUSEMOTION:
			if soya.get_mod() & soya.sdlconst.MOD_CTRL:
				self.cursor.grid_step = STEP
			else: self.cursor.grid_step = 0.0
			
			if self.camera_mode:
				self.camera.turn_y(float(event[3]))
				self.camera.turn_x(float(event[4]))
				
			x, y = event[1], event[2]
			if   x == 0:                                   self.camera += soya.Vector(self.camera, -0.1,  0.0, 0.0)
			elif x == self.camera.get_screen_width()  - 1: self.camera += soya.Vector(self.camera,  0.1,  0.0, 0.0)
			if   y == 0:                                   self.camera += soya.Vector(self.camera,  0.0,  0.1, 0.0)
			elif y == self.camera.get_screen_height() - 1: self.camera += soya.Vector(self.camera,  0.0, -0.1, 0.0)
			
			self.cursor.mouse_moved(x, y)
			
		elif event[0] == soya.sdlconst.MOUSEBUTTONDOWN:
			if event[1] < 3: # Left or middle button
				current = time.time()
				if current - self.last_click < 0.2:
					self.cursor.button_pressed(2, soya.get_mod() & soya.sdlconst.MOD_SHIFT) # Double-click is the same that middle click
				else:
					self.cursor.button_pressed(event[1], soya.get_mod() & soya.sdlconst.MOD_SHIFT)
				self.last_click = current
			elif event[1] == 3: self.camera_mode = 1
			
		elif event[0] == soya.sdlconst.MOUSEBUTTONUP:
			if self.camera_mode:
				if   event[1] == 3: self.camera_mode = 0
				elif event[1] == 4: self._zoom(-1.0)
				elif event[1] == 5: self._zoom( 1.0)
			else:
				if   event[1] <  3: self.cursor.button_released(event[1])
				elif event[1] == 4: self.cursor.mouse_rolled(-0.25)
				elif event[1] == 5: self.cursor.mouse_rolled( 0.25)
				
		elif event[0] == soya.sdlconst.KEYDOWN:
			# Page up, page down
			if   event[1] == 280: self.cursor.mouse_rolled(-1 - 9 * (soya.get_mod() & soya.sdlconst.MOD_SHIFT))
			elif event[1] == 281: self.cursor.mouse_rolled( 1 + 9 * (soya.get_mod() & soya.sdlconst.MOD_SHIFT))
			
			# Left, right, up, down
			elif event[1] == 276: self.camera += soya.Vector(self.camera, -1.0 - 9.0 * (soya.get_mod() & soya.sdlconst.MOD_SHIFT),  0.0, 0.0)
			elif event[1] == 275: self.camera += soya.Vector(self.camera,  1.0 + 9.0 * (soya.get_mod() & soya.sdlconst.MOD_SHIFT),  0.0, 0.0)
			elif event[1] == 273: self.camera += soya.Vector(self.camera,  0.0,  1.0 + 9.0 * (soya.get_mod() & soya.sdlconst.MOD_SHIFT), 0.0)
			elif event[1] == 274: self.camera += soya.Vector(self.camera,  0.0, -1.0 - 9.0 * (soya.get_mod() & soya.sdlconst.MOD_SHIFT), 0.0)
			
			# o : toggle ortho camera
			elif event[1] == 111:
				self.camera.ortho = not self.camera.ortho
				self.camera.fov = 60.0
				
			# +, - : zoom
			elif event[1] == 270: self._zoom(-1.0 - 9 * (soya.get_mod() & soya.sdlconst.MOD_SHIFT))
			elif event[1] == 269: self._zoom( 1.0 + 9 * (soya.get_mod() & soya.sdlconst.MOD_SHIFT))
			
			# 4, 6, 8, 2, 5, 0 : predefined views
			elif event[1] == 260:
				a, b = self.world.get_box()
				cameray, cameraz = self.camera.y, self.camera.z
				self.camera.set_identity()
				self.camera.set_xyz(min((a % self.scene).x, (b % self.scene).x) - 3.0, cameray, cameraz)
				self.camera.look_at(soya.Vector(None,  1.0,  0.0,  0.0))
			elif event[1] == 262:
				a, b = self.world.get_box()
				cameray, cameraz = self.camera.y, self.camera.z
				self.camera.set_identity()
				self.camera.set_xyz(max((a % self.scene).x, (b % self.scene).x) + 3.0, cameray, cameraz)
				self.camera.look_at(soya.Vector(None, -1.0,  0.0,  0.0))
			elif event[1] == 264:
				a, b = self.world.get_box()
				camerax, cameraz = self.camera.x, self.camera.z
				self.camera.set_identity()
				self.camera.set_xyz(camerax, max((a % self.scene).y, (b % self.scene).y) + 3.0, cameraz)
				self.camera.look_at(soya.Vector(None,  0.0, -1.0,  0.0))
			elif event[1] == 258:
				a, b = self.world.get_box()
				camerax, cameraz = self.camera.x, self.camera.z
				self.camera.set_identity()
				self.camera.set_xyz(camerax, min((a % self.scene).y, (b % self.scene).y) - 3.0, cameraz)
				self.camera.look_at(soya.Vector(None,  0.0,  1.0,  0.0))
			elif event[1] == 261:
				a, b = self.world.get_box()
				camerax, cameray = self.camera.x, self.camera.y
				self.camera.set_identity()
				self.camera.set_xyz(camerax, cameray, min((a % self.scene).z, (b % self.scene).z) - 3.0)
				self.camera.look_at(soya.Vector(None,  0.0,  0.0,  1.0))
			elif event[1] == 256:
				a, b = self.world.get_box()
				camerax, cameray = self.camera.x, self.camera.y
				self.camera.set_identity()
				self.camera.set_xyz(camerax, cameray, max((a % self.scene).z, (b % self.scene).z) + 3.0)
				self.camera.look_at(soya.Vector(None,  0.0,  0.0, -1.0))
				
			# q, t : new quad, new triangle
			elif event[1] == 113:
				if hasattr(self.current, "children"): into = self.current
				else:                                 into = self.current.parent
				into.append(soya.Quad())
			elif event[1] == 116:
				if hasattr(self.current, "children"): into = self.current
				else:                                 into = self.current.parent
				into.append(soya.Triangle())
			else:
				if KEY_BINDINGS.has_key(event[1]):
					KEY_BINDINGS[event[1]](self.world, self.current)
					
	def _zoom(self, z):
		if self.camera.ortho: self.camera.fov = self.camera.fov * (1.0 + z / 10.0)
		else:                 self.camera += soya.Vector(self.camera, 0.0, 0.0, z)
			
	def render(self):
		if self.active:
			self.scene.begin_round()
			self.scene.advance_time(1.0)
			self.scene.begin_round()
			self.scene.advance_time(1.0)
			self.scene.begin_round()
			self.scene.advance_time(1.0)
			self.scene.begin_round()
			self.scene.advance_time(1.0)
			self.scene.begin_round()
			self.scene.advance_time(1.0)
			soya.render()
			
	def activate(self, event = None):
		if not self.active:
			self.active = 1
			soya.set_root_widget(self.camera)
			soya.cursor_set_visible(0)
			self.auto_render()
			
	def auto_render(self):
		for event in soya.coalesce_motion_event(soya.process_event()): self.on_event(event)
		self.render()
		self.cancel = self.dialog.after(150, self.auto_render)
		
	def deactivate(self, event = None):
		if self.active:
			self.active = 0
			soya.cursor_set_visible(1)
			self.dialog.after_cancel(self.cancel)
			
	def on_changed(self, obj, type, new, old):
		if type is list:
			for item in new:
				if not item in old:
					self.add_handles_for(item)
					if isinstance(item, soya.Face):
						for vertex in item.vertices:
							if getattr(vertex, "immature", 0):
								self.cursor.manage_click(FaceClickManager(self, item))
								break
					elif hasattr(item.__class__, "__clickmanager__"):
						self.cursor.manage_click(item.__class__.__clickmanager__(self, item))
						
			for item in old:
				if not item in new: self.remove_handles_of(item)
				
		else:
			if (not hasattr(obj, "children")) and (not hasattr(obj, "items")):
				unobserve_tree(obj, self.on_changed)
				
RED    = soya.Material(); RED   .diffuse = (1.0, 0.0, 0.0, 1.0)
GREEN  = soya.Material(); GREEN .diffuse = (0.0, 1.0, 0.0, 1.0)
BLUE   = soya.Material(); BLUE  .diffuse = (0.0, 0.0, 1.0, 1.0)
YELLOW = soya.Material(); YELLOW.diffuse = (1.0, 1.0, 0.0, 1.0)

RED_HANDLE = GREEN_HANDLE = BLUE_HANDLE = YELLOW_HANDLE = None

def build_handles():
	global RED_HANDLE, GREEN_HANDLE, BLUE_HANDLE, YELLOW_HANDLE
	
	red_cube    = cube.Cube(None, RED);    red_cube   .scale(STEP, STEP, STEP)
	green_cube  = cube.Cube(None, GREEN);  green_cube .scale(STEP, STEP, STEP)
	blue_cube   = cube.Cube(None, BLUE);   blue_cube  .scale(STEP, STEP, STEP)
	yellow_cube = cube.Cube(None, YELLOW); yellow_cube.scale(STEP, STEP, STEP)
	
	RED_HANDLE    = red_cube   .to_model()
	GREEN_HANDLE  = green_cube .to_model()
	BLUE_HANDLE   = blue_cube  .to_model()
	YELLOW_HANDLE = yellow_cube.to_model()
	
build_handles()

class Cursor(cursor.Cursor):
	def __init__(self, parent = None, camera = None, handles = None, light = None):
		cursor.Cursor.__init__(self, parent, camera, GREEN_HANDLE)
		
		self.handles        = handles
		self.draging        = 0
		self.light          = light
		self.click_managers = []
		
	def manage_click(self, click_manager):
		self.click_managers.append(click_manager)
		
	def move(self, pos): self.add_vector(self >> pos)
		
	def add_vector(self, dep):
		cursor.Cursor.add_vector(self, dep)
		for handle in self.handles: handle.cursor_moved(self, self.is_near, dep)
		self.light.move(self)
		
		if self.click_managers:
			if not self.click_managers[-1].on_motion(self): del self.click_managers[-1]
			
	__iadd__ = add_vector
	
	def is_near(self, position): return position.distance_to(self) < STEP
	def near(self, a, b): return ((self.distance_to(a) < self.distance_to(b)) and a) or b
	
	def button_pressed(self, button, multiselect = 0):
		if   button == 1:
			pred = self.is_near
			print "%s, %s, %s" % (self.x, self.y, self.z)
		else:             pred = self.is_under_tester(STEP)
		
		if self.click_managers:
			if not self.click_managers[-1].on_click(self): del self.click_managers[-1]
		else:
			handles = filter(pred, self.handles)
			if handles:
				handle = min(map(lambda handle: (self.distance_to(handle), handle), handles))[1]
				# move the cursor at the handle's Z (in the camera coordinate system)
				mouse = self % self.camera
				self.mouse_rolled((handle % self.camera).z - mouse.z)
				handle.select()
				
				if not multiselect:
					for h in self.handles:
						if not h is handle: h.highlight(0)
			else:
				for h in self.handles: h.highlight(0)
				
			self.draging = 1
				
	def button_released(self, button):
		for handle in self.selected_handles():
			handle.cursor_endmove(self)
			
		if self.click_managers:
			if not self.click_managers[-1].on_release(self): del self.click_managers[-1]
		else: self.draging = 0
		
	def selected_handles        (self): return filter(lambda handle: handle.selected   , self.handles)
	def highlighted_handles     (self): return filter(lambda handle: handle.highlighted, self.handles)
	def highlighted_only_handles(self): return filter(lambda handle: handle.highlighted and not handle.selected, self.handles)
	def nearest_selected_handle(self):
		selected_handles = self.selected_handles()
		return selected_handles and min(map(lambda handle: (self.distance_to(handle), handle), selected_handles))[1]
	def over_handle(self):
		handles = self.highlighted_only_handles()
		return handles and min(map(lambda handle: (self.distance_to(handle), handle), handles))[1]
		
class ClickManager:
	def on_motion(self, cursor):
		"""Called when the cursor is moved. Must returns true if this manager is still usefull, or false if this manager's task is achieved."""
		return 1
	def on_click(self, cursor):
		"""Called when the cursor is clicked. Must returns true if this manager is still usefull, or false if this manager's task is achieved."""
		return 1
	def on_release(self, cursor):
		"""Called when the cursor is released. Must returns true if this manager is still usefull, or false if this manager's task is achieved."""
		return 1
	
class FaceClickManager(ClickManager):
	def __init__(self, editor, face):
		self.editor = editor
		self.face   = face
		
	def on_motion(self, cursor):
		i = 0
		while not getattr(self.face.vertices[i], "immature", 0): i = i + 1
		
		while i < len(self.face.vertices):
			self.face.vertices[i].parent = self.face.parent
			self.face.vertices[i].move(cursor)
			i = i + 1
			
		return 1
	
	def on_click(self, cursor):
		i = 0
		while not getattr(self.face.vertices[i], "immature", 0): i = i + 1
		
		vertex = self.face.vertices[i]
		del vertex.immature
		
		handle = cursor.over_handle()
		if handle:
			if isinstance(handle, VertexHandle):
				handle.add_vertex(self.face.vertices[i])
			else:
				self.face.vertices[i].parent = self.face.parent
				self.face.vertices[i].move(handle)
				
				self.editor.add_handles_for_vertex(vertex)
		else:
			self.face.vertices[i].parent = self.face.parent
			self.face.vertices[i].move(cursor)
			
			self.editor.add_handles_for_vertex(vertex)
			
		return i < len(self.face.vertices) - 1
	
class MoveClickManager(ClickManager):
	def __init__(self, editor, item):
		self.editor = editor
		self.item   = item
		
	def on_motion(self, cursor):
		self.item.move(cursor)
		return 1
	
	def on_click(self, cursor):
		handle = cursor.over_handle()
		if handle:
			self.item.move(handle)
		else:
			self.item.move(cursor)
			
		return 0

# List of 3D items' classes that are positionned at the next mouse click's position.

class Handle(soya.Body):
	def __init__(self, parent, editor = None):
		soya.Body.__init__(self, parent, self.NATURAL)
		self.editor      = editor
		self.selected    = 0
		self.highlighted = 0
		self.ideal       = soya.Point(parent)
		
	def del_for(self, item):
		if self.is_for(item):
			self.parent.remove(self)
			self.editor.handles.remove(self)
			return 1
		
	def highlight(self, value = 1):
		self.highlighted = value
		if value:
			self.set_model(GREEN_HANDLE)
		else:
			if self.selected: self.select(0)
			self.set_model(self.NATURAL)
			
	def select(self, value = 1):
		self.selected = value
		if value:
			if not self.highlighted: self.highlight(1)
			
	def cursor_moved(self, cursor, pred, dep):
		if self.selected:
			if cursor.draging:
				self.ideal += dep
				if cursor.grid_step:
					pos   = self.ideal.copy()
					step  = cursor.grid_step
					d     = step / 2.0
					pos.x = ((pos.x + d) // step) * step
					pos.y = ((pos.y + d) // step) * step
					pos.z = ((pos.z + d) // step) * step
					self.move(pos)
				else: self.move(self.ideal)
		else:
			if self.highlighted:
				if not pred(self): self.highlight(0)
			elif pred(self): self.highlight()
			
	def cursor_endmove(self, cursor): pass
	

class PositionHandle(Handle):
	NATURAL = BLUE_HANDLE
	def __init__(self, parent, editor, position):
		Handle.__init__(self, parent, editor)
		
		self.position = position
		self.ideal.move(position)
		Handle.move(self, position)
		
		observe(position, self.on_changed)
		world = position.parent
		while world:
			observe(world, self.on_parent_changed)
			world = world.parent
			
	def is_for (self, item): return item is self.position
	
	def move(self, position):
		Handle.move(self, position)
		self.position.move(position)
		
	def add_vector(self, vector):
		Handle.add_vector(self, vector)
		self.position.add_vector(vector)
	__iadd__ = add_vector
	
	def on_changed(self, obj, type, new, old):
		if type is object:
			if (new["x"] != old["x"]) or (new["y"] != old["y"]) or (new["z"] != old["z"]):
				Handle.move(self, obj)
				self.ideal.move(obj)
			if new["parent"] != old["parent"]:
				self.update_hierarchy(new["parent"], old["parent"])
				Handle.move(self, self.position)
				self.ideal.move(obj)
				
	def on_parent_changed(self, obj, type, new, old):
		if type is object:
			if (new["x"] != old["x"]) or (new["y"] != old["y"]) or (new["z"] != old["z"]):
				Handle.move(self, self.position)
				self.ideal.move(self.position)
			if new["parent"] != old["parent"]:
				self.update_hierarchy(new["parent"], old["parent"])
				Handle.move(self, self.position)
				self.ideal.move(self.position)
				
	def update_hierarchy(self, newparent, oldparent):
		world = oldparent
		while world:
			unobserve(world, self.on_parent_changed)
			world = world.parent
			
		world = newparent
		while world:
			observe(world, self.on_parent_changed)
			world = world.parent
			
	def __repr__(self): return "<PositionHandle for %s>" % (self.position,)
	
class VertexHandle(Handle):
	NATURAL = RED_HANDLE
	def __init__(self, parent, editor, vertex):
		Handle.__init__(self, parent, editor)
		self.vertices = [vertex]
		Handle.move(self, vertex)
		self.ideal.move(vertex)
		
		observe(vertex, self.on_changed)
		world = vertex.parent
		while world:
			observe(world, self.on_parent_changed)
			world = world.parent
			
	def is_for(self, item):
		for vertex in self.vertices:
			if vertex is item: return 1
		return 0
	
	def del_for(self, item):
		for vertex in self.vertices:
			if vertex is item:
				self.vertices.remove(vertex)
				unobserve(vertex, self.on_changed)
				if not self.vertices:
					self.parent.remove(self)
					self.editor.handles.remove(self)
					self.editor.vertex_handles.remove(self)
					
	def del_for_all(self):
		for vertex in self.vertices:
			unobserve(vertex, self.on_changed)
			
		self.parent.remove(self)
		self.editor.handles.remove(self)
		
	def move(self, position):
		Handle.move(self, position)
		for vertex in self.vertices: vertex.move(position)
		
	def add_vector(self, vector):
		Handle.add_vector(self, vector)
		for vertex in self.vertices:
			vertex.add_vector(vector)
	__iadd__ = add_vector
	
	def on_changed(self, obj, type, new, old):
		if type is object:
			if (new["x"] != old["x"]) or (new["y"] != old["y"]) or (new["z"] != old["z"]):
				if len(self.vertices) == 1:
					Handle.move(self, obj)
					self.ideal.move(obj)
				else:
					self.give_up_vertex(obj)
					
			if new["parent"] != old["parent"]: self.give_up_vertex(obj)
			
	def on_parent_changed(self, obj, type, old, new):
		if type is object:
			if (new["x"] != old["x"]) or (new["y"] != old["y"]) or (new["z"] != old["z"]):
				Handle.move(self, self.vertices[0])
				self.ideal.move(self.vertices[0])
			elif new["parent"] != old["parent"]:
				self.update_hierarchy(new["parent"], old["parent"])
				Handle.move(self, self.vertices[0])
				self.ideal.move(self.vertices[0])
			
	def update_hierarchy(self, newparent, oldparent):
		world = oldparent
		while world:
			unobserve(world, self.on_parent_changed)
			world = world.parent
			
		world = newparent
		while world:
			observe(world, self.on_parent_changed)
			world = world.parent
			
	def add_vertex(self, vertex):
		vertex.parent = self.vertices[0].parent
		vertex.move(self)
		self.vertices.append(vertex)
		observe(vertex, self.on_changed)
		
	def give_up_vertex(self, vertex):
		self.del_for(vertex)
		self.editor.add_handles_for_vertex(vertex)
		
	def cursor_endmove(self, cursor):
		handle = cursor.over_handle()
		if handle:
			if isinstance(handle, VertexHandle):
				self.del_for_all()
				for vertex in self.vertices: handle.add_vertex(vertex)
			else:
				self.move(handle)
				
	def __repr__(self): return "<VertexHandle for %s>" % (self.vertices,)

class OrientationHandle(Handle):
	NATURAL = YELLOW_HANDLE
	def __init__(self, parent, editor, orientation):
		Handle.__init__(self, parent, editor)
		
		self.orientation = orientation
		self.place()
		self.ideal.move(soya.Point(orientation, 0.0, 0.0, -1.0))
		
		observe(orientation, self.on_changed)
		world = orientation.parent
		while world:
			observe(world, self.on_parent_changed)
			world = world.parent
			
	def is_for (self, item): return item is self.orientation
	
	def place(self): Handle.move(self, soya.Point(self.orientation, 0.0, 0.0, -1.0))
		
	def move(self, position):
		if soya.get_mod() & soya.sdlconst.MOD_SHIFT:
			position = soya.Point(position.parent, position.x, position.y, position.z)
			position.convert_to(self.orientation.parent)
			position.y = self.orientation.y
		self.orientation.look_at(position)
		self.place()
		
	def add_vector(self, vector):
		self.move(self.position() + vector)
	__iadd__ = add_vector
	
	def on_changed(self, obj, type, new, old):
		if type is object:
			if (new["x"] != old["x"]) or (new["y"] != old["y"]) or (new["z"] != old["z"]):
				self.place()
				self.ideal.move(self)
			if new["parent"] != old["parent"]:
				self.update_hierarchy(new["parent"], old["parent"])
				self.ideal.move(self)
				self.place()
			
	def on_parent_changed(self, obj, type, new, old):
		if type is object:
			if (new["x"] != old["x"]) or (new["y"] != old["y"]) or (new["z"] != old["z"]):
				self.place()
				self.ideal.move(self)
			if new["parent"] != old["parent"]:
				self.update_hierarchy(new["parent"], old["parent"])
				self.place()
				self.ideal.move(self)
				
	def update_hierarchy(self, newparent, oldparent):
		world = oldparent
		while world:
			unobserve(world, self.on_parent_changed)
			world = world.parent
			
		world = newparent
		while world:
			observe(world, self.on_parent_changed)
			world = world.parent
			
	def __repr__(self): return "<OrientationHandle for %s>" % (self.orientation,)
