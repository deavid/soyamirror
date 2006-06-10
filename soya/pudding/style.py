# -*- indent-tabs-mode: t -*-

""" Style class for pudding """
__revision__ = "$Revision: 1.1 $"

import os

import unittest

import soya
from soya.opengl import *

import soya.pudding, soya.pudding.sysfont

STYLE_NONE = -1

class Style:
	""" this holds the constant values of all the styles.
	styles can be accessed like:
		
		>>> styles.box_background

	"""

	def __init__(self):
		self.default_font = soya.Font(soya.pudding.sysfont.SysFont('sans, freesans'), 15, 15 )
		
		self.box_background = (.1, .1, .12, .8)
		self.box_border = (.7, .7, .7, 1.)
		self.box_border_width = 1
		
		self.button_border = self.box_border
		self.button_border_width = 1
		self.button_background = (.2, .2, .22, .8)
				
		self.panel_font = self.default_font
		self.panel_font_color = (.8, .8, .85, 1.)
		self.panel_bar = (.2, .2, .22, 1.)

	def draw_bordered_box(self, width, height, background = None, border = None,
												border_width = None):

		""" draw a basic bordered box """

		glEnable(GL_BLEND)
		
		if background != STYLE_NONE:
			glColor4f( *( background or self.box_background) )

			glBegin(GL_QUADS)
			glVertex3f( 0, 0, 0)
			glVertex3f( 0, height, 0)
			glVertex3f( width, height, 0)
			glVertex3f( width, 0, 0)
			glEnd()

			glColor4f( *( border or self.box_border) )

		if border != STYLE_NONE and border_width != 0:
			glLineWidth( border_width or self.box_border_width)
			
			glBegin(GL_LINE_STRIP)
			glVertex3f( 0, 0, 0)
			glVertex3f( 0, height, 0)
			glVertex3f( width, height, 0)
			glVertex3f( width, 0, 0)
			glVertex3f( 0, 0 , 0)
			glEnd()

		glDisable(GL_BLEND)

	def draw_button(self, width, height, background = None, border = None,
								border_width = None):
		""" draw a button """

		self.draw_bordered_box(width, height, background or self.button_background, 
																			border or self.button_border, 
																			border_width or self.button_border_width)


	def draw_panel(self, width, height, background = None, border = None,
								border_width = None, label = ''):
		""" draw a panel """

		self.draw_bordered_box(width, height, background, border, border_width)
		
		glPushMatrix()
		used_border_width = border_width or self.box_border_width
		glTranslatef(used_border_width, used_border_width, 0)

		self.draw_bordered_box(width - (2 * used_border_width), 
													self.panel_font.height + 5, 
													background = self.panel_bar, border_width = 0 )

		if label:
			glColor4f(*self.panel_font_color)
			self.panel_font.draw(label, 2, 0, 0)

		glPopMatrix()

class TestStyle(unittest.TestCase):
	def testCreate(self):
		style = Style()


"""
	def draw_bordered_box(self, width, height, background = None, border = None,
												border_width = None):

		#def draw_rounded_box( width, height, radius, background = None, border = None,
		#                      border_width = None):
		glColor4f(*( border or self.box_border) ) 
		glLineWidth( border_width or self.box_border_width) 

		ang=0 

		glBegin(GL_LINES) 
		glVertex2f(0, radius) 
		glVertex2f(0, height - radius) # Left Line 

		glVertex2f(radius, 0) 
		glVertex2f(width - radius, 0) # Top Line 

		glVertex2f(width, radius) 
		glVertex2f(width, height - radius) # Right Line 

		glVertex2f(radius, height) 
		glVertex2f(width - radius, height) # Bottom Line 
		glEnd() 

		cX= radius 
		cY = radius 
		glBegin(GL_LINE_STRIP) 
		for ang in range(pi, 1.5*pi, 0.05)
		for(ang = PI ang <= (1.5*PI); ang = ang + 0.05) 
			glVertex2d(radius* cos(ang) + cX, radius * sin(ang) + cY) //Top Left 
		cX = x+width-radius 
		glEnd() 

		glBegin(GL_LINE_STRIP) 
		for(ang = (1.5*PI) ang <= (2 * PI); ang = ang + 0.05) 
			glVertex2d(radius* cos(ang) + cX, radius * sin(ang) + cY) //Top Right 
		glEnd() 

		glBegin(GL_LINE_STRIP) 
		cY = y+height-radius 
		for(ang = 0 ang <= (0.5*PI); ang = ang + 0.05) 
			glVertex2d(radius* cos(ang) + cX, radius * sin(ang) + cY) //Bottom Right 
		glEnd() 

		glBegin(GL_LINE_STRIP) 
		cX = x+radius 
		for(ang = (0.5*PI) ang <= PI; ang = ang + 0.05) 
			glVertex2d(radius* cos(ang) + cX, radius * sin(ang) + cY)//Bottom Left 
		glEnd() 
"""
