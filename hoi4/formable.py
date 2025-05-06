from .filetype import fileType
from .pdxscript import get, format, reformat, Pair, Collection
import os
from .filetypes import fileType
from . import globals
import shutil
import json

class Formable(fileType):
    def define(self):
        with open(self.path, "r") as file:
            data = get(file.read())[0]

        id = data[0]
        data = data[-1].val()

        return id, data

    def run(self):
        head, tail = os.path.split(self.path)
        parent_dir = os.path.abspath(os.path.join(head, os.pardir))

        id, data = self.define()

        namespace = data.extract("namespace")

        name = data.extract("name").replace("\"", "")
        name_adj = data.extract("name_adj").replace("\"", "")
        name_def = data.extract("name_def").replace("\"", "")
        name_extras = data.extract("name_extras", Collection())
        color = data.extract("color")
        allowed = data.extract("allowed")
        states = data.extract("states")
        extras = data.extract("extras", Collection())
        claims = data.extract("claims", Collection())
        gfx = data.extract("gfx", "GFX_decision_cat_generic_hre")
        exclusive = data.extract("exclusive", "no")
        on_formed = data.extract("on_formed", "")
        extra_reqs = data.extract("extra_reqs", "")

        os.makedirs(parent_dir+"/localisation/", exist_ok=True)
        loc_file = parent_dir+"/localisation/"+namespace+"_dynamic_formable_loc_"+"_l_english.yml"

        if not os.path.exists(loc_file):
            with open(loc_file, "w", encoding="utf-8-sig") as file:
                file.write("l_english:")

        with open(loc_file, "a", encoding="utf-8-sig") as file:
            template = f"""
  formable_{id}_category:0 "Form {name_def}"
  formable_{id}_category_desc:0 "Form {name_def}"
  formable_view_{id}:0 "View Cores"
  formable_form_{id}:0 "Form {name_def}"
  formable_apply_{id}:0 "Re-Apply Cosmetic"
  {id}_formable_cosmetic:0 "Akhand Bharat"
  {id}_formable_cosmetic_ADJ:0 "Bharatyan"
  {id}_formable_cosmetic_DEF:0 "{name_def}"
  formable_{id}_core:0 "Integrate [FROM.GetName]"
  formable_{id}_core_desc:0 "Cores [FROM.GetName] once over 50% compliance"


  
  formable_form_{id}_desc:0 "This is an exclusive formable! You will not be able to form any others after this.
"""
            file.write(template)


    def clean(self):
        head, tail = os.path.split(self.path)
        parent_dir = os.path.abspath(os.path.join(head, os.pardir))

        id, data = self.define()

        namespace = data.extract("namespace")

        try:
            os.remove(parent_dir+"/localisation/"+namespace+"_dynamic_formable_loc_"+"_l_english.yml")
        except:
            pass


    def required_dir(self):
        return ["formables"]
    def blocked_dir(self):
        return ["common/formables"]



class JsonFormable(Formable):
    def define(self):
        file = open(self.path, "r")
        data = json.loads(file.read())
        file.close()

        temp = {}
        for k in data.keys(): #Not case sensitive
            temp[k.lower()] = data[k]
        data = temp

        data["color"] = data["color"].removeprefix("rgb(").removesuffix(")").strip().replace(",", " ").replace("  ", " ").split(" ")

        data = reformat(data)

        id = data.extract("id")
        data.remove(data.select("id"))

        return id, data