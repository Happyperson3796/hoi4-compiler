from .filetype import fileType
from .pdxscript import get, format, Pair, Collection, Value
import os
from .filetypes import fileType
from . import globals
import shutil
import json

class Formable(fileType):
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