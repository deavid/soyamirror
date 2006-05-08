#!/usr/bin/env python

#twisted imports
from twisted.spread import pb
from twisted.internet import reactor
from twisted.cred import credentials
from twisted.python import reflect

#the file where all the objects for in game reside
import servergameobjects as gameobjects

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

# find and append the soya data dir
HERE = os.path.dirname(sys.argv[0])
datadir=os.path.join(HERE,"data")
# make sure the path exists
assert(os.path.isdir(datadir))
soya.path.append(datadir)

SOUNDS=os.path.join(HERE,'data','sounds')

# the star material we use for all the particle effects
material_star=soya.Material()
material_star.additive_blending=1
material_star.texture=soya.Image.get('littlestar.png')

# we use these to hold our sound effects
explosion_sound=None
bonus_sound=None

# will hold our state machine class when initialized
stateMachine=None

def getScene():
    """ helper function to return current scene object """
    return soya.IDLER.scenes[0]
    
class ClientPlayer(pb.Referenceable):
    """This class acts as the players connection to the server. All
    communicated info is routed through here, we inheirt """
    
    def __init__(self, address = "localhost", port = 8001, username = "user1", password = "pass1"):
        """initialize all data for a player to define iteself and allow it
        to do stuff"""
        
        self.address = address
        #the address of the connection we want defaults to loacal host
        self.port = port 
        self.username = username
        self.password = password
        self.isconnected = 0
        self.generalmsg = ''#used to help display messages such as chat on screen like
        #general msg should be changed to an array so that several simultaneous or near
        #near simultaneous messages can be displayed
        self.wantedstate =''
        self.state = ''
        self.maindeferred = 'None' #the root deferred object that is given by twisted. You'll see why we save it later
        self.gamecharacter = ''#this is the character that user desires as his avatar
        self.objectfactory = ObjectFactory()
        
    
    #twisted related functions
    #these functions are to help diagnos data transfers and to
    #pacify twisted as it likes to get upset and not work
    #if these aren't in certain callbacks
    
    def success(self, msg):
        """twisted callback if successful"""
        print "succeded"
    
    def failure(self, error):
        """twisted callback if there is an error"""
        print "failure reason:", error
    
    def store_deferred(self, deferred):
        """stores a twisted deferred object so that we may call functions
        on the players representation on the server"""
        self.maindeferred = deferred

    #these are the chat message related methods
    """The twisted way is using deferreds and callbacks. The reason is
    that a call over the wire is not instataneous (or near) so in order
    for the program to continue twisted immediately returns a deferred
    object and when the connection is completed it the deferreds callback
    This effectively results in any one call actually being two seperate calls
    You can also string multiple calls together if desired, I try to avoid 
    this though. 
    If this is confusing look below to see the examples and you will get
    the hang of it"""
    
    def send_chatmsg(self, themsg):
        """the first method in sending a chat message"""
        """this is a method called by the client app and is the first step
        in calling a method on the players server representation. Notice the
        aruguments in the addCallback first is the method that we want to call
        next are the arguments that need to be sent to that method they are
        seperated by commas. you can also add an default method if something 
        should go wrong this is what will be called and is added with the 
        addErrback method.
        Note anything that is sent over the wire needs to be a native Python type
        or a composite of python types any self defined classes or derived class
        will not transfer for security reasons"""
        self.maindeferred.addCallback(self.sending_chatmsg, themsg).addErrback(self.failure)
        
    def sending_chatmsg(self, perspective, themsg):
        """the second method in calling a chat message. It does the actual sending"""
        """Once the deferred returns we can call the actuall method on the server.
        Notice the arguments to the method we have added "perspective" this is the
        handle for the player to call their representation or perspective on the
        server. Also note it returns another deferred for another call to be
        made. Also remember that anymethod called in this manner must be 
        preceded on the server by "perspective_ otherwise it is not calleable
        this is done for security and is mandated by twisted. MAKE SURE you return
        the perspective if you don't you will be unable to call additional methods 
        over the network and you will get something that alternates between working
        and not working"""
        print "sending chat msg", themsg
        d = perspective.callRemote("distribute_chatmsg", themsg)
        d.addCallback(self.success)#call this if success
        d.addErrback(self.failure)#call this if it failed
        return perspective#RETURN YOUR PERSPECTIVE
        
    def remote_received_chatmsg(self, themsg):
        """method called by the server to display the chat message"""
        """The first thing to note about this method is the prefix "remote_ 
        Its that prefix that lets the players server representation call this
        method. otherwise its a basic method saving the message sent by the server
        in generalmsg for displaying """
        self.generalmsg = themsg
        print "recieved chat msg", themsg
        
    #def State related methods are here
    def send_changestaterequest(self, state):
        """first step in letting the server node player wants to change its state"""
        """if you have questions on how this works look at the chatmsg methods"""
        self.maindeferred.addCallback(self.sending_changestaterequest, state).addErrback(self.failure)
            
    def sending_changestaterequest(self, perspective, state):
        """second step in changing state"""
        #the below call sets a flag on the server saying that we have yet to change 
        #our state
        self.maindeferred.addCallback(self.setting_changedstate, 0).addErrback(self.failure)
        #actually request the change of state from the server
        print "sending changestate request to:", state
        d = perspective.callRemote("changemystate", state)
        d.addCallback(self.success)
        d.addErrback(self.failure)
        #remember return that perspective
        return perspective
        
    def remote_received_changestate(self, newstate):
        """server called method telling client what state to change to"""
        print "trying to change state to ", newstate
        self.state = newstate
        print "succesfully changed state to ", newstate
        #the below call starts the series to let the server know we have changed state
        self.maindeferred.addCallback(self.setting_changedstate, 1).addErrback(self.failure)
     
    def setting_changedstate(self, perspective, value):
        """method that actually sets the flag on the server to let it know if we
        have actually changed state or not"""
        print "setting isstatechanged to:", value
        d = perspective.callRemote("set_isstatechanged", value)
        d.addCallback(self.success)
        d.addErrback(self.failure)
        #self.send_chatmsg("ping pong form client")
        return perspective#return your perspective
    
    #methods for object messsages are here
    def remote_received_object(self, obj):
        """server calls this when there is a new object to be added. It
        simply passes the object to the object factory so it can be
        properly handled"""
        self.objectfactory.object_parser(obj)
        
        
    def select_character(self, character):
        """first step in selecting a character for the player to use"""
        print "checkingout character ",character
        self.gamecharacter = character
        #note no arguments sent but in callbacks arguments perspective appears
        #this is put their automatically by twisted
        self.maindeferred.addCallback(self.sending_selectedcharacter).addErrback(self.failure)
        
    def sending_selectedcharacter(self, perspective):
        """actually calls the server method for character server selection"""
        d = perspective.callRemote("select_character", self.gamecharacter)
        d.addCallback(self.success)
        d.addErrback(self.failure)
        return perspective
    
    def send_playeraction(self, action):
        """clientplayers has made a move this is first step in sending to 
        server"""
        self.maindeferred.addCallback(self.sending_playeraction, action).addErrback(self.failure)
    
    def sending_playeraction(self, perspective, action): 
        """Clientplayer has mad a move sending to the server"""
        d = perspective.callRemote("playeraction", action)
        d.addCallback(self.success)
        d.addErrback(self.failure)
        return perspective
        
    def remote_received_playeractionupdate(self, objid, theaction):

        """a player (not necessarily the local player. has moved 
        updateing their character"""

        try:
          object = self.objectfactory.gameobjects[objid]
        except KeyError:
          raise "%s is not a valid key. vaild names are %s" % (objid, self.objectfactory.gameobjects.keys())

        action = self.determineaction(theaction)
        object.begin_action(action)
        
    def determineaction(self, theaction):
        """this returns the desired player action based on the
        pressedkeys"""
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

    #connection communications are here
    def attempt_connection(self):
        """starts the connection of the client to the server"""
        print "attempting to connect"
        reactor.connectTCP(clientplayer.address, clientplayer.port, factory)
        def1 = factory.login(credentials.UsernamePassword(self.username, self.password), client = self)
        print def1
        def1.addCallback(self.connected).addErrback(self.failure)
        self.store_deferred(def1)
       
    
    def connected(self, perspective):
        """call the necessary things to tell server it has a new client to listen too
        This might/should be replaced with a mind(twisted) argument"""
        
        d = perspective.callRemote("newclient")
        print "connected"
        self.generalmsg = "Connected!!."
        return perspective
    
    def close_connection(self):
        reactor.stop()
  
