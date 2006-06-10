# -*- indent-tabs-mode: t -*-

""" Application style class for puddding """

import soya.pudding as pudding

__revision__ = '$Revision: 1.1 $'

import os
import soya
from soya.opengl import *

import soya.pudding.style
from soya.pudding.style import STYLE_NONE

class Style(pudding.style.Style):
	""" Application style for pudding """

	def __init__(self):
		pudding.style.Style.__init__(self)

		font_file = os.path.join( soya.DATADIR, "FreeSans.ttf")
		self.default_font = soya.Font(font_file, 10, 10)
		
		self.button_border_width = 2
		self.button_background = (.4, .4, .4, .9)

	def draw_button(self, width, height, background = None, border = None,
								border_width = None):

		glEnable(GL_BLEND)
		
		if background != STYLE_NONE:
			glColor4f( *( background or self.button_background) )

			glBegin(GL_QUADS)
			glVertex3f( 0, 0, 0)
			glVertex3f( 0, height, 0)
			glVertex3f( width, height, 0)
			glVertex3f( width, 0, 0)
			glEnd()


		if border != STYLE_NONE and border_width != 0:
			color = border or self.box_border
			bwidth = border_width or self.button_border_width

			glColor4f( *color )
			glLineWidth( bwidth )
			
			glColor4f(color[0] - .2, color[1] - .2, color[2] - .2, color[3]) 
			glBegin(GL_LINES)
			glVertex3f( 0, 0, 0)
			glVertex3f( 0, height + bwidth, 0)
			glVertex3f( 0, 0, 0)
			glVertex3f( width, 0, 0)
			glEnd()


			glColor4f(color[0] + .2, color[1] + .2, color[2] + .2, color[3]) 
			glBegin(GL_LINES)
			glVertex3f( width, 0 , 0)
			glVertex3f( width, height + bwidth, 0)
			glVertex3f( 0, height , 0)
			glVertex3f( width , height, 0)
			glEnd()

		glDisable(GL_BLEND)


