from .filetype import fileType
from .pdxscript import get, format, Pair, Collection
import shutil
import os
from . import globals

def strip(text):
    texts = text.replace(".focus", ".txt").split(".")
    if texts[-1] == "txt":
        if "/" not in texts[-2] and "\\" not in texts[-2]:
            texts.pop(-2)
    return ".".join(texts)

class Focus(fileType):

    def run(self):
        head, tail = os.path.split(self.path)

        vanilla_path = globals.vanilla_path+"/common/national_focus/"

        if not os.path.exists(strip(self.path)):
            shutil.copyfile(vanilla_path+strip(tail), strip(self.path))

        file_from = self.path
        file_to = strip(self.path)

        focus = open(file_to, "r", encoding="utf-8-sig")
        focus_data = get(focus.read()).get().val()
        
        with open(file_from, "r", encoding="utf-8-sig") as file:
            data = get(file.read()).get().val()

            for x in data:
                try:
                    id = x.get().get("id").val()

                    override = False
                    try:
                        if (x.get().get("override").val() == "yes"):
                            override = True
                            index = -1
                            for obj in x.get().val():
                                index += 1
                                if obj[0] == "override":
                                    x.get().val().pop(index)
                    except: pass

                    replaced = False
                    for y in focus_data:
                        try:
                            if id == y.get().get("id").val():

                                if not override:

                                    for objx in x.get().val():
                                        replaced_2 = False
                                        for objy in y.get().val():
                                            if (objx[0] == objy[0]):
                                                if objx[0] != "prerequisite":
                                                    objy.get().set(objx.get())
                                                    replaced_2 = True
                                                else:
                                                    if (str(objx[-1].val()) == str(objy[-1].val())):
                                                        replaced_2 = True

                                        if not replaced_2:
                                            y.get().val().append(objx)
                                
                                else:
                                    y.set(x.get())

                                replaced = True
                                break

                        except: pass

                    if not replaced:
                        focus_data.append(x)

                except: pass

            collected = Collection()
            collected.append(Pair("focus_tree", "=", focus_data))
            
            with open(strip(file_from), "w") as file:
                file.write(format(collected))

        focus.close()



    def clean(self):
        try:
            os.remove(strip(self.path))
        except: pass