class ObjectFactory:
    """this class does everything that needs to be done with a object
    """
    def __init__(self):
        #the list of game objects 
        self.gameobjects ={}
        
    def object_parser(self, obj):
        """this method takes an object and decided if its an update or not
        """
        try:
            self.object_update(obj)
        except:
            self.create_object(obj)
            
    def object_update(self, obj):
        """if the object is an update update it"""
        object = self.gameobjects[obj['objid']]
        
    def create_object(self, obj):
        """object was not in the base so lets create it. This also
        determines where to put it based on the parent"""
        
        if obj['parent'] == 'scene':
          parent = getScene()
        else:
          parent = self.gameobjects[obj['parent']]
 
        makeobject = getattr(gameobjects, obj['type'])
        object = makeobject(parent, obj)
 
        self.gameobjects[obj['objid']] = object
            
    def get_object(self, objid):
        """allows other methods to get a object based on its id"""
        return self.gameobjects[objid] 
        

class StateMachine(dict):
  
  def __init__(self,initialdata={}):
    dict.__init__(self,initialdata)
    self.__currentState=None

  def __getstate__(self):
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


class MenuIdler(WidgetedIdler):
  """ all our menu screens will be a subclass of this """

  def create_scene(self):
    WidgetedIdler.create_scene(self)

    # setup a nice background for our menu screens
    
    # some lighting 
    sun = soya.Light(self.scene)
    sun.directional = 1
    sun.diffuse = (1.0, 0.8, 0.4, 1.0)
    sun.rotate_vertical(-45.0)

    # atmosphere
    atmosphere = soya.SkyAtmosphere()
    atmosphere.ambient = (0.3, 0.3, 0.4, 1.0)
    atmosphere.fog = 1
    atmosphere.fog_type  = 0
    atmosphere.fog_start = 40.0
    atmosphere.fog_end   = 50.0
    atmosphere.fog_color = atmosphere.bg_color = (0.2, 0.5, 0.7, 1.0)
    atmosphere.skyplane  = 1
    atmosphere.sky_color = (1.5, 1.0, 0.8, 1.0)

    self.scene.atmosphere = atmosphere

    # balazar can be our center-piece
    balazar=soya.Cal3dShape.get("balazar")
    self.perso=soya.Cal3dVolume(self.scene,balazar)
    self.perso.animate_blend_cycle("attente")
    self.perso.turn_lateral(180)
    self.perso.y-=1
    self.perso.z-=1

    # some particles
    particle= gameobjects.Explosion(self.scene)
    particle.set_xyz(-1,0,0)

    particle= gameobjects.Explosion(self.scene)
    particle.set_xyz(1,0,0)

  def advance_time(self,p):
    WidgetedIdler.advance_time(self,p)

    self.perso.turn_lateral(1.*p)
  
  def create_widgets(self):  
    WidgetedIdler.create_widgets(self)

    self.title=widget.Label(soya.root_widget,"Balazar Bomber",align=1)

  def resize(self):
    WidgetedIdler.resize(self)

    self.title.width=soya.root_widget.width
    self.title.height=soya.root_widget.height


