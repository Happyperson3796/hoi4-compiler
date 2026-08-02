from .filetype import fileType
from ..pdxscript import get, format, Pair, Collection, Value
import shutil
import os
from .. import globals

def strip(text):
    texts = text.replace(".focus", ".txt").split(".")
    if texts[-1] == "txt":
        if "/" not in texts[-2] and "\\" not in texts[-2]:
            texts.pop(-2)
    return ".".join(texts)

class Focus(fileType):

    def run(self):
        head, tail = os.path.split(self.path)
        base_dir = os.path.abspath(os.path.join(os.path.abspath(os.path.join(head, os.pardir)), os.pardir))

        vanilla_path = globals.vanilla_path+"/common/national_focus/"

        if tail.endswith(".core.focus") or tail.endswith(".0.focus"):
            with open(strip(self.path), "w", encoding="utf-8-sig") as file:
                shutil.copyfile(self.path, strip(self.path))

        if not os.path.exists(strip(self.path)):
            shutil.copyfile(vanilla_path+strip(tail), strip(self.path))

        extras = Collection()

        file_from = self.path
        file_to = strip(self.path)

        focus = open(file_to, "r", encoding="utf-8-sig")
        focus_data = get(focus.read())
        for x in focus_data:
            if x[0] != "focus_tree":
                extras.append(x)
        focus_data = focus_data.get("focus_tree")
        
        with open(file_from, "r", encoding="utf-8-sig") as file:
            data = get(file.read())
            for x in data:
                if x[0] != "focus_tree":
                    extras.append(x)
            data = data.get("focus_tree")

            remove = []
            inline_ideas = ""
            inline_loc = ""
            def traverse(x, parent):
                nonlocal inline_ideas
                nonlocal inline_loc
                if isinstance(x, Collection):
                    for y in x:
                        traverse(y, x)
                elif isinstance(x, Value):
                    traverse(x._value(), x)
                elif isinstance(x, Pair):
                    traverse(x[-1], x)


                    if x[0] == "define_idea":
                        idea: Collection = get(str(x))[0][-1]
                        remove.append([parent, x])

                        name = str(idea.get("name"))
                        idea.remove(idea.get_pair("name"))

                        desc = str(idea.get("desc", ""))
                        if desc != "": idea.remove(idea.get_pair("desc"))

                        id = str(idea.get("id"))
                        idea.remove(idea.get_pair("id"))
                        
                        inline_loc += " "+id+": "+name+"\n"
                        if desc != "": inline_loc += " "+id+"_desc: "+desc+"\n"

                        inline_ideas += "\n        " + id +" = {"+(("\n"+format(idea)).replace("\n", "\n            ")).removesuffix("    ")+"}"
                        
            traverse(data, None)
            for x, y in remove:
                x.remove(y)

            if inline_ideas != "":
                os.makedirs(base_dir+"/common/ideas/", exist_ok=True)
                if os.path.exists(base_dir+"/common/ideas/"+tail+"_inline_ideas.txt"):
                    with open(base_dir+"/common/ideas/"+tail+"_inline_ideas.txt", "r") as ideas:
                        lines = ideas.readlines()
                        inline_ideas = "".join(lines[2:-2]) + inline_ideas

                with open(base_dir+"/common/ideas/"+tail+"_inline_ideas.txt", "w", encoding="utf-8") as ideas:
                    ideas.write("ideas = {\n    country = {\n" + inline_ideas.removeprefix("\n") + "\n    }\n}")

            if inline_loc != "":
                os.makedirs(base_dir+"/localisation/", exist_ok=True)            
                if os.path.exists(base_dir+"/localisation/"+tail+"_inline_localisation_l_english.yml"):
                    with open(base_dir+"/localisation/"+tail+"_inline_localisation_l_english.yml", "r", encoding="utf-8-sig") as loc:
                        inline_loc = loc.read() + "\n" + inline_loc
                else: inline_loc = "l_english:\n" + inline_loc

                with open(base_dir+"/localisation/"+tail+"_inline_localisation_l_english.yml", "w", encoding="utf-8-sig") as loc:
                    loc.write(inline_loc)
            


            for x in data:
                try:
                    id = str(x.value().get("id"))
                    try:
                        name = " "+id+": "+str(x.value().get("name"))
                        x.value().remove(x.value().get_pair("name"))
                    except: name = ""
                    try:
                        desc = " "+id+"_desc: "+str(x.value().get("desc"))
                        x.value().remove(x.value().get_pair("desc"))
                    except: desc = ""

                    if name != "" or desc != "":
                        focus_loc = name+"\n"+desc+"\n"
                        os.makedirs(base_dir+"/localisation/", exist_ok=True)            
                        if os.path.exists(base_dir+"/localisation/"+tail+"_inline_localisation_l_english.yml"):
                            with open(base_dir+"/localisation/"+tail+"_inline_localisation_l_english.yml", "r", encoding="utf-8-sig") as loc:
                                focus_loc = loc.read() + "\n" + focus_loc
                        else: focus_loc = "l_english:\n" + focus_loc

                        with open(base_dir+"/localisation/"+tail+"_inline_localisation_l_english.yml", "w", encoding="utf-8-sig") as loc:
                            loc.write(focus_loc)

                    override = False
                    try:
                        if (str(x.value().get("override")) == "yes"):
                            override = True
                            index = -1
                            for obj in x.value():
                                index += 1
                                if obj[0] == "override":
                                    x.value().pop(index)
                    except: pass

                    replaced = False
                    for y in focus_data:
                        try:
                            if id == str(y.value().get("id")):

                                if not override:

                                    for objx in x.value():
                                        replaced_2 = False
                                        for objy in y.value():
                                            if (objx[0] == objy[0]):
                                                if objx[0] != "prerequisite":
                                                    objy.value().set(objx.value())
                                                    replaced_2 = True
                                                else:
                                                    if (str(objx[-1]) == str(objy[-1])):
                                                        replaced_2 = True

                                        if not replaced_2:
                                            y.value().append(objx)
                                
                                else:
                                    y[-1] = x.value()

                                replaced = True
                                break

                        except: pass

                    if not replaced:
                        focus_data.append(x)

                except: pass

            collected = extras
            collected.append(Pair("focus_tree", "=", focus_data))
            
            with open(strip(file_from), "w", encoding="utf-8-sig") as file:
                file.write(format(collected))

        focus.close()



    def clean(self):
        head, tail = os.path.split(self.path)
        base_dir = os.path.abspath(os.path.join(os.path.abspath(os.path.join(head, os.pardir)), os.pardir))

        try:
            os.remove(strip(self.path))
        except: pass

        try:
            os.remove(base_dir+"/common/ideas/"+tail+"_inline_ideas.txt")
        except: pass

        try:
            os.remove(base_dir+"/localisation/"+tail+"_inline_localisation_l_english.yml")
        except: pass



    def required_dir(self):
        return ["common/national_focus"]