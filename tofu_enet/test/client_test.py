

import sys, soya, tofu_enet, cerealizer, soya.cerealizer4soya

tofu_enet.HOST = "127.0.0.1"
if len(sys.argv) > 1: tofu_enet.LOGIN = sys.argv[1]

cerealizer.register(tofu_enet.Level, soya.cerealizer4soya.SavedInAPathHandler(tofu_enet.Level))
cerealizer.register(tofu_enet.Mobile)

tofu_enet.set_mode("client")
main_loop = tofu_enet.MainLoop(soya.World())
main_loop.main_loop()
