from ..pdxscript import get, format, Pair, Collection, Jom
import os
from .. import globals

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

