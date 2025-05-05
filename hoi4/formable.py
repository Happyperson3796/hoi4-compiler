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

        name = data.extract("name")
        name_adj = data.extract("name_adj")
        name_def = data.extract("name_def")
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

        #os.makedirs(parent_dir+"/localisation/", exist_ok=True)
        #loc_file = parent_dir+"/localisation/"+namespace+"_dynamic_subideology_l_english.yml"

        #if not os.path.exists(loc_file):
        #    with open(loc_file, "w", encoding="utf-8-sig") as file:
        #        file.write("l_english:")

    def clean(self):
        head, tail = os.path.split(self.path)
        parent_dir = os.path.abspath(os.path.join(head, os.pardir))


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

        data = reformat(data)

        id = data.extract("id")
        data.remove(data.select("id"))

        return id, data