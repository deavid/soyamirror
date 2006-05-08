# Soya 3D tutorial
# Copyright (C) 2005 Javier Correa Villanueva (jbcorrea@puc.cl)
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


# widget-1: Widget system : a game presentation

# WARNING :
# soya.widget is now deprecated, you should rather consider using soya.pudding instead.


#!/usr/bin/env python -O 

import sys, os, os.path
import soya
import soya.sdlconst
import soya.widget as widget 


soya.init()
soya.path.append(os.path.join(os.path.dirname(sys.argv[0]), "data"))
# Some fonts
big_font = soya.Font(os.path.join(soya.DATADIR, "FreeSans.ttf"), 40, 60)
medium_font=widget.default_font
small_font = soya.Font(os.path.join(soya.DATADIR, "FreeSans.ttf"), 10, 15) 

# This class is to get an input widget
# When you press RETURN key, it will call action with the text introduced as parameter
class Input(widget.Label):
 def __init__(self, master = None, text = "", action=None,align = 0, color = (1.0, 1.0, 1.0, 1.0), font = None, resize_style = None):
   self.action=action
   widget.Label.__init__(self,master,text,align,color,font,resize_style) 

 def widget_begin_round(self):
   for event in soya.process_event():
     self.process_event(event) 

 def process_event(self,event):
   if event[0]==soya.sdlconst.KEYDOWN :
     if event[1]==soya.sdlconst.K_RETURN or event[1]==soya.sdlconst.K_KP_ENTER:
       if self.action:
         self.action(self.text)
       else:
         pass
     elif event[1]==soya.sdlconst.K_DELETE or event[1]==soya.sdlconst.K_BACKSPACE:
      if len(self.text)>0:
        length=len(self.text)
        temp_text=self.text[0:length-1]
        self.text=temp_text
     elif event[1]<256 and chr(event[1]).isalnum():
       last_character=event[1]
       # Now check is shift is pressed, i had to use numbers instead of
       # macros, my soya isntalation didn't have macros for shift modification
       if event[2]==1 or event[2]==2:
         last_character-=32
       temp_text=self.text
       temp_text=temp_text+chr(last_character)
       self.text=temp_text 

# Password input, same as normal input, but display only * when character are introduced
class PasswordInput(widget.Label):
 def __init__(self, master = None, text = "", action=None,align = 0, color = (1.0, 1.0, 1.0, 1.0), font = None, resize_style = None):
   self.action=action
   self.real_text=""
   widget.Label.__init__(self,master,text,align,color,font,resize_style) 

 def widget_begin_round(self):
   for event in soya.process_event():
     self.process_event(event) 

 def process_event(self,event):
   if event[0]==soya.sdlconst.KEYDOWN :
     if event[1]==soya.sdlconst.K_RETURN or event[1]==soya.sdlconst.K_KP_ENTER:
       if self.action:
         self.action(self.real_text)
       else:
         pass
     elif event[1]==soya.sdlconst.K_DELETE or event[1]==soya.sdlconst.K_BACKSPACE:
      if len(self.text)>0:
        length=len(self.text)
        temp_text=self.text[0:length-1]
        self.text=temp_text
        temp_text=self.real_text[0:length-1]
        self.real_text=temp_text 

     elif event[1]<256 and chr(event[1]).isalnum():
       last_character=event[1]
       if event[2]==1 or event[2]==2:
         last_character-=32
       self.text+='*'
       self.real_text=self.real_text+chr(last_character) 

# Widget with a few effects, fade and move
# It may be very ineficient
class EffectWidget:
 # Change the init so if read a hash with the information to change
 def __init__(self,fade_speed=0.05,up_speed=1.5,down_speed=1.5,left_speed=1.5,right_speed=1.5):
   # Variables for fading effect
   self.fadein=None
   self.fadeout=None
   self.faded=1
   self.fade_speed=fade_speed
   # Variable for moving
   self.move_up=None
   self.move_down=None
   self.move_right=None
   self.move_left=None
   self.up_speed=up_speed
   self.down_speed=down_speed
   self.right_speed=right_speed
   self.left_speed=left_speed
   # The distance to move
   self.up_distance=50
   self.down_distance=50
   self.left_distance=50
   self.right_distance=50
   # The traveled so far
   self.up_travel=0
   self.down_travel=0
   self.left_travel=0
   self.right_travel=0 

 def fadeIn(self):
   self.fadein=1
   self.fadeout=None 

 def fadeOut(self):
   self.fadeout=1
   self.fadein=None 

 def startUp(self):
   self.move_up=1
   self.move_down=None
 def stopUp(self):
   self.move_up=None 

 def startDown(self):
   self.move_down=1
   self.move_up=None
 def stopDown(self):
   self.move_down=None 

 def startLeft(self):
   self.move_left=1
   self.move_right=None
 def stopLeft(self):
   self.move_left=None 

 def startRight(self):
   self.move_right=1
   self.move_left=None
 def stopRight(self):
   self.move_right=None 

 def resetMove(self):
   # Variable for moving
   self.move_up=None
   self.move_down=None
   self.move_right=None
   self.move_left=None
   # The traveled so far
   self.up_travel=0
   self.down_travel=0
   self.left_travel=0
   self.right_travel=0 

 def doMove(self,proportion):
   # Implementation of moving animation
   if self.move_up:
     if self.up_travel>self.up_distance:
       self.move_up=None
       self.up_travel=0
     else:
       self.top-=self.up_speed*proportion
       self.up_travel+=self.up_speed*proportion
   if self.move_down:
     if self.down_travel>self.down_distance:
       self.move_down=None
       self.down_travel=0
     else:
       self.top+=self.down_speed*proportion
       self.down_travel+=self.down_speed*proportion 

   if self.move_left:
     if self.left_travel>self.left_distance:
       self.move_left=None
       self.left_travel=0
     else:
       self.top-=self.left_speed*proportion
       self.left_travel+=self.left_speed*proportion
   if self.move_right:
     if self.right_travel>self.right_distance:
       self.move_right=None
       self.right_travel=0
     else:
       self.top+=self.right_speed*proportion
       self.right_travel+=self.right_speed*proportion 

