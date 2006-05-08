import soya
from soya.opengl import *

class Arrow(soya.PythonCoordSyst):
  def __init__(self,parent, vector, color = (0, 0, 1, 1), depth_test = True):
    soya.PythonCoordSyst.__init__(self,parent)

    self.dp = -1

    self._material=soya.DEFAULT_MATERIAL
 
    self.vector = vector
    self.color = color

    self.depth_test = depth_test
 
  def batch(self):
    return 2,self,None

  def make_list(self):
    if not self.depth_test:
      glDisable(GL_DEPTH_TEST)
  
    glDisable(GL_LIGHTING)

    self._material.activate()

    glColor4f(*self.color)

    v = self.vector

    glBegin(GL_LINES)
    glVertex3f(0, 0, 0)
    glVertex3f(v.x, v.y, v.z)
    glEnd()

  def render(self):
    self.make_list()

