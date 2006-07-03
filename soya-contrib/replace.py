import sys, os, os.path, re

# Your source directory

DIR = "/home/jiba/src/soya"



EXT = [".py", ".pxd", ".pyx"]

EXC = "/build/"

def replace_all(SRC, DST):
  def replace_dir(arg, dirname, names):
    for name in names:
      name = os.path.join(dirname, name)

      if EXC in name: continue

      for ext in EXT:
        if name.endswith(ext): break
      else: continue

      print name, "->",

      s = open(name).read()
      os.unlink(name)

      s    = s   .replace(SRC, DST)
      name = name.replace(SRC, DST)
      print name

      open(name, "w").write(s)


  os.path.walk(DIR, replace_dir, None)



replace_all("Volume", "Body")
replace_all("volume", "body")
replace_all("VOLUME", "BODY")
replace_all("set_sound_body", "set_sound_volume")

replace_all("Idler", "MainLoop")
replace_all("idler", "main_loop")
replace_all("IDLER", "MAIN_LOOP")
replace_all("IDLEING_ITEMS", "MAIN_LOOP_ITEMS")
replace_all("idle", "main_loop")

replace_all("Landscape", "Terrain")
replace_all("landscape", "terrain")
replace_all("LANDSCAPE", "TERRAIN")

replace_all("Land", "Terrain")
replace_all("land", "terrain")
replace_all("LAND", "TERRAIN")

replace_all("Cal3dShape", "AnimatedModel")
replace_all("cal3d_shape", "animated_model")
replace_all("CAL3D_SHAPE", "ANIMATED_MODEL")

replace_all("Shape", "Model")
replace_all("shape", "model")
replace_all("SHAPE", "MODEL")

replace_all("Shapifier", "ModelBuilder")
replace_all("shapifier", "model_builder")
replace_all("SHAPIFIER", "MODEL_BUILDER")
replace_all("shapify", "to_model")

