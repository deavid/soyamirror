# -*- indent-tabs-mode: t -*-

# Soya 3D
# Copyright (C) 2001-2003 Jean-Baptiste LAMY -- jiba@tuxfamily.org
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

"""soya.facecutter -- A model beautifier

Cuts some faces in two (or more), in order to get smoother model."""

import soya
from soya import Point, Vector

import bisect, copy

def cut(world, nb_new_faces = 0, max_length = 10E1000, precision = 5, add_relief = 1.0):
	"""cut(world, nb_new_faces, max_size = inf, precision = 5, relief_surface_ratio = 5.0, add_relief = 1.0) -> int

Cuts some faces (recursively) in world WORLD, so as at least NB_NEW_FACES are added, and
each edge length is less than MAX_LENGTH. For 'cut' to be usefull, you should give at
least NB_NEW_FACES or MAX_LENGTH.

Facecutter cuts first the longest edge. It can cut a triangle in 2 triangles, and a quad
in 3 triangles.

The exact number of new faces may slighly differ from NB_NEW_FACES; the exact number
is returned.

PRECISION is the number of decimals taken into account (as required by the 'round'
builtin function) for vertex sharing. Two vertices separated by less than 10E(-PRECISION)
are considered to share the same position.

For smooth_lit faces, ADD_RELIEF is a coefficient that multiply the relief
added. 1.0 is the normal value; though 2.0 can also give good results.

It is safe to apply 'cut' successively several times (though it will take longer to
compute)."""
	
	edge_sizes = []
	def index_face(face):
		for vertex in face: index_vertex(vertex)
		index_edges(face)
	def index_edges(face):
		a = face.vertices[-1]
		for b in face.vertices:
			bisect.insort(edge_sizes, (a.distance_to(b), a, b))
			a = b
			
	def unindex_face(face):
		for vertex in face: unindex_vertex(vertex)
		
	def add_triangle(face, a, b, c):
		triangle = copy.deepcopy(face)
		face.parent.add(triangle)
		while triangle.vertices: del triangle.vertices[0]
		triangle.append(a); triangle.append(b); triangle.append(c)
		index_face(triangle)
		return triangle
	def add_quad(face, a, b, c, d):
		quad = copy.deepcopy(face)
		face.parent.add(quad)
		while quad.vertices: del quad.vertices[0]
		quad.append(a); quad.append(b); quad.append(c); quad.append(d)
		index_face(quad)
		return quad
		
	coords_to_vertices = {}
	vertex_to_vertices = {}
	
	def index_vertex(vertex):
		coords   = round(vertex.x, precision), round(vertex.y, precision), round(vertex.z, precision)
		vertices = coords_to_vertices.get(coords)
		if vertices is None:
			coords_to_vertices[coords] = vertex_to_vertices[vertex] = [vertex]
		else:
			vertices.append(vertex)
			vertex_to_vertices[vertex] = vertices
	def unindex_vertex(vertex):
		try:
				vertex_to_vertices[vertex].remove(vertex)
				del vertex_to_vertices[vertex]
		except KeyError:
				pass
		
	def edge_to_faces(a, b):
		faces_with_a = vertex_to_vertices[a]
		faces_with_b = vertex_to_vertices[b]
		faces = []
		for a in faces_with_a:
			for b in faces_with_b:
				if a.face is b.face:
					if len(a.face.vertices) == 4: # Check if the 2 vertices are consecutive (else they do not belong to an edge)
						if not abs(a.face.vertices.index(a) - a.face.vertices.index(b)) in (1, 3): continue
					faces.append((a.face, a, b))
		return faces
	
	def normal_at_vertex(a):
		normal = None
		for vertex in vertex_to_vertices[a]:
			if vertex.face.smooth_lit: # No smooth_lit means no vertex normal
				face = vertex.face
				
				if normal is None: normal = Vector(face.normal.parent)
				
				i = face.vertices.index(vertex)
				a = face.vertices[i - 1]
				if i + 1 == len(face.vertices): b = face.vertices[0]
				else:                           b = face.vertices[i + 1]
				
				normal.add_mul_vector((vertex >> a).angle_to(vertex >> b), face.normal)
				
		normal.normalize()
		return normal
	
	
	def split_triangle(face, a, b, h):
		# Check for rotation sens
		for i in range(len(face.vertices)):
			if face.vertices[i] is b:
				if face.vertices[i - 1] is not a: a, b = b, a
				break
			
		# Check for c (the last vertex)
		for c in face.vertices:
			if (not c is a) and (not c is b): break
		else: raise Warning()
		
		h = barycenter(a, b, 0.5, pos = h)
		add_triangle(face, clone(a),       h , clone(c))
		add_triangle(face, clone(h), clone(b), clone(c))
		
		face.parent.remove(face); unindex_face(face)
		face.removed = 1
		
	def split_quad(face, a, b, h):
		# Check for rotation sens
		for i in range(len(face.vertices)):
			if face.vertices[i] is b:
				if face.vertices[i - 1] is a:
					i += 1
					if i > 3: i = 0
					c = face.vertices[i]
					i += 1
					if i > 3: i = 0
					d = face.vertices[i]
					
				else:
					a, b = b, a
					
					i -= 1
					if i > 3: i = 0
					d = face.vertices[i]
					i -= 1
					if i > 3: i = 0
					c = face.vertices[i]
				break
				
		h = barycenter(a, b, 0.5, pos = h)
		add_triangle(face,       h , clone(d), clone(a))
		add_triangle(face, clone(h), clone(c), clone(d))
		add_triangle(face, clone(h), clone(b), clone(c))
		
		face.parent.remove(face); unindex_face(face)
		
		
	# Index faces and vertices
	faces = filter(lambda face: isinstance(face, soya.Face) and (len(face.vertices) in (3, 4)), world.recursive())
	
	for face in faces:
		#if face.smooth_lit: face.compute_normal() # Normal may be needed later (for smooth_lit faces)
		for vertex in face: index_vertex(vertex)
		
	for face in faces: index_edges(face)
	
	
	nb_new_faces_real = 0
	while (nb_new_faces_real < nb_new_faces) or (edge_sizes[-1][0] > max_length):
		size, a, b = edge_sizes.pop()
		
		try:
			edges = edge_to_faces(a, b)
		except KeyError: continue
		if not edges: continue
		
		h = barycenter(a, b, 0.5)
		if edges[0][0].smooth_lit: # Smooth the model
			a_normal = normal_at_vertex(a)
			b_normal = normal_at_vertex(b)
			
			h_normal = a_normal + b_normal
			
			f = (1.0 / h_normal.length() - 0.5) * add_relief * a.distance_to(b)
			h_normal.normalize()
			h.add_mul_vector(f, h_normal)
			
			# Old (0.6.1) formula
			#h.add_mul_vector((1.0 - h_normal.length() / 2.0) * add_relief, h_normal)
			
		for face, a, b in edges:
			if face.parent:
				if len(face.vertices) == 3: split_triangle(face, a, b, h); nb_new_faces_real += 1
				else:                       split_quad    (face, a, b, h); nb_new_faces_real += 2
				
	return nb_new_faces_real




