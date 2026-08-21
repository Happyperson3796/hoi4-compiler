from .filetype import fileType
from ..pdxscript import get, format, Pair, Collection
import os
from .. import globals
import shutil

class Pulled(fileType):
    def execute(head: str, base_file: str, dest_file: str, lines=[]):
        dest_file = head+"/"+dest_file
        if not os.path.exists(dest_file):
            try:
                shutil.copyfile(globals.vanilla_path+base_file, dest_file)
                if len(lines) > 0:
                    with open(dest_file, "r") as file:
                        content = file.readlines()
                    with open(dest_file, "w") as file:
                        file.writelines(lines)
                        file.writelines(content)
            except:
                open(head+"/"+base_file, "w").close() #Create if not found
                print("\n\x1b[33;20mUnable to pull "+base_file+"\x1b[0m")

    def run(self):
        head, tail = os.path.split(self.path)
        
        with open(self.path, "r") as file:
            lines = file.readlines()
            base_file = lines[0].replace("#","").strip()
            dest_file = lines[1].replace("#","").strip()
            lines.pop(1)
            lines.pop(0)

        Pulled.execute(head, base_file, dest_file, lines)



    def clean(self):
        pass
        #head, tail = os.path.split(self.path)

        #with open(self.path, "r") as file:
        #    lines = file.readlines()
        #    base_file = lines[0].replace("#","").strip()
        #    dest_file = lines[1].replace("#","").strip()

        #try:
        #    os.remove(head+"/"+dest_file)
        #except: pass