class GameIdler(WidgetedIdler):
  """ Idler for the actual game play """

  def create_scene(self):
    self.scene = soya.World()
    
    #self.level = gameobjects.ClientLevel()
    #self.level.create()
    
    self.controller = Keyboardcontroller()
    
    #self.scene.add(self.level)

  def create_camera(self):
    self.camera = soya.Camera(self.scene)
    dist=6.
    self.camera.set_xyz(-1, dist+dist+5, dist+0)
    #level = clientplayer.objectfactory.get_object('level1')
    #self.camera.look_at(soya.Point(level,-1.,0.,-1.))
    self.camera.look_at(soya.Point(self.scene, -1.,0.,-1.))
    
  def create_widgets(self):
    soya.root_widget.add(widget.FPSLabel())

  def resize(self):
    pass

  def begin_round(self):
    #cycle the controler
    action = self.controller.next()
    clientplayer.send_playeraction(action)
    
    #cycle the network
    reactor.iterate()
    
    #check if the player is still playing
    if clientplayer.state != 'game':
            stateMachine.change_state(clientplayer.state)
    
class FadingLabel(soya.widget.Label):
  """ A Simple fading label """

  def widget_advance_time(self,p):
    # get our current colour
    r,g,b,a=self.get_color()
    
    a-=.01*p
    
    # if alpha is < 0 then the label cannot be seen anymore so should be removed
    if a<0.:
      # see if we have an attribute called on_remove and if so call it as a function
      if hasattr(self,'on_remove'): self.on_remove()

      # remove ourselves
      soya.root_widget.remove(self)

    # set the color back with the new alpha value
    self.set_color((r,g,b,a))


