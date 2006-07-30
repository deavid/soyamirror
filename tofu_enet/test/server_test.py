
import sys, os, os.path

import soya, tofu_enet, cerealizer, soya.cerealizer4soya

try: os.mkdir("/tmp/tofu_data")
except: pass
try: os.mkdir("/tmp/tofu_data/players")
except: pass
try: os.mkdir("/tmp/tofu_data/levels")
except: pass

soya.path.append("/tmp/tofu_data")

tofu_enet.set_mode("server")




class TestPlayer(tofu_enet.Player):
  def __init__(self, filename, password, opt_data = ""):
    tofu_enet.Player.__init__(self, filename, password, opt_data)
    
    mobile = tofu_enet.Mobile()
    LEVEL.add_mobile(mobile)
    self.add_mobile(mobile)
    self.save()

tofu_enet.CREATE_PLAYER = TestPlayer

cerealizer.register(tofu_enet.Level, soya.cerealizer4soya.SavedInAPathHandler(tofu_enet.Level))
cerealizer.register(tofu_enet.Mobile)
cerealizer.register(TestPlayer, soya.cerealizer4soya.SavedInAPathHandler(TestPlayer))

LEVEL = tofu_enet.Level()
LEVEL.filename = "test2"
LEVEL.save()

#LEVEL = tofu_enet.Level.get("test2")


#TestPlayer("r", "test").save()




main_loop = tofu_enet.MainLoop(soya.World())
main_loop.main_loop()

