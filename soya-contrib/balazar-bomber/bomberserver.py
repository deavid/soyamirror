#!/usr/bin/env python

#Balazar-bombers server


from twisted.spread import pb
from twisted.cred import checkers, portal, credentials
from twisted.internet import reactor

from optparse import OptionParser

import sys
import os
from random import random, shuffle
from math import sqrt
import string

import traceback

# soya imports
try:
    import soya
    import soya.widget as widget
    import soya.sdlconst as sdlconst
    import soya.particle
    import soya.sphere
except ImportError:
    traceback.print_exc()
    raise "You dont have soya installed or your installation is bad"

#game import modules
import servergameobjects as gameobjects


# find and append the soya data dir
HERE = os.path.dirname(sys.argv[0])
datadir=os.path.join(HERE,"data")
# make sure the path exists
assert(os.path.isdir(datadir))
soya.path.append(datadir)

stateMachine = None

def getScene():
    """ helper function to return current scene object """
    #print "servers direct scenes are ",soya.IDLER.scenes[:]
    
    return soya.IDLER.scenes[0]
    
class StateMachine(dict):
   
    def __init__(self,initialdata={}):
        dict.__init__(self,initialdata)
        self.__currentState=None
    
    def __getstate__(
self):
        return self.__currentState
    
    def change_state(self,state):
        """ stop any current state and start the requested named state """
        if self.__currentState:
            self.__currentState.stop()
    
        try:
            idler=self[state]
        except KeyError:
            raise "%s is not a state of %s" % (state,self)
    
        self.__currentState=idler()
        self.__currentState.idle()
        self.__currentState=None
    
    state=property(__getstate__,change_state,doc='set or get the current state key.\nsetting this value will cause change_state to be called')

class WidgetedIdler(soya.Idler):
    """ This is the base class we will use for other idlers.
    You should override the create_* to methods to create the relevant
    objects. The resize function should be overidden to position any 
    widgets when the screen size changes
    """
    
    class RootWidget(widget.Group):
        """ used to get round having to checking the event queue for resize events.
        soya calls the root_widgets resize method automatically so we make use of that 
        here. its currently easier to resize widgets on your own.
        """
    
        def resize(self,parent_left,parent_top,parent_width,parent_height):
            # just in case any widgets do have a good resize function ( eg FPSLabel ) 
            # we call the ancestor function
            widget.Group.resize(self,parent_left,parent_top,parent_width,parent_height)
        
            # call the idlers resize method to allow the developer to specifiy positions
            # soya.IDLER should always refer to the parent class
            if soya.IDLER:
                soya.IDLER.resize()
        
    def __init__(self):
        # in theory this shouldnt need to be overriden 
        
        # create the scene. for simple menus this can probably be left alone
        self.create_scene()
    
        # create the camera
        self.create_camera()
        
        # set the root widget to our local class with the modified resize event 
        soya.set_root_widget(self.RootWidget())
    
        # add the camera
        soya.root_widget.add(self.camera)
    
        # create all our widgets. subclasses will override this 
        self.create_widgets()
    
        # resize all our widgets initially. the same function will be called for 
        # video resize events. subclasses will override this 
        self.resize()
    
        soya.Idler.__init__(self,self.scene)
    
    def create_scene(self):
        """ creates self.scene and any other objects connected to the scene apart
        from the camera
        """
    
        self.scene=soya.World()
    
    def create_camera(self):
        """ creates the camera """
    
        self.camera=soya.Camera(self.scene)
        self.camera.z=3.
    
    def create_widgets(self):
        """ create any widgets """
        pass
    
    def resize(self):
        """ called on video resize events """
        pass
   
 

class LobbyIdler(WidgetedIdler):
    def create_scene(self):
        self.scene = soya.World()
        #gameobjects.setScene(self.scene)
        
    def begin_round(self):
        WidgetedIdler.begin_round(self)
            
        # just send all events to the input 
        for e in soya.process_event():
            self.input.process_event(e)
            
        reactor.iterate()
        #print realm.server.state
        for player in players:
            if player.isstatechanged == 1:
                realm.server.state = "game"
                
        if realm.server.state != 'lobby':
            stateMachine.change_state(realm.server.state)
        