class IntroIdler(MenuIdler):
  """ Idler for the splash/startup screen """
  def create_widgets(self):
    MenuIdler.create_widgets(self)

    # simple instruction label
    self.label=widget.Label(soya.root_widget,"Press any key to continue",align=1)

    # messages we will scroll thru on the intro screen
    self.messages=["A Soya Demo",
                   "http://home.gna.org/oomadness/en/soya/",
                   "Thanks to the all involved in Soya",
                   "Visit #slune irc.freenode.net",
                   ]

    # which message to show next
    self.current_message=0

    self.create_message_label()

    # there should probably be somewhere better for this 
    #explosion_sound.play()

  def create_message_label(self):
    # create our FadingLabel instance with the current message 
    self.messageLabel=FadingLabel(soya.root_widget,self.messages[self.current_message],align=1)

    # set the on_remove attribute so we can create a new message at the end of its life
    self.messageLabel.on_remove=self.create_message_label

    # position the label above the simple instructions
    self.messageLabel.width=soya.root_widget.width
    self.messageLabel.top=soya.root_widget.height-150

    # incremenent the current message variable
    self.current_message+=1
    # wrap around the messages if we've gone too far
    if self.current_message>=len(self.messages):
      self.current_message=0

  def resize(self):
    MenuIdler.resize(self)

    self.label.width=soya.root_widget.width
    self.label.top=soya.root_widget.height-100
    self.label.height=soya.root_widget.height

  def begin_round(self):
    MenuIdler.begin_round(self)

    # wait for any keystroke to advance onto the menu
    for e in soya.process_event():
      if e[0]==sdlconst.KEYDOWN and e[3]!=0:
        clientplayer.state='menu'
        
    if clientplayer.state != 'intro':
            stateMachine.change_state(clientplayer.state)

class MainMenuIdler(MenuIdler):
  """ Main Menu Idler """

  def start_game_state(self):
    #explosion_sound.play()
    clientplayer.state='game'

  def start_lobby_state(self):
    #explosion_sound.play()
    clientplayer.state='lobby'
  
  def create_widgets(self):
    MenuIdler.create_widgets(self)

    # all our menu choices
    choices=[ widget.Choice('Start Game',self.start_game_state),
              widget.Choice('Lobby Test',self.start_lobby_state),
              widget.Choice('Exit',lambda: sys.exit()),
            ]
    
    self.choicelist=widget.ChoiceList(soya.root_widget,choices)
        
    #explosion_sound.play()

  def resize(self):
    MenuIdler.resize(self)

    self.choicelist.top=150
    # fit the height of the list to exactly match the amount of items in the list
    self.choicelist.height=len(self.choicelist.choices)*(widget.default_font.height+10)
    self.choicelist.width=soya.root_widget.width
   
  def begin_round(self):
    MenuIdler.begin_round(self)
    
    # pass all events to the choicelist
    for e in soya.process_event():
      self.choicelist.process_event(e)
    
    if clientplayer.state != 'menu':
            stateMachine.change_state(clientplayer.state)

