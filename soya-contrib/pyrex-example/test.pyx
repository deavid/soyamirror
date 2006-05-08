include "c_opengl.pxd"

cimport _soya 

from _soya cimport PythonCoordSyst

# here we will make a subclass of soya.PythonCoordSyst and render 
# something of our own. for this test we make a subclass 
# suitable for displaying the x,y,z axis.

# we must subclass PythonCoordSyst as trying to call something 
# like this: 
#  _soya.renderer._batch(renderer.opaque,     self, coordsyst, -1)
# results in python not being able to find renderer.
# Preferably we would use the regular CoordSyst but because of 
# this we must use PythonCoordSyst

cdef class AxesMarker(PythonCoordSyst):
  
  def batch(self):
    # it would be nicer to override the cdef void _batch 
    # method but i cannot seem the get handle on _soya.renderer.
    # so here we override the python batch function to return 
    # 1 ( non alpha batch), self ( coordsyst ) and None ( the material )
    # The material argument is never used in my opinion
    # Reference for the first argument:
    #   0 - dont render
    #   1 - non alpha
    #   2 - alpha
    #   3 - second pass ( this is undocumented )
    return 1, self, None

  cdef void _render(self, _soya.CoordSyst coordsyst):
    # here we can successfully override _render.
    
    # this function should probably contain all the opengl
    # commands you want to run 

    # we turn off all depth testing and lighting so we will 
    # always be able to see the marker even if it is behind 
    # other ojects
    # we should probably get some of this from the coordsyst 
    # ( where is the .lit property? )
    glDisable(_soya.GL_CULL_FACE)
    glDisable(_soya.GL_DEPTH_TEST)
    glDisable(_soya.GL_LIGHTING)

    # here we draw the lines:
    #   red for x axis
    #   green for y axis
    #   blue for z axis

    # all lines point in theyre positive direction

    glBegin(_soya.GL_LINES)
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

    # put soya back the way it should be 
    glEnable(_soya.GL_LIGHTING)
    glEnable(_soya.GL_DEPTH_TEST)
    glEnable(_soya.GL_CULL_FACE)



