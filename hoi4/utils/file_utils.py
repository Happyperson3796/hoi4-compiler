from ..pdxscript import get, format, Pair, Collection, Jom
import os, shutil
from .. import globals
from charset_normalizer import from_path

def get_encoding(path):
    # Fast initial detection
    encoding = from_path(path).best().encoding
    normalized = encoding.lower().replace('-', '_')

    # Most files will hit this and skip the BOM check
    if normalized != 'utf_8':
        return encoding

    # Only check BOM if it's detected as plain utf_8
    with open(path, 'rb') as f:
        if f.read(3).startswith(b'\xef\xbb\xbf'):
            return 'utf_8_sig'

    return encoding

def write_file(raw_path: str, name: str, data: Collection):
    path = globals.mod+"/"+raw_path+"/"
    os.makedirs(path, exist_ok=True)
    with open(path+name, "w", encoding="utf-8-sig") as file:
        file.write(format(data))

localization_dir_path = "localisation/"

class Locfile():
    def __init__(self, filename: str, lang: str = "english"):
        self.lang = lang

        if ".yml" not in filename: filename += "_l_"+self.lang+".yml"

        dir = localization_dir_path+self.lang+"/"
        dirs = dir+"/".join(filename.split("/")[:-1])
        os.makedirs(dirs, exist_ok=True)

        self.name = filename
        self.filepath = dir+filename

    def add(self, key: str, val: str):
        loc = "\n "+key+": \""+val+"\""

        if not os.path.exists(self.filepath):
            with open(self.filepath, "w", encoding="utf-8-sig") as file:
                file.write("l_"+self.lang+":")
        else:
            with open(self.filepath, "r", encoding="utf-8-sig") as file:
                lines = file.read()
                for x in lines.split("\n"):
                    if x.strip() == loc.strip(): return
        
        with open(self.filepath, "a", encoding="utf-8-sig") as file:
            file.write(loc)

    def remove(self, key: str, val: str):

        if not os.path.exists(self.filepath):
            return
        else:
            with open(self.filepath, "r", encoding="utf-8-sig") as file:
                lines = file.read()

            with open(self.filepath, "w", encoding="utf-8-sig") as file:
                text = []
                for x in lines.split("\n"):
                    if x.split(": ")[0].strip() != key.strip():
                        text.append(x)
                file.write("\n".join(text))

class Gfx():
    def __init__(self, cwd, name: str, texture: str, group: str = ""):
        texture = "gfx/interface/"+texture.replace("\\", "/")
        if group == "": group = name.removeprefix("GFX_")
        cwd = cwd.replace("\\", "/")
        if not cwd.endswith("/"): cwd = "/".join(cwd.split("/")[:-1])

        os.makedirs(globals.mod+"/".join(texture.split("/")[:-1]), exist_ok=True)
        shutil.copy(cwd+"/"+texture.split("/")[-1], globals.mod+texture)

        os.makedirs(globals.mod+"interface", exist_ok=True)

        gfx = globals.mod+"interface/generated_gfx_"+group+".gfx"
        if not os.path.exists(gfx):
            with open(gfx, "w") as file:
                data = Collection(Pair("spriteTypes","=",Collection()))
        else:
            with open(gfx, "r") as file:
                data = get(file.read())

        sprites = data[0][-1]
        sprites.append(Pair("spriteType","=",Collection(
            Pair("name","=","\""+name+"\""),
            Pair("texturefile","=","\""+texture+"\"")
        )))

        with open(gfx, "w") as file:
            file.write(format(data))