class SimpleInput(widget.ChoiceList):
    """ A simple bodge to fake a text input """
    
    class ChoiceInput(widget.ChoiceInput):
        """ A modified version of ChoiceInput to change the output formatting and to catch
        enter key presses"""
        def set_label_name(self, label):
            self.label = label
        def get_label(self):
            # make some sort of prompt and cursor
            newlabel = self.label + self.value +"_"
            return newlabel#">%s_" % self.value
    
        def key_down(self,key_id,mods):
            # if the key is enter we want to call our owners on_enter function
            # otherwise just let soya.ChoiceInput deal with it 
            if key_id==sdlconst.K_RETURN:
                self.parent.on_enter()
            elif key_id in [sdlconst.K_DELETE,sdlconst.K_BACKSPACE,sdlconst.K_CLEAR]:
                self.value=self.value[:-1]
            elif key_id!=0:
                # make sure the character is considered printable. 
                # is there a better way than this?
                if chr(key_id) in string.printable:
                    self.value+=chr(key_id)
            else: print key_id,mods
    
    def process_event(self,event):
        # we must subclass this to make use of the unicode data in the event
    
        if (event[0] == soya.sdlconst.KEYDOWN):
            self.input.key_down(event[3],event[2])      
        
    def get_value(self):
        return self.input.value
    
    def set_value(self,value):
        self.input.value=value
    
    # create a property to make this class seem more like a single control
    value=property(get_value,set_value)
    
    def __init__(self,parent,value='',enter_func=None, label = "> "):
        # our modified soya.ChoiceInput
        self.input=self.ChoiceInput()
        self.input.set_label_name(label)
        # give the choice a handle back to here so we can call on_enter
        self.input.parent=self
        self.value=value
        self.enter_func=enter_func
        
        widget.ChoiceList.__init__(self,parent,[self.input],align=0)
    
        self.height=(widget.default_font.height+10)
    
    def on_enter(self):
        """ called whenever enter is pressed """
        if self.enter_func!=None:
            self.enter_func(self.value)
    


class LobbyIdler(WidgetedIdler):
    """ Idler for the networking Lobby """
    
    
    def create_widgets(self):
        WidgetedIdler.create_widgets(self)
    
        # create a message to display
        message="""This is a lobby test using the default soya widgets.

Commands
---------------------------------
\\exit to return to the main menu.
\\start to start a new game 
\\connect xxx.xxx.xxx.xxx portnum username     to connect to a server
just type to chat

"""
        #variable to let us know if we are connected to a server
        #should be subclassed so pl;ayers don't have to reconnect after each game
        
        
         #this is where output will go. ie stdout
        self.text=BufferedLabel(soya.root_widget,message.split("\n"))
        
        # this is our "edit box". ie stdin
        self.input=SimpleInput(soya.root_widget,enter_func=self.send, label = ">:")

    def resize(self):
        WidgetedIdler.resize(self)
        
        # fill the main body of the screen
        self.text.top=100
        self.text.left=30
        self.text.width=soya.root_widget.width-60
        self.text.height=soya.root_widget.height-100
    
        # calculate how many lines we should display 
        self.text.show_lines=self.text.height/(widget.default_font.height)
        self.text.show_lines-=3
        print "showlines=",self.text.show_lines
        self.text.update()
    
        # position at the bottom of the screen
        self.input.top=soya.root_widget.height-50
        self.input.left=30
        self.input.width=soya.root_widget.width-60
        
    def send(self,string):
        """ this happens when the user presses enter. this would probably 
        be used to send a command or chat to a server
        """
    
        # check if the input was a command 
        if self.input.value[:1]=='\\':
            rest =self.input.value[1:].lower()
            command = rest.split(' ')
            if command[0]=='exit':
                clientplayer.state='menu'
                
            elif command[0]=='start':
                #stateMachine.change_state('game')
                clientplayer.send_changestaterequest("game")
            
            elif command[0]=='char':
                #command to set desired character only functions after connection
                #has been made atm
                clientplayer.select_character(command[1])
                
            elif command[0]=='connect':
                #start the connection and set any desired arguments
                
                try:
                    clientplayer.address = command[1]
                    clientplayer.port = int(command[2])
                    clientplayer.username = command[3]
                    clientplayer.password = "notusedatm"
                except:
                    clientplayer.address = "localhost"
                    clientplayer.port = 8001
                    clientplayer.username = 'anon'
                    clientplayer.password = "notusedatm"
                    self.text.append_line("format needs to be \connect xxx.xxx.xxx.xxx port username")
                    self.text.append_line("can also be url port username")
                    self.text.append_line("default is localhost 8001 anon")
                    

                self.text.append_line("attempting connection")
                clientplayer.isconnected = 1
                try:
                    clientplayer.attempt_connection()
                    
                except:
                    clientplayer.isconnected = 0
                    self.text.append_line("Connection failed")
        else:
            if clientplayer.isconnected !=0:
                clientplayer.send_chatmsg(self.input.value[:])
            else:
                self.text.append_line("You are not connected")
                
        self.input.value=''
        
   
    def begin_round(self):
        
        # just send all events to the input 
        for e in soya.process_event():
            self.input.process_event(e)
        
        #iterate the twisted reator so it can process all its stuff    
        if clientplayer.isconnected != 0:
            reactor.iterate()
        
        if clientplayer.generalmsg !='':
            self.text.append_line(clientplayer.generalmsg)

            clientplayer.generalmsg =''
        
        if clientplayer.state != 'lobby':
            stateMachine.change_state(clientplayer.state)
            

 


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