# A choice wich is fadable also
class EffectChoice(EffectWidget,widget.ChoiceList):
 def __init__(self, master = None, choices = [], font = None, color = (1.0, 0.5, 0.5,0.0),highlight = (1.0, 1.0, 0.0, 0.0), cancel = None,align=1,fade_speed=0.05):
   widget.ChoiceList.__init__(self,master,choices,font,color,highlight,cancel,align)
   EffectWidget.__init__(self,fade_speed) 

 def widget_begin_round(self):
   if not self.faded:
     widget.ChoiceList.widget_begin_round(self)
     for event in soya.process_event():
       self.process_event(event) 

 def widget_advance_time(self,proportion):
   # Implementation of fadinf animation
   if self.fadeout:
     r1,g1,b1,a=self.color
     r2,g2,b2,a2=self.highlight
     a-=self.fade_speed*proportion
     if a<0:
       self.master.remove(self)
       self.fadeout=None
       self.faded=1
     self.color=(r1,g1,b1,a)
     self.highlight=(r2,g2,b2,a)
   elif self.fadein:
     if self.faded:
       self.faded=None
     r1,g1,b1,a=self.color
     r2,g2,b2,a2=self.highlight
     a+=self.fade_speed*proportion
     if a<1:
       self.color=(r1,g1,b1,a)
       self.highlight=(r2,g2,b2,a)
     else:
       self.fadein=None
       self.faded=None
   self.doMove(proportion) 

# A fadable label
class EffectLabel(EffectWidget,widget.Label):
 def __init__(self, master = None, text = "", align = 0, color = (1.0, 1.0, 1.0, 0.0), font = None,resize_style = None,fade_speed=0.05):
   widget.Label.__init__(self,master,text,align,color,font,resize_style)
   EffectWidget.__init__(self,fade_speed) 

 def widget_advance_time(self,proportion):
   if self.fadeout:
     r,g,b,a=self.get_color()
     a-=self.fade_speed*proportion
     if a<0:
       self.master.remove(self)
       self.faded=1
       self.fadeout=None
     self.set_color((r,g,b,a))
   elif self.fadein:
     r,g,b,a=self.get_color()
     a+=self.fade_speed*proportion
     if a<1:
       self.set_color((r,g,b,a))
     else:
       self.faded=None
       self.fadein=None
   self.doMove(proportion) 

# The configuration screen
class ConfigureScreen(widget.Group):
 def __init__(self,caller,background):
   widget.Group.__init__(self)
   self.caller=caller
   self.state=0
   if not background:
     material=soya.Material()
     #material.texture=soya.Image.get('back.png')
     background=widget.Image(None,material)
     background.resize_style=soya.widget.WIDGET_RESIZE_MAXIMIZE
   self.add(background)
   self.configureLabel=EffectLabel(self,'Configuration',1)
   self.configureLabel.resize_style=soya.widget.WIDGET_RESIZE_MAXIMIZE
   self.configureLabel.resize(0,-50,640,480)
   self.configureLabel.resize_style=None
   # The initial options of the game
   optionResolution=widget.Choice('Change Resolution',self.changeResolution)
   optionFullscreen=widget.Choice('Togle Fullscreen',self.goFullscreen)
   optionServer=widget.Choice('Change Server',self.changeServer)
   optionBack=widget.Choice('Back',self.goBack)
   # The menu itself
   self.optionsMenu=EffectChoice(self,[optionResolution,optionFullscreen,optionServer,optionBack])
   self.optionsMenu.resize_style=soya.widget.WIDGET_RESIZE_MAXIMIZE 

   # Show the menu
   self.configureLabel.fadeIn()
   self.configureLabel.startDown()
   self.optionsMenu.fadeIn() 

 def widget_begin_round(self):
   widget.Group.widget_begin_round(self)
   if self.state==10:
     if self.configureLabel.faded:
       self.master.add(self.caller)
       self.master.remove(self)
       self.add(self.configureLabel)
       self.add(self.optionsMenu)
       self.configureLabel.fadeIn()
       self.configureLabel.startDown()
       self.optionsMenu.fadeIn()
       self.state=0 

 def changeResolution(self):
   pass
 def goFullscreen(self):
   pass
 def changeServer(self):
   pass
 def goBack(self):
   self.state=10
   self.configureLabel.fadeOut()
   self.configureLabel.startUp()
   self.optionsMenu.fadeOut() 