class GameIdler(WidgetedIdler):
    
    def create_scene(self):
        self.scene = soya.World()
        #gameobjects.setScene(self.scene)
        #print "from server CurrentScene is ", gameobjects.CurrentScene
        level = gameobjects.Level()
        levelbaseobjects = level.create()
                
        #create acutal objects
        for obj in levelbaseobjects:
            realm.server.object_parser(obj)
            
        
        #create the player characters
        realm.server.create_players()
        
          
    def begin_round(self):
        WidgetedIdler.begin_round(self)
        for e in soya.process_event():
                self.input.process_event(e)
                
        reactor.iterate()
        
        if realm.server.state != 'game':
            stateMachine = realm.server.state
        
    def resize(self):
        pass


class Action:
  def __init__(self, action):
    self.action = action

# The available actions
ACTION_WAIT          = 0
ACTION_ADVANCE       = 1
ACTION_ADVANCE_LEFT  = 2
ACTION_ADVANCE_RIGHT = 3
ACTION_TURN_LEFT     = 4
ACTION_TURN_RIGHT    = 5
ACTION_GO_BACK       = 6
ACTION_GO_BACK_LEFT  = 7
ACTION_GO_BACK_RIGHT = 8
ACTION_JUMP          = 9
ACTION_FIRE          = 10

class GameServer:
    """This is where actual game logic takes place"""
    def __init__ (self):
        self.state = ''
        self.gameobjects = {}
        self.Objects = gameobjects.Objects()
          
       
    def object_parser(self, obj):
        #try:
           # self.object_update(obj)
            #sendobjects to players    
            #for player in players:
            #    player.send_object(obj)
        #except:
            self.create_object(obj)
            #sendobjects to players    
            for player in players:
                player.send_object(obj)    
        
    def object_update(self, obj):
        object = self.gameobjects[obj['objid']]
        
    def create_object(self, obj):
        #print "create object is being called on the server"
        #print getScene().recursive()
        if obj['parent'] == 'scene':
          parent = getScene()
        else:
          parent = self.gameobjects[obj['parent']]
 
        makeobject = getattr(gameobjects, obj['type'])
        object = makeobject(parent, obj)
 
        self.gameobjects[obj['objid']] = object
            
            
    def get_object(self, objid):
        return self.gameobjects[objid] 

            
    def create_players(self):
        for player in players:
            #construct the player object
            playercharacter = self.Objects.base_object()
            playercharacter['objid'] = player.name + player.character
            print "player id is %s " % playercharacter['objid']
            playercharacter['parent'] = 'level1'
            player.gameid = playercharacter['objid']
            playercharacter['type'] = 'Player'
            playercharacter['mesh'] = player.character
            playercharacter['position'] = (-1,4,-1)
            self.object_parser(playercharacter)
          
    def playeraction(self, objectid, theaction):
        object = self.gameobjects[objectid]
        action = self.determineaction(theaction)
        object.begin_action(action)
        #print "player action", theaction 
        for player in players:
            player.playeraction_update(objectid, theaction)
    
    def determineaction(self, theaction):
        self.action_table = {
         (0, 0, 1, 0) : Action(ACTION_ADVANCE),
         (1, 0, 1, 0) : Action(ACTION_ADVANCE_LEFT),
         (0, 1, 1, 0) : Action(ACTION_ADVANCE_RIGHT),
         (1, 0, 0, 0) : Action(ACTION_TURN_LEFT),
         (0, 1, 0, 0) : Action(ACTION_TURN_RIGHT),
         (0, 0, 0, 1) : Action(ACTION_GO_BACK),
         (1, 0, 0, 1) : Action(ACTION_GO_BACK_LEFT),
         (0, 1, 0, 1) : Action(ACTION_GO_BACK_RIGHT),
        }
        self.default_action = Action(ACTION_WAIT)
    
        if theaction[4]:
            return Action(ACTION_JUMP)
        elif theaction[5]:
            return Action(ACTION_FIRE)
        else:
            return self.action_table.get((theaction[0], theaction[1],
                                  theaction[2], theaction[3]),
                                 self.default_action) 
    def saysomething(self):
        print "hi there"
        


