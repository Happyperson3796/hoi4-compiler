from .filetype import fileType
from ..pdxscript import get, format, Pair, Collection
import os
from ..filetypes import fileType
import json

class Appended(fileType):
    def run(self):
        head, tail = os.path.split(self.path)
        
        with open(self.path, "r") as file:
            text = file.readlines()
            base_file = text[0].replace("#","").strip()

            if text[1].startswith("#disable_override"): #Always append if #disable_override is set
                override_existing = False
            else: override_existing = True
            
        with open(self.path, "r") as file:
            override = get(file.read())

        if not os.path.exists(head+"/"+base_file):
            open(head+"/"+base_file, "w").close() #Create if not found

        with open(head+"/"+base_file, "r") as file:
            base = get(file.read())

        for x in override:
            if str(x) in str(base) and override_existing:
                continue
            base.append(x)

        with open(head+"/"+base_file, "w") as file:
            file.write(format(base))


    def clean(self):
        head, tail = os.path.split(self.path)

        with open(self.path, "r") as file:
            base_file = file.readlines()[0].replace("#","").strip()

        #try: #Mostly replaced by #override toggle
        #    os.remove(self.path)
        #except: pass
