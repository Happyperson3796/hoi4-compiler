from .filetype import fileType
from .pdxscript import get, format, Pair, Collection
import os
from .filetypes import fileType
from PIL import Image

class Nation(fileType):
    def run(self):
        head, tail = os.path.split(self.path)
        
        with open(self.path, "r", encoding="utf-8") as file:
            data = get(file.read())

            namespace = data.get("namespace").val()

            tag = data.get("tag").val()
            name = data.get("loc").val().get("$", False, True).val().replace("\"","")
            #name_def = data.get("loc").val().get("$_DEF", False, True).val().replace("\"","")
            #name_adj = data.get("loc").val().get("$_ADJ", False, True).val().replace("\"","")
            color = data.get("color").val()
            history = data.get("history").val()
            cores = data.get("cores").val()
        
        base = os.path.dirname(head).removesuffix("\\").removesuffix("/")

        filename = "dynamic_nations_"+namespace

        file_history = base+"/history/countries/"+tag+" - "+name+".txt"
        file_countries = base+"/common/countries/"+name+".txt"
        file_tags = base+"/common/country_tags/"+filename+"_tags.txt"
        file_colors = base+"/common/countries/"+name+"_color.merge"
        file_loc = base+"/localisation/"+filename+"_loc_l_english.yml"
        file_flag = base+"/gfx/flags/"+tag+".tga"
        file_cores = base+"/common/on_actions/"+filename+"_cores_on_actions.txt"

        try:
            with open(file_loc, "r+", encoding="utf-8-sig") as file:
                if len(file.readlines()) < 1:
                    file.write("l_english: ")
        except:
            with open(file_loc, "w", encoding="utf-8-sig") as file:
                file.write("l_english: ")

        with open(file_loc, "a+", encoding="utf-8-sig") as file:
            loc = data.get("loc").val()
            file.write("\n")
            for key in loc:
                key = str(key)
                if key.startswith("$"):
                    key = key.replace("$", tag, 1)

                key = key.replace(" = ", ":0 ", 1)
                file.write("\n  "+key)

        with open(file_history, "w") as file:
            file.write(format(history))

        with open(file_tags, "a") as file:
            file.write("\n"+tag+" = \"countries/"+name+".txt\"")

        with open(file_countries, "w") as file:
            file.write("graphical_culture = western_european_gfx\ngraphical_culture_2d = western_european_2d")
            file.write("\ncolor = "+str(color).replace("\n"," "))

        try:
            with open(file_colors, "r") as file:
                lines = file.readlines()
                if lines[0].strip() == "#colors.txt":
                    lines.pop(0)
        except:
            lines = []

        with open(file_colors, "w") as file:
            file.write("#colors.txt\n")
            file.write(tag+" = {\n    color = rgb "+str(color).replace("\n"," ")+"\n    color_ui = rgb "+str(color).replace("\n"," ")+"\n}\n")
            file.writelines(lines)

        try:
            with open(file_cores, "r") as file:
                lines = file.readlines()[3:-3]
        except:
            lines = []
            
        with open(file_cores, "w") as file:
            file.write("on_actions = {\n    on_startup = {\n        effect = {\n")
            #file.write("            every_state = {\n                limit = { is_core_of = "+tag+" }\n                remove_core_of = "+tag+"\n            }\n")
            for s in cores:
                file.write("            "+s.val()+" = { add_core_of = "+tag+" }\n")
            if len(lines) > 0: file.writelines(lines)
            file.write("        }\n    }\n}")


        head, tail = os.path.split(file_flag)

        try:
            os.makedirs(head+"/medium")
        except: pass
        try:
            os.makedirs(head+"/small")
        except: pass

        with Image.open(file_flag) as img:
            
            medium = img.resize((41,26))
            small = img.resize((10,7))

            medium.save(head+"/medium/"+tail)
            small.save(head+"/small/"+tail)








    def clean(self):
        head, tail = os.path.split(self.path)
        
        with open(self.path, "r", encoding="utf-8") as file:
            data = get(file.read())

            namespace = data.get("namespace").val()

            tag = data.get("tag").val()
            name = data.get("loc").val().get("$", False, True).val().replace("\"","")
            #name_def = data.get("loc").val().get("$_DEF", False, True).val().replace("\"","")
            #name_adj = data.get("loc").val().get("$_ADJ", False, True).val().replace("\"","")
            color = data.get("color").val()
            history = data.get("history").val()
            cores = data.get("cores").val()
        
        base = os.path.dirname(head).removesuffix("\\").removesuffix("/")

        filename = "dynamic_nations_"+namespace

        file_history = base+"/history/countries/"+tag+" - "+name+".txt"
        file_countries = base+"/common/countries/"+name+".txt"
        file_tags = base+"/common/country_tags/"+filename+"_tags.txt"
        file_colors = base+"/common/countries/"+name+"_color.merge"
        file_loc = base+"/localisation/"+filename+"_loc_l_english.yml"
        file_flag = base+"/gfx/flags/"+tag+".tga"
        file_cores = base+"/common/on_actions/"+filename+"_cores_on_actions.txt"

        try:
            os.remove(file_history)
        except: pass
        try:
            os.remove(file_countries)
        except: pass
        try:
            os.remove(file_tags)
        except: pass
        try:
            os.remove(file_colors)
        except: pass
        try:
            os.remove(file_loc)
        except: pass
        try:
            os.remove(file_cores)
        except: pass

        head, tail = os.path.split(file_flag)
        try:
            os.remove(head+"/medium/"+tail)
        except: pass
        try:
            os.remove(head+"/small/"+tail)
        except: pass


    def required_dir(self):
        return ["countries"]
    def blocked_dir(self):
        return ["history/countries"]