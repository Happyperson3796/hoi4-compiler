from .filetype import fileType
from ..pdxscript import get, format, Pair, Collection
from ..utils.file_utils import Locfile
from .. import globals
import os

class Embeddable(fileType):

    def run(self, data, locfilename, embeddable_loc: dict):
        self.embedded_loc = {}
        self.embedded_modifiers = Collection()
        locfile = Locfile(locfilename)

        self.scan_data(data, locfile, embeddable_loc)

        for x, y in self.embedded_loc.items():
            locfile.add(x, y)

        modifier_path = globals.mod+"/main_menu/common/static_modifiers/"
        os.makedirs(modifier_path, exist_ok=True)
        with open(modifier_path+self.path.split("\\")[-1].split(".")[0]+"_inline_modifiers.txt", "w", encoding="utf-8-sig") as file:
            file.write(format(self.embedded_modifiers))

    def clean(self, data, locfilename, embeddable_loc: dict):
        self.embedded_loc = {}
        self.embedded_modifiers = Collection()
        locfile = Locfile(locfilename)

        self.scan_data(data, locfile, embeddable_loc)

        for x, y in self.embedded_loc.items():
            locfile.remove(x, y)

        modifier_path = globals.mod+"/main_menu/common/static_modifiers/"
        try: os.remove(modifier_path+self.path.split("\\")[-1].split(".")[0]+"_inline_modifiers.txt")
        except: pass

    def scan_data(self, obj, locfile, embeddable_loc: dict, root=""):
        if isinstance(obj, Pair):
            if obj[0] == "inline_modifiers":
                for x in obj[-1]:
                    id = x[0]
                    modifier_data = x[-1]
                    loc = modifier_data.get_pop("name", "").unquote()
                    if loc != "": self.embedded_loc["STATIC_MODIFIER_NAME_"+id] = loc
                    self.embedded_modifiers.append(Pair(id,"=",modifier_data))

                obj[0] = ""
                obj[1] = ""
                obj[-1] = ""
                return

            for x, y in embeddable_loc.items():
                x = x.replace("$ROOT", root)
                if isinstance(y, list):
                    z = []
                    for n in y:
                        z.append(n.replace("$ROOT", root))
                    y = z
                else: y = y.replace("$ROOT", root)

                if x == obj[0]:
                    newKey = x
                    if isinstance(y, list):
                        newKey = y[-1]
                        y = y[0]

                    obj[0] = newKey
                    o = obj[-1]
                    if o.startswith("\"") and o.endswith("\"") and y not in self.embedded_loc.keys(): # str(o) x2 on this line if it breaks
                        self.embedded_loc[y] = o.unquote() #Don't include unquoted embeds, probably are loc keys
                        o.set(y)

            if root == "":
                root = obj[0]
            self.scan_data(obj[-1], locfile, embeddable_loc, root)
        elif isinstance(obj, Collection):
            for x in obj:
                self.scan_data(x, locfile, embeddable_loc, root)