class Keyboardcontroller:
  def __init__(self):
    self.left_key_down = self.right_key_down = self.up_key_down = self.down_key_down = 0
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
    
  def next(self):
    jump = 0
    fire = 0
    #print "running controllers next method"
    
    for event in soya.process_event():
      if   event[0] == sdlconst.KEYDOWN:
        if   (event[1] == sdlconst.K_q) or (event[1] == sdlconst.K_ESCAPE):
          clientplayer.state = 'menu'
          
        elif event[1] == sdlconst.K_LSHIFT:
          jump = 1

        elif event[1] == sdlconst.K_SPACE:
          fire = 1
        elif event[1] == sdlconst.K_F1:
          soya.screenshot().save(os.path.join(os.path.dirname(sys.argv[0]), "results", os.path.basename(sys.argv[0])[:-3] + ".jpg"))
          
        elif event[1] == sdlconst.K_LEFT:  self.left_key_down  = 1
        elif event[1] == sdlconst.K_RIGHT: self.right_key_down = 1
        elif event[1] == sdlconst.K_UP:    self.up_key_down    = 1
        elif event[1] == sdlconst.K_DOWN:  self.down_key_down  = 1
        
      elif event[0] == sdlconst.KEYUP:
        if   event[1] == sdlconst.K_LEFT:  self.left_key_down  = 0
        elif event[1] == sdlconst.K_RIGHT: self.right_key_down = 0
        elif event[1] == sdlconst.K_UP:    self.up_key_down    = 0
        elif event[1] == sdlconst.K_DOWN:  self.down_key_down  = 0
    
    #if jump: return Action(ACTION_JUMP)
    #if fire: return Action(ACTION_FIRE)
    
    return (self.left_key_down, self.right_key_down, self.up_key_down, self.down_key_down, jump, fire)


class BufferedLabel(widget.Label):
    def __init__(self,parent,lines=[]):
        widget.Label.__init__(self,parent,align=0)

        self.show_lines=1
        self.lines=lines

    def update(self):
        #print "updating to:"
        self.set_text("\n".join(self._lines[-self.show_lines:]))
        #print self.get_text()
        #print
    
    def set_lines(self,lines):
        self._lines=lines
        self.update()

    def get_lines(self):
        return self._lines

    def append_line(self,line):
        self._lines.append(line)
        self.update()

    def write(self,line):
        self.append_line(line)

    lines=property(get_lines,set_lines)


clientplayer = ClientPlayer()
factory = pb.PBClientFactory()

if __name__=='__main__':
  soya.init(width=800,height=600,title="Balazar Bomber")
  
  #soya.init_audio()

  # play our music file on loop forever :D
  #music=soya.MusicFile(os.path.join(SOUNDS,'test.mod'))
  #music.play(-1)
  
  # we load this for later
  #explosion_sound=soya.AudioFile(os.path.join(SOUNDS,'explosion.wav'))
  #bonus_sound=soya.AudioFile(os.path.join(SOUNDS,'arcade.wav'))
  
  # turn on unicode key events for better text input
  soya.set_use_unicode(True)
  
  # the global state machine object
  stateMachine=StateMachine()
  
  # all our application states
  stateMachine['intro']=IntroIdler
  stateMachine['menu']=MainMenuIdler
  stateMachine['lobby']=LobbyIdler
  stateMachine['game']=GameIdler

  # run the first state
  clientplayer.state = "intro"
  stateMachine.state= clientplayer.state