def size_of_triangle(a, b, c):
	ab = a >> b
	ac = a >> c
	h = c >> (a + (ab * ab.dot_product(ac)))
	return ab.length() * h.length() / 2.0

	
def clone(vertex):
	v = copy.deepcopy(vertex)
	v.parent = vertex.parent
	return v

def barycenter(a, b, f = 0.5, pos = None):
	f_ = 1 - f
	
	aa = copy.deepcopy(a)
	if pos: aa.move(pos)
	else:   aa.add_vector((a >> b) * f)
	aa.tex_x = f_ * a.tex_x + f * b.tex_x
	aa.tex_y = f_ * a.tex_y + f * b.tex_y
	if not((a.color is None) and (b.color is None)):
		aa.color = tuple(map(lambda a, b: f_ * a + f * b, a.color or soya.WHITE, b.color or soya.WHITE))
	aa.parent = a.parent
	return aa



def check_quads(world, threshold = 0.00001):
	"""check_quads(world) -> int

Checks (recursively) if all quad's vertices in WORLD are coplanar.
Non coplanar quads are splitted in 2 triangles.
Returns the number of splits."""
	
	nb = 0
	
	for face in world.recursive():
		if isinstance(face, soya.Face) and (not face.is_coplanar()):
			nb += 1
			
			clone = copy.deepcopy(face)
			face.parent.add(clone)
			
			# Cut so as the new edge is the shortest possible one (OpenGL often does a better texture interpolation in this case)
			if face.vertices[0].distance_to(face.vertices[2]) < face.vertices[1].distance_to(face.vertices[3]):
				del clone.vertices[1]
				del face .vertices[3]
			else:
				del clone.vertices[0]
				del face .vertices[2]
				
	return nb
