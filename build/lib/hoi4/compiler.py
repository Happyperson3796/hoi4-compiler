from . import filetypes
import os
import shutil
import distutils.dir_util
import json

def scan(dir, parsed_files = []):
    for path in os.scandir(dir):
        if path.is_dir() and path.name != "Hoi4 modding tools":
            scan(path.path)
        elif filetypes.should_run(path.path):
            stringified_file = ""
            try:
                with open(path.path, "r") as file:
                    stringified_file = file.read()
            except:
                pass

            if stringified_file not in parsed_files:
                filetypes.get(path.path).run()

            if stringified_file != "":
                parsed_files.append(stringified_file)


class Build():
    def __init__(self, mod_path):
        self.mod = mod_path

        self.clean()

        self.parsed_files = []

        try:
            with open("build.hoi4", "r") as file:
                self.data = json.load(file)
        except:
            print("No build file found")
            self.data = {
                "excludes": [],
                "overrides": ""
            }

    def clean(self, dir=""):
        if dir == "": dir = self.mod
        for path in os.scandir(dir):
            if path.is_dir():
                self.clean(path.path)
            else:
                filetypes.get(path.path).clean()

    def exclude(self, text):
        if text in self.data["excludes"]:
            return True
        elif ".py" in text:
            return True
        elif ".pyr" in text:
            return True
        elif ".git" in text:
            return True
        elif len(text) > 0 and text[0] == "#":
            return True
        else:
            return False
        

    def apply_overrides(self):
        head, tail = os.path.split(self.mod)

        overrides = []
        for file in os.scandir(self.data["overrides"].replace("$USER", os.path.expanduser("~"))):
            if file.is_dir():
                if tail+"_overrides" in file.name:
                    overrides.append(file.path)
        overrides.sort(reverse=True)

        for override in overrides:
            print("Applying "+override+"...")
            for file in os.scandir(override):
                if not self.exclude(file.name):
                    if file.is_file():
                        shutil.copyfile(file.path, self.mod+"/"+file.name)
                    else:
                        distutils.dir_util.copy_tree(file.path, self.mod+"/"+file.name)
                    
            scan(self.mod, self.parsed_files)

    def build(self):
        scan(self.mod, self.parsed_files)
        self.apply_overrides()
