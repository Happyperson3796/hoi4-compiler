from .filetype import fileType
from .pdxscript import get, format, Pair, Collection
import os
from .filetypes import fileType
import json

class Merged(fileType):
    def run(self):
        head, tail = os.path.split(self.path)
        
        with open(self.path, "r") as file:
            line = file.readlines()

            base_file = line[0].replace("#","").strip()

            reverse = line[1].strip()
            if (reverse == "#reverse = yes"): reverse = True
            
        with open(self.path, "r") as file:
            override = get(file.read())

        if not os.path.exists(head+"/"+base_file):
            open(head+"/"+base_file, "w").close() #Create if not found

        with open(head+"/"+base_file, "r") as file:
            base = get(file.read())

        override.merge(base, reverse)

        with open(head+"/"+base_file, "w") as file:
            file.write(format(override))


    def clean(self):
        head, tail = os.path.split(self.path)

        with open(self.path, "r") as file:
            base_file = file.readlines()[0].replace("#","").strip()

        try:
            os.remove(head+"/"+base_file)
        except: pass

        #try:
        #    os.remove(self.path) #removed for now, potentially unstable
        #except: pass
