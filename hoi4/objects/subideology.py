from .filetype import fileType
from ..pdxscript import get, format, Pair, Collection, Value
import os
from .. import globals
import shutil

#Example/Template
"""
namespace = test

base = neutrality
id = technocracy

loc = {
    $ = "Technocracy"
    $_desc = "My ideology type's description" # Shows up when hovering over an ideology icon in-game
    USA_$ = "Sub-ideological Country"
}

def = {
    color = { 1 1 1 }
    can_be_randomly_selected = no
}
"""

class Subideology(fileType):
    def run(self):
        head, tail = os.path.split(self.path)
        parent_dir = os.path.abspath(os.path.join(head, os.pardir))
        
        with open(self.path, "r") as file:
            data = get(file.read())

        namespace = data.retrieve("namespace").val()
        base = data.retrieve("base").val()
        id = data.retrieve("id").val()
        loc = data.retrieve("loc").val()
        defines = data.retrieve("def", Value(Collection())).val()


        os.makedirs(parent_dir+"/interface/", exist_ok=True)
        os.makedirs(parent_dir+"/gfx/interface/ideologies/", exist_ok=True)
        if os.path.exists(parent_dir+"/gfx/interface/ideologies/"+id+".dds"):
            gfx_file = parent_dir+"/interface/"+namespace+"_dynamic_subideologies.gfx"

            if os.path.exists(gfx_file):
                with open(gfx_file, "r", encoding="utf-8-sig") as file:
                    gfx = get(file.read())
            else:
                gfx = get("spriteTypes = {}")

            gfx[0][-1].val().append(Pair("spriteType","=",Value(Collection([Pair("name","=",Value("GFX_ideology_"+id)),Pair("texturefile","=",Value("gfx/interface/ideologies/"+id+".dds"))]))))

            with open(gfx_file, "w", encoding="utf-8-sig") as file:
                file.write(format(gfx))
        else:
            print(id+" icon not found in /gfx/interface/ideologies/"+id+".dds")


        os.makedirs(parent_dir+"/localisation/", exist_ok=True)
        loc_file = parent_dir+"/localisation/"+namespace+"_dynamic_subideology_l_english.yml"

        if not os.path.exists(loc_file):
            with open(loc_file, "w", encoding="utf-8-sig") as file:
                file.write("l_english:")

        for l in loc:
            l[0] = l[0].replace("$",id,1)
            l[1] = ":"

            with open(loc_file, "a", encoding="utf-8-sig") as file:
                file.write("\n    "+str(l).replace(" :",":",1))


        for x in [globals.vanilla_path, parent_dir]:
            try:
                for path in os.scandir(x+"/common/ideologies/"):
                    if path.path.endswith(".txt"):
                        try:
                            with open(path.path, "r") as file:
                                get(file.read()).retrieve("ideologies").val().retrieve(base).val()
                                ideologies = path.path
                                break
                        except: pass
            except: pass

        with open(ideologies, "r") as file:
            ideologies_data = get(file.read())
            try:
                ideologies_data.retrieve("ideologies").val().retrieve(base).val().retrieve("types").val().retrieve(id).set(defines)
            except:
                try:
                    x = ideologies_data.retrieve("ideologies").val().retrieve(base).val().retrieve("types").val()
                except:
                    x = ideologies_data.retrieve("ideologies").val().retrieve(base).val()
                    x.append(Pair("types","=",Collection()))
                    x = ideologies_data.retrieve("ideologies").val().retrieve(base).val().retrieve("types").val()
                
                x.append(Pair(id,"=",defines))

        ihead, itail = os.path.split(ideologies)

        os.makedirs(parent_dir+"/common/ideologies/", exist_ok=True)

        with open(parent_dir+"/common/ideologies/"+itail, "w") as file:
            file.write(format(ideologies_data))




    def clean(self):
        head, tail = os.path.split(self.path)
        parent_dir = os.path.abspath(os.path.join(head, os.pardir))
        
        with open(self.path, "r") as file:
            data = get(file.read())

        namespace = data.retrieve("namespace").val()
        base = data.retrieve("base").val()
        id = data.retrieve("id").val()
        loc = data.retrieve("loc").val()
        defines = data.retrieve("def").val()

        gfx_file = parent_dir+"/interface/"+namespace+"_dynamic_subideologies.gfx"

        try:
            os.remove(gfx_file)
        except: pass

        loc_file = parent_dir+"/localisation/"+namespace+"_dynamic_subideology_l_english.yml"

        try:
            os.remove(loc_file)
        except: pass

        try:
            for path in os.scandir(parent_dir+"/common/ideologies/"):
                if path.path.endswith(".txt"):
                    try:
                        with open(path.path, "r") as file:
                            get(file.read()).retrieve("ideologies").val().retrieve(base).val()
                            ideologies = path.path
                            break
                    except: pass
        except: pass

        try:
            with open(ideologies, "r") as file:
                ideologies_data = get(file.read())
            i = -1
            for x in ideologies_data.retrieve("ideologies").val().retrieve(base).val().retrieve("types").val().copy():
                i += 1
                if x[0] == id:
                    ideologies_data.retrieve("ideologies").val().retrieve(base).val().retrieve("types").val().pop(i)
                    i -= 1

            with open(ideologies, "w") as file:
                file.write(format(ideologies_data))
        except:
            pass


    def required_dir(self):
        return ["subideologies"]
    def blocked_dir(self):
        return ["common/subideologies"]