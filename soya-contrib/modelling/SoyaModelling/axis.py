import soya
from soya.opengl import *

class Axis(soya.PythonCoordSyst):
  dp = -1

  def __init__(self,parent=None,material=None):
    soya.PythonCoordSyst.__init__(self,parent)

    self._material=material or soya.DEFAULT_MATERIAL

  def batch(self):
    return 2,self,None

  def render(self):
    if Axis.dp ==-1:
      self.dp = glGenLists(1)
      glNewList(Axis.dp, GL_COMPILE_AND_EXECUTE)
      self.make_list()
      glEndList()
    else:
      glCallList(Axis.dp)
  
  def make_list(self):
    glDisable(GL_CULL_FACE)
    glDisable(GL_DEPTH_TEST)
    glDisable(GL_LIGHTING)
    
    glColor4f(1.,0.,0.,1.)

    glBegin(GL_LINES)
    glColor4f(1.,0.,0.,1.)
    glVertex3f(0.,0.,0.)
    glVertex3f(1.,0.,0.)
    glColor4f(0.,1.,0.,1.)
    glVertex3f(0.,0.,0.)
    glVertex3f(0.,1.,0.)
    glColor4f(0.,0.,1.,1.)
    glVertex3f(0.,0.,0.)
    glVertex3f(0.,0.,1.)
    glEnd()

    glEnable(GL_LIGHTING)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_CULL_FACE)

