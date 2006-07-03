
# Example of Pudding list object, by Reto Spoerri (thanks :-))

import soya, soya.pudding, soya.pudding.listbox

soya.init(width = 800, height = 600, fullscreen=False)

soya.pudding.init()

rootWidget = soya.pudding.core.RootWidget(width = 800, height = 600)

soya.set_root_widget(rootWidget)
scene = soya.World()

list = ["obj0","obj1","obj2","obj3","obj4","obj5","obj6"]
a = soya.pudding.listbox.ListBox( rootWidget, list )

camera = soya.Camera( scene )
rootWidget.add_child( camera )

soya.pudding.main_loop.MainLoop( scene ).main_loop()