class ServerPlayer(pb.Avatar):
    """this class is the players representation on the server. Anything that
    the player can do is implemented through this class
    methods that the remote player can implement are prefixed with 'prespective_'
    In other words all network events are routed through this class which then acts
    on the players behalf on the server"""
        
    #def perspective_foo(self, arg):
    #    """a sample function of a remotely implementable method"""
    #    print "I am", self.name, "perspective_foo(",arg,")
        
    def __init__(self, name):
        self.name = name #the players username 
        self.character = 'balazar' #holds which character that the player is using
        self.gameid = ''
        self.state = None 
        self.isstatechanged = 0
        
    def attached(self, mind):
        self.remote = mind
        
    def detached(self, mind):
        """stuff to do when a player becomes disconnected"""
        self.remote = None
        players.remove(self)
        
    def success(self, msg):
        """function to handle twisted deferreds and callbacks"""
        print "comm succeded"
        return msg
    
    def failure(self, error):
        """function to handle twisteds error msges"""
        print "comm failed Reason:", error
        return error
        
    #methods for chating
    def perspective_distribute_chatmsg(self, themsg):
        print "distributing chat msg"
        newmsg = "<"+self.name+">"+themsg
        for player in players:
            player.remote.callRemote("received_chatmsg", newmsg).addErrback(self.failure)
        
        
    #methods for changing state
    def perspective_changemystate(self, state):
        print "changing players state"
        #note this should check if all players are ready
        #for now though we just change all players on the first change
        #maybe move to game server as this is game related
        for player in players:
            player.state = state
            player.remote.callRemote("received_changestate", player.state).addErrback(self.failure)
        
        
    def perspective_set_isstatechanged(self, value):
        print self.name +" isstatechanged has changed to: ", value
        self.isstatechanged = value
        
    #methods for sendingobjects
    def send_object(self, obj):
        #print "sending obj :", obj
        self.remote.callRemote("received_object", obj).addErrback(self.failure)
        return self.remote
    
    def perspective_select_character(self, desiredgamecharacter):
        self.character = desiredgamecharacter
        msg = "I'm the character "+ desiredgamecharacter
        self.perspective_distribute_chatmsg(msg)
        
    def perspective_playeraction(self, action):
        #print "passing on player action to game server"
        self.server.playeraction(self.gameid, action)
    
    def playeraction_update(self, objid, action):
        #print "distributing player actions"
        self.remote.callRemote("received_playeractionupdate", objid, action).addErrback(self.failure)
        return self.remote
            
        
    #methods for new connections           
    def perspective_newclient(self):
        """the stuff to do when a new clientis joins"""
        #print "adding player :", self.name
        players.append(self)
        for player in players:
            print "server has this player:", player.name
            

    
    
class UserRealm:
    """This class is needed for twisted to gain unique avatars for each player"""
    __implements__ = portal.IRealm

    def requestAvatar(self, avatarID, mind, *interfaces):
        assert pb.IPerspective in interfaces
        avatar = ServerPlayer(avatarID)
        avatar.server = self.server
        avatar.attached(mind)
        return pb.IPerspective, avatar, lambda a=avatar:a.detached(mind)
        
class UndescriminatingChecker(object):
    """this is a custom checker to allow all incoming connections and give each a
    different avatar. This is where on would implement retreiving saved stat info
    or other things about a persistent players existence which is not needed for
    b-bomber. For more info about this check out the twisted sites HOW-TOs for 
    prespectives and Avatars as well as the checker.py file in the twisted module
    """
    __implements__ = (checkers.ICredentialsChecker,)
    #on a twisted note(hehe) when using the perspective broker IUsernameHashedPassword
    #is needed as opposed to IUsernamePassword
    credentialInterfaces = (credentials.IUsernameHashedPassword,)

    def requestAvatarId(self, credentials):
        """this returns a unique identifier based on the username"""
        return credentials.username


#this is for twisted portals and checkers are used to validate incoming connections
#and place them with the approptiate avatars if needed. Here we create a portal a 
#checker and then register that checker with the portal for more info see
#twisteds HOW-TO on perspectives and Avatars under the Perspective Broker
players = []
realm = UserRealm()
realm.server = GameServer()
c = UndescriminatingChecker()
p = portal.Portal(realm, [c])


#parse the options
parser = OptionParser()
parser.add_option("-p","--port", action="store", type="int", dest="port", default=8001)
(options, args) = parser.parse_args()
print "Server is using port :",options.port

#tell the twisted server what and where to listen to
reactor.listenTCP(options.port, pb.PBServerFactory(p))

# the global state machine object
stateMachine=StateMachine()

# all our application states
#stateMachine['intro']=IntroIdler
#stateMachine['menu']=MainMenuIdler
stateMachine['lobby']=LobbyIdler
stateMachine['game']=GameIdler

# run the first state
realm.server.state = 'lobby'
stateMachine.state= realm.server.state


