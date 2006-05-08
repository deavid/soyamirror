import soya
import soya.pudding as pudding

soya.init()
pudding.init()

scene = soya.World()

camera = soya.Camera(scene)

soya.set_root_widget(pudding.core.RootWidget())
soya.root_widget.add_child(camera)

text = pudding.control.SimpleLabel(soya.root_widget, label = "Hello World!",  autosize = True)

pudding.idler.Idler(scene).idle()
