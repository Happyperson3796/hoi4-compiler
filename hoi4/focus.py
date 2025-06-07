from .filetype import fileType
from .pdxscript import get, format, Pair, Collection, Value
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

            inline_ideas = ""
            inline_loc = ""
            def traverse(x, parent):
                nonlocal inline_ideas
                nonlocal inline_loc
                if isinstance(x, Collection):
                    for y in x:
                        traverse(y, x)
                elif isinstance(x, Value):
                    traverse(x.val(), x)
                elif isinstance(x, Pair):
                    traverse(x[-1], x)


                    if x[0] == "define_idea":
                        idea: Collection = get(str(x))[0][-1].val()
                        parent.remove(x)

                        name = idea.extract("name")
                        idea.remove(idea.select("name"))

                        desc = idea.extract("desc", "")
                        if desc != "": idea.remove(idea.select("desc"))

                        id = idea.extract("id")
                        idea.remove(idea.select("id"))
                        
                        inline_loc += " "+id+": "+name+"\n"
                        if desc != "": inline_loc += " "+id+"_desc: "+desc+"\n"

                        inline_ideas += "\n        " + id +" = {"+(("\n"+format(idea)).replace("\n", "\n            ")).removesuffix("    ")+"}"
                        
            traverse(data, None)

            os.makedirs(head+"/common/ideas/", exist_ok=True)
            if os.path.exists(head+"/common/ideas/"+tail+"_inline_ideas.txt"):
                with open(head+"/common/ideas/"+tail+"_inline_ideas.txt", "r") as ideas:
                    lines = ideas.readlines()
                    inline_ideas = "".join(lines[2:-2]) + inline_ideas

            with open(head+"/common/ideas/"+tail+"_inline_ideas.txt", "w") as ideas:
                ideas.write("ideas = {\n    country = {\n" + inline_ideas.removeprefix("\n") + "\n    }\n}")


            os.makedirs(head+"/localisation/", exist_ok=True)            
            if os.path.exists(head+"/localisation/"+tail+"_inline_localisation.yml"):
                with open(head+"/localisation/"+tail+"_inline_localisation.yml", "r") as loc:
                    inline_loc = loc.read() + "\n" + inline_loc
            else: inline_loc = "l_english:\n" + inline_loc

            with open(head+"/localisation/"+tail+"_inline_localisation.yml", "w") as loc:
                loc.write(inline_loc)
            


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
        head, tail = os.path.split(self.path)

        try:
            os.remove(strip(self.path))
        except: pass

        try:
            os.remove(head+"/common/ideas/"+tail+"_inline_ideas.txt")
        except: pass

        try:
            os.remove(head+"/localisation/"+tail+"_inline_localisation.yml")
        except: pass