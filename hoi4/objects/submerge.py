from .filetype import fileType
from ..pdxscript import get, format, Pair, Collection
import os
import json

class SubMerged(fileType):
    def run(self):
        head, tail = os.path.split(self.path)
        
        with open(self.path, "r") as file:
            line = file.readlines()

            base_file = line[0].replace("#","").strip()

            subpath = line[1].replace("#","").strip().split("/")

            reverse = line[2].strip()
            if (reverse == "#reverse = yes"): reverse = True
            
        with open(self.path, "r") as file:
            override = get(file.read())

        if not os.path.exists(head+"/"+base_file):
            open(head+"/"+base_file, "w").close() #Create if not found

        with open(head+"/"+base_file, "r") as file:
            base = get(file.read())
            subbase = base.retrieve(subpath[0])
            for p in subpath[1:]:
                subbase = subbase.val().retrieve(p)

        suboverride = override.retrieve(subpath[0])
        for p in subpath[1:]:
            suboverride = suboverride.val().retrieve(p)

        subbase.val().merge(suboverride.val(), reverse)

        with open(head+"/"+base_file, "w") as file:
            file.write(format(base))


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
