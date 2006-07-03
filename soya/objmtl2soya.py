# -*- indent-tabs-mode: t -*-

#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Obj Import
# Copyright (C) 2003-2004 David PHAM-VAN / AB2R -- david@ab2r.com
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

"""objmtl2soya

This script is an OBJ/MTL exporter for Soya.

"""


import sys, os, os.path, soya

__all__ = ["getObj", "getModel"]

def loadMat(fileName, mat):
	f=open(fileName,'r')
	lines=f.readlines()
	f.close()
	curmat=None
	for line in lines:
		line=line.strip()
		if line!='' and line[0]!='#':
			spline=line.split()
			fn=spline[0]
			pr=spline[1:]
			if fn=='newmtl':
				curmat=pr[0]
				mat[curmat]=soya.Material()
			elif fn=='illum':
				pass
			elif fn=='Kd':
				mat[curmat].diffuse = (float(pr[0]), float(pr[1]), float(pr[2]), 1.0)
			elif fn=='Ka':
				pass
			elif fn=='Ks':
				mat[curmat].specular = (float(pr[0]), float(pr[1]), float(pr[2]), 1.0)
			elif fn=='Ns':
				mat[curmat].shininess=float(pr[0])
			elif fn=='Tf':
				mat[curmat].diffuse=(mat[curmat].diffuse[0], mat[curmat].diffuse[1], mat[curmat].diffuse[2], float(pr[0]))
			elif fn=='Ni':
				pass
			elif fn=='map_Kd':
				mat[curmat].texture = soya.Image.get(pr[0])
				mat[curmat].diffuse = (1.0, 1.0, 1.0, 1.0)
			else:
				print line
	f.close()

def loadObj(fileName):
	f=open(fileName,'r')
	lines=f.readlines()
	f.close()
	obj_w = soya.World()
	curmat=soya.DEFAULT_MATERIAL
	materials={}
	geometric_vertices=[]
	texture_vertices=[]
	vertex_normals=[]
	smooth=0
	nline=1
	try:
		for line in lines:
			line=line.strip()
			if line!='' and line[0]!='#':
				spline=line.split()
				fn=spline[0]
				pr=spline[1:]
				if fn=='mtllib':
					m=loadMat(os.path.join(os.path.dirname(fileName),pr[0]),materials)
				elif fn=='o':
					pass
				elif fn=='g':
					pass
				elif fn=='v':
					geometric_vertices.append([float(pr[0]), float(pr[1]),  float(pr[2])])
				elif fn=='s':
					smooth=pr[0]!='off'
				elif fn=='f':
					mf=[]
					for face in pr:
						spface=face.split('/')
						
						if int(spface[0]) < 0: gv = geometric_vertices[int(spface[0])]
						else:                  gv = geometric_vertices[int(spface[0]) - 1]
						if len(spface)>=2 and spface[1]!='':
							if int(spface[1]) < 0: tv = texture_vertices[int(spface[1])]
							else:                  tv = texture_vertices[int(spface[1]) - 1]
						else:
							mf.append(soya.Vertex(obj_w, gv[0], gv[1], gv[2], tv[0], - tv[1]))
							mf.append(soya.Vertex(obj_w, gv[0], gv[1], gv[2]))
							
					face=soya.Face(obj_w, mf, curmat)
					face.smooth_lit=smooth
				elif fn=='vt':
						texture_vertices.append([float(pr[0]), float(pr[1])])
				elif fn=='vn':
					pass
				elif fn=='usemtl':
					curmat=materials[pr[0]]
				else:
					print line
	except:
		print str(nline)+' : '+line
		raise
	f.close()
	return obj_w

def makeWorld(Name):
	df=os.path.join(soya.path[0],'worlds',Name+'.data')
	of=os.path.join(soya.path[0],'obj',Name+'.obj')
	mf=os.path.join(soya.path[0],'obj',Name+'.mtl')
	haveToDoIt=False
	if os.path.exists(df):
		if os.path.exists(of):
			if os.path.getmtime(of)>os.path.getmtime(df):
				haveToDoIt=True
		if os.path.exists(mf):
			if os.path.getmtime(mf)>os.path.getmtime(df):
				haveToDoIt=True    
	else:
		haveToDoIt=True
	if haveToDoIt:
		print "* Soya * Compiling obj "+of+" to world..."
		o=loadObj(of)
		o.filename=Name
		o.save()

def getObj(Name):
	"""getObj(NAME) -> World

Imports a "{name}.obj" file (from the "obj" directory) and converts it into a Soya World."""
	makeWorld(Name)
	return soya.World.get(Name)

def getModel(Name):
	"""getModel(NAME) -> World

Imports a "{name}.obj" file (from the "obj" directory) and converts it into a Soya Model."""
	makeWorld(Name)
	return soya.Model.get(Name)

def main():
	"""Imports the .obj file given as arg 1 and saves the created world to the 
file given as arg 2. Does not add the .data extension. Put this in
your worlds directory or to_model it."""
	infilename = sys.argv[1]
	outfilename = sys.argv[2]
	
	world = loadObj(infilename)
	world.save(outfilename)
	
if __name__ == '__main__':
	main()
