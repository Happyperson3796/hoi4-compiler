from .filetype import fileType
from ..pdxscript import get, format, Pair, Collection
import os
import shutil
from pathlib import Path

class FocusIcon(fileType):
    def run(self):
        head, tail = os.path.split(self.path)

        name = tail.replace(".focus.dds", ".dds")
        gfx = name.split(".")[0]
        name = name.split(".")
        if len(name) >= 3: namespace = name.pop(-2)
        else: namespace = name[0]
        name = ".".join(name)

        root = str(Path(self.path).parent.parent.parent.parent)
        os.makedirs(root+"/interface/", exist_ok=True)
        gfx_file = root+"/interface/"+namespace+".gfx"

        shutil.copyfile(self.path, head+"/"+name)

        if not os.path.exists(gfx_file):
            with open(gfx_file, "w") as file:
                file.write("spriteTypes = {\n\n}")

        with open(gfx_file, "r") as file:
            text = file.read()

        template = f"""    SpriteType = {{
        name = "GFX_{gfx}"
        texturefile = "gfx/interface/goals/{name}"            
    }}

	SpriteType = {{
		name = "GFX_{gfx}_shine"
		texturefile = "gfx/interface/goals/{name}"
		effectFile = "gfx/FX/buttonstate.lua"
		animation = {{
			animationmaskfile = "gfx/interface/goals/{name}"
			animationtexturefile = "gfx/interface/goals/shine_overlay.dds"
			animationrotation = -90.0
			animationlooping = no
			animationtime = 0.75
			animationdelay = 0
			animationblendmode = "add"
			animationtype = "scrolling"
			animationrotationoffset = {{ x = 0.0 y = 0.0 }}
			animationtexturescale = {{ x = 1.0 y = 1.0 }}
		}}

		animation = {{
			animationmaskfile = "gfx/interface/goals/{name}"
			animationtexturefile = "gfx/interface/goals/shine_overlay.dds"
			animationrotation = 90.0
			animationlooping = no
			animationtime = 0.75
			animationdelay = 0
			animationblendmode = "add"
			animationtype = "scrolling"
			animationrotationoffset = {{ x = 0.0 y = 0.0 }}
			animationtexturescale = {{ x = 1.0 y = 1.0 }}
		}}
		legacy_lazy_load = no
	}}
"""

        text = text.strip().removesuffix("}") + template + "\n}"

        with open(gfx_file, "w") as file:
            file.write(text)



    def clean(self):
        head, tail = os.path.split(self.path)

        name = tail.replace(".focus.dds", ".dds")
        name = name.split(".")
        if len(name) >= 3: namespace = name.pop(-2)
        else: namespace = name[0]
        name = ".".join(name)

        root = str(Path(self.path).parent.parent.parent.parent)
        gfx_file = root+"/interface/"+namespace+".gfx"

        try:
            os.remove(head+"/"+name)
        except: pass

        try:
            os.remove(gfx_file)
        except: pass


    def required_dir(self):
        return ["gfx/interface/goals"]