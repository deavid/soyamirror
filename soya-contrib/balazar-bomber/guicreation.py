
import sys, os, os.path, math
import soya
import soya.widget as widget
import soya.sdlconst as sdlconst
import tofu, tofu.pickle_sec, tofu4soyapudding

import pudding.core
import pudding.control
import pudding.idler
import pudding.ext.fpslabel
import pudding.sysfont


    
def introgui(interface, avatar):
    
    #msg = "hello from the gui maker"
    singlebutton = pudding.control.Button(interface.root, 'Single', left = 10, width = 50, height = 40)
    singlebutton.set_pos_bottom_right(right = 300, bottom = 300)
    singlebutton.anchors = pudding.ANCHOR_ALL
    singlebutton.on_click = lambda:avatar.change_level("level2_bbomber")
    
    multibutton = pudding.control.Button(interface.root, 'Online', left = 10, width = 50, height = 40)
    multibutton.set_pos_bottom_right(right = 300, bottom = 250)
    multibutton.anchors = pudding.ANCHOR_ALL
    multibutton.on_click = lambda:interface.end_game("client")
    
    
    quitbutton = pudding.control.Button(interface.root, 'Quit', left = 10, width = 50, height = 40)
    quitbutton.set_pos_bottom_right(right= 300,bottom = 200)
    #button.set_pos_left(left = 100)
    quitbutton.anchors = pudding.ANCHOR_BOTTOM | pudding.ANCHOR_LEFT
    quitbutton.on_click = interface.end_game
    interface.root.on_resize()
    
    