class LoginScreen(widget.Group):
 def __init__(self,background=None):
   widget.Group.__init__(self)
   if not background:
     material=soya.Material()
     #material.texture=soya.Image.get('back.png')
     background=widget.Image(None,material)
     background.resize_style=soya.widget.WIDGET_RESIZE_MAXIMIZE
   self.add(background)
   # The state on the login process
   self.state=0
   self.configScreen=ConfigureScreen(self,background)
   # This will be the title of the game, always present
   self.gameName=EffectLabel(self,"The Name of the Game",1,(.3,.3,1.0,0.0),big_font)
   self.gameName.resize_style=soya.widget.WIDGET_RESIZE_MAXIMIZE 

   # The initial options of the game
   optionLogin=widget.Choice('Login',self.startLogin)
   optionConfig=widget.Choice('Configure',self.doConfiguration)
   optionQuit=widget.Choice('Quit',self.quitGame)
   # The menu itself
   self.optionsMenu=EffectChoice(self,[optionLogin,optionConfig,optionQuit])
   self.optionsMenu.resize_style=soya.widget.WIDGET_RESIZE_MAXIMIZE 

   # A label saying "Enter username" and user input
   self.userLabel=EffectLabel(None,'Username:',1)
   self.userLabel.resize_style=soya.widget.WIDGET_RESIZE_MAXIMIZE
   self.userLabel.resize(0,100,640,100)
   self.userLabel.resize_style=None
   self.userInput=Input(None,"",self.setUser,1)
   self.userInput.resize_style=soya.widget.WIDGET_RESIZE_MAXIMIZE
   self.userInput.resize(0,200,640,100)
   self.userInput.resize_style=None 

   # The password label and input
   self.passLabel=EffectLabel(None,'Password:',1)
   self.passLabel.resize_style=soya.widget.WIDGET_RESIZE_MAXIMIZE
   self.passLabel.resize(0,100,640,100)
   self.passLabel.resize_style=None
   self.passInput=PasswordInput(None,"",self.doLogin,1)
   self.passInput.resize_style=soya.widget.WIDGET_RESIZE_MAXIMIZE
   self.passInput.resize(0,200,640,100)
   self.passInput.resize_style=None 

   # Everything set, let's show the menu
   self.optionsMenu.fadeIn()
   self.gameName.fadeIn() 

 def widget_begin_round(self):
   widget.Group.widget_begin_round(self)
   if self.state==1:
     if self.optionsMenu.faded:
       self.optionsMenu.resetMove()
       self.gameName.resetMove()
       self.state=2
   elif self.state==2:
     self.add(self.userLabel)
     self.add(self.userInput)
     self.userLabel.fadeIn()
     self.state=3
   elif self.state==4:
     if self.userLabel.faded:
       self.state=5
   elif self.state==5:
     self.add(self.passLabel)
     self.add(self.passInput)
     self.passLabel.fadeIn()
     self.state=6
   elif self.state==10:
     if self.optionsMenu.faded:
       self.optionsMenu.resetMove()
       self.gameName.resetMove()
       self.master.add(self.configScreen)
       self.master.remove(self)
       # Set fadeIn, so the next time we add this widget to the root, it will fade in
       self.add(self.optionsMenu)
       self.add(self.gameName)
       self.optionsMenu.fadeIn()
       self.gameName.fadeIn()
       self.state=0 

 def startLogin(self):
   self.optionsMenu.fadeOut()
   self.optionsMenu.startDown()
   self.state=1 

 def mainMenu(self):
   self.add(self.optionsMenu)
   self.optionsMenu.fadeIn()
   self.state=0 

 def setUser(self,text):
   self.userLabel.fadeOut()
   self.remove(self.userInput)
   self.state=4 

 def doLogin(self,text):
   self.passLabel.fadeOut()
   self.remove(self.passInput)
   print 'The End'
   self.mainMenu() 

 def doConfiguration(self):
   self.optionsMenu.fadeOut()
   self.optionsMenu.startUp()
   self.gameName.fadeOut()
   self.gameName.startDown()
   self.state=10 

 def quitGame(self):
   sys.exit() 


scene = soya.World()
root=soya.widget.Group()
soya.set_root_widget(root)
root.add(LoginScreen())
soya.Idler(scene).idle() 
