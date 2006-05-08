import soya
from soya.opengl import *

class BoundingBox(soya.PythonCoordSyst):
  def __init__(self,parent, object = None):
    soya.PythonCoordSyst.__init__(self,parent)

    self.dp = -1

    self._material=soya.DEFAULT_MATERIAL
 
    self.corner1, self.corner2 = soya.Point(self,-.5, -.5, -.5), soya.Point(self, .5, .5, .5)

    self.object = object
 
    self.update()

  def batch(self):
    return 2,self,None

  def update(self):
    if self.object:
      self.corner1, self.corner2 = self.object.get_box()
   
    print "%s %s %s" % (self, self.corner1, self.corner2)
   
    self.needs_update = True

  def make_list(self):
    glDisable(GL_DEPTH_TEST)
    glDisable(GL_LIGHTING)

    c1 = self.corner1
    c2 = self.corner2

    self._material.activate()

    glColor4f(1., 0., 0., 1.)

    glBegin(GL_LINE_LOOP)
    glVertex3f(c1.x, c1.y, c1.z)
    glVertex3f(c1.x, c2.y, c1.z)
    glVertex3f(c2.x, c2.y, c1.z)
    glVertex3f(c2.x, c1.y, c1.z)
    glEnd()

    glBegin(GL_LINE_LOOP)
    glVertex3f(c1.x, c1.y, c1.z)
    glVertex3f(c2.x, c1.y, c1.z)
    glVertex3f(c2.x, c1.y, c2.z)
    glVertex3f(c1.x, c1.y, c2.z)
    glEnd()

    glBegin(GL_LINE_LOOP)
    glVertex3f(c1.x, c1.y, c2.z)
    glVertex3f(c2.x, c1.y, c2.z)
    glVertex3f(c2.x, c2.y, c2.z)
    glVertex3f(c1.x, c2.y, c2.z)
    glEnd()

    glBegin(GL_LINE_LOOP)
    glVertex3f(c1.x, c2.y, c1.z)
    glVertex3f(c2.x, c2.y, c1.z)
    glVertex3f(c2.x, c2.y, c2.z)
    glVertex3f(c1.x, c2.y, c2.z)
    glEnd()

  def render(self):
    if self.needs_update:
      if self.dp ==-1:
        self.dp = glGenLists(1)
        
      glNewList(self.dp, GL_COMPILE_AND_EXECUTE)
      self.make_list()
      glEndList()

      self.needs_update = False
    else:
      glCallList(self.dp)

