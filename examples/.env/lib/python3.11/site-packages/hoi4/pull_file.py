from .filetype import fileType
from .pdxscript import get, format, Pair, Collection
import os
from .filetypes import fileType
from . import globals
import shutil

class Pulled(fileType):
    def run(self):
        head, tail = os.path.split(self.path)
        
        with open(self.path, "r") as file:
            lines = file.readlines()
            base_file = lines[0].replace("#","").strip()
            dest_file = lines[1].replace("#","").strip()
            lines.pop(1)
            lines.pop(0)

        if not os.path.exists(head+"/"+dest_file):
            try:
                shutil.copyfile(globals.vanilla_path+"/"+base_file, head+"/"+dest_file)
                if len(lines) > 0:
                    with open(head+"/"+dest_file, "r") as file:
                        content = file.readlines()
                    with open(head+"/"+dest_file, "w") as file:
                        file.writelines(lines)
                        file.writelines(content)
            except:
                open(head+"/"+base_file, "w").close() #Create if not found
                print("Unable to pull "+base_file)

    def clean(self):
        head, tail = os.path.split(self.path)

        with open(self.path, "r") as file:
            lines = file.readlines()
            base_file = lines[0].replace("#","").strip()
            dest_file = lines[1].replace("#","").strip()

        try:
            os.remove(head+"/"+dest_file)
        except: pass

        try:
            os.remove(self.path)
        except: